param(
    [Parameter(Mandatory = $true)][string]$Docx,
    [Parameter(Mandatory = $true)][string]$Report,
    [ValidateSet('right', 'justify')][string]$BodyAlignment = 'right',
    [ValidateSet('center', 'right')][string]$HeaderFooterAlignment = 'center',
    [string[]]$JustifyStyles = @('Normal', 'Body Text')
)

$ErrorActionPreference = 'Stop'
$source = (Resolve-Path -LiteralPath $Docx).Path
$reportPath = [IO.Path]::GetFullPath($Report)
$persian = [regex]'[\u0600-\u06FF]'
$wordRtl = 0
$wordLtr = 1
$alignLeft = 0
$alignCenter = 1
$alignRight = 2
$alignJustify = 3

function Test-Paragraph {
    param($Paragraph, [string]$Story, [bool]$UnifiedHeaderFooter = $false)
    $text = $Paragraph.Range.Text.Trim([char]13, [char]7, [char]12)
    if ([string]::IsNullOrWhiteSpace($text)) { return $null }
    $hasPersian = $persian.IsMatch($text)
    $expectedOrder = if ($hasPersian) { $wordRtl } else { $wordLtr }
    $style = ''
    try { $style = [string]$Paragraph.Style.NameLocal } catch { }
    $rowIndex = 0
    try { $rowIndex = [int]$Paragraph.Range.Cells.Item(1).RowIndex } catch { }
    $inTable = $rowIndex -gt 0
    $primaryTitle = $style -in @('Title', 'Heading 1')
    $expectedAlignment = if ($UnifiedHeaderFooter) {
        if ($HeaderFooterAlignment -eq 'center') { $alignCenter } elseif ($hasPersian) { $alignRight } else { $alignLeft }
    }
    elseif ($primaryTitle -or $rowIndex -eq 1) { $alignCenter }
    elseif ($BodyAlignment -eq 'justify' -and $hasPersian -and -not $inTable -and $style -in $JustifyStyles) { $alignJustify }
    elseif ($hasPersian) { $alignRight }
    else { $alignLeft }
    $actualOrder = [int]$Paragraph.Range.ParagraphFormat.ReadingOrder
    $actualAlignment = [int]$Paragraph.Range.ParagraphFormat.Alignment
    [pscustomobject]@{
        story = $Story
        text = $text.Substring(0, [Math]::Min(120, $text.Length))
        style = $style
        tableRow = $rowIndex
        expectedReadingOrder = $expectedOrder
        actualReadingOrder = $actualOrder
        expectedAlignment = $expectedAlignment
        actualAlignment = $actualAlignment
        passed = $actualOrder -eq $expectedOrder -and $actualAlignment -eq $expectedAlignment
    }
}

$hashBefore = (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash
$word = $null
$doc = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $doc = $word.Documents.Open($source, $false, $true, $false)
    $doc.Repaginate()
    $checks = @()
    foreach ($firstRange in $doc.StoryRanges) {
        $currentRange = $firstRange
        while ($null -ne $currentRange) {
            $storyType = [int]$currentRange.StoryType
            $isHeaderFooter = $storyType -in @(6, 7, 8, 9, 10, 11)
            foreach ($paragraph in $currentRange.Paragraphs) {
                $check = Test-Paragraph $paragraph "story-$storyType" $isHeaderFooter
                if ($null -ne $check) { $checks += $check }
            }
            try { $currentRange = $currentRange.NextStoryRange } catch { $currentRange = $null }
        }
    }
    $failures = @($checks | Where-Object { -not $_.passed })
    $hashAfter = (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash
    $result = [ordered]@{
        document = $source
        wordVersion = $word.Version
        pageCount = [int]$doc.ComputeStatistics(2)
        sourceSha256Before = $hashBefore
        sourceSha256After = $hashAfter
        sourceUnchanged = $hashBefore -ceq $hashAfter
        bodyAlignment = $BodyAlignment
        checkedParagraphs = $checks.Count
        failedParagraphs = $failures.Count
        passed = $failures.Count -eq 0 -and $hashBefore -ceq $hashAfter
        failures = $failures
    }
    [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($reportPath)) | Out-Null
    $result | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $reportPath -Encoding utf8
    $result | ConvertTo-Json -Depth 6
    if (-not $result.passed) { exit 1 }
}
finally {
    if ($null -ne $doc) { $doc.Close($false) }
    if ($null -ne $word) { $word.Quit() }
    if ($null -ne $doc) { [void][Runtime.InteropServices.Marshal]::ReleaseComObject($doc) }
    if ($null -ne $word) { [void][Runtime.InteropServices.Marshal]::ReleaseComObject($word) }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
