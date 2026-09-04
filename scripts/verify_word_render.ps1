param(
    [Parameter(Mandatory = $true)]
    [string]$Docx,
    [Parameter(Mandatory = $true)]
    [string]$OutputDirectory,
    [string]$PdfToPpmPath = ""
)

$ErrorActionPreference = "Stop"
$source = (Resolve-Path -LiteralPath $Docx).Path
$output = [IO.Path]::GetFullPath($OutputDirectory)
New-Item -ItemType Directory -Force -Path $output | Out-Null
$pdfNoUpdate = Join-Path $output "word-no-field-update.pdf"
$pdfUpdated = Join-Path $output "word-in-memory-field-update.pdf"
$manifest = Join-Path $output "word-verification.json"

function Compare-PdfRenders($firstPdf, $secondPdf, $directory, $converterOverride) {
    $converter = $converterOverride
    if ([string]::IsNullOrWhiteSpace($converter)) {
        $command = Get-Command pdftoppm -ErrorAction SilentlyContinue
        if ($null -eq $command) {
            throw "pdftoppm is required for page-image comparison. Pass -PdfToPpmPath explicitly."
        }
        $converter = $command.Source
    }
    if (-not (Test-Path -LiteralPath $converter -PathType Leaf)) {
        throw "pdftoppm was not found at: $converter"
    }
    $token = [Guid]::NewGuid().ToString("N")
    $firstPrefix = Join-Path $directory ("render-no-update-" + $token)
    $secondPrefix = Join-Path $directory ("render-field-update-" + $token)
    & $converter -png -r 144 $firstPdf $firstPrefix | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "pdftoppm failed for the no-update PDF." }
    & $converter -png -r 144 $secondPdf $secondPrefix | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "pdftoppm failed for the field-update PDF." }
    $firstPages = @(Get-ChildItem -LiteralPath $directory -Filter ((Split-Path $firstPrefix -Leaf) + "-*.png") | Sort-Object Name)
    $secondPages = @(Get-ChildItem -LiteralPath $directory -Filter ((Split-Path $secondPrefix -Leaf) + "-*.png") | Sort-Object Name)
    $equal = $firstPages.Count -eq $secondPages.Count
    $mismatches = [System.Collections.Generic.List[int]]::new()
    if ($equal) {
        for ($index = 0; $index -lt $firstPages.Count; $index++) {
            $leftHash = (Get-FileHash -LiteralPath $firstPages[$index].FullName -Algorithm SHA256).Hash
            $rightHash = (Get-FileHash -LiteralPath $secondPages[$index].FullName -Algorithm SHA256).Hash
            if ($leftHash -cne $rightHash) {
                $equal = $false
                $mismatches.Add($index + 1)
            }
        }
    }
    return [ordered]@{
        equal = $equal
        pageCountWithoutUpdate = $firstPages.Count
        pageCountWithUpdate = $secondPages.Count
        mismatchedPages = @($mismatches)
        converter = $converter
        dpi = 144
    }
}

function Get-FieldSnapshot($document) {
    $items = [System.Collections.Generic.List[object]]::new()
    foreach ($story in $document.StoryRanges) {
        $range = $story
        while ($null -ne $range) {
            foreach ($field in $range.Fields) {
                $items.Add([ordered]@{
                    storyType = $range.StoryType
                    code = ($field.Code.Text -replace "\s+", " ").Trim()
                    result = $field.Result.Text
                })
            }
            $range = $range.NextStoryRange
        }
    }
    return $items
}

function Update-AllFields($document) {
    for ($pass = 1; $pass -le 2; $pass++) {
        $document.Repaginate()
        foreach ($toc in $document.TablesOfContents) {
            $tocField = $toc.Range.Fields.Item(1)
            if (-not $tocField.Locked) { $toc.Update() }
        }
        foreach ($story in $document.StoryRanges) {
            $range = $story
            while ($null -ne $range) {
                if ($range.Fields.Count -gt 0) { $null = $range.Fields.Update() }
                $range = $range.NextStoryRange
            }
        }
        $null = $document.Fields.Update()
    }
    $document.Repaginate()
}

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
    $first = $word.Documents.Open($source, $false, $true)
    $first.Repaginate()
    $pagesBefore = $first.ComputeStatistics(2)
    $fieldsBefore = Get-FieldSnapshot $first
    $first.ExportAsFixedFormat($pdfNoUpdate, 17)
    $first.Close(0)

    $second = $word.Documents.Open($source, $false, $true)
    Update-AllFields $second
    $pagesAfter = $second.ComputeStatistics(2)
    $fieldsAfter = Get-FieldSnapshot $second
    $second.ExportAsFixedFormat($pdfUpdated, 17)
    $second.Close(0)

    $beforeJson = $fieldsBefore | ConvertTo-Json -Depth 6 -Compress
    $afterJson = $fieldsAfter | ConvertTo-Json -Depth 6 -Compress
    $configuration = Get-ItemProperty -LiteralPath "HKLM:\SOFTWARE\Microsoft\Office\ClickToRun\Configuration" -ErrorAction SilentlyContinue
    $productReleaseIds = [string]$configuration.ProductReleaseIds
    $word2024Installed = $productReleaseIds -match "2024"
    $wordExecutable = Join-Path $word.Path "WINWORD.EXE"
    $word2024DefaultComUsed = $word2024Installed -and (Test-Path -LiteralPath $wordExecutable -PathType Leaf)
    $renderComparison = Compare-PdfRenders $pdfNoUpdate $pdfUpdated $output $PdfToPpmPath
    $wordStatisticsEqual = $pagesBefore -eq $pagesAfter
    $stable = ($beforeJson -ceq $afterJson) -and $renderComparison.equal
    $report = [ordered]@{
        docx = $source
        sha256 = (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash
        productReleaseIds = $productReleaseIds
        word2024Installed = $word2024Installed
        wordExecutable = $wordExecutable
        word2024DefaultComUsed = $word2024DefaultComUsed
        wordVersion = $word.Version
        pagesBeforeFieldUpdate = $pagesBefore
        pagesAfterFieldUpdate = $pagesAfter
        wordStatisticsEqual = $wordStatisticsEqual
        fieldSnapshotsEqual = ($beforeJson -ceq $afterJson)
        renderedPagesEqual = $renderComparison.equal
        renderComparison = $renderComparison
        stable = $stable
        pdfWithoutUpdate = $pdfNoUpdate
        pdfWithInMemoryUpdate = $pdfUpdated
    }
    $report | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $manifest -Encoding utf8
    $report | ConvertTo-Json -Depth 6
    if (-not $stable) { exit 2 }
}
finally {
    $word.Quit()
}
