[CmdletBinding()]
param(
    [ValidateRange(1, 65535)]
    [int]$Port = 9222,

    [string]$ChromePath
)

$ErrorActionPreference = 'Stop'

function Get-ChromePath {
    param([string]$RequestedPath)

    if ($RequestedPath) {
        if (Test-Path -LiteralPath $RequestedPath -PathType Leaf) {
            return (Resolve-Path -LiteralPath $RequestedPath).Path
        }

        throw "The Chrome executable supplied with -ChromePath does not exist: $RequestedPath"
    }

    $candidates = @(
        (Get-Command chrome.exe -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source -First 1),
        (Get-Command chrome -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source -First 1),
        (Join-Path $env:ProgramFiles 'Google\Chrome\Application\chrome.exe'),
        (Join-Path ${env:ProgramFiles(x86)} 'Google\Chrome\Application\chrome.exe'),
        (Join-Path $env:LOCALAPPDATA 'Google\Chrome\Application\chrome.exe')
    ) | Where-Object { $_ }

    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate -PathType Leaf) {
            return (Resolve-Path -LiteralPath $candidate).Path
        }
    }

    return $null
}

try {
    $chrome = Get-ChromePath -RequestedPath $ChromePath
    if (-not $chrome) {
        throw @"
Google Chrome could not be found automatically.

Install Google Chrome, or tell your coding assistant where Chrome is installed by providing the full path to chrome.exe. For example:
  powershell -ExecutionPolicy Bypass -File .\.agents\scripts\start-research-chrome.ps1 -ChromePath 'C:\Program Files\Google\Chrome\Application\chrome.exe'

If you are using a chatbot app and it called this script, paste this error and the full path to chrome.exe into the chat. Do not provide a browser profile, password, or other private data.
"@
    }

    # This profile is task-only. It never opens or changes the user's normal
    # Chrome profile. Keep the port synchronized with .codex/config.toml.
    $profileDir = Join-Path ([System.IO.Path]::GetTempPath()) "codex-research-chrome-$Port"
    New-Item -ItemType Directory -Force -Path $profileDir | Out-Null

    Start-Process -FilePath $chrome -ArgumentList @(
        "--remote-debugging-port=$Port",
        "--user-data-dir=$profileDir",
        '--no-first-run',
        '--no-default-browser-check'
    )

    Write-Host "Started isolated research Chrome on CDP port $Port."
} catch {
    Write-Error $_.Exception.Message
    exit 1
}
