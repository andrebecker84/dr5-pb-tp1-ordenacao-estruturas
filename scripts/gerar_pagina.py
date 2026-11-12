# -*- coding: utf-8 -*-
"""Publica o notebook executado como pagina estatica do GitHub Pages (docs/index.html).

    uv run --no-project --python 3.12 --with nbconvert python scripts/gerar_pagina.py

O nbviewer busca o notebook pela API do GitHub com uma cota compartilhada por todos os usuarios do
servico; quando ela acaba, responde "503: GitHub API rate limit exceeded" para qualquer notebook. A
pagina gerada aqui e servida pelo proprio GitHub Pages (Settings > Pages > main, pasta /docs), sem
cota de terceiros: https://andrebecker84.github.io/dr5-pb-tp1-ordenacao-estruturas/

As celulas marcadas com "hide-input" (as que so montam tabelas, figuras e graficos) aparecem so com
a saida, como no notebook; o codigo dos programas continua visivel nos trechos de src/.
"""
import io
import os

import nbformat
from nbconvert import HTMLExporter
from nbconvert.preprocessors import TagRemovePreprocessor

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTEBOOK = os.path.join(RAIZ, 'andre_becker_PB_TP1.ipynb')
DESTINO = os.path.join(RAIZ, 'docs')
TITULO = 'PB-TP1 · Listagem, Ordenação e Estruturas de Dados · André Luis Becker'

nb = nbformat.read(NOTEBOOK, as_version=4)
nb.metadata['title'] = TITULO

exportador = HTMLExporter(template_name='lab')
remover = TagRemovePreprocessor(remove_input_tags={'hide-input'}, enabled=True)
exportador.register_preprocessor(remover, enabled=True)
corpo, _ = exportador.from_notebook_node(nb, resources={'metadata': {'name': TITULO}})

# Largura de leitura confortavel e respiro nas margens; o resto e o estilo padrao do Jupyter.
estilo = ('<style>body.jp-Notebook{max-width:1100px;margin:0 auto;padding:24px 28px 64px}'
          '.jp-InputPrompt,.jp-OutputPrompt{display:none}</style>')
corpo = corpo.replace('</head>', estilo + '</head>', 1)

os.makedirs(DESTINO, exist_ok=True)
with io.open(os.path.join(DESTINO, 'index.html'), 'w', encoding='utf-8', newline='\n') as f:
    f.write(corpo)
# Sem o .nojekyll o Pages passa a pasta pelo Jekyll, que ignora arquivos e pastas iniciados por "_".
io.open(os.path.join(DESTINO, '.nojekyll'), 'w').close()
print('gerado: %s (%.0f KB)' % (os.path.join(DESTINO, 'index.html'),
                                os.path.getsize(os.path.join(DESTINO, 'index.html')) / 1024))
