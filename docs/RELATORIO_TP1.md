<div align="center">

<img src="https://capsule-render.vercel.app/api?section=header&type=waving&color=0:1E3A8A,100:2A78D6&height=170&text=Relat%C3%B3rio%20de%20entrega&fontSize=40&fontColor=ffffff&fontAlignY=34&desc=PB-TP1%20%C2%B7%20Listagem%2C%20Ordena%C3%A7%C3%A3o%20e%20Estruturas%20de%20Dados&descAlignY=58&descSize=16" width="100%" />

[![Página do relatório](https://img.shields.io/badge/Relat%C3%B3rio-p%C3%A1gina%20online-2DA44E?style=for-the-badge&logo=githubpages&logoColor=white)](https://andrebecker84.github.io/dr5-pb-tp1-ordenacao-estruturas/)
[![nbviewer](https://img.shields.io/badge/nbviewer-notebook-1E3A8A?style=for-the-badge&logo=jupyter&logoColor=white)](https://nbviewer.org/github/andrebecker84/dr5-pb-tp1-ordenacao-estruturas/blob/main/andre_becker_PB_TP1.ipynb)
[![Repositório](https://img.shields.io/badge/reposit%C3%B3rio-voltar%20ao%20README-4D4D4D?style=for-the-badge&logo=github&logoColor=white)](../README.md)

</div>

| | |
|---|---|
| **Disciplina** | DR5 · Projeto de Bloco: Ciência da Computação |
| **Professor** | Ricardo Pires Mesquita |
| **Aluno** | André Luis Becker |
| **Turma · Trimestre** | GRLENGR2C2-N2-L1 · 26E4 |

> [!NOTE]
> Este arquivo é a fonte do PDF de entrega (`andre_becker_PB_TP1.pdf`). O
> [`gerar_documento.py`](../scripts/gerar_documento.py) monta o documento sobre o molde institucional:
> capa, as seções abaixo e, em seguida, o relatório completo do notebook, convertido pelo
> [`relatorio_notebook.py`](../scripts/relatorio_notebook.py), com telas, tabelas, gráficos,
> trechos de código e referências. Este cabeçalho não entra no PDF.

<!--
Dialeto lido pelo gerador (o que vem antes do primeiro "## " e ignorado):
  ## titulo com faixa decorativa · ### subtitulo · tabelas | · listas 1. e - · links [rotulo](url)
  em linhas seguidas viram a tabela de links do molde · o marcador "@@notebook" (no comentario la
  embaixo) e trocado pelo conteudo do notebook executado.
-->

## Apresentação

Este Teste de Performance integra **Linux**, **Python** e **análise de algoritmos**. Uma listagem real
de arquivos, gerada no terminal, alimenta dois programas que medem como algoritmos de ordenação e
estruturas de dados se comportam na prática e confrontam essas medições com a notação Big O.

### O que foi feito

1. **Parte 1 · Linux.** No Ubuntu 24.04 (WSL2), o script `gerar_listagem.sh` executa
   `find /usr/lib -type f > listagem_arquivos.txt 2>/dev/null` e grava os **17.520 arquivos** do
   diretório, distribuídos em 2.975 subdiretórios.
2. **Programa 1 · ordenação.** O `ordenacao.py` ordena a listagem com **Bubble Sort**, **Selection
   Sort** e **Insertion Sort** e registra o tempo de cada execução, o crescimento com N e o efeito da
   ordem inicial.
3. **Programa 2 · estruturas.** O `estruturas.py` guarda a listagem em **Hashtable**, **Pilha** e
   **Fila**, recupera os arquivos das posições 1, 100, 1.000, 5.000 e da última, adiciona e remove
   itens e mede o tempo e a memória de cada tarefa.
4. **Análise.** O notebook explica a lógica dos programas, calcula o Big O e compara teoria e prática.
   Os dois programas foram escritos no editor GNU nano e usam só a biblioteca padrão.

### Principais resultados

| Medida | Resultado | Leitura |
|---|---|---|
| Ordenação da listagem completa | Insertion **1,86 s** · Selection 3,81 s · Bubble 6,84 s | os três são O(N²); o tempo fica ≈ 4× maior quando N dobra |
| Por que o Insertion venceu | a listagem tem só **28,3%** de inversões | o custo do Insertion acompanha as inversões: O(N + I) |
| Consulta da posição k | hashtable **≈ 0,2 µs** em qualquer k; fila e pilha até ≈ 0,2 ms | O(1) na hashtable, O(k) na fila, O(N − k) na pilha |
| Adição e remoção (lote de 1.000) | 91 a 835 ns por item | O(1) nas três estruturas |
| Memória por item | pilha e fila **48 B** · hashtable **237 B** | O(N) nas três; a hashtable paga ≈ 4,9× pelo acesso direto |

As seções seguintes trazem o relatório completo, com a lógica dos programas, o Big O de cada
algoritmo, os prints do terminal, as tabelas e os gráficos. A versão online e os arquivos do projeto
estão nos links abaixo.

## Links do projeto

[Repositório no GitHub · andrebecker84/dr5-pb-tp1-ordenacao-estruturas](https://github.com/andrebecker84/dr5-pb-tp1-ordenacao-estruturas)

[Relatório online (GitHub Pages) · notebook completo, sem depender do nbviewer](https://andrebecker84.github.io/dr5-pb-tp1-ordenacao-estruturas/)

[Notebook no nbviewer · andre_becker_PB_TP1.ipynb](https://nbviewer.org/github/andrebecker84/dr5-pb-tp1-ordenacao-estruturas/blob/main/andre_becker_PB_TP1.ipynb)

[Listagem gerada no Linux · listagem_arquivos.txt (17.520 linhas)](https://github.com/andrebecker84/dr5-pb-tp1-ordenacao-estruturas/blob/main/listagem_arquivos.txt)

[Códigos-fonte · gerar_listagem.sh, ordenacao.py e estruturas.py](https://github.com/andrebecker84/dr5-pb-tp1-ordenacao-estruturas/tree/main/src)

<!-- @@notebook -->
