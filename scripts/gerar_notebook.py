# -*- coding: utf-8 -*-
"""Monta e executa andre_becker_PB_TP1.ipynb.

    uv run --no-project --python 3.12 --with nbformat --with nbclient --with ipykernel --with matplotlib python scripts/gerar_notebook.py

Os numeros citados no texto vem de resultados/*.json (a execucao do Ubuntu mostrada nas figuras),
entao texto, tabelas e graficos sempre concordam.
"""
import json
import os
import re
import sys

import nbformat
from nbclient import NotebookClient

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(RAIZ, 'andre_becker_PB_TP1.ipynb')
REPO = 'https://github.com/andrebecker84/dr5-pb-tp1-ordenacao-estruturas'


def ler(nome):
    with open(os.path.join(RAIZ, 'resultados', nome), encoding='utf-8') as f:
        return json.load(f)


O, E = ler('ordenacao.json'), ler('estruturas.json')
sys.path.insert(0, os.path.join(RAIZ, 'src'))
from apoio_notebook import milhar, seg, ns, mem  # noqa: E402

N = O['n']
P = O['principal_s']
B, S, I = P['Bubble Sort'], P['Selection Sort'], P['Insertion Sort']
INV = O['inversoes']
PARES = O['pares']
C = O['cenarios_s']
EH, EP, EF = (E['estruturas'][k] for k in ('Hashtable', 'Pilha', 'Fila'))
TAB = EH['tabela']
pct = lambda x: f'{x:.1%}'.replace('.', ',')
num = lambda x, d=1: f'{x:.{d}f}'.replace('.', ',')
cons = lambda e, k: next(c for c in e['consultas'] if c['posicao'] == k)

REPO_BADGES = ''.join(
    f'<img src="https://img.shields.io/badge/{b}" /> ' for b in [
        'Ubuntu-24.04.5%20LTS%20(WSL2)-E95420?style=flat-square&logo=ubuntu&logoColor=white',
        f'Python-{O["python"]}-3776AB?style=flat-square&logo=python&logoColor=white',
        'depend%C3%AAncias-s%C3%B3%20biblioteca%20padr%C3%A3o-3776AB?style=flat-square',
        'editor-GNU%20nano%207.2-4D4D4D?style=flat-square&logo=gnu&logoColor=white',
        f'listagem-{milhar(N).replace(".", "%2E")}%20arquivos-1E3A8A?style=flat-square',
        'Big%20O-O(1)%20%C2%B7%20O(N)%20%C2%B7%20O(N%C2%B2)-6250D6?style=flat-square',
    ])

celulas = []
VOLTAR = '<p align="right"><sub><a href="#sumario">⬆ voltar ao sumário</a></sub></p>\n\n'
REP = E['repeticoes']


def _caixa(titulo, corpo, cor):
    """Caixa de diagrama em HTML (o desenho em ASCII desalinha conforme a fonte do visualizador)."""
    return (f'<td style="border:1px solid #d9dce3;border-top:4px solid {cor};border-radius:6px;padding:10px 14px;'
            f'vertical-align:top;background:#fbfcfe"><div style="font-weight:700;color:#1E3A8A;margin-bottom:4px">'
            f'{titulo}</div><div style="font-size:12.5px;color:#34332f;line-height:1.55">{corpo}</div></td>')


def _seta(rotulo=''):
    return (f'<td style="text-align:center;vertical-align:middle;color:#52514e;font-size:12px;padding:0 6px;'
            f'border:none">{rotulo}<div style="font-size:22px;line-height:1">➜</div></td>')


def _no(texto):
    return (f'<span style="display:inline-block;border:1px solid #9fb3d9;border-radius:4px;padding:1px 6px;'
            f'background:#fff;font-family:monospace;font-size:12px">{texto}</span>')


def _cartao(valor, texto, cor):
    return (f'<td style="padding:10px 16px;border-left:4px solid {cor};background:#f6f8fc;vertical-align:top">'
            f'<div style="font-size:21px;font-weight:700;color:#1E3A8A;line-height:1.2">{valor}</div>'
            f'<div style="font-size:12px;color:#52514e;margin-top:3px">{texto}</div></td>')


def _inline(t):
    t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
    t = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'(?<![\w*])\*([^*]+)\*(?![\w*])', r'<i>\1</i>', t)
    return re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', t)


def _tabela(linhas):
    cel = [[c.strip() for c in l.strip().strip('|').split('|')] for l in linhas]
    cab, corpo = cel[0], cel[2:]
    th = ''.join(f'<th style="text-align:left;padding:7px 12px;background:#1E3A8A;color:#fff">{_inline(c)}</th>'
                 for c in cab) if any(cab) else ''
    tr = ''.join('<tr>' + ''.join(f'<td style="text-align:left;padding:6px 12px;border-bottom:1px solid #e4e3df">'
                                  f'{_inline(c)}</td>' for c in l) + '</tr>' for l in corpo)
    thead = f'<thead><tr>{th}</tr></thead>' if th else ''
    return (f'<table style="margin-left:0;margin-right:auto;border-collapse:collapse;font-size:13px">'
            f'{thead}<tbody>{tr}</tbody></table>')


def tabelas_em_html(texto):
    """Tabelas markdown viram HTML alinhado a esquerda (Jupyter e VS Code centralizam as de markdown)."""
    saida, bloco, em_codigo = [], [], False
    for l in texto.split('\n') + ['']:
        if l.startswith('```'):
            em_codigo = not em_codigo
        if l.startswith('|') and not em_codigo:
            bloco.append(l)
            continue
        if bloco:
            saida.append(_tabela(bloco))
            bloco = []
        saida.append(l)
    return '\n'.join(saida[:-1])


def md(t):
    celulas.append(nbformat.v4.new_markdown_cell(tabelas_em_html(t.strip('\n'))))


def leitura(t, titulo='Leitura'):
    """Analise em destaque: bloco de citacao com o titulo em negrito."""
    linhas = t.strip('\n').split('\n')
    corpo = '\n'.join('> ' + l if l.strip() else '>' for l in linhas)
    md(f'> 💡 **{titulo}.**\n>\n{corpo}')


def py(t):
    """Celulas que so montam figuras, tabelas e graficos ficam com o codigo recolhido (a saida aparece)."""
    c = nbformat.v4.new_code_cell(t.strip('\n'))
    so_apresentacao = (t.lstrip().startswith(('figura(', 'codigo(')) or 'plt.' in t or 'from apoio_notebook' in t
                       or "est = E['estruturas']" in t or 'ops = {' in t or 'ordenacao.ler_listagem' in t)
    if so_apresentacao:
        c.metadata['jupyter'] = {'source_hidden': True}
        c.metadata['tags'] = ['hide-input']
    celulas.append(c)

