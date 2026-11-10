# Exporta andre_becker_PB_TP1.docx para PDF pelo proprio Word (mesma renderizacao do arquivo aberto).
#
#     powershell -ExecutionPolicy Bypass -File scripts/exportar_pdf.ps1
$raiz = Split-Path -Parent $PSScriptRoot
[string]$docx = Join-Path $raiz 'andre_becker_PB_TP1.docx'
[string]$pdf  = Join-Path $raiz 'andre_becker_PB_TP1.pdf'

$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Open($docx, $false, $true)   # sem conversao, somente leitura
    $doc.Fields.Update() | Out-Null
    # 17 = PDF, 0 = impressao, 0 = documento inteiro, 0 = conteudo; IncludeDocProps grava titulo e
    # autor no PDF e CreateBookmarks = 1 transforma os titulos em marcadores.
    $doc.ExportAsFixedFormat($pdf, 17, $false, 0, 0, 1, 1, 0, $true, $true, 1, $true, $true, $false)
    $doc.Close($false)
} finally {
    $word.Quit()
}
"gerado: $pdf"
