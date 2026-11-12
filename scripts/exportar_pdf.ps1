# Exporta andre_becker_PB_TP1.docx para PDF pelo proprio Word (mesma renderizacao do arquivo aberto).
#
#     powershell -ExecutionPolicy Bypass -File scripts/exportar_pdf.ps1
#
# Com documentos longos, o Word as vezes se desconecta do COM logo depois de exportar
# (RPC_E_DISCONNECTED ao fechar). O PDF ja esta gravado nesse ponto, entao o fechamento e tolerante
# a esse erro; o que decide o sucesso e o PDF ter sido regravado nesta execucao.
$ErrorActionPreference = 'Stop'
$raiz = Split-Path -Parent $PSScriptRoot
[string]$docx = Join-Path $raiz 'andre_becker_PB_TP1.docx'
[string]$pdf  = Join-Path $raiz 'andre_becker_PB_TP1.pdf'
$inicio = Get-Date

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
$doc = $null
try {
    $doc = $word.Documents.Open($docx, $false, $true)   # sem conversao, somente leitura
    $doc.Fields.Update() | Out-Null
    # 17 = PDF, 0 = impressao, 0 = documento inteiro, 0 = conteudo; IncludeDocProps grava titulo e
    # autor no PDF e CreateBookmarks = 1 transforma os titulos em marcadores.
    $doc.ExportAsFixedFormat($pdf, 17, $false, 0, 0, 1, 1, 0, $true, $true, 1, $true, $true, $false)
} finally {
    # Fecha so o que este script abriu; erros de desconexao aqui nao afetam o PDF ja exportado.
    if ($doc) { try { $doc.Close($false) } catch { } }
    try { $word.Quit() } catch { }
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
}

if ((Test-Path $pdf) -and ((Get-Item $pdf).LastWriteTime -ge $inicio)) {
    "gerado: $pdf"
} else {
    Write-Error "o PDF nao foi gerado nesta execucao: $pdf"
    exit 1
}