# =====================================================================================  CAPA
md(f"""
<img src="https://capsule-render.vercel.app/api?section=header&type=waving&color=0:1E3A8A,100:2A78D6&height=190&text=Listagem%2C%20Ordena%C3%A7%C3%A3o%20e%20Estruturas&fontSize=44&fontColor=ffffff&fontAlignY=36&desc=Projeto%20de%20Bloco%20%C2%B7%20PB-TP1&descAlignY=58&descSize=17" width="100%" />

# 🗂️ Listagem, Ordenação e Estruturas de Dados

**Do terminal Linux à análise Big O: 17 mil caminhos de arquivo ordenados com Bubble, Selection e Insertion Sort e armazenados em Hashtable, Pilha e Fila**

{REPO_BADGES}

| | |
|---|---|
| **Aluno** | André Luis Becker |
| **Professor** | Ricardo Pires Mesquita |
| **Disciplina** | DR5 · Projeto de Bloco: Ciência da Computação |
| **Bloco · Trimestre** | Ciência da Computação · 26E4 |
| **Turma** | GRLENGR2C2-N2-L1 |
| **Repositório** | [{REPO.split('github.com/')[1]}]({REPO}) |
| **Entrega** | `andre_becker_PB_TP1.pdf` · fontes em [`src/`]({REPO}/tree/main/src) · listagem completa em [`listagem_arquivos.txt`]({REPO}/blob/main/listagem_arquivos.txt) |

#### ✨ Destaques

<table style="border-collapse:separate;border-spacing:8px 0;margin-left:-8px"><tr>
{_cartao(milhar(N), 'arquivos listados com <code>find</code><br>em /usr/lib', '#1E3A8A')}
{_cartao(seg(I), 'Insertion Sort, o mais rápido<br>dos três O(N²)', '#1baf7a')}
{_cartao(num(B / I) + '×', 'Bubble ÷ Insertion:<br>mesma classe, constantes diferentes', '#eb6834')}
{_cartao(ns(max(c['tempo_ns'] for c in EH['consultas'])), 'consulta na hashtable,<br>qualquer posição: O(1)', '#2a78d6')}
{_cartao(f"{EP['carga']['memoria'][0] / N:.0f} / {EH['carga']['memoria'][0] / N:.0f} B", 'memória por item:<br>pilha e fila / hashtable', '#6250D6')}
</tr></table>
""")

md("""
<a id="sumario"></a>

## 📚 Sumário

| | Seção | | Seção |
|:-:|---|:-:|---|
| 1 | [Visão geral e ambiente](#visao) | 6 | [Programa 2: lógica e funcionamento](#p2) |
| 2 | [Parte 1: listagem no Linux](#parte1) | 7 | [Programa 2: posições, tempo e memória](#p2res) |
| 3 | [Editor não gráfico](#editor) | 8 | [Teoria × prática: quadro comparativo](#comparativo) |
| 4 | [Programa 1: lógica e Big O](#p1) | 9 | [Conclusão](#conclusao) |
| 5 | [Programa 1: tempos e análise](#p1res) | 10 | [Referências](#referencias) |

<details>
<summary><b>🎯 Mapa da rubrica</b> · onde cada um dos 25 critérios é atendido (clique para abrir)</summary>

| Critérios | O que pedem | Onde está |
|---|---|---|
| 1 a 3 | print do terminal, comando de listagem e script com redirecionamento | [Seção 2](#parte1), Figuras 1 e 2 |
| 4 a 7 | programa que lê o arquivo e os três algoritmos de ordenação | [Seção 4](#p1), código e Figura 3 |
| 8, 10, 11 | lógica do programa e Big O calculado e explicado | [Seção 4](#p1), resumo teórico |
| 9, 12 | tempo de cada ordenação e comparação com a teoria | [Seção 5](#p1res), Tabelas 1 a 4, Gráficos 1 a 3 |
| 17 a 19, 24 | pilha, fila e hashtable e a lógica do programa | [Seção 6](#p2), código e Figura 4 |
| 20 a 22 | arquivos nas posições 1, 100, 1.000, 5.000 e última, por estrutura | [Seção 7.1](#p2res), Tabelas 5 a 7, Figura 6 |
| 13 a 16, 23 | tempo e memória das tarefas, adição e remoção, explicação | [Seção 7](#p2res), Tabelas 8 a 11, Gráficos 4 e 5 |
| 25 | relatório com tabelas e gráficos | todo o notebook e o [quadro comparativo](#comparativo) |

</details>
""")

# =====================================================================================  1. VISÃO GERAL
md(f"""
<a id="visao"></a>

## 🧭 1 · Visão geral e ambiente

O trabalho é um pipeline de três etapas, todas executadas no meu terminal, o **WezTerm** com o Ubuntu do
WSL2 e o shell **fish**:

<table style="border-collapse:separate;border-spacing:0;margin:6px 0 12px 0"><tr>
{_caixa('🐧 Parte 1 · bash', '<code>find /usr/lib -type f</code><br><code>&gt; listagem_arquivos.txt</code>', '#1E3A8A')}
{_seta('<code>.txt</code>')}
{_caixa('🐍 Parte 2 · Python', '<code>ordenacao.py</code> → 3 algoritmos<br><code>estruturas.py</code> → 3 estruturas', '#2a78d6')}
{_seta('<code>.json</code>')}
{_caixa('📓 Parte 3 · notebook', 'tabelas, gráficos<br>e análise Big O', '#1baf7a')}
</tr></table>

| Item | Valor |
|---|---|
| Sistema | Ubuntu 24.04.5 LTS no WSL2 (kernel 6.18 da Microsoft), Windows 11 Pro |
| Hardware | Intel Core i9-12900H, 16 GB de RAM reservados ao WSL |
| Terminal | WezTerm, shell fish com prompt starship; scripts de shell em bash |
| Linguagem | Python {O['python']} no Ubuntu, só biblioteca padrão |
| Diretório listado | `/usr/lib`: **{milhar(N)} arquivos** em 2.976 subdiretórios aninhados |
| Medição de tempo | `time.perf_counter` / `perf_counter_ns`, mediana de várias execuções |
| Medição de memória | `tracemalloc`, em passada separada da medição de tempo |

Escolhi o `/usr/lib` porque ele cumpre o requisito do enunciado (pelo menos 10.000 arquivos, na raiz
e em subdiretórios aninhados) e existe em qualquer Ubuntu, o que torna o experimento reproduzível.
O script recebe o diretório como argumento, então a mesma execução vale para qualquer outra pasta.

> 📌 **Como ler este notebook.** Os números vêm de `resultados/*.json`, gravados pelos dois programas na
> execução que aparece nos prints do terminal. As células de código só leem esses arquivos, montam as
> tabelas e os gráficos e conferem os algoritmos; nenhuma medição é refeita aqui no Windows.
>
> O Programa 1 rodou em 04/11/2026. O Programa 2 foi reexecutado em 10/11/2026, sobre a **mesma**
> listagem, depois de um refinamento da medição (coletor de lixo desligado durante o cronômetro e lista
> de itens removidos descontada da memória líquida); por isso as Figuras 4, 6 e 7 têm essa data. Entre
> as duas datas o kernel do WSL2 foi atualizado de {O['sistema'].split()[1].split('-')[0]} para
> {E['sistema'].split()[1].split('-')[0]}, sem efeito sobre os programas.
""")

py("""
import sys
sys.path.insert(0, 'src')
from apoio_notebook import *          # tabelas, figuras, formatos pt-BR e estilo dos gráficos
import ordenacao, estruturas            # os dois programas, importados como módulos
import matplotlib.pyplot as plt
estilo()
O, E = carregar('ordenacao.json'), carregar('estruturas.json')
print(f"Resultados carregados: N = {milhar(O['n'])} arquivos | Python {O['python']} | {O['sistema']}")
""")

