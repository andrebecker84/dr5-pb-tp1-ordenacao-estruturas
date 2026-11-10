# -*- coding: utf-8 -*-
"""Funcoes de apresentacao do notebook (tabelas, figuras, formatos e estilo dos graficos).

Nao mede nada: os numeros vem de resultados/*.json, gravados por ordenacao.py e estruturas.py
na execucao do Ubuntu (WSL2) mostrada nas figuras do terminal.
"""
import base64
import html
import inspect
import json
import os

import matplotlib as mpl
from IPython.display import HTML, display

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Paleta categorica validada (3 primeiras posicoes: passam em todos os pares, inclusive daltonismo).
AZUL, LARANJA, VERDE_AGUA = '#2a78d6', '#eb6834', '#1baf7a'
CINZA, TINTA, TINTA_2, GRADE = '#8a8985', '#0b0b0b', '#52514e', '#e4e3df'
CORES_ORD = {'Bubble Sort': AZUL, 'Selection Sort': LARANJA, 'Insertion Sort': VERDE_AGUA}
CORES_EST = {'Hashtable': AZUL, 'Pilha': LARANJA, 'Fila': VERDE_AGUA}


def estilo():
    mpl.rcParams.update({
        'figure.dpi': 120, 'savefig.dpi': 160, 'figure.facecolor': '#fcfcfb', 'axes.facecolor': '#fcfcfb',
        'font.family': 'DejaVu Sans', 'font.size': 10, 'axes.titlesize': 12, 'axes.titleweight': 'bold',
        'axes.titlelocation': 'left', 'axes.edgecolor': GRADE, 'axes.labelcolor': TINTA_2,
        'axes.spines.top': False, 'axes.spines.right': False, 'axes.grid': True, 'axes.axisbelow': True,
        'grid.color': GRADE, 'grid.linewidth': 0.8, 'xtick.color': TINTA_2, 'ytick.color': TINTA_2,
        'legend.frameon': False, 'lines.linewidth': 2, 'lines.markersize': 7,
    })


def carregar(nome):
    with open(os.path.join(RAIZ, 'resultados', nome), encoding='utf-8') as f:
        return json.load(f)


# ------------------------------------------------------------------ formatos pt-BR
def milhar(n):
    return f'{n:,.0f}'.replace(',', '.')


def seg(s):
    """Segundos em ms ou s, com virgula decimal."""
    txt = f'{s * 1000:.1f} ms' if s < 1 else f'{s:.3f} s'
    return txt.replace('.', ',')


def ns(v):
    if v < 1_000:
        txt = f'{v:.0f} ns'
    elif v < 1_000_000:
        txt = f'{v / 1_000:.1f} µs'
    else:
        txt = f'{v / 1_000_000:.2f} ms'
    return txt.replace('.', ',')


def mem(b):
    sinal, b = ('−' if b < 0 else ''), abs(b)
    if b < 1024:
        txt = f'{b:.0f} B'
    elif b < 1024 ** 2:
        txt = f'{b / 1024:.1f} KiB'
    else:
        txt = f'{b / 1024 ** 2:.2f} MiB'
    return sinal + txt.replace('.', ',')


# ------------------------------------------------------------------ blocos visuais
ESTILO_TAB = ('border-collapse:collapse;margin:6px 0 14px 0;font-size:13px;'
              'font-family:-apple-system,Segoe UI,Roboto,sans-serif')


def tabela(cabecalho, linhas, legenda=None, destaque=None, alinhar=None):
    """Tabela HTML compacta, alinhada a esquerda. `destaque`: indice de linha em negrito.
    `alinhar`: string com 'l'/'r' por coluna."""
    alinhar = alinhar or 'l' + 'r' * (len(cabecalho) - 1)
    al = {'l': 'left', 'r': 'right', 'c': 'center'}
    th = ''.join(f'<th style="text-align:{al[a]};padding:7px 12px;background:#1E3A8A;color:#fff;'
                 f'font-weight:600">{c}</th>' for c, a in zip(cabecalho, alinhar))
    corpo = ''
    for i, linha in enumerate(linhas):
        fundo = '#f3f6fc' if i % 2 else '#ffffff'
        peso = 'font-weight:700;' if destaque is not None and i == destaque else ''
        corpo += '<tr>' + ''.join(
            f'<td style="text-align:{al[a]};padding:6px 12px;border-bottom:1px solid #e4e3df;'
            f'background:{fundo};{peso}">{c}</td>' for c, a in zip(linha, alinhar)) + '</tr>'
    cap = (f'<caption style="caption-side:bottom;text-align:left;color:#52514e;font-size:12px;'
           f'padding-top:6px">{legenda}</caption>') if legenda else ''
    display(HTML(f'<table style="{ESTILO_TAB}">{cap}<thead><tr>{th}</tr></thead><tbody>{corpo}</tbody></table>'))


def figura(caminho, legenda, largura=900):
    """Embute a imagem no notebook (fica no .ipynb e no PDF exportado) com a legenda abaixo."""
    with open(os.path.join(RAIZ, caminho), 'rb') as f:
        dados = base64.b64encode(f.read()).decode()
    display(HTML(f'<figure style="margin:8px 0 18px 0"><img src="data:image/png;base64,{dados}" '
                 f'style="max-width:{largura}px;width:100%;border-radius:8px;'
                 f'box-shadow:0 2px 10px rgba(0,0,0,.18)"/><figcaption style="color:#52514e;'
                 f'font-size:12px;margin-top:6px">{legenda}</figcaption></figure>'))


def codigo(*objetos):
    """Codigo-fonte das funcoes/classes, lido do proprio arquivo em src/ (inspect), com as linhas."""
    for obj in objetos:
        linhas, inicio = inspect.getsourcelines(obj)
        arquivo = os.path.basename(inspect.getsourcefile(obj))
        _bloco(arquivo, inicio, inicio + len(linhas) - 1, ''.join(linhas).rstrip())


def _bloco(arquivo, inicio, fim, fonte):
    texto = html.escape(fonte)
    display(HTML(f'<div style="font-size:11px;color:#52514e;margin-top:4px">src/{arquivo} · linhas '
                 f'{inicio}–{fim}</div><pre style="background:#0f172a;color:#e2e8f0;padding:12px 14px;'
                 f'border-radius:8px;font-size:12px;line-height:1.45;overflow-x:auto">{texto}</pre>'))


def mostrar(nome):
    """Ajusta, grava o grafico em evidencias/graficos/<nome>.png (usado no README) e exibe."""
    import matplotlib.pyplot as plt
    pasta = os.path.join(RAIZ, 'evidencias', 'graficos')
    os.makedirs(pasta, exist_ok=True)
    plt.tight_layout()
    plt.savefig(os.path.join(pasta, nome + '.png'), bbox_inches='tight')
    plt.show()


def legenda_grafico(texto):
    display(HTML(f'<div style="color:#52514e;font-size:12px;margin:-4px 0 16px 0">{texto}</div>'))
