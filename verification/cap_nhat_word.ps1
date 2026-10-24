$ErrorActionPreference = 'Stop'
$auditRoot = (Get-Location).Path
$auditDoc = Join-Path $auditRoot 'docs\BaoCao_QuanLyQuanCaPhe_DRAFT.docx'
$auditPdf = Join-Path $auditRoot 'verification\bao_cao_kiem_tra.pdf'
$auditWord = New-Object -ComObject Word.Application
$auditWord.Visible = $false
$auditWord.DisplayAlerts = 0
$auditDocument = $null
try {
    $auditDocument = $auditWord.Documents.Open($auditDoc, $false, $false)
    for ($auditPass = 1; $auditPass -le 3; $auditPass++) {
        $null = $auditDocument.Fields.Update()
        foreach ($auditToc in $auditDocument.TablesOfContents) { $auditToc.Update() }
        foreach ($auditFigures in $auditDocument.TablesOfFigures) { $auditFigures.Update() }
        $auditDocument.Repaginate()
    }
    $auditDocument.Save()
    $auditDocument.ExportAsFixedFormat($auditPdf,17)
    $auditResult = [ordered]@{
        time = (Get-Date).ToString('o')
        tool = 'Microsoft Word COM'
        word_version = $auditWord.Version
        pages = $auditDocument.ComputeStatistics(2)
        tables = $auditDocument.Tables.Count
        inline_shapes = $auditDocument.InlineShapes.Count
        tables_of_contents = $auditDocument.TablesOfContents.Count
        tables_of_figures = $auditDocument.TablesOfFigures.Count
        fields = $auditDocument.Fields.Count
        hyperlinks = $auditDocument.Hyperlinks.Count
        pdf = $auditPdf
    }
    $auditResult | ConvertTo-Json | Set-Content -LiteralPath 'verification\word_render.json' -Encoding UTF8
    $auditResult | ConvertTo-Json
} finally {
    if ($null -ne $auditDocument) { $auditDocument.Close(0) }
    $auditWord.Quit()
    [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($auditWord)
}
