#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Programa 1 - ordena a listagem de arquivos com Bubble, Selection e Insertion Sort.

    python3 ordenacao.py [listagem_arquivos.txt]

1. Le a listagem gerada por gerar_listagem.sh (um caminho por linha).
2. Ordena a listagem completa com os tres algoritmos e mede o tempo de cada execucao.
3. Mede o crescimento do tempo com N (prefixos de 1.000 a 16.000 caminhos) e o efeito da
   ordem inicial (listagem original, ja ordenada e invertida).
4. Grava os resultados em resultados/ordenacao.json e a listagem ordenada em
   resultados/listagem_ordenada.txt.

So biblioteca padrao. A comparacao entre strings e lexicografica por ponto de codigo
Unicode, a mesma ordem de `LC_ALL=C sort` no Linux.
"""
import gc
import json
import os
import platform
import statistics
import sys
import time

RAIZ = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(RAIZ, 'resultados')
TAMANHOS = [1000, 2000, 4000, 8000, 16000]   # dobrando N: num algoritmo O(N^2) o tempo deve ~quadruplicar
N_CENARIOS = 4000
REPETICOES = 3                        # cada tempo registrado e a mediana de 3 execucoes

COR = sys.stdout.isatty()
def cor(texto, codigo):
    return f'\033[{codigo}m{texto}\033[0m' if COR else texto


# ------------------------------------------------------------------ leitura
def ler_listagem(caminho):
    """Uma entrada por linha; surrogateescape preserva nomes que nao sejam UTF-8 valido."""
    with open(caminho, encoding='utf-8', errors='surrogateescape') as arquivo:
        return [linha.rstrip('\n') for linha in arquivo if linha.strip()]


# ------------------------------------------------------------------ algoritmos (in-place)
def bubble_sort(a):
    """Compara vizinhos e troca os fora de ordem; a cada passada o maior "borbulha" para o fim.
    Para se uma passada inteira nao fizer nenhuma troca (lista ja ordenada)."""
    n = len(a)
    for i in range(n - 1):
        trocou = False
        for j in range(n - 1 - i):
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                trocou = True
        if not trocou:
            break


def selection_sort(a):
    """Procura o menor elemento da parte nao ordenada e o coloca na posicao i (uma troca por passada)."""
    n = len(a)
    for i in range(n - 1):
        menor = i
        for j in range(i + 1, n):
            if a[j] < a[menor]:
                menor = j
        if menor != i:
            a[i], a[menor] = a[menor], a[i]


def insertion_sort(a):
    """Insere a[i] na posicao certa do prefixo ja ordenado, deslocando os maiores uma casa a direita."""
    for i in range(1, len(a)):
        chave = a[i]
        j = i - 1
        while j >= 0 and a[j] > chave:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = chave


def timsort(a):
    """list.sort() do Python (Timsort, O(N log N)): so como referencia de um algoritmo eficiente."""
    a.sort()


ALGORITMOS = {'Bubble Sort': bubble_sort,
              'Selection Sort': selection_sort,
              'Insertion Sort': insertion_sort}


def contar_inversoes(v):
    """Pares (i < j) com v[i] > v[j], via merge sort em O(N log N). E exatamente o numero de trocas
    do Bubble Sort e de deslocamentos do Insertion Sort, o que explica a diferenca de tempo entre eles."""
    if len(v) < 2:
        return list(v), 0
    meio = len(v) // 2
    esq, inv_e = contar_inversoes(v[:meio])
    dir_, inv_d = contar_inversoes(v[meio:])
    junta, i, j, inv = [], 0, 0, inv_e + inv_d
    while i < len(esq) and j < len(dir_):
        if esq[i] <= dir_[j]:
            junta.append(esq[i]); i += 1
        else:
            junta.append(dir_[j]); j += 1
            inv += len(esq) - i
    junta += esq[i:] + dir_[j:]
    return junta, inv


# ------------------------------------------------------------------ medicao
def cronometrar(funcao, dados):
    """Ordena uma copia e devolve o tempo em segundos. A copia fica fora do cronometro e o coletor de
    lixo e desligado durante a medicao, para nao interromper o algoritmo no meio."""
    copia = list(dados)
    gc.collect(); gc.disable()
    inicio = time.perf_counter()
    funcao(copia)
    fim = time.perf_counter()
    gc.enable()
    if copia != sorted(dados):
        raise AssertionError(f'{funcao.__name__} nao ordenou corretamente')
    return fim - inicio, copia


def mediana(funcao, dados, repeticoes=REPETICOES):
    return statistics.median(cronometrar(funcao, dados)[0] for _ in range(repeticoes))


def milhar(n):
    return f'{n:,}'.replace(',', '.')


def fmt(segundos):
    return f'{segundos * 1000:,.1f} ms'.replace(',', '.') if segundos < 1 else f'{segundos:,.3f} s'


def titulo(texto):
    print('\n' + cor(texto, '1;36'))
    print(cor('-' * len(texto), '36'))


# ------------------------------------------------------------------ principal
def main():
    origem = sys.argv[1] if len(sys.argv) > 1 else os.path.join(RAIZ, 'listagem_arquivos.txt')
    os.makedirs(SAIDA, exist_ok=True)

    t0 = time.perf_counter()
    lista = ler_listagem(origem)
    t_leitura = time.perf_counter() - t0
    n = len(lista)
    _, inversoes = contar_inversoes(lista)
    pares = n * (n - 1) // 2

    titulo('PROGRAMA 1 - ORDENACAO DA LISTAGEM DE ARQUIVOS')
    print(f'Arquivo lido      : {origem}')
    print(f'Entradas (N)      : {n:,}'.replace(',', '.'))
    print(f'Tempo de leitura  : {fmt(t_leitura)}')
    print(f'Inversoes         : {inversoes:,} de {pares:,} pares ({inversoes / pares:.1%})'.replace(',', '.'))
    print(f'Python {platform.python_version()} | {platform.system()} {platform.release()}')

    # 1) listagem completa: cada execucao confere o resultado contra sorted()
    titulo(f'1) Listagem completa (N = {milhar(n)}, mediana de {REPETICOES} execucoes)')
    principal, execucoes = {}, {}
    for nome, funcao in ALGORITMOS.items():
        execucoes[nome] = [cronometrar(funcao, lista)[0] for _ in range(REPETICOES)]
        principal[nome] = statistics.median(execucoes[nome])
        todas = ' | '.join(fmt(t) for t in execucoes[nome])
        print(f'{nome:<16} {fmt(principal[nome]):>10}   [{todas}]  {cor("[OK]", "32")}')
    t_timsort, ordenada = cronometrar(timsort, lista)
    print(f'{"list.sort()":<16} {fmt(t_timsort):>10}   (Timsort, referencia O(N log N))')

    with open(os.path.join(SAIDA, 'listagem_ordenada.txt'), 'w', encoding='utf-8',
              errors='surrogateescape') as arquivo:
        arquivo.write('\n'.join(ordenada) + '\n')

    # 2) crescimento com N
    titulo(f'2) Crescimento com N (mediana de {REPETICOES} execucoes)')
    print(f'{"N":>7} ' + ''.join(f'{nome:>16}' for nome in ALGORITMOS))
    crescimento = {nome: [] for nome in ALGORITMOS}
    for tam in TAMANHOS:
        linha = f'{tam:>7,} '.replace(',', '.')
        for nome, funcao in ALGORITMOS.items():
            segundos = mediana(funcao, lista[:tam])
            crescimento[nome].append(segundos)
            linha += f'{fmt(segundos):>16}'
        print(linha)
    print(f'{n:>7,} '.replace(',', '.') + ''.join(f'{fmt(principal[a]):>16}' for a in ALGORITMOS))

    # 3) efeito da ordem inicial
    titulo(f'3) Ordem inicial (N = {milhar(N_CENARIOS)}, mediana de {REPETICOES} execucoes)')
    base = lista[:N_CENARIOS]
    entradas = {'Original (find)': base, 'Ja ordenada': sorted(base), 'Invertida': sorted(base, reverse=True)}
    print(f'{"Entrada":<16}' + ''.join(f'{nome:>16}' for nome in ALGORITMOS))
    cenarios = {}
    for rotulo, dados in entradas.items():
        cenarios[rotulo] = {nome: mediana(funcao, dados) for nome, funcao in ALGORITMOS.items()}
        print(f'{rotulo:<16}' + ''.join(f'{fmt(cenarios[rotulo][a]):>16}' for a in ALGORITMOS))

    resultado = {
        'arquivo': origem, 'n': n, 'inversoes': inversoes, 'pares': pares,
        'tempo_leitura_s': t_leitura, 'python': platform.python_version(),
        'sistema': f'{platform.system()} {platform.release()}',
        'principal_s': principal, 'execucoes_s': execucoes, 'timsort_s': t_timsort,
        'tamanhos': TAMANHOS + [n],
        'crescimento_s': {a: crescimento[a] + [principal[a]] for a in ALGORITMOS},
        'n_cenarios': N_CENARIOS, 'cenarios_s': cenarios,
    }
    with open(os.path.join(SAIDA, 'ordenacao.json'), 'w', encoding='utf-8') as arquivo:
        json.dump(resultado, arquivo, ensure_ascii=False, indent=2)
    print('\n' + cor('Resultados gravados em resultados/ordenacao.json e resultados/listagem_ordenada.txt', '33'))


if __name__ == '__main__':
    main()
