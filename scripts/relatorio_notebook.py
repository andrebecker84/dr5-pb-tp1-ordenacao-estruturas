# -*- coding: utf-8 -*-
"""Converte o notebook executado (andre_becker_PB_TP1.ipynb) no markdown do gerador do documento.

Usado por scripts/gerar_documento.py, que troca a linha "@@notebook" do docs/RELATORIO_TP1.md pelo
texto devolvido por converter(). Assim o PDF de entrega traz o mesmo conteudo do nbviewer: textos,
tabelas (inclusive as geradas pelas celulas), telas do terminal, graficos e trechos de codigo.

Dialeto de saida (o que o gerador entende):
  ## / ###                titulo de secao / subtitulo
  | a | b |               tabela; a linha seguinte "Tabela N. ..." vira legenda
  ```                     bloco de codigo
  @@imagem caminho | leg  imagem do projeto com legenda
  - item / 1. item        listas
"""
import html
import io
import json
import os
import re
from html.parser import HTMLParser

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTEBOOK = os.path.join(RAIZ, 'andre_becker_PB_TP1.ipynb')

EMOJI = re.compile('[\U0001F300-\U0001FAFF⌀-⏿☀-➿️‍]+')


# ------------------------------------------------------------------ HTML -> markdown
def inline(h):
    """Trecho HTML curto (celula de tabela, legenda) para markdown inline."""
    h = re.sub(r'<br\s*/?>', ' · ', h)
    h = re.sub(r'</?(b|strong)>', '**', h)
    h = re.sub(r'</?(i|em)>', '*', h)
    h = re.sub(r'<code>(.*?)</code>', lambda m: '`%s`' % re.sub(r'<[^>]+>', '', m.group(1)), h, flags=re.S)
    h = re.sub(r'<[^>]+>', '', h)
    t = html.unescape(h)
    t = t.replace('**`', '`').replace('`**', '`').replace('✅', 'sim')
    return re.sub(r'\s+', ' ', t).strip().replace('|', '/')


class _Tabela(HTMLParser):
    """Linhas de uma <table> como listas de HTML interno de cada celula, mais a <caption>."""

    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.linhas, self.cap, self._cel, self._prof, self._em_cap = [], '', None, 0, False
        self.estilos = []

    def handle_starttag(self, tag, attrs):
        if tag == 'tr':
            self.linhas.append([])
        elif tag in ('td', 'th') and self._cel is None:
            self._cel, self._prof = [], 0
            self.estilos.append(dict(attrs).get('style', ''))
            return
        elif tag == 'caption':
            self._em_cap = True
            return
        if self._cel is not None:
            self._cel.append(self.get_starttag_text())

    def handle_endtag(self, tag):
        if tag in ('td', 'th') and self._cel is not None:
            self.linhas[-1].append(''.join(self._cel))
            self._cel = None
        elif tag == 'caption':
            self._em_cap = False
        elif self._cel is not None:
            self._cel.append('</%s>' % tag)

    def handle_data(self, data):
        if self._em_cap:
            self.cap += data
        elif self._cel is not None:
            self._cel.append(data)

    def handle_entityref(self, name):
        self.handle_data('&%s;' % name)

    def handle_charref(self, name):
        self.handle_data('&#%s;' % name)


def tabela_md(h):
    """<table> HTML -> linhas de tabela markdown (+ legenda). Caixas de diagrama viram uma tabela
    com os titulos no cabecalho; setas entre caixas sao descartadas."""
    p = _Tabela()
    p.feed(h)
    linhas = [l for l in p.linhas if l]
    if not linhas:
        return []
    if 'border-top:4px' in h:                     # diagrama de caixas
        cel = [c for c in linhas[0] if 'font-weight:700' in c]
        cab = [inline(re.search(r'<div[^>]*>(.*?)</div>', c, re.S).group(1)) for c in cel]
        corpo = [inline(re.findall(r'<div[^>]*>(.*?)</div>', c, re.S)[1]) for c in cel]
        out = ['| ' + ' | '.join(EMOJI.sub('', x).strip() for x in cab) + ' |',
               '|' + '---|' * len(cab), '| ' + ' | '.join(corpo) + ' |']
        return out
    # Caminhos longos nao tem onde quebrar e estouram a coluna: um espaco de largura zero depois de
    # cada "/" deixa o Word quebrar a linha ali, sem mudar o texto visivel.
    cel = lambda c: re.sub(r'/(?=\S)', '/​', inline(c)) if len(inline(c)) > 30 else inline(c)
    cab = [inline(c) or ' ' for c in linhas[0]]
    out = ['| ' + ' | '.join(cab) + ' |', '|' + '---|' * len(cab)]
    for l in linhas[1:]:
        out.append('| ' + ' | '.join(cel(c) or ' ' for c in l) + ' |')
    if p.cap.strip():
        out += ['', inline(p.cap)]
    return out


