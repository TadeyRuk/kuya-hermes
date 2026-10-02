<#
.SYNOPSIS
  Install Kuya Hermes (persona + sari-sari-store skill + nightly report) into a local Hermes Agent.

.EXAMPLE
  # First time: creates a new Google Sheet, installs everything, schedules the 9 PM report
  powershell -ExecutionPolicy Bypass -File setup\install.ps1 -TelegramChatId 123456789

.EXAMPLE
  # Reuse an existing sheet, keep your current persona
  powershell -ExecutionPolicy Bypass -File setup\install.ps1 -SheetId 1abc... -SkipPersona
#>
param(
    [string]$SheetId,
    [string]$TelegramChatId,
    [switch]$SkipPersona
)

$ErrorActionPreference = 'Stop'
$Repo = Split-Path -Parent $PSScriptRoot
$HermesHome = if ($env:HERMES_HOME) { $env:HERMES_HOME } else { Join-Path $env:LOCALAPPDATA 'hermes' }
$Py = Join-Path $HermesHome 'hermes-agent\venv\Scripts\python.exe'
$GSetup = Join-Path $HermesHome 'skills\productivity\google-workspace\scripts\setup.py'
$SkillDst = Join-Path $HermesHome 'skills\productivity\sari-sari-store'
$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)

function Step($msg) { Write-Host "==> $msg" -ForegroundColor Cyan }

if (-not (Test-Path $Py)) { throw "Hermes not found at $HermesHome. Install Hermes Agent first." }
$env:HERMES_HOME = $HermesHome

Step 'Checking Google Workspace auth'
& $Py $GSetup --check
if ($LASTEXITCODE -ne 0) { throw 'Google not authenticated. Set up the google-workspace skill first (see README).' }

if (-not $SheetId) {
    Step 'Creating Google Sheet'
    $json = & $Py (Join-Path $Repo 'setup\create_sheet.py') | Out-String
    if ($LASTEXITCODE -ne 0) { throw "Sheet creation failed:`n$json" }
    $SheetId = ($json | ConvertFrom-Json).spreadsheetId
}
$SheetUrl = "https://docs.google.com/spreadsheets/d/$SheetId/edit"

Step "Installing skill to $SkillDst"
New-Item -ItemType Directory -Force (Join-Path $SkillDst 'scripts') | Out-Null
Copy-Item (Join-Path $Repo 'skill\sari-sari-store\scripts\store.py') (Join-Path $SkillDst 'scripts\store.py') -Force
$skill = [IO.File]::ReadAllText((Join-Path $Repo 'skill\sari-sari-store\SKILL.md'), $Utf8NoBom)
$skill = $skill.Replace('{{PYTHON}}', ($Py -replace '\\', '/'))
$skill = $skill.Replace('{{STORE_PY}}', ((Join-Path $SkillDst 'scripts\store.py') -replace '\\', '/'))
$skill = $skill.Replace('{{SHEET_URL}}', $SheetUrl)
[IO.File]::WriteAllText((Join-Path $SkillDst 'SKILL.md'), $skill, $Utf8NoBom)
[IO.File]::WriteAllText((Join-Path $SkillDst 'sheet_id.txt'), $SheetId, $Utf8NoBom)

if (-not $SkipPersona) {
    $soul = Join-Path $HermesHome 'SOUL.md'
    if (Test-Path $soul) {
        $bak = "$soul.bak-$(Get-Date -Format yyyyMMdd-HHmmss)"
        Copy-Item $soul $bak
        Step "Backed up existing persona to $bak"
    }
    Step 'Installing Kuya Hermes persona'
    Copy-Item (Join-Path $Repo 'persona\SOUL.md') $soul -Force
}

if ($TelegramChatId) {
    $existing = hermes cron list 2>&1 | Out-String
    if ($existing -match 'Sari-sari nightly report') {
        Step 'Nightly report job already exists, skipping'
    } else {
        Step 'Scheduling 9 PM nightly report'
        $prompt = 'Daily store report for the owner. Run the sari-sari-store skill''s summary command for today, then send a short Taglish recap: cash sales, utang given, utang collected, top items, low-stock items to reorder, and total outstanding utang with the top 3 customers. If there were no transactions today, say so in one line. Do not log or change anything.'
        hermes cron create '0 21 * * *' $prompt --name 'Sari-sari nightly report' --skill sari-sari-store --deliver "telegram:$TelegramChatId"
    }
}

Step 'Smoke test'
& $Py (Join-Path $SkillDst 'scripts\store.py') utang

Write-Host ''
Write-Host "Done. Sheet: $SheetUrl" -ForegroundColor Green
Write-Host 'Next: run  hermes gateway restart  then send /new to the bot in Telegram.'