# =====================================================================================  2. PARTE 1
md(f"""
{VOLTAR}<a id="parte1"></a>

## 🐧 2 · Parte 1: listagem dos arquivos no Linux

### Teoria

No Linux os arquivos ficam numa árvore única de diretórios que começa na raiz `/`
(TANENBAUM; BOS, 2016). Para listar **todos** os arquivos de uma subárvore usei o `find`, que
percorre os diretórios recursivamente e imprime um caminho por linha (FREE SOFTWARE FOUNDATION, 2024).
O `ls -R` também é recursivo, mas imprime blocos por diretório, com cabeçalhos e linhas em branco, e
não o caminho completo de cada arquivo; com o `find` cada linha já é um item pronto para o Python.

O filtro `-type f` mantém só arquivos regulares (sem diretórios nem links). A saída vai para o
arquivo de texto por **redirecionamento**: todo processo tem uma saída padrão (*stdout*, descritor 1)
e uma saída de erro (*stderr*, descritor 2); `>` envia o stdout para um arquivo, sobrescrevendo-o
(`>>` acrescentaria ao fim), e `2>/dev/null` descarta os erros, como “Permissão negada”, para que
não se misturem à listagem (SHOTTS, 2019, cap. 6 e 17).

```bash
find /usr/lib -type f > listagem_arquivos.txt 2>/dev/null
```

### Execução

Primeiro acessei o diretório no terminal e contei o que havia nele: **2.976 subdiretórios** e
**{milhar(N)} arquivos regulares** (Figura 1). Depois gravei o comando no script `gerar_listagem.sh`,
dei permissão de execução e o executei (Figura 2).
""")

py("""
figura('evidencias/telas/01-diretorio-listado.png',
       'Figura 1. WezTerm com Ubuntu 24.04 (WSL2): acesso ao /usr/lib e contagem de subdiretórios e arquivos.')
figura('evidencias/telas/02-listagem.png',
       'Figura 2. Script gerar_listagem.sh: find com redirecionamento para listagem_arquivos.txt (17.520 linhas).')
""")

md("""
O arquivo tem um caminho absoluto por linha, na ordem em que o `find` percorre o disco, e essa ordem
**não é alfabética**, o que o torna uma boa entrada para os algoritmos de ordenação. A célula abaixo
lê o arquivo com a mesma função usada pelos dois programas:
""")

py("""
lista = ordenacao.ler_listagem('listagem_arquivos.txt')
profundidade = [c.count('/') - 2 for c in lista]          # níveis abaixo de /usr/lib
tabela(['Métrica', 'Valor'], [
    ['Arquivos na listagem', milhar(len(lista))],
    ['Primeiro / último', f'<code>{lista[0]}</code><br><code>{lista[-1]}</code>'],
    ['Maior caminho', f"{max(map(len, lista))} caracteres"],
    ['Profundidade média / máxima', f"{sum(profundidade) / len(lista):.1f} / {max(profundidade)} níveis".replace('.', ',')],
    ['Já está em ordem alfabética?', 'não' if lista != sorted(lista) else 'sim'],
], alinhar='ll')
""")

# =====================================================================================  3. EDITOR
md(f"""
{VOLTAR}<a id="editor"></a>

## ⌨️ 3 · Desenvolvimento em editor não gráfico

Os dois programas foram escritos no **GNU nano 7.2**, editor de texto que roda dentro do próprio
terminal, com numeração de linhas e realce de sintaxe Python. As Figuras 3 e 4 mostram os arquivos
abertos no nano, nos trechos dos algoritmos e das estruturas.
""")

py("""
figura('evidencias/telas/03-nano-ordenacao.png', 'Figura 3. ordenacao.py no GNU nano: Bubble, Selection e Insertion Sort.')
figura('evidencias/telas/04-nano-estruturas.png', 'Figura 4. estruturas.py no GNU nano: classes Pilha e Fila sobre nós encadeados.')
""")

# =====================================================================================  4. PROGRAMA 1
md(f"""
{VOLTAR}<a id="p1"></a>

## 🔢 4 · Programa 1 (`ordenacao.py`): lógica e complexidade

### Funcionamento

1. **Lê** `listagem_arquivos.txt` numa lista Python (uma string por caminho).
2. Para cada algoritmo, **copia** a lista (fora do cronômetro), desliga o coletor de lixo, **ordena**
   a cópia e mede o tempo com `time.perf_counter`, o relógio monotônico de maior resolução do Python
   (PYTHON SOFTWARE FOUNDATION, 2026a).
3. **Confere** cada resultado contra `sorted()`; uma ordenação errada interrompe o programa.
4. **Registra** a mediana de 3 execuções em três experimentos: a listagem completa
   (N = {milhar(N)}), o crescimento com N (1.000 a 16.000 caminhos, dobrando) e o efeito da ordem
   inicial (original, já ordenada, invertida).
5. Grava `resultados/ordenacao.json` e a listagem ordenada, que conferi contra o `sort` do Linux.

As strings são comparadas por ponto de código Unicode, a mesma ordem de `LC_ALL=C sort`. Os três
algoritmos ordenam **no lugar** (memória extra O(1)).

### Notação Big O

T(N) é O(f(N)) quando existem constantes c > 0 e N₀ tais que T(N) ≤ c·f(N) para todo N ≥ N₀: a
notação descreve a **taxa de crescimento** do custo e despreza constantes e termos de menor ordem
(CORMEN et al., 2012, cap. 3). Para os três algoritmos, conto as comparações entre chaves, a operação
que domina o tempo.
""")

md("""
### Bubble Sort

**Ideia.** Percorre a lista comparando vizinhos e trocando os que estão fora de ordem; ao fim de cada
passada o maior elemento restante “borbulha” para a posição final (KNUTH, 1998, seção 5.2.2;
WENGROW, 2020, cap. 4). Minha versão para quando uma passada inteira não faz troca nenhuma.

**Complexidade.** A passada *i* faz N − 1 − *i* comparações. No pior caso são
(N−1) + (N−2) + … + 1 = **N(N−1)/2 comparações → O(N²)**. Cada troca desfaz exatamente uma
*inversão* (par fora de ordem), então o número de trocas é igual ao número de inversões da entrada,
que no pior caso também é N(N−1)/2. No melhor caso (lista já ordenada) a primeira passada não troca
nada e o laço para: **N − 1 comparações → O(N)**.
""")
py("codigo(ordenacao.bubble_sort)")

md("""
### Selection Sort

**Ideia.** A cada passada procura o menor elemento da parte ainda não ordenada e o troca com a
primeira posição dessa parte (CORMEN et al., 2012, exercício 2.2-2; WENGROW, 2020, cap. 5).

**Complexidade.** A busca do menor sempre varre o resto da lista, qualquer que seja a ordem inicial:
**N(N−1)/2 comparações em todos os casos → O(N²)**, com **no máximo N − 1 trocas**
(SEDGEWICK; WAYNE, 2011, seção 2.1). É o único dos três que não se beneficia de uma lista já ordenada.
""")
py("codigo(ordenacao.selection_sort)")

md("""
### Insertion Sort

**Ideia.** Mantém um prefixo ordenado e insere o próximo elemento na posição certa, deslocando os
maiores uma casa para a direita, como quem organiza cartas na mão (CORMEN et al., 2012, seção 2.1).

**Complexidade.** Cada deslocamento corrige uma inversão, então o algoritmo faz **I deslocamentos e
entre I e I + N − 1 comparações**, onde I é o número de inversões da entrada (SEDGEWICK; WAYNE, 2011,
seção 2.1). Pior caso (lista invertida, I = N(N−1)/2): **O(N²)**; caso médio (I ≈ N²/4): **O(N²)**;
melhor caso (lista ordenada, I = 0): **N − 1 comparações → O(N)**.
""")
py("codigo(ordenacao.insertion_sort)")

