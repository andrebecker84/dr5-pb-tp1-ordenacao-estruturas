# Listagem, Ordenação e Estruturas de Dados

> **PB-TP1 · Bloco Ciência da Computação**\
> Disciplina: DR5 · Projeto de Bloco: Ciência da Computação\
> Trimestre: 26E4\
> Professor: Ricardo Pires Mesquita\
> Aluno: André Luis Becker\
> Turma: GRLENGR2C2-N2-L1\
> Repositório: [andrebecker84/dr5-pb-tp1-ordenacao-estruturas](https://github.com/andrebecker84/dr5-pb-tp1-ordenacao-estruturas)

<!--
Fonte do documento de entrega (scripts/gerar_documento.py monta o .docx sobre o molde institucional e
scripts/exportar_pdf.ps1 exporta o PDF). O documento e de proposito curto: apresenta o trabalho e aponta
para o repositorio, onde estao o notebook com o relatorio completo, os fontes e a listagem.
-->

## Apresentação

Este Teste de Performance integra Linux, Python e análise de algoritmos. No terminal do Ubuntu 24.04
(WSL2), gerei com `find /usr/lib -type f > listagem_arquivos.txt` a listagem completa de 17.520
arquivos, distribuídos em 2.976 subdiretórios. Essa listagem alimenta dois programas em Python, escritos
no editor GNU nano e só com a biblioteca padrão.

O primeiro ordena a listagem com Bubble Sort, Selection Sort e Insertion Sort e mede o tempo de cada
execução. Os três são O(N²): quando N dobra, o tempo fica cerca de 4 vezes maior. Ainda assim, o Insertion
Sort foi o mais rápido (1,86 s, contra 3,81 s do Selection e 6,84 s do Bubble), porque o seu custo
acompanha o número de inversões da entrada, que aqui era de apenas 28,3% dos pares.

O segundo armazena a listagem em uma Hashtable, uma Pilha e uma Fila, recupera os arquivos das posições
1, 100, 1.000, 5.000 e da última, adiciona e remove itens e mede o tempo e a memória de cada tarefa.
A consulta por posição custa O(1) na hashtable, O(k) na fila e O(N − k) na pilha; adicionar e remover
custa O(1) nas três. Em troca do acesso direto, a hashtable usa cerca de 5 vezes mais memória por item.

O relatório completo, com a lógica dos programas, o Big O de cada algoritmo, os prints do terminal, as
tabelas e os gráficos, está no notebook do repositório.

## Links do projeto

[Repositório no GitHub · andrebecker84/dr5-pb-tp1-ordenacao-estruturas](https://github.com/andrebecker84/dr5-pb-tp1-ordenacao-estruturas)

[Relatório completo · notebook andre_becker_PB_TP1.ipynb (nbviewer)](https://nbviewer.org/github/andrebecker84/dr5-pb-tp1-ordenacao-estruturas/blob/main/andre_becker_PB_TP1.ipynb)

[Listagem gerada no Linux · listagem_arquivos.txt (17.520 linhas)](https://github.com/andrebecker84/dr5-pb-tp1-ordenacao-estruturas/blob/main/listagem_arquivos.txt)

[Códigos-fonte · gerar_listagem.sh, ordenacao.py e estruturas.py](https://github.com/andrebecker84/dr5-pb-tp1-ordenacao-estruturas/tree/main/src)

## Referências

CORMEN, T. H.; LEISERSON, C. E.; RIVEST, R. L.; STEIN, C. **Algoritmos: teoria e prática**. Tradução da 3. ed. americana. Rio de Janeiro: Elsevier, 2012.

GOODRICH, M. T.; TAMASSIA, R.; GOLDWASSER, M. H. **Data structures and algorithms in Python**. Hoboken: Wiley, 2013.

KNUTH, D. E. **The art of computer programming**: volume 3: sorting and searching. 2. ed. Reading: Addison-Wesley, 1998.

SEDGEWICK, R.; WAYNE, K. **Algorithms**. 4. ed. Upper Saddle River: Addison-Wesley, 2011.

SHOTTS, W. **The Linux command line**: a complete introduction. 2. ed. San Francisco: No Starch Press, 2019.
