param(
    [Parameter(Mandatory = $true)]
    [string]$PythonPath,
    [Parameter(Mandatory = $true)]
    [string]$WorkingDirectory
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$work = Join-Path ([IO.Path]::GetFullPath($WorkingDirectory)) ("word-table-order-" + [Guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Force -Path $work | Out-Null
$raw = Join-Path $work "ltr-negative.docx"
$hardened = Join-Path $work "rtl-positive.docx"
$positiveReport = Join-Path $work "positive.json"
$negativeReport = Join-Path $work "negative.json"

& $PythonPath (Join-Path $root "scripts\make_bidi_fixture.py") $raw
if ($LASTEXITCODE -ne 0) { throw "Fixture generation failed." }
& $PythonPath (Join-Path $root "scripts\harden_docx_bidi.py") $raw $hardened --mode auto
if ($LASTEXITCODE -ne 0) { throw "Fixture hardening failed." }

$auditor = Join-Path $root "scripts\audit_word_table_order.ps1"
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $auditor -Docx $hardened -Report $positiveReport
$positiveExit = $LASTEXITCODE
if ($positiveExit -ne 0) { throw "The positive RTL fixture failed the Word table-order audit." }

$oldPreference = $ErrorActionPreference
$ErrorActionPreference = "Continue"
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $auditor -Docx $raw -Report $negativeReport 2>$null
$negativeExit = $LASTEXITCODE
$ErrorActionPreference = $oldPreference
if ($negativeExit -eq 0) { throw "The negative LTR fixture incorrectly passed the Word table-order audit." }

[ordered]@{
    passed = $true
    workingDirectory = $work
    positiveReport = $positiveReport
    negativeReport = $negativeReport
} | ConvertTo-Json -Depth 4