md("""
### Resumo teórico

| Algoritmo | Melhor caso | Caso médio | Pior caso | Trocas / escritas | Memória extra | Estável |
|---|---|---|---|---|---|---|
| Bubble Sort (com parada) | O(N) | O(N²) | O(N²) | I trocas (até N²/2) | O(1) | sim |
| Selection Sort | O(N²) | O(N²) | O(N²) | ≤ N − 1 trocas | O(1) | não |
| Insertion Sort | O(N) | O(N²) | O(N²) | I deslocamentos | O(1) | sim |

*I = número de inversões da entrada. Fontes: Cormen et al. (2012); Sedgewick e Wayne (2011); Knuth (1998).*

A célula abaixo confere os três algoritmos, importados de `src/ordenacao.py`, numa amostra pequena da
listagem e nos casos-limite (lista vazia, um elemento, repetidos):
""")
py("""
import random
amostra = random.Random(42).sample(lista, 300)
casos = [amostra, [], ['/a'], ['/b', '/a', '/b', '/a'], sorted(amostra), sorted(amostra, reverse=True)]
for nome, alg in ordenacao.ALGORITMOS.items():
    ok = all((alg(c := list(caso)) or c) == sorted(caso) for caso in casos)
    print(f'{nome:<15} {"[OK]" if ok else "[FALHA]"} em {len(casos)} casos de teste')
""")

# =====================================================================================  5. RESULTADOS P1
md(f"""
{VOLTAR}<a id="p1res"></a>

## ⏱️ 5 · Programa 1: tempos de execução e análise

A Figura 5 é a execução completa do `ordenacao.py` no terminal, com a conferência final contra o
`sort` do Linux (`cmp` sem diferenças).
""")
py("figura('evidencias/telas/05-ordenacao.png', 'Figura 5. Execução do ordenacao.py: listagem completa, crescimento com N e ordem inicial.')")

md("### 5.1 Listagem completa")
py("""
P, X = O['principal_s'], O['execucoes_s']
linhas = [[nome, *(seg(t) for t in X[nome]), f'<b>{seg(P[nome])}</b>', f"{P[nome] / P['Insertion Sort']:.1f}×".replace('.', ',')]
          for nome in ordenacao.ALGORITMOS]
linhas.append(['list.sort() (Timsort, referência)', '—', '—', '—', seg(O['timsort_s']), '—'])
tabela(['Algoritmo', '1ª execução', '2ª execução', '3ª execução', 'Mediana', 'vs. Insertion'], linhas,
       legenda=f"Tabela 1. Tempo para ordenar os {milhar(O['n'])} caminhos (Python {O['python']}, Ubuntu/WSL2).")

fig, ax = plt.subplots(figsize=(8.2, 2.6))
nomes = list(ordenacao.ALGORITMOS)[::-1]
barras = ax.barh(nomes, [P[n] for n in nomes], color=[CORES_ORD[n] for n in nomes], height=0.55)
for b, n in zip(barras, nomes):
    ax.text(b.get_width() + 0.08, b.get_y() + b.get_height() / 2, seg(P[n]), va='center', color=TINTA, fontsize=10)
ax.set_xlabel('segundos (mediana de 3)'); ax.grid(axis='y', visible=False)
ax.set_title(f"Tempo para ordenar N = {milhar(O['n'])} caminhos"); ax.set_xlim(0, max(P.values()) * 1.15)
mostrar('01_tempo_listagem_completa')
razao = f"{P['Bubble Sort'] / P['Insertion Sort']:.1f}".replace('.', ',')
legenda_grafico(f'Gráfico 1. Os três são O(N²), mas o Bubble Sort leva {razao}× o tempo do Insertion Sort.')
""")

leitura(f"""
Os três algoritmos têm a mesma classe O(N²), mas os tempos diferem em até
{num(B / I)}×. A notação Big O descarta constantes, e são justamente as constantes e o número de
inversões que separam os três aqui. A listagem tem **I = {milhar(INV)} inversões**, {pct(INV / PARES)}
dos {milhar(PARES)} pares possíveis (uma lista aleatória teria cerca de 50%), porque o `find` já
entrega juntos os arquivos de cada diretório. Com isso dá para estimar o trabalho de cada um:
""")
py("""
n, inv, pares = O['n'], O['inversoes'], O['pares']
ops = {'Bubble Sort':    (pares, inv, 'até N(N−1)/2 comparações + I trocas'),
       'Selection Sort': (pares, n - 1, 'N(N−1)/2 comparações + ≤ N−1 trocas'),
       'Insertion Sort': (inv + n - 1, inv, '≈ I + N comparações + I deslocamentos')}
tabela(['Algoritmo', 'Modelo (Big O)', 'Comparações (≈)', 'Trocas / deslocamentos', 'Tempo', 'ns por comparação'],
       [[a, m, milhar(c), milhar(t), seg(P[a]), f'{P[a] / c * 1e9:.1f}'.replace('.', ',')] for a, (c, t, m) in ops.items()],
       legenda='Tabela 2. Trabalho estimado a partir das inversões. Bubble: limite superior (a parada antecipada pode poupar passadas finais).')
""")
leitura(titulo='Por que a ordem é Insertion < Selection < Bubble', t=f"""
- **Selection Sort** faz {milhar(PARES)} comparações, o máximo possível, mas quase nenhuma troca;
  cada comparação é barata.
- **Bubble Sort** faz praticamente as mesmas comparações **e ainda {milhar(INV)} trocas**, cada uma
  com duas leituras e duas escritas na lista; por isso é o mais lento, cerca de {num(B / S)}× o
  Selection. Knuth (1998, seção 5.2.2) conclui que o Bubble Sort parece não ter nada a recomendá-lo,
  além do nome fácil de lembrar e de alguns problemas teóricos interessantes; os números aqui confirmam.
- **Insertion Sort** só compara enquanto há inversão a desfazer: com {pct(INV / PARES)} de inversões,
  faz cerca de {pct((INV + N) / PARES)} das comparações do Selection e termina em {seg(I)}. É o
  efeito da complexidade sensível à entrada (SEDGEWICK; WAYNE, 2011).
- **`list.sort()`** leva {seg(O['timsort_s'])}, cerca de {milhar(I / O['timsort_s'])}× menos que o
  Insertion. Somam-se dois fatores: o Timsort é O(N log N) e aproveita trechos já ordenados (PETERS,
  2002), e roda em C, sem o custo do interpretador a cada comparação. Não é uma comparação só de
  algoritmos, mas mostra o que muda quando se sai de O(N²).
""")

md("### 5.2 Crescimento com N")
py("""
tam, cres = O['tamanhos'], O['crescimento_s']
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 3.8))
for nome, ts in cres.items():
    a1.plot(tam, ts, marker='o', color=CORES_ORD[nome], label=nome)
    a2.loglog(tam, ts, marker='o', color=CORES_ORD[nome], label=nome)
ref = [cres['Bubble Sort'][0] * (x / tam[0]) ** 2 for x in tam]
a2.loglog(tam, ref, ls='--', color=CINZA, lw=1.4, label='inclinação 2 (N²)')
a1.set_title('Tempo × N'); a1.set_xlabel('N (caminhos)'); a1.set_ylabel('segundos')
a2.set_title('Escala log-log'); a2.set_xlabel('N (caminhos)'); a2.set_ylabel('segundos')
a1.legend(); a2.legend(fontsize=8.5)
mostrar('02_crescimento_com_n')
legenda_grafico('Gráfico 2. À esquerda, as parábolas típicas de O(N²); à direita, em log-log, as retas seguem a inclinação 2 da curva N² (tracejada).')

linhas = []
for i, t in enumerate(tam):
    lin = [milhar(t)]
    for nome in cres:
        razao = '' if i == 0 or t != 2 * tam[i - 1] else f" <span style='color:#52514e'>(×{cres[nome][i] / cres[nome][i - 1]:.1f})</span>".replace('.', ',')
        lin.append(seg(cres[nome][i]) + razao)
    linhas.append(lin)
tabela(['N', *cres], linhas, legenda='Tabela 3. Mediana de 3 execuções; entre parênteses, a razão T(2N)/T(N). Para O(N²) a teoria prevê ×4.')
""")
def _razoes(nome):
    t, v = O['tamanhos'], O['crescimento_s'][nome]
    r = [v[i] / v[i - 1] for i in range(1, len(t)) if t[i] == 2 * t[i - 1]]
    return f'{num(min(r))}× a {num(max(r))}×'


