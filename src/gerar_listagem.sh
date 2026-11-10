#!/usr/bin/env bash
# Parte 1 - gera a listagem completa dos arquivos de um diretorio (raiz e subdiretorios
# aninhados) e redireciona a saida para um arquivo de texto.
#
#     ./gerar_listagem.sh [DIRETORIO] [ARQUIVO_SAIDA]
#
# find percorre a arvore recursivamente; -type f seleciona so arquivos regulares (sem
# diretorios); o ">" redireciona a saida padrao (stdout) para o arquivo, sobrescrevendo-o,
# e "2>/dev/null" descarta as mensagens de erro (stderr), como "Permissao negada".
set -euo pipefail

DIRETORIO="${1:-/usr/lib}"
SAIDA="${2:-listagem_arquivos.txt}"

find "$DIRETORIO" -type f > "$SAIDA" 2>/dev/null

echo "Diretorio listado : $DIRETORIO"
echo "Arquivo gerado    : $SAIDA"
echo "Total de arquivos : $(wc -l < "$SAIDA")"
