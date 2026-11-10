#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Programa 2 - armazena a listagem em Hashtable, Pilha e Fila e mede tempo e memoria.

    python3 estruturas.py [listagem_arquivos.txt]

Para cada estrutura:
  1. carga     : insere todos os caminhos da listagem, na ordem do arquivo;
  2. consulta  : recupera os arquivos nas posicoes 1, 100, 1.000, 5.000 e N da listagem;
  3. adicao    : adiciona 1 item e depois um lote de 1.000 itens;
  4. remocao   : remove 1 item e depois um lote de 1.000 itens.
Tempo com time.perf_counter_ns (mediana de varias execucoes) e memoria com tracemalloc,
em passadas separadas: o tracemalloc intercepta cada alocacao e distorceria o tempo.

As tres estruturas sao implementadas aqui, so com a biblioteca padrao:
  - Hashtable : encadeamento separado, compressao MAD e redimensionamento com fator de carga 0,75;
  - Pilha     : lista simplesmente encadeada, topo = ultimo inserido (LIFO);
  - Fila      : lista simplesmente encadeada com ponteiros de inicio e fim (FIFO).
Pilha e fila so dao acesso a uma extremidade; para ler a posicao k da listagem e preciso
percorrer os nos a partir dela, e e justamente isso que as medicoes mostram.
"""
import gc
import json
import os
import platform
import random
import statistics
import sys
import time
import tracemalloc

RAIZ = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(RAIZ, 'resultados')
LOTE = 1000
REPETICOES = 21                     # consultas: rapidas e sensiveis a ruido, mais repeticoes
REPETICOES_CARGA = 3                # carga: dezenas de milissegundos, pouco ruido
REPETICOES_OP = 11                  # adicao/remocao: cada execucao recria a estrutura

COR = sys.stdout.isatty()
def cor(texto, codigo):
    return f'\033[{codigo}m{texto}\033[0m' if COR else texto


# ------------------------------------------------------------------ estruturas
class _No:
    __slots__ = ('elemento', 'proximo')     # sem __dict__: cada no ocupa so dois ponteiros + cabecalho

    def __init__(self, elemento, proximo=None):
        self.elemento, self.proximo = elemento, proximo


class Pilha:
    """LIFO: push e pop no topo em O(1). Os nos apontam do topo para a base."""

    def __init__(self):
        self._topo, self._tamanho = None, 0

    def __len__(self):
        return self._tamanho

    def push(self, elemento):
        self._topo = _No(elemento, self._topo)
        self._tamanho += 1

    def pop(self):
        if self._topo is None:
            raise IndexError('pilha vazia')
        elemento, self._topo = self._topo.elemento, self._topo.proximo
        self._tamanho -= 1
        return elemento

    def topo(self):
        return self._topo.elemento

    def posicao(self, k):
        """k-esimo item na ordem de insercao (1 = base). O topo guarda o N-esimo, entao e preciso
        descer N - k nos a partir dele: O(N - k)."""
        no = self._topo
        for _ in range(self._tamanho - k):
            no = no.proximo
        return no.elemento


class Fila:
    """FIFO: enqueue no fim e dequeue no inicio, ambos O(1) gracas aos dois ponteiros."""

    def __init__(self):
        self._inicio = self._fim = None
        self._tamanho = 0

    def __len__(self):
        return self._tamanho

    def enqueue(self, elemento):
        novo = _No(elemento)
        if self._fim is None:
            self._inicio = novo
        else:
            self._fim.proximo = novo
        self._fim = novo
        self._tamanho += 1

    def dequeue(self):
        if self._inicio is None:
            raise IndexError('fila vazia')
        elemento, self._inicio = self._inicio.elemento, self._inicio.proximo
        if self._inicio is None:
            self._fim = None
        self._tamanho -= 1
        return elemento

    def frente(self):
        return self._inicio.elemento

    def posicao(self, k):
        """k-esimo item a partir do inicio (1 = primeiro a entrar): k - 1 saltos, O(k)."""
        no = self._inicio
        for _ in range(k - 1):
            no = no.proximo
        return no.elemento


class HashTable:
    """Mapa chave -> valor com encadeamento separado. A chave e a posicao do arquivo na listagem.
    h(k) = ((a * hash(k) + b) mod p) mod m  (metodo MAD), com p primo e a, b sorteados.
    Quando N / m passa de 0,75 a tabela dobra e reespalha tudo: O(N) raramente, O(1) amortizado."""
    P = 109_345_121                          # primo maior que qualquer chave usada aqui
    CARGA_MAX = 0.75

    def __init__(self, capacidade=16, semente=42):
        sorteio = random.Random(semente)
        self._a, self._b = sorteio.randrange(1, self.P), sorteio.randrange(self.P)
        self._baldes = [[] for _ in range(capacidade)]
        self._tamanho = 0

    def __len__(self):
        return self._tamanho

    def _indice(self, chave):
        return (self._a * hash(chave) + self._b) % self.P % len(self._baldes)

    def put(self, chave, valor):
        balde = self._baldes[self._indice(chave)]
        for i, (k, _) in enumerate(balde):
            if k == chave:
                balde[i] = (chave, valor)
                return
        balde.append((chave, valor))
        self._tamanho += 1
        if self._tamanho > self.CARGA_MAX * len(self._baldes):
            self._redimensionar(2 * len(self._baldes))

    def get(self, chave):
        for k, v in self._baldes[self._indice(chave)]:
            if k == chave:
                return v
        raise KeyError(chave)

    def remove(self, chave):
        balde = self._baldes[self._indice(chave)]
        for i, (k, v) in enumerate(balde):
            if k == chave:
                del balde[i]
                self._tamanho -= 1
                return v
        raise KeyError(chave)

    def _redimensionar(self, capacidade):
        itens = [par for balde in self._baldes for par in balde]
        self._baldes = [[] for _ in range(capacidade)]
        for chave, valor in itens:
            self._baldes[self._indice(chave)].append((chave, valor))

    def estatisticas(self):
        ocupados = [len(b) for b in self._baldes if b]
        return {'baldes': len(self._baldes), 'fator_carga': self._tamanho / len(self._baldes),
                'baldes_vazios': len(self._baldes) - len(ocupados), 'maior_balde': max(ocupados)}


# ------------------------------------------------------------------ operacoes por estrutura
# Cada estrutura expoe as mesmas quatro tarefas, para medir tudo com o mesmo codigo.
def carregar(nome, lista):
    if nome == 'Hashtable':
        e = HashTable()
        for pos, caminho in enumerate(lista, 1):
            e.put(pos, caminho)
    elif nome == 'Pilha':
        e = Pilha()
        for caminho in lista:
            e.push(caminho)
    else:
        e = Fila()
        for caminho in lista:
            e.enqueue(caminho)
    return e


def consultar(nome, e, k):
    return e.get(k) if nome == 'Hashtable' else e.posicao(k)


def adicionar(nome, e, novos, n0):
    """Pilha: push no topo; fila: enqueue no fim; hashtable: put com as chaves N+1, N+2, ..."""
    if nome == 'Hashtable':
        for i, caminho in enumerate(novos, n0 + 1):
            e.put(i, caminho)
    elif nome == 'Pilha':
        for caminho in novos:
            e.push(caminho)
    else:
        for caminho in novos:
            e.enqueue(caminho)


def remover(nome, e, quantidade, n0):
    """Pilha: pop (sai o ultimo que entrou); fila: dequeue (sai o primeiro que entrou);
    hashtable: remove por chave, das ultimas chaves para as primeiras a partir de n0."""
    if nome == 'Hashtable':
        return [e.remove(k) for k in range(n0, n0 - quantidade, -1)]
    if nome == 'Pilha':
        return [e.pop() for _ in range(quantidade)]
    return [e.dequeue() for _ in range(quantidade)]


# ------------------------------------------------------------------ medicao
def tempo_ns(funcao, preparo=None, repeticoes=REPETICOES):
    """Mediana de `repeticoes` execucoes. `preparo` recria o estado antes de cada uma, fora do cronometro.
    O coletor de lixo fica desligado durante a medicao (como no timeit): com dezenas de milhares de nos
    vivos, uma coleta disparada no meio de uma operacao O(1) mediria o coletor, nao a estrutura."""
    tempos = []
    gc.disable()
    try:
        for _ in range(repeticoes):
            estado = preparo() if preparo else None
            inicio = time.perf_counter_ns()
            funcao(estado)
            tempos.append(time.perf_counter_ns() - inicio)
    finally:
        gc.enable()
    return statistics.median(tempos)


def memoria(funcao, preparo=None, com_retorno=True):
    """(variacao liquida, pico) em bytes durante `funcao`, medidos pelo tracemalloc.
    O rastreamento comeca antes do `preparo`: o tracemalloc so enxerga a liberacao de blocos que ele
    viu nascer, e sem isso a remocao nunca mostraria a memoria devolvida pelos nos. Na carga o retorno e
    a propria estrutura e entra na conta; com com_retorno=False (remocao) a lista dos itens removidos
    entra so no pico e e descartada antes da variacao liquida, que mede apenas o que muda na estrutura.
    Uma execucao de aquecimento, fora do rastreamento, tira da conta as alocacoes internas que o
    interpretador faz na primeira chamada de cada trecho de codigo."""
    funcao(preparo() if preparo else None)
    tracemalloc.start()
    estado = preparo() if preparo else None
    antes = tracemalloc.get_traced_memory()[0]
    tracemalloc.reset_peak()
    retorno = funcao(estado)
    pico = tracemalloc.get_traced_memory()[1]
    if not com_retorno:
        del retorno
    atual = tracemalloc.get_traced_memory()[0]
    tracemalloc.stop()
    return atual - antes, pico - antes


def ler_listagem(caminho):
    with open(caminho, encoding='utf-8', errors='surrogateescape') as arquivo:
        return [linha.rstrip('\n') for linha in arquivo if linha.strip()]


def fmt_t(ns):
    if ns < 1_000:
        return f'{ns:.0f} ns'
    if ns < 1_000_000:
        return f'{ns / 1_000:.1f} us'
    return f'{ns / 1_000_000:.2f} ms'


def fmt_m(b):
    sinal = '-' if b < 0 else ''
    b = abs(b)
    if b < 1024:
        return f'{sinal}{b} B'
    if b < 1024 ** 2:
        return f'{sinal}{b / 1024:.1f} KiB'
    return f'{sinal}{b / 1024 ** 2:.2f} MiB'


def titulo(texto):
    print('\n' + cor(texto, '1;36'))


# ------------------------------------------------------------------ relatorio no terminal
def imprimir(resultado):
    """Tabelas comparativas: as tres estruturas lado a lado em cada tarefa."""
    est, n, lote = resultado['estruturas'], resultado['n'], resultado['lote']
    nomes = list(est)
    cab = ''.join(f'{nome:>24}' for nome in nomes)

    titulo(f'1) Carga dos {n:,} caminhos'.replace(',', '.'))
    print(f'{"":<16}' + cab)
    print(f'{"Tempo":<16}' + ''.join(f'{fmt_t(est[x]["carga"]["tempo_ns"]):>24}' for x in nomes))
    print(f'{"Memoria":<16}' + ''.join(f'{fmt_m(est[x]["carga"]["memoria"][0]):>24}' for x in nomes))
    print(f'{"Bytes por item":<16}' + ''.join(f'{est[x]["carga"]["memoria"][0] / n:>22.0f} B' for x in nomes))

    titulo('2) Arquivos nas posicoes pedidas (o mesmo arquivo nas tres estruturas)')
    for i, c in enumerate(est['Hashtable']['consultas']):
        iguais = all(est[x]['consultas'][i]['arquivo'] == c['arquivo'] for x in nomes)
        print(f'{c["posicao"]:>8,}'.replace(',', '.') + f'  {c["arquivo"]}  ' + cor('[OK]' if iguais else '[DIFERENTE]', '32'))

    titulo('3) Tempo de consulta por posicao (pico de memoria)')
    print(f'{"Posicao":>8}' + cab)
    for i, c in enumerate(est['Hashtable']['consultas']):
        celulas = ''.join(f'{fmt_t(v["tempo_ns"]) + " (" + fmt_m(v["memoria"][1]) + ")":>24}'
                          for v in (est[x]['consultas'][i] for x in nomes))
        print(f'{c["posicao"]:>8,}'.replace(',', '.') + celulas)

    titulo('4) Adicao e remocao (tempo | memoria liquida)')
    print(f'{"Operacao":<16}' + cab)
    for op in est['Hashtable']['operacoes']:
        print(f'{op:<16}' + ''.join(f'{fmt_t(v["tempo_ns"]) + " | " + fmt_m(v["memoria"][0]):>24}'
                                     for v in (est[x]['operacoes'][op] for x in nomes)))

    titulo(f'5) Depois de adicionar e remover {lote:,} itens (LIFO x FIFO)'.replace(',', '.'))
    extremo = {'Hashtable': f'chave {n:,}'.replace(',', '.'), 'Pilha': 'topo', 'Fila': 'frente'}
    for x in nomes:
        ef = est[x]['efeito']
        print(f'{x:<10} 1o removido: {ef["primeiro_removido"]}')
        print(cor(f'{"":<10} {extremo[x]}: {ef["referencia_apos"]}', '33'))


# ------------------------------------------------------------------ principal
def main():
    origem = sys.argv[1] if len(sys.argv) > 1 else os.path.join(RAIZ, 'listagem_arquivos.txt')
    os.makedirs(SAIDA, exist_ok=True)
    lista = ler_listagem(origem)
    n = len(lista)
    posicoes = [1, 100, 1000, 5000, n]
    novos = [f'/novo/arquivo_{i:04d}.txt' for i in range(1, LOTE + 1)]

    titulo('PROGRAMA 2 - HASHTABLE, PILHA E FILA')
    print(f'Arquivo lido : {origem}')
    print(f'Entradas (N) : {n:,}'.replace(',', '.'))
    print(f'Python {platform.python_version()} | {platform.system()} {platform.release()} | '
          f'tempo: mediana (carga {REPETICOES_CARGA}x, consulta {REPETICOES}x, adicao/remocao {REPETICOES_OP}x) | '
          f'memoria: tracemalloc')

    resultado = {'arquivo': origem, 'n': n, 'posicoes': posicoes, 'lote': LOTE,
                 'python': platform.python_version(), 'sistema': f'{platform.system()} {platform.release()}',
                 'repeticoes': {'carga': REPETICOES_CARGA, 'consulta': REPETICOES, 'operacao': REPETICOES_OP},
                 'estruturas': {}}

    print(cor('Medindo carga, consultas, adicao e remocao nas tres estruturas...', '2'))
    for nome in ('Hashtable', 'Pilha', 'Fila'):
        r = resultado['estruturas'][nome] = {}

        # 1) carga
        r['carga'] = {'tempo_ns': tempo_ns(lambda _: carregar(nome, lista), repeticoes=REPETICOES_CARGA),
                      'memoria': memoria(lambda _: carregar(nome, lista))}

        # 2) consulta das posicoes pedidas
        e = carregar(nome, lista)
        if nome == 'Hashtable':
            r['tabela'] = e.estatisticas()
        r['consultas'] = []
        for k in posicoes:
            achado = consultar(nome, e, k)
            assert achado == lista[k - 1], (nome, k)
            t = tempo_ns(lambda _: consultar(nome, e, k))
            m = memoria(lambda _: consultar(nome, e, k))
            r['consultas'].append({'posicao': k, 'arquivo': achado, 'tempo_ns': t, 'memoria': m})

        # 3) adicao e 4) remocao: 1 item e um lote de LOTE itens, sempre sobre uma estrutura recem-carregada
        def nova():
            return carregar(nome, lista)

        def com_lote():
            est = carregar(nome, lista)
            adicionar(nome, est, novos, n)
            return est

        ops = {
            'adicionar_1':    (lambda est: adicionar(nome, est, novos[:1], n), nova),
            f'adicionar_{LOTE}': (lambda est: adicionar(nome, est, novos, n), nova),
            'remover_1':      (lambda est: remover(nome, est, 1, n + LOTE), com_lote),
            f'remover_{LOTE}': (lambda est: remover(nome, est, LOTE, n + LOTE), com_lote),
        }
        r['operacoes'] = {}
        for rotulo, (funcao, preparo) in ops.items():
            t = tempo_ns(funcao, preparo, repeticoes=REPETICOES_OP)
            m = memoria(funcao, preparo, com_retorno=False)
            r['operacoes'][rotulo] = {'tempo_ns': t, 'memoria': m}

        # o que sai e o que fica em cada extremidade depois das operacoes (mostra LIFO x FIFO)
        est = com_lote()
        saiu = remover(nome, est, LOTE, n + LOTE)
        if nome == 'Pilha':
            fica = est.topo()
        elif nome == 'Fila':
            fica = est.frente()
        else:
            fica = est.get(n)
        r['efeito'] = {'primeiro_removido': saiu[0], 'ultimo_removido': saiu[-1],
                       'tamanho_final': len(est), 'referencia_apos': fica}

    imprimir(resultado)
    with open(os.path.join(SAIDA, 'estruturas.json'), 'w', encoding='utf-8') as arquivo:
        json.dump(resultado, arquivo, ensure_ascii=False, indent=2)
    print('\n' + cor('Resultados gravados em resultados/estruturas.json', '33'))


if __name__ == '__main__':
    main()