leitura(f"""
Quando N dobra, um algoritmo O(N²) deve levar cerca de **4× mais tempo**, pois
(2N)² = 4N². Bubble ({_razoes('Bubble Sort')}) e Selection ({_razoes('Selection Sort')}) ficam em torno
de 4, e no gráfico log-log as três curvas acompanham a reta de inclinação 2: é a confirmação
experimental do crescimento quadrático. O Insertion Sort oscila mais ({_razoes('Insertion Sort')})
porque o custo dele é O(N + I): cada prefixo da listagem tem uma fração diferente de inversões, e o
tempo segue as inversões, não só N. Tempos de poucos milissegundos também sofrem mais com cache e com
o escalonador do sistema.
""")

md(f"### 5.3 Efeito da ordem inicial (N = {milhar(O['n_cenarios'])})")
py("""
cen = O['cenarios_s']
ROTULO = {'Ja ordenada': 'Já ordenada'}          # o terminal imprime sem acento
fig, ax = plt.subplots(figsize=(9, 3.4))
largura, x = 0.26, range(len(cen))
for k, nome in enumerate(ordenacao.ALGORITMOS):
    vals = [cen[c][nome] * 1000 for c in cen]
    bs = ax.bar([i + (k - 1) * largura for i in x], vals, largura - 0.03, color=CORES_ORD[nome], label=nome)
    for b, v in zip(bs, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 6, f'{v:.0f}' if v >= 1 else f'{v:.1f}'.replace('.', ','),
                ha='center', fontsize=8, color=TINTA_2)
ax.set_xticks(list(x), [ROTULO.get(c, c) for c in cen]); ax.set_ylabel('milissegundos'); ax.grid(axis='x', visible=False)
ax.set_title('Mesmo N, ordens iniciais diferentes'); ax.legend(ncol=3, loc='upper left')
mostrar('03_ordem_inicial')
legenda_grafico('Gráfico 3. Com a lista já ordenada, Bubble e Insertion caem para O(N); o Selection não muda.')
tabela(['Entrada', *ordenacao.ALGORITMOS], [[ROTULO.get(c, c), *(seg(cen[c][a]) for a in ordenacao.ALGORITMOS)] for c in cen],
       legenda='Tabela 4. Mediana de 3 execuções sobre os mesmos 4.000 caminhos.')
""")
leitura(f"""
Este experimento separa melhor caso, caso médio e pior caso:

- **Já ordenada:** Bubble ({seg(C['Ja ordenada']['Bubble Sort'])}) e Insertion
  ({seg(C['Ja ordenada']['Insertion Sort'])}) fazem uma única passada, **O(N)**, centenas a milhares de vezes
  mais rápidos que na entrada original. O Selection ({seg(C['Ja ordenada']['Selection Sort'])}) continua
  **O(N²)**, porque precisa varrer o resto da lista para ter certeza de qual é o menor.
- **Invertida (pior caso):** todos os pares são inversões. Bubble e Insertion atingem o máximo de
  trocas e deslocamentos e ficam mais lentos que na entrada original; o Selection quase não muda.
- **Original:** posição intermediária, coerente com {pct(INV / PARES)} de inversões.
""")

# =====================================================================================  6. PROGRAMA 2
md(f"""
{VOLTAR}<a id="p2"></a>

## 🧱 6 · Programa 2 (`estruturas.py`): lógica e funcionamento

### As três estruturas

Implementei as três estruturas, em vez de usar `dict`, `list` ou `deque` prontos, para que o custo de
cada operação ficasse visível no código e nas medições:

<table style="border-collapse:separate;border-spacing:10px 0;margin:6px 0 12px -10px"><tr>
{_caixa('Pilha (LIFO)', 'topo ↓<br>' + _no('arq N') + ' → ' + _no('arq N−1') + ' → … → ' + _no('arq 1') + '<br><b>push</b> / <b>pop</b> no topo: O(1)', '#eb6834')}
{_caixa('Fila (FIFO)', 'início ↓ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ↓ fim<br>' + _no('arq 1') + ' → ' + _no('arq 2') + ' → … → ' + _no('arq N') + '<br><b>enqueue</b> no fim, <b>dequeue</b> no início: O(1)', '#1baf7a')}
{_caixa('Hashtable (encadeamento separado)', 'índice = ((a·hash(k) + b) mod p) mod m<br>' + _no('0') + ' → (k, arquivo) → (k, arquivo)<br>' + _no('1') + ' → (k, arquivo)<br><b>put</b> / <b>get</b> / <b>remove</b>: O(1) médio', '#2a78d6')}
</tr></table>

- **Pilha:** lista simplesmente encadeada; `push` e `pop` mexem só no topo: **O(1)**
  (GOODRICH; TAMASSIA; GOLDWASSER, 2013, cap. 6 e 7).
- **Fila:** lista encadeada com ponteiros para o início e o fim; `enqueue` liga um nó no fim e
  `dequeue` retira do início: **O(1)**. Uma `list` do Python não serve como fila eficiente, porque
  `pop(0)` desloca todos os elementos, O(N) (PYTHON SOFTWARE FOUNDATION, 2026c).
- **Hashtable:** a chave é a **posição do arquivo na listagem** (1 a N) e o valor é o caminho. A
  função de hash usa o método MAD (*multiply-add-divide*) (GOODRICH; TAMASSIA; GOLDWASSER, 2013,
  seção 10.2) e as colisões vão para listas em cada balde (encadeamento separado). Com fator de carga α = N/m, a busca custa em média **Θ(1 + α)**
  (CORMEN et al., 2012, cap. 11). Mantenho α ≤ 0,75 dobrando a tabela quando ele passa disso; o
  redimensionamento é O(N), mas raro, e o custo **amortizado** por inserção continua O(1).
- Os nós usam `__slots__`, que dispensa o dicionário de atributos de cada objeto e reduz a memória
  por nó (PYTHON SOFTWARE FOUNDATION, 2026d).

### Recuperar a posição k

Pilha e fila só oferecem acesso a uma extremidade, e essa é a definição do tipo abstrato. Para ler o
arquivo da posição *k* da listagem é preciso caminhar pelos nós: na **fila** o 1º arquivo está no
início, então são *k* − 1 saltos, **O(k)**; na **pilha** o último arquivo inserido está no topo,
então são N − *k* saltos, **O(N − k)**. A hashtable calcula o balde direto pela chave: **O(1)**.

### Roteiro de cada estrutura

1. **Carga:** insere os {milhar(N)} caminhos na ordem do arquivo.
2. **Consulta:** recupera as posições 1, 100, 1.000, 5.000 e {milhar(N)} (a última) e confere cada uma
   contra a lista original.
3. **Adição:** 1 item e um lote de {milhar(E['lote'])} itens novos (`push`, `enqueue`, `put` com as chaves N+1, N+2…).
4. **Remoção:** 1 item e um lote de {milhar(E['lote'])} (`pop`, `dequeue`, `remove` por chave).

O tempo é medido com `perf_counter_ns` e registrado como mediana: {REP['carga']} execuções na carga,
{REP['consulta']} em cada consulta e {REP['operacao']} em cada adição ou remoção, estas sempre sobre uma
estrutura recém-carregada. Durante o cronômetro o coletor de lixo fica desligado, como faz o `timeit`:
com dezenas de milhares de nós vivos, uma coleta disparada no meio de uma operação O(1) mediria o
coletor, não a estrutura.

A memória vem do `tracemalloc`, que registra cada bloco alocado pelo Python (PYTHON SOFTWARE
FOUNDATION, 2026b), numa passada separada, porque ele deixa cada alocação mais lenta e distorceria o
tempo. Registro a **variação líquida** (o que muda na estrutura) e o **pico** (máximo durante a
tarefa). Uma execução de aquecimento antes do rastreamento tira da conta as alocações que o
interpretador faz na primeira chamada de cada trecho, e a lista com os itens removidos, que a função
devolve, entra no pico mas não na variação líquida.
""")
py("codigo(estruturas.Pilha, estruturas.Fila)")
py("codigo(estruturas.HashTable)")

