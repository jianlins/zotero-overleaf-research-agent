#!/usr/bin/env python3
"""Safely merge Zotero Local API BibLaTeX exports into a manuscript bibliography.

The Local API is the only supported source.  It is read-only from Zotero's
perspective: this program writes only the local bibliography and key-lock file.
"""

from __future__ import annotations

import argparse
import difflib
import json
import os
import re
import sys
import tempfile
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple


LOCAL_API_DEFAULT = "http://127.0.0.1:23119/api/"
ITEM_KEY_RE = re.compile(r"_([A-Z0-9]{8})$")
CITE_RE = re.compile(r"\\[A-Za-z]*cite[A-Za-z*]*\s*(?:\[[^\]]*\]\s*)*\{([^}]*)\}")


class SyncError(Exception):
    """An actionable condition that prevents an unsafe bibliography update."""


@dataclass
class BibEntry:
    key: str
    raw: str
    start: int
    end: int

    @property
    def zotero_key(self) -> Optional[str]:
        match = ITEM_KEY_RE.search(self.key)
        return match.group(1) if match else None

    @property
    def doi(self) -> Optional[str]:
        value = bib_field(self.raw, "doi")
        return normalize_doi(value) if value else None


def validate_local_api(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise SyncError("--api-base must be an http://localhost loopback Local API URL")
    return url.rstrip("/") + "/"


def request(api_base: str, resource: str, params: Optional[Sequence[Tuple[str, str]]] = None) -> Tuple[bytes, object]:
    url = urllib.parse.urljoin(api_base, resource.lstrip("/"))
    if params:
        url += "?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return response.read(), response.headers
    except urllib.error.HTTPError as exc:
        raise SyncError(f"Zotero Local API returned HTTP {exc.code} for {resource}") from exc
    except urllib.error.URLError as exc:
        raise SyncError(
            "Cannot reach Zotero Local API. Start Zotero and enable “Allow other applications "
            "on this computer to communicate with Zotero”."
        ) from exc


def request_json(api_base: str, resource: str, params: Optional[Sequence[Tuple[str, str]]] = None) -> Tuple[object, object]:
    body, headers = request(api_base, resource, params)
    try:
        return json.loads(body.decode("utf-8")), headers
    except json.JSONDecodeError as exc:
        raise SyncError(f"Zotero Local API returned invalid JSON for {resource}") from exc


def scan_balanced(text: str, start: int, opener: str, closer: str) -> int:
    """Return the index just after a balanced BibTeX entry."""
    depth = 0
    quoted = False
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == '"':
            quoted = not quoted
            continue
        if quoted:
            continue
        if char == opener:
            depth += 1
        elif char == closer:
            depth -= 1
            if depth == 0:
                return index + 1
    raise SyncError("Unbalanced braces or parentheses in a .bib file")


def parse_bib_entries(text: str) -> List[BibEntry]:
    entries: List[BibEntry] = []
    cursor = 0
    while True:
        start = text.find("@", cursor)
        if start == -1:
            break
        header = re.match(r"@\s*([A-Za-z]+)\s*([\{(])\s*", text[start:])
        if not header:
            cursor = start + 1
            continue
        entry_type, opener = header.group(1).lower(), header.group(2)
        if entry_type in {"comment", "preamble", "string"}:
            cursor = start + len(header.group(0))
            continue
        key_start = start + len(header.group(0))
        comma = text.find(",", key_start)
        if comma == -1:
            raise SyncError("A BibTeX entry is missing the comma after its citation key")
        key = text[key_start:comma].strip()
        if not key:
            raise SyncError("A BibTeX entry has an empty citation key")
        closer = "}" if opener == "{" else ")"
        end = scan_balanced(text, start + len(header.group(0)) - 1, opener, closer)
        entries.append(BibEntry(key=key, raw=text[start:end], start=start, end=end))
        cursor = end
    if not entries:
        raise SyncError("No bibliographic entries found in .bib content")
    return entries


def bib_field(raw: str, field_name: str) -> Optional[str]:
    match = re.search(r"(?:^|,)\s*" + re.escape(field_name) + r"\s*=\s*", raw, re.IGNORECASE | re.MULTILINE)
    if not match:
        return None
    cursor = match.end()
    if cursor >= len(raw):
        return None
    delimiter = raw[cursor]
    if delimiter == "{":
        end = scan_balanced(raw, cursor, "{", "}")
        return raw[cursor + 1 : end - 1].strip()
    if delimiter == '"':
        cursor += 1
        value: List[str] = []
        escaped = False
        while cursor < len(raw):
            char = raw[cursor]
            if escaped:
                value.append(char)
                escaped = False
            elif char == "\\":
                value.append(char)
                escaped = True
            elif char == '"':
                return "".join(value).strip()
            else:
                value.append(char)
            cursor += 1
        raise SyncError("Unclosed quoted field in a .bib entry")
    end = raw.find(",", cursor)
    return raw[cursor : end if end != -1 else len(raw)].strip()


def normalize_doi(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", value)
    value = re.sub(r"^doi:\s*", "", value)
    return value.rstrip(" .")


def with_key(entry: BibEntry, citation_key: str) -> str:
    pattern = re.compile(r"^(\s*@\s*[A-Za-z]+\s*[\{(]\s*)[^,\s]+", re.DOTALL)
    revised, count = pattern.subn(r"\g<1>" + citation_key, entry.raw, count=1)
    if count != 1:
        raise SyncError(f"Cannot rewrite citation key for {entry.key}")
    return revised


def metadata_for_item(api_base: str, item_key: str) -> Dict[str, object]:
    payload, _ = request_json(api_base, f"users/0/items/{urllib.parse.quote(item_key, safe='')}", [("format", "json")])
    if not isinstance(payload, dict):
        raise SyncError(f"Zotero metadata response for {item_key} is not an object")
    data = payload.get("data", payload)
    if not isinstance(data, dict) or data.get("key") not in {None, item_key}:
        raise SyncError(f"Zotero metadata response does not identify item {item_key}")
    return data


def citation_fragment(value: object, fallback: str) -> str:
    normalized = unicodedata.normalize("NFKD", str(value or ""))
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    compact = re.sub(r"[^A-Za-z0-9]", "", ascii_value)
    return compact or fallback


def stable_new_key(metadata: Dict[str, object], zotero_key: str) -> str:
    """Create a readable, collision-proof key without using title text."""
    creators = metadata.get("creators")
    author = None
    if isinstance(creators, list):
        for creator in creators:
            if isinstance(creator, dict) and creator.get("creatorType") == "author":
                author = creator.get("lastName") or creator.get("name")
                break
    author_part = citation_fragment(author, "Anon")
    date_match = re.search(r"(?:15|16|17|18|19|20|21)\d{2}", str(metadata.get("date", "")))
    year_part = date_match.group(0) if date_match else "nodate"
    return f"{author_part}{year_part}_{zotero_key}"


def remove_field(raw: str, field_name: str) -> str:
    """Remove a BibTeX field without touching nested braces in its value."""
    pattern = re.compile(r"(?:^|,)\s*" + re.escape(field_name) + r"\s*=\s*", re.IGNORECASE | re.MULTILINE)
    while True:
        match = pattern.search(raw)
        if not match:
            return raw
        value_start = match.end()
        if value_start >= len(raw):
            raise SyncError(f"Malformed {field_name} field in a BibTeX entry")
        delimiter = raw[value_start]
        if delimiter == "{":
            value_end = scan_balanced(raw, value_start, "{", "}")
        elif delimiter == '"':
            cursor = value_start + 1
            escaped = False
            while cursor < len(raw):
                char = raw[cursor]
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    cursor += 1
                    break
                cursor += 1
            else:
                raise SyncError(f"Unclosed {field_name} field in a BibTeX entry")
            value_end = cursor
        else:
            comma = raw.find(",", value_start)
            value_end = comma if comma != -1 else len(raw)
        end = value_end
        while end < len(raw) and raw[end].isspace():
            end += 1
        if end < len(raw) and raw[end] == ",":
            end += 1
        raw = raw[: match.start()] + raw[end:]


def locked_entry_map(entries: Sequence[BibEntry], lock: Dict[str, str]) -> Dict[str, str]:
    by_citation_key = {citation_key: zotero_key for zotero_key, citation_key in lock.items()}
    if len(by_citation_key) != len(lock):
        raise SyncError("The citation-key lock maps multiple Zotero items to one citation key")
    current_keys = {entry.key for entry in entries}
    if current_keys != set(by_citation_key):
        raise SyncError(
            "The citation-key lock does not exactly match the current bibliography. Restore or explicitly "
            "reconcile the two before syncing."
        )
    return {by_citation_key[entry.key]: entry.key for entry in entries}


def load_lock(path: Path, server_id: str, current: Sequence[BibEntry]) -> Tuple[Dict[str, str], bool]:
    if not path.exists():
        return entry_map(current, "current bibliography"), True
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SyncError(f"Cannot read citation-key lock file {path}") from exc
    if data.get("schema") != 1 or not isinstance(data.get("entries"), dict):
        raise SyncError(f"{path} has an unsupported citation-key lock format")
    if data.get("server_id") != server_id:
        raise SyncError(
            "Zotero-Server-ID differs from the key lock. This appears to be a different Zotero database; "
            "review mappings before intentionally creating a new lock."
        )
    entries = data["entries"]
    if not all(isinstance(item, str) and isinstance(key, str) for item, key in entries.items()):
        raise SyncError(f"{path} has invalid citation-key mappings")
    return locked_entry_map(current, entries), False


def entry_map(entries: Sequence[BibEntry], label: str) -> Dict[str, str]:
    result: Dict[str, str] = {}
    keys_seen: Set[str] = set()
    for entry in entries:
        if entry.key in keys_seen:
            raise SyncError(f"Duplicate citation key {entry.key!r} in {label}")
        keys_seen.add(entry.key)
        zotero_key = entry.zotero_key
        if not zotero_key:
            raise SyncError(
                f"Citation key {entry.key!r} in {label} lacks the required _ZOTEROITEM suffix; "
                "add an explicit mapping before using strict sync."
            )
        if zotero_key in result and result[zotero_key] != entry.key:
            raise SyncError(f"Zotero item {zotero_key} maps to multiple citation keys in {label}")
        result[zotero_key] = entry.key
    return result


def item_keys_from_collection(api_base: str, collection: str) -> List[str]:
    payload, _ = request_json(api_base, f"users/0/collections/{urllib.parse.quote(collection, safe='')}/items/top", [("format", "json")])
    if not isinstance(payload, list):
        raise SyncError("Collection request did not return an item list")
    keys = []
    for item in payload:
        if isinstance(item, dict):
            key = item.get("key") or item.get("data", {}).get("key")
            if isinstance(key, str) and re.fullmatch(r"[A-Z0-9]{8}", key):
                keys.append(key)
    if not keys:
        raise SyncError(f"Collection {collection!r} contains no top-level Zotero items")
    return sorted(set(keys))


def export_biblatex(api_base: str, item_keys: Sequence[str]) -> Dict[str, BibEntry]:
    """Export one item at a time to bind output unambiguously to its Zotero key.

    Zotero's official BibLaTeX exporter is allowed to choose a human-readable
    citation key.  The item URL is therefore the authoritative identity; never
    infer identity from an exporter's citation-key pattern.
    """
    exported: Dict[str, BibEntry] = {}
    for item_key in item_keys:
        body, _ = request(
            api_base,
            f"users/0/items/{urllib.parse.quote(item_key, safe='')}",
            [("format", "biblatex")],
        )
        entries = parse_bib_entries(body.decode("utf-8"))
        if len(entries) != 1:
            raise SyncError(f"Zotero returned {len(entries)} BibLaTeX entries for item {item_key}")
        exported[item_key] = entries[0]
    return exported


def cited_keys(paths: Iterable[Path]) -> Set[str]:
    result: Set[str] = set()
    for path in paths:
        try:
            source = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise SyncError(f"Cannot read TeX source {path}") from exc
        for match in CITE_RE.finditer(source):
            result.update(key.strip() for key in match.group(1).split(",") if key.strip())
    return result


def replace_entries(original: str, replacements: Dict[str, str], entries: Sequence[BibEntry], additions: Sequence[str]) -> str:
    result: List[str] = []
    cursor = 0
    for entry in entries:
        result.append(original[cursor : entry.start])
        result.append(replacements.get(entry.key, entry.raw))
        cursor = entry.end
    result.append(original[cursor:])
    revised = "".join(result).rstrip() + "\n"
    if additions:
        revised += "\n" + "\n\n".join(addition.strip() for addition in additions) + "\n"
    return revised


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        handle.write(content)
        temporary = Path(handle.name)
    try:
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--collection", help="Zotero collection key to export")
    source_group.add_argument("--item-key", action="append", help="Zotero item key; repeat for multiple items")
    parser.add_argument("--current", type=Path, required=True, help="Current canonical references.bib")
    parser.add_argument("--lock", type=Path, required=True, help="Citation-key lock JSON file")
    parser.add_argument("--tex", type=Path, action="append", required=True, help="TeX source to validate; repeat as needed")
    parser.add_argument("--api-base", default=LOCAL_API_DEFAULT, help="Official Zotero Local API base URL")
    parser.add_argument("--apply", action="store_true", help="Write the merged bibliography and key lock; default is dry-run")
    args = parser.parse_args(argv)

    try:
        api_base = validate_local_api(args.api_base)
        _, headers = request(api_base, "")
        server_id = headers.get("Zotero-Server-ID")
        if not server_id:
            raise SyncError("Zotero Local API did not return Zotero-Server-ID; Zotero 10+ is required")

        current_text = args.current.read_text(encoding="utf-8")
        current_entries = parse_bib_entries(current_text)
        lock, creating_lock = load_lock(args.lock, server_id, current_entries)
        entries_by_citation_key = {entry.key: entry for entry in current_entries}
        current_by_item = {zotero_key: entries_by_citation_key[citation_key] for zotero_key, citation_key in lock.items()}
        current_doi_to_item = {
            entry.doi: zotero_key
            for zotero_key, entry in current_by_item.items()
            if entry.doi
        }

        item_keys = item_keys_from_collection(api_base, args.collection) if args.collection else args.item_key
        assert item_keys is not None
        item_keys = sorted(set(item_keys))
        if not all(re.fullmatch(r"[A-Z0-9]{8}", key) for key in item_keys):
            raise SyncError("Every --item-key must be an eight-character Zotero item key")
        incoming_entries = export_biblatex(api_base, item_keys)

        replacements: Dict[str, str] = {}
        additions: List[str] = []
        actions: List[Dict[str, str]] = []
        seen_new_keys: Set[str] = set()
        for zotero_key, incoming in incoming_entries.items():
            fixed_key = lock.get(zotero_key, stable_new_key(metadata_for_item(api_base, zotero_key), zotero_key))
            existing_for_key = next((item for item, key in lock.items() if key == fixed_key and item != zotero_key), None)
            if existing_for_key:
                raise SyncError(
                    f"Citation key {fixed_key!r} belongs to Zotero item {existing_for_key}, not {zotero_key}"
                )
            duplicate_item = current_doi_to_item.get(incoming.doi) if incoming.doi else None
            if duplicate_item and duplicate_item != zotero_key:
                raise SyncError(
                    f"DOI {incoming.doi} is already represented by Zotero item {duplicate_item}; "
                    f"incoming Zotero item {zotero_key} requires duplicate review"
                )
            revised = remove_field(with_key(incoming, fixed_key), "file")
            existing = current_by_item.get(zotero_key)
            if existing:
                replacements[existing.key] = revised
                actions.append({"action": "update", "zotero_item": zotero_key, "citation_key": fixed_key})
            else:
                if fixed_key in seen_new_keys or any(entry.key == fixed_key for entry in current_entries):
                    raise SyncError(f"New citation key conflict: {fixed_key!r}")
                additions.append(revised)
                seen_new_keys.add(fixed_key)
                lock[zotero_key] = fixed_key
                actions.append({"action": "add", "zotero_item": zotero_key, "citation_key": fixed_key})

        merged = replace_entries(current_text, replacements, current_entries, additions)
        merged_entries = parse_bib_entries(merged)
        available = {entry.key for entry in merged_entries}
        missing_citations = sorted(cited_keys(args.tex) - available)
        if missing_citations:
            raise SyncError("Cited keys absent after merge: " + ", ".join(missing_citations))

        report = {
            "ok": True,
            "mode": "apply" if args.apply else "dry-run",
            "server_id": server_id,
            "lock_created": creating_lock,
            "actions": actions,
            "cited_key_count": len(cited_keys(args.tex)),
        }
        print(json.dumps(report, indent=2, sort_keys=True))
        diff = "".join(
            difflib.unified_diff(
                current_text.splitlines(keepends=True), merged.splitlines(keepends=True),
                fromfile=str(args.current), tofile=str(args.current),
            )
        )
        if diff:
            print(diff, end="" if diff.endswith("\n") else "\n")
        else:
            print("No bibliography text changes.")

        if args.apply:
            atomic_write(args.current, merged)
            lock_content = json.dumps(
                {"schema": 1, "server_id": server_id, "entries": dict(sorted(lock.items()))},
                indent=2,
                sort_keys=True,
            ) + "\n"
            atomic_write(args.lock, lock_content)
        return 0
    except SyncError as exc:
        print(f"sync failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
