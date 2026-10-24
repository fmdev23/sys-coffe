$ErrorActionPreference = 'Stop'
$auditWord = New-Object -ComObject Word.Application
$auditWord.Visible = $false
$auditWord.DisplayAlerts = 0
$auditDocument = $null
try {
    $auditPath = Join-Path (Get-Location).Path 'docs\BaoCao_QuanLyQuanCaPhe_DRAFT.docx'
    if (-not (Test-Path -LiteralPath $auditPath)) {
        $auditPath = Join-Path (Get-Location).Path 'docs\BaoCao_QuanLyQuanCaPhe_FINAL.docx'
    }
    $auditDocument = $auditWord.Documents.Open($auditPath,$false,$true)
    $auditFields = @()
    foreach ($auditField in $auditDocument.Fields) {
        $auditMatch = [regex]::Match($auditField.Code.Text,'PAGEREF\s+([^\s]+)')
        if ($auditMatch.Success) {
            $auditAnchor = $auditMatch.Groups[1].Value
            $auditActualPage = $auditDocument.Bookmarks.Item($auditAnchor).Range.Information(1)
            $auditCached = $auditField.Result.Text.Trim()
            $auditFields += [ordered]@{bookmark=$auditAnchor;cached_page=$auditCached;actual_page=$auditActualPage;matches=($auditCached -eq [string]$auditActualPage)}
        }
    }
    $auditRows = @()
    $auditTableNumber = 0
    foreach ($auditTable in $auditDocument.Tables) {
        $auditTableNumber++
        foreach ($auditRow in $auditTable.Rows) {
            $auditRange = $auditRow.Range.Duplicate
            $auditRange.End = $auditRange.End - 1
            $auditFirst = $auditRange.Duplicate
            $auditFirst.Collapse(1)
            $auditLast = $auditRange.Duplicate
            $auditLast.Collapse(0)
            $auditStartPage = $auditFirst.Information(3)
            $auditEndPage = $auditLast.Information(3)
            $auditRows += [ordered]@{table=$auditTableNumber;row=$auditRow.Index;first_page=$auditStartPage;last_page=$auditEndPage;not_split=($auditStartPage -eq $auditEndPage)}
        }
    }
    [ordered]@{
        time=(Get-Date).ToString('o')
        opened_read_only=$true
        page_references=$auditFields
        rows=$auditRows
        fields_match=(@($auditFields | Where-Object {-not $_.matches}).Count -eq 0)
        no_split_rows=(@($auditRows | Where-Object {-not $_.not_split}).Count -eq 0)
        word_version=$auditWord.Version
    } | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath 'verification\truong_word.json' -Encoding UTF8
    Write-Output ('PAGEREF: '+$auditFields.Count+', rows: '+$auditRows.Count)
} finally {
    if ($null -ne $auditDocument) {$auditDocument.Close(0)}
    $auditWord.Quit()
    [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($auditWord)
}