# =====================================================================================  7. RESULTADOS P2
md(f"""
{VOLTAR}<a id="p2res"></a>

## 📊 7 · Programa 2: posições recuperadas, tempo e memória

A Figura 6 é a execução completa do `estruturas.py` no terminal.
""")
py("figura('evidencias/telas/06-estruturas.png', 'Figura 6. Execução do estruturas.py: carga, consultas às posições, adição e remoção em cada estrutura.')")

md("### 7.1 Arquivos nas posições 1, 100, 1.000, 5.000 e última")
py("""
est = E['estruturas']
for nome in est:
    linhas = [[milhar(c['posicao']), f"<code>{c['arquivo']}</code>", ns(c['tempo_ns']), mem(c['memoria'][1])] for c in est[nome]['consultas']]
    tabela(['Posição', f'Arquivo recuperado da {nome}', 'Tempo', 'Pico de memória'], linhas, alinhar='rlrr',
           legenda=f"Tabela {5 + list(est).index(nome)}. {nome}: posições pedidas (a última é a {milhar(E['n'])}ª).")
iguais = all(est['Hashtable']['consultas'][i]['arquivo'] == est[o]['consultas'][i]['arquivo'] == lista[c['posicao'] - 1]
             for o in ('Pilha', 'Fila') for i, c in enumerate(est['Hashtable']['consultas']))
print('As três estruturas devolveram os mesmos arquivos, iguais aos da listagem:', iguais)
""")

md("### 7.2 Tempo de consulta por posição")
py("""
fig, ax = plt.subplots(figsize=(9, 3.6))
for nome in est:
    pos = [c['posicao'] for c in est[nome]['consultas']]
    ax.plot(pos, [c['tempo_ns'] / 1000 for c in est[nome]['consultas']], marker='o', color=CORES_EST[nome], label=nome)
ax.set_xscale('log'); ax.set_yscale('log')
ax.set_xticks(pos, [milhar(p) for p in pos]); ax.minorticks_off()
ax.set_xlabel('posição k na listagem (escala log)'); ax.set_ylabel('microssegundos (escala log)')
ax.set_title('Custo para recuperar o arquivo da posição k'); ax.legend()
mostrar('04_consulta_por_posicao')
legenda_grafico('Gráfico 4. Hashtable constante, O(1); fila cresce com k, O(k); pilha cai com k, O(N − k).')
""")
leitura(f"""
Cada curva tem a forma prevista pela teoria:

- **Hashtable, O(1):** entre {ns(min(c['tempo_ns'] for c in EH['consultas']))} e
  {ns(max(c['tempo_ns'] for c in EH['consultas']))} em qualquer posição: calcula o balde e percorre uma
  lista curta (fator de carga {num(TAB['fator_carga'], 2)}, maior balde com {TAB['maior_balde']} itens).
- **Fila, O(k):** a posição 1 é a própria frente ({ns(cons(EF, 1)['tempo_ns'])}); a última exige
  {milhar(N - 1)} saltos ({ns(cons(EF, N)['tempo_ns'])}). Entre 1.000 e 5.000 o tempo sobe cerca de
  {num(cons(EF, 5000)['tempo_ns'] / cons(EF, 1000)['tempo_ns'])}×, para 5× previstos pela teoria (de 999 para 4.999 saltos);
  a ordem de grandeza confere, e a diferença é ruído de medição e de cache num percurso de microssegundos.
- **Pilha, O(N − k):** é o espelho da fila. A última posição está no topo
  ({ns(cons(EP, N)['tempo_ns'])}) e a primeira, na base, exige descer a pilha inteira
  ({ns(cons(EP, 1)['tempo_ns'])}). Nas posições 1, 100 e 1.000 o percurso quase não muda
  ({milhar(N - 1)}, {milhar(N - 100)} e {milhar(N - 1000)} saltos), e as diferenças entre esses três tempos
  ({ns(cons(EP, 1)['tempo_ns'])}, {ns(cons(EP, 100)['tempo_ns'])} e {ns(cons(EP, 1000)['tempo_ns'])}) são ruído; a queda
  aparece de fato em k = 5.000 ({milhar(N - 5000)} saltos, {ns(cons(EP, 5000)['tempo_ns'])}) e no topo.

**Memória.** Nenhuma consulta aloca memória proporcional a N ou a k: a memória extra é **O(1)**. A pilha
só move um ponteiro pelos nós ({mem(max(c['memoria'][1] for c in EP['consultas']))} de pico) e a fila
fica em no máximo {mem(max(c['memoria'][1] for c in EF['consultas']))}, um bloco temporário do
interpretador que não muda com k. Na hashtable a posição 1 também não aloca nada, mas da posição 100
em diante o pico é de {mem(max(c['memoria'][1] for c in EH['consultas']))}: o produto a·k + b do MAD
passa de 2³⁰, deixa de caber em um único "dígito" interno dos inteiros do CPython, e o cálculo do
índice cria inteiros temporários maiores, liberados ao fim da consulta.
""")

md("### 7.3 Carga, adição e remoção")
py("""
L = E['lote']
linhas = []
for nome in est:
    r = est[nome]
    linhas.append([nome, ns(r['carga']['tempo_ns']), mem(r['carga']['memoria'][0]), f"{r['carga']['memoria'][0] / E['n']:.0f} B"])
tabela(['Estrutura', f"Carga de {milhar(E['n'])} itens", 'Memória da estrutura', 'Bytes por item'], linhas,
       legenda='Tabela 8. Memória alocada pela própria estrutura. As strings dos caminhos não entram: são as mesmas da lista lida, só referenciadas.')

rot = {'adicionar_1': 'Adicionar 1', f'adicionar_{L}': f'Adicionar {milhar(L)}', 'remover_1': 'Remover 1', f'remover_{L}': f'Remover {milhar(L)}'}
linhas = []
for op, txt in rot.items():
    lin = [txt]
    for nome in est:
        v = est[nome]['operacoes'][op]
        lin += [ns(v['tempo_ns']), mem(v['memoria'][0])]
    linhas.append(lin)
tabela(['Operação', 'Hash: tempo', 'Hash: memória', 'Pilha: tempo', 'Pilha: memória', 'Fila: tempo', 'Fila: memória'], linhas,
       legenda=f"Tabela 9. Mediana de {E['repeticoes']['operacao']} execuções; memória = variação líquida medida pelo tracemalloc (negativa = memória devolvida).")

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 3.4))
nomes = list(est)
for ax, op, titulo_ in ((a1, f'adicionar_{L}', f'Adicionar {milhar(L)} itens'), (a2, f'remover_{L}', f'Remover {milhar(L)} itens')):
    vals = [est[n]['operacoes'][op]['tempo_ns'] / L for n in nomes]
    bs = ax.bar(nomes, vals, color=[CORES_EST[n] for n in nomes], width=0.55)
    for b, v in zip(bs, vals):
        ax.text(b.get_x() + b.get_width() / 2, v * 1.02, f'{v:.0f} ns', ha='center', fontsize=9, color=TINTA)
    ax.set_title(titulo_); ax.set_ylabel('ns por item'); ax.grid(axis='x', visible=False); ax.set_ylim(0, max(vals) * 1.2)
mostrar('05_adicao_remocao')
legenda_grafico('Gráfico 5. Custo por item nas operações em lote: todas O(1); a hashtable paga uma constante maior (hash, MAD e varredura do balde).')

tabela(['Estrutura', 'Primeiro removido', 'Último removido', 'Extremidade depois da remoção'],
       [[n, f"<code>{est[n]['efeito']['primeiro_removido']}</code>", f"<code>{est[n]['efeito']['ultimo_removido']}</code>",
         f"<code>{est[n]['efeito']['referencia_apos']}</code>"] for n in nomes], alinhar='llll',
       legenda=f'Tabela 10. Depois de adicionar e remover {milhar(L)} itens: a pilha devolve os recém-chegados (LIFO); a fila, os primeiros da listagem (FIFO).')
""")

