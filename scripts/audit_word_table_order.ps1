param(
    [Parameter(Mandatory = $true)]
    [string]$Docx,
    [Parameter(Mandatory = $true)]
    [string]$Report
)

$ErrorActionPreference = "Stop"
$source = (Resolve-Path -LiteralPath $Docx).Path
$sourceHashBefore = (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash
$reportPath = [IO.Path]::GetFullPath($Report)
$reportParent = Split-Path -Parent $reportPath
if ($reportParent) {
    New-Item -ItemType Directory -Force -Path $reportParent | Out-Null
}

$word = $null
$document = $null
$tables = [System.Collections.Generic.List[object]]::new()
$failures = [System.Collections.Generic.List[object]]::new()

function Get-CellText($cell) {
    return (($cell.Range.Text -replace "[\r\a]", "").Trim())
}

try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $document = $word.Documents.Open($source, $false, $true, $false)

    for ($tableIndex = 1; $tableIndex -le $document.Tables.Count; $tableIndex++) {
        $table = $document.Tables.Item($tableIndex)
        $headerCells = $table.Rows.Item(1).Cells
        $declaredColumns = $null
        try { $declaredColumns = [int]$table.Columns.Count } catch { }
        $positions = [System.Collections.Generic.List[object]]::new()
        for ($cellIndex = 1; $cellIndex -le $headerCells.Count; $cellIndex++) {
            $cell = $headerCells.Item($cellIndex)
            $probe = $cell.Range.Duplicate
            $probe.Collapse(1)
            $positions.Add([ordered]@{
                logicalColumn = $cellIndex
                text = Get-CellText $cell
                xPoints = [math]::Round([double]$probe.Information(5), 2)
                page = [int]$cell.Range.Information(3)
            })
            [void][Runtime.InteropServices.Marshal]::ReleaseComObject($probe)
        }

        $monotonicRightToLeft = $true
        for ($index = 1; $index -lt $positions.Count; $index++) {
            if ([double]$positions[$index - 1].xPoints -le [double]$positions[$index].xPoints) {
                $monotonicRightToLeft = $false
                break
            }
        }
        $maximumX = [double]::NegativeInfinity
        $minimumX = [double]::PositiveInfinity
        foreach ($position in $positions) {
            $positionX = [double]$position.xPoints
            if ($positionX -gt $maximumX) { $maximumX = $positionX }
            if ($positionX -lt $minimumX) { $minimumX = $positionX }
        }
        $firstIsRightmost = $positions.Count -le 1 -or [double]$positions[0].xPoints -eq $maximumX
        $lastIsLeftmost = $positions.Count -le 1 -or [double]$positions[$positions.Count - 1].xPoints -eq $minimumX
        $directionIsRtl = [int]$table.TableDirection -eq 0
        $headerShapeIsUniform = $null -eq $declaredColumns -or $declaredColumns -eq $positions.Count
        $passed = $directionIsRtl -and $headerShapeIsUniform -and $firstIsRightmost -and $lastIsLeftmost -and $monotonicRightToLeft

        $entry = [ordered]@{
            table = $tableIndex
            columns = $positions.Count
            declaredColumns = $declaredColumns
            tableDirection = [int]$table.TableDirection
            directionIsRtl = $directionIsRtl
            headerShapeIsUniform = $headerShapeIsUniform
            firstIsRightmost = $firstIsRightmost
            lastIsLeftmost = $lastIsLeftmost
            monotonicRightToLeft = $monotonicRightToLeft
            passed = $passed
            headerCells = @($positions)
        }
        $tables.Add($entry)
        if (-not $passed) { $failures.Add($entry) }
    }

    $tableCount = [int]$document.Tables.Count
    $document.Close($false)
    [void][Runtime.InteropServices.Marshal]::ReleaseComObject($document)
    $document = $null
    $sourceHashAfter = (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash
    $payload = [ordered]@{
        document = $source
        sourceSha256Before = $sourceHashBefore
        sourceSha256After = $sourceHashAfter
        sourceUnchanged = $sourceHashBefore -ceq $sourceHashAfter
        wordVersion = $word.Version
        tableCount = $tableCount
        failedTableCount = $failures.Count
        passed = $failures.Count -eq 0 -and $sourceHashBefore -ceq $sourceHashAfter
        tables = @($tables)
    }
    $payload | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $reportPath -Encoding utf8
    if (-not $payload.passed) {
        throw "Word table-order audit failed: $($failures.Count) table(s) failed or the source changed. See $reportPath"
    }
}
finally {
    if ($null -ne $document) { $document.Close($false) }
    if ($null -ne $word) { $word.Quit() }
    if ($null -ne $document) { [void][Runtime.InteropServices.Marshal]::ReleaseComObject($document) }
    if ($null -ne $word) { [void][Runtime.InteropServices.Marshal]::ReleaseComObject($word) }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