def markdown_celula(src):
    """Celula markdown do notebook -> dialeto do gerador."""
    src = re.sub(r'<p align="right">.*?</p>', '', src, flags=re.S)       # "voltar ao sumario"
    src = re.sub(r'<a id="[^"]*"></a>', '', src)
    src = re.sub(r'<sub>.*?</sub>', '', src, flags=re.S)                  # nota de reproducao
    # <details> do mapa da rubrica: vira uma secao propria
    src = re.sub(r'<details>\s*<summary>.*?</summary>', '## Atendimento à rubrica\n', src, flags=re.S)
    src = src.replace('</details>', '')
    out = []
    for bloco in re.split(r'(<table.*?</table>)', src, flags=re.S):
        if bloco.startswith('<table'):
            out += [''] + tabela_md(bloco) + ['']
            continue
        for l in bloco.split('\n'):
            # destaques em citacao: o prefixo "> " sai; o titulo "💡 **Leitura.**" vira subtitulo
            if l.startswith('>'):
                l = l[1:].lstrip(' ') if not l.startswith('> ') else l[2:]
            m = re.match(r'^💡 \*\*(.+?)\.\*\*\s*$', l)
            if m:
                out.append('### ' + m.group(1))
                continue
            if l.startswith('#'):
                nivel, texto = re.match(r'^(#+)\s*(.*)$', l).groups()
                texto = EMOJI.sub('', texto).replace('`', '').strip()   # a faixa do titulo nao formata codigo
                if nivel == '#':
                    continue
                if texto.endswith('Referências'):
                    texto = 'Referências'
                if texto == 'Sumário':
                    continue
                out.append(('## ' if nivel == '##' else '### ') + texto)
                continue
            l = EMOJI.sub('', l).replace('  ', ' ') if l.lstrip().startswith(('📌',)) else l
            l = re.sub(r'\[([^\]]+)\]\(#[^)]*\)', r'\1', l)                 # ancoras internas
            l = l.replace('\\_', '_')
            # a celula que le o arquivo nao aparece no documento, so a tabela que ela monta
            l = l.replace('ordenação. A célula abaixo', 'ordenação. A tabela abaixo')
            l = l.replace('lê o arquivo com a mesma função usada pelos dois programas:',
                          'resume o arquivo, lido com a mesma função usada pelos dois programas:')
            l = l.replace('A célula abaixo', 'O código abaixo')
            l = l.replace('Como ler este notebook.', 'Origem dos números.')
            l = l.replace('✅', 'sim')
            out.append(l if l.startswith('```') else EMOJI.sub('', l).lstrip(' ') if l.lstrip().startswith('**') else EMOJI.sub('', l))
    return out


# ------------------------------------------------------------------ celulas de codigo
FONTE_VISIVEL = ('for nome, alg in ordenacao.ALGORITMOS', 'free list')   # codigo que interessa ler


def codigo_celula(c):
    src = ''.join(c['source'])
    out = []
    if any(m in src for m in FONTE_VISIVEL):
        # so a medicao; a montagem da tabela (tabela(...)) fica de fora, o resultado vem logo abaixo
        out += ['```'] + src.split('\ntabela(')[0].rstrip().split('\n') + ['```', '']
    figuras = re.findall(r"figura\('([^']+)',\s*'([^']+)'\)", src)
    graficos = re.findall(r"mostrar\('([^']+)'\)", src)
    for caminho, leg in figuras:
        out += ['@@imagem %s | %s' % (caminho, leg), '']
    pendentes = list(graficos)
    for o in c.get('outputs', []):
        dados = o.get('data', {})
        if o.get('output_type') == 'stream':
            if 'from apoio_notebook' in src:
                continue
            out += ['```'] + ''.join(o['text']).rstrip().split('\n') + ['```', '']
        elif 'text/html' in dados:
            h = ''.join(dados['text/html'])
            if '<figure' in h:
                continue                              # telas: ja inseridas pelo caminho
            if '<pre' in h:                           # codigo(): rotulo + fonte
                for rot, fonte in re.findall(r'<div[^>]*>(src/[^<]+)</div><pre[^>]*>(.*?)</pre>', h, re.S):
                    arq, faixa = html.unescape(rot).split(' · ')
                    out += ['Trecho de `%s` (%s)' % (arq, faixa), '```']
                    out += html.unescape(fonte).split('\n') + ['```', '']
                continue
            if '<table' in h:
                out += tabela_md(h) + ['']
                continue
            texto = inline(h)
            if texto.startswith('Gráfico') and pendentes:
                out += ['@@imagem evidencias/graficos/%s.png | %s' % (pendentes.pop(0), texto), '']
        elif 'image/png' in dados and not graficos:
            pass
    return out


def converter(caminho=NOTEBOOK):
    nb = json.load(io.open(caminho, encoding='utf-8'))
    out = []
    for i, c in enumerate(nb['cells']):
        if i == 0:
            continue                                   # capa do notebook: o documento tem a sua
        if c['cell_type'] == 'markdown':
            out += markdown_celula(''.join(c['source'])) + ['']
        else:
            out += codigo_celula(c)
    texto = '\n'.join(out)
    # o sumario do notebook (tabela de links internos) nao serve no papel
    texto = re.sub(r'\| *\| *Seção *\|.*?(?=\n\n)', '', texto, flags=re.S)
    return re.sub(r'\n{3,}', '\n\n', texto)


if __name__ == '__main__':
    print(converter())