OPS = lambda e: e['operacoes']
UM = [OPS(e)[op]['tempo_ns'] for e in (EH, EP, EF) for op in ('adicionar_1', 'remover_1')]
UM_M = [OPS(e)[op]['memoria'][0] for e in (EH, EP, EF) for op in ('adicionar_1', 'remover_1')]
LT = E['lote']
ADD_P, REM_P = OPS(EP)[f'adicionar_{LT}']['memoria'][0], OPS(EP)[f'remover_{LT}']['memoria'][0]
ADD_H, REM_H = OPS(EH)[f'adicionar_{LT}']['memoria'][0], OPS(EH)[f'remover_{LT}']['memoria'][0]
LOTE_T = [OPS(e)[op]['tempo_ns'] / LT for e in (EH, EP, EF) for op in (f'adicionar_{LT}', f'remover_{LT}')]

leitura(titulo='Leitura do tempo', t=f"""
- **Adição e remoção são O(1) nas três estruturas.** No lote de {milhar(LT)}, cada operação
  custa de {num(min(LOTE_T), 0)} a {num(max(LOTE_T), 0)} ns e o total cresce com o tamanho do lote, não
  com N. Na operação isolada os tempos ficam entre {ns(min(UM))} e {ns(max(UM))}, porque dominam custos
  fixos que não dependem da estrutura: chamada de função, estrutura recém-criada fora do cache e a
  resolução do relógio.
- **A hashtable tem a maior constante.** Cada `put`/`remove` calcula `hash()`, aplica o MAD, escolhe o
  balde e o percorre; pilha e fila só criam ou desligam um nó. A classe é a mesma, O(1), mas a
  constante é várias vezes maior, e é por isso que a carga da hashtable ({ns(EH['carga']['tempo_ns'])})
  leva bem mais que a da pilha ({ns(EP['carga']['tempo_ns'])}) e a da fila ({ns(EF['carga']['tempo_ns'])}).
  A carga inclui ainda os redimensionamentos (16 → 32 → … → {milhar(TAB['baldes'])} baldes), cada um O(N).
- **LIFO × FIFO (Tabela 10):** a pilha remove primeiro o último arquivo que entrou; a fila remove os
  primeiros da listagem e deixa na frente o arquivo da posição {milhar(LT + 1)}.
""")

leitura(titulo='Leitura da memória', t=f"""
- **Pilha e fila: {EP['carga']['memoria'][0] / N:.0f} B por item.** Cada nó com `__slots__` guarda dois
  ponteiros de 8 bytes (elemento e próximo) mais o cabeçalho do objeto e o do coletor de lixo do CPython.
  Adicionar {milhar(LT)} itens aloca {mem(ADD_P)} ({milhar(ADD_P)} B = {milhar(LT)} × {ADD_P / LT:.0f} B) e removê-los
  devolve o mesmo ({mem(REM_P)}): a memória é **O(N)** e acompanha a estrutura, nó a nó.
- **Hashtable: {EH['carga']['memoria'][0] / N:.0f} B por item, cerca de {num(EH['carga']['memoria'][0] / EP['carga']['memoria'][0])}× a pilha.**
  Também é O(N), mas cada item ocupa uma tupla (chave, valor) e um inteiro para a chave, e a tabela
  mantém {milhar(TAB['baldes'])} baldes, cada um uma lista própria, {milhar(TAB['baldes_vazios'])} deles vazios.
  É a troca clássica das tabelas de dispersão: gasta-se memória para ter acesso por chave em O(1).
- **Por que a hashtable devolve menos do que alocou.** O lote adiciona {mem(ADD_H)}, mas a remoção só
  devolve {mem(-REM_H)}. O que volta são principalmente os {milhar(LT)} inteiros das chaves. As
  {milhar(LT)} tuplas (chave, valor) não voltam ao sistema: o CPython as guarda numa lista de
  reaproveitamento (*free list*) para as próximas tuplas, e o `tracemalloc` continua contando esses
  blocos como alocados. Os vetores internos das listas dos baldes também não encolhem. A Tabela 11,
  logo abaixo, reproduz o efeito das tuplas isoladamente.
- **Operações de 1 item** variam entre {mem(min(UM_M))} e {mem(max(UM_M))}: na pilha e na fila é
  exatamente um nó ({mem(OPS(EP)['adicionar_1']['memoria'][0])} ao entrar, {mem(OPS(EP)['remover_1']['memoria'][0])} ao sair); na hashtable o
  valor mistura a tupla, a chave e blocos internos do interpretador, e a leitura confiável é a do lote.
- O pico da remoção fica perto de zero porque a tarefa libera mais do que ocupa a lista temporária dos
  itens removidos (8 B por item).
""")

py("""
import sys, tracemalloc
tracemalloc.start()
pares = [(10**9 + i, '/novo/x') for i in range(1000)]   # 1.000 tuplas (chave, valor), como nos baldes
antes = tracemalloc.get_traced_memory()[0]
lista_e_chaves = sys.getsizeof(pares) + sum(sys.getsizeof(k) for k, _ in pares)
del pares                                               # apaga a lista, as tuplas e as chaves
depois = tracemalloc.get_traced_memory()[0]
outros = [(2 * 10**9 + i, '/novo/y') for i in range(1000)]
refeito = tracemalloc.get_traced_memory()[0]
tracemalloc.stop()
tupla = sys.getsizeof((1, 2))
tabela(['Etapa', 'Variação medida', 'Lista + chaves (calculado)', 'Tuplas (calculado)', 'Leitura'], [
    ['Apagar 1.000 tuplas', mem(depois - antes), mem(-lista_e_chaves), mem(-1000 * tupla),
     'só a lista e as chaves voltam; as tuplas ficam na free list'],
    ['Criar outras 1.000 tuplas', mem(refeito - depois), mem(lista_e_chaves), mem(1000 * tupla),
     'de novo só a lista e as chaves: as tuplas reaproveitam os blocos guardados'],
], alinhar='lrrrl', legenda=f'Tabela 11. Free list de tuplas do CPython observada pelo tracemalloc (Python {sys.version.split()[0]}, kernel do notebook).')
""")

md("""
A Figura 7 mostra os artefatos que ficaram no diretório de trabalho depois das duas execuções: os três
fontes, a listagem e os resultados gravados pelos programas.
""")
py("figura('evidencias/telas/07-artefatos.png', 'Figura 7. Artefatos gerados: fontes, listagem_arquivos.txt e resultados/ (JSON e listagem ordenada).')")

# =====================================================================================  8. COMPARATIVO
md(f"""
{VOLTAR}<a id="comparativo"></a>

## ⚖️ 8 · Teoria × prática: quadro comparativo

| Operação | Teoria | Observado (N = {milhar(N)}) | Confere? |
|---|---|---|:-:|
| Bubble Sort, listagem | O(N²), I trocas | {seg(B)}; ×≈4 a cada N dobrado | ✅ |
| Selection Sort, listagem | O(N²) sempre, ≤ N − 1 trocas | {seg(S)}; não muda com a lista já ordenada | ✅ |
| Insertion Sort, listagem | O(N + I) | {seg(I)}, o mais rápido ({pct(INV / PARES)} de inversões) | ✅ |
| Bubble / Insertion, lista já ordenada (N = {milhar(O['n_cenarios'])}) | O(N) | {seg(C['Ja ordenada']['Bubble Sort'])} / {seg(C['Ja ordenada']['Insertion Sort'])} | ✅ |
| Hashtable: consulta da posição k | O(1) médio | {ns(min(c['tempo_ns'] for c in EH['consultas']))} a {ns(max(c['tempo_ns'] for c in EH['consultas']))}, qualquer k | ✅ |
| Fila: consulta da posição k | O(k) | {ns(cons(EF, 1)['tempo_ns'])} (k = 1) → {ns(cons(EF, N)['tempo_ns'])} (k = N) | ✅ |
| Pilha: consulta da posição k | O(N − k) | {ns(cons(EP, N)['tempo_ns'])} (k = N) → {ns(cons(EP, 1)['tempo_ns'])} (k = 1) | ✅ |
| push / enqueue / put | O(1) (put: amortizado) | {num(EP['operacoes']['adicionar_1000']['tempo_ns'] / 1000, 0)} / {num(EF['operacoes']['adicionar_1000']['tempo_ns'] / 1000, 0)} / {num(EH['operacoes']['adicionar_1000']['tempo_ns'] / 1000, 0)} ns por item | ✅ |
| pop / dequeue / remove | O(1) | {num(EP['operacoes']['remover_1000']['tempo_ns'] / 1000, 0)} / {num(EF['operacoes']['remover_1000']['tempo_ns'] / 1000, 0)} / {num(EH['operacoes']['remover_1000']['tempo_ns'] / 1000, 0)} ns por item | ✅ |
| Memória: pilha e fila / hashtable | O(N) | {EP['carga']['memoria'][0] / N:.0f} B / {EH['carga']['memoria'][0] / N:.0f} B por item | ✅ |
""")

# =====================================================================================  9. CONCLUSÃO
md(f"""
{VOLTAR}<a id="conclusao"></a>

## ✅ 9 · Conclusão

- No Linux, `find … -type f > arquivo 2>/dev/null` gera em uma linha a listagem recursiva completa
  ({milhar(N)} arquivos), já no formato que o Python consome.
- A notação Big O previu corretamente **como** cada tempo cresce: quando N dobra, os três algoritmos de
  ordenação levam cerca de 4× mais tempo (o Insertion oscila mais, porque depende das inversões), e a
  consulta por posição é constante na hashtable, linear em k na fila e linear em N − k na pilha.
- A notação **não** diz qual algoritmo é mais rápido dentro da mesma classe. Isso dependeu da entrada
  e das constantes: com {pct(INV / PARES)} de inversões, o Insertion Sort foi {num(B / I)}× mais rápido
  que o Bubble Sort. Na prática, contar inversões e trocas explicou a ordem Insertion < Selection < Bubble.
- Na escolha da estrutura, o critério é a operação mais frequente: **hashtable** para acesso por chave,
  ao custo de cerca de {num(EH['carga']['memoria'][0] / EP['carga']['memoria'][0])}× mais memória;
  **pilha** para desfazer na ordem inversa (LIFO); **fila** para processar na ordem de chegada (FIFO).
  Em pilha e fila, acesso por posição é O(N) e não deve ser a operação principal.
""")

# =====================================================================================  10. REFERÊNCIAS
md(f"""
{VOLTAR}<a id="referencias"></a>

## 📖 10 · Referências

CORMEN, T. H.; LEISERSON, C. E.; RIVEST, R. L.; STEIN, C. **Algoritmos: teoria e prática**. Tradução da 3. ed. americana. Rio de Janeiro: Elsevier, 2012.

FREE SOFTWARE FOUNDATION. **GNU Findutils: finding files**. Boston: FSF, 2024. Disponível em: https://www.gnu.org/software/findutils/manual/html_mono/find.html. Acesso em: 4 nov. 2026.

GOODRICH, M. T.; TAMASSIA, R.; GOLDWASSER, M. H. **Data structures and algorithms in Python**. Hoboken: Wiley, 2013.

KNUTH, D. E. **The art of computer programming**: volume 3: sorting and searching. 2. ed. Reading: Addison-Wesley, 1998.

PETERS, T. **listsort.txt**: description of Timsort. Python Software Foundation, 2002. Disponível em: https://github.com/python/cpython/blob/main/Objects/listsort.txt. Acesso em: 4 nov. 2026.

PYTHON SOFTWARE FOUNDATION. **time: time access and conversions**. 2026a. Disponível em: https://docs.python.org/3/library/time.html. Acesso em: 4 nov. 2026.

PYTHON SOFTWARE FOUNDATION. **tracemalloc: trace memory allocations**. 2026b. Disponível em: https://docs.python.org/3/library/tracemalloc.html. Acesso em: 4 nov. 2026.

PYTHON SOFTWARE FOUNDATION. **TimeComplexity**. Python Wiki, 2026c. Disponível em: https://wiki.python.org/moin/TimeComplexity. Acesso em: 4 nov. 2026.

PYTHON SOFTWARE FOUNDATION. **Data model: \\_\\_slots\\_\\_**. 2026d. Disponível em: https://docs.python.org/3/reference/datamodel.html#slots. Acesso em: 4 nov. 2026.

SEDGEWICK, R.; WAYNE, K. **Algorithms**. 4. ed. Upper Saddle River: Addison-Wesley, 2011.

SHOTTS, W. **The Linux command line**: a complete introduction. 2. ed. San Francisco: No Starch Press, 2019.

TANENBAUM, A. S.; BOS, H. **Sistemas operacionais modernos**. 4. ed. São Paulo: Pearson, 2016.

WENGROW, J. **A common-sense guide to data structures and algorithms**: level up your core programming skills. 2. ed. Raleigh: The Pragmatic Bookshelf, 2020.

---

<sub>Reprodução: `scripts/capturar_wezterm.py` abre o WezTerm, digita os comandos da Parte 1 e dos dois programas no fish
e grava as telas, a listagem e `resultados/` (com `--so-estruturas`, refaz só as telas do Programa 2 sobre a listagem já
gerada); `scripts/gerar_notebook.py` monta e executa este notebook.</sub>
""")

nb = nbformat.v4.new_notebook(cells=celulas)
nb.metadata['kernelspec'] = {'name': 'python3', 'display_name': 'Python 3', 'language': 'python'}
nb.metadata['language_info'] = {'name': 'python'}
nb.metadata['title'] = 'andre_becker_PB_TP1'

if __name__ == '__main__':
    NotebookClient(nb, timeout=600, kernel_name='python3', resources={'metadata': {'path': RAIZ}}).execute()
    nbformat.write(nb, SAIDA)
    print('gerado: %s | celulas: %d' % (SAIDA, len(nb.cells)))
