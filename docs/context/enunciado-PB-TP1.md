# 📋 Enunciado · PB-TP1 · DR5 - Projeto de Bloco: Ciência da Computação

> [!NOTE]
> Texto da disciplina, reproduzido apenas como referência para a avaliação (veja a Cláusula 6.1 do
> [LICENSE](../../LICENSE)). Veja também a [rubrica](rubrica-PB-TP1.md) e o [README](../../README.md), que mapeia cada critério
> para a seção do notebook que o atende.

O objetivo deste projeto é permitir que você demonstre suas habilidades em sistemas operacionais Linux, programação em Python, estruturas de dados e análise de algoritmos. Você será responsável por criar uma listagem dos arquivos de um diretório fornecido pelo professor, redirecionar essa listagem para um arquivo de texto e, em seguida, usar esse arquivo em dois programas Python:

* No primeiro, você desenvolverá para realizar a ordenação dos dados usando os algoritmos aprendidos e irá analisar o tempo de execução de cada algoritmo e explicar seus resultados usando a notação Big O.
* No segundo, você irá desenvolver um programa que armazena o conteúdo da listagem em 3 estruturas conhecidas: hashtable, pilha e fila. O programa deve retornar o nome do primeiro arquivo da lista, o nome do último arquivo da listagem e o nome dos arquivos nas posições 100, 1000 e 5000. Além disso, você irá adicionar e remover itens de cada estrutura. Para cada execução, você irá mensurar o tempo de execução e o consumo de memória, explicando os resultados baseados no seu conhecimento de estrutura de dados.

## Parte 1: Manipulação de Arquivos em Linux

1. Utilize um emulador de terminal Linux para acessar um diretório específico fornecido pelo professor (esse diretório terá pelo menos 10000 arquivos, presentes na raiz ou em subdiretórios aninhados).
2. Gere uma listagem completa dos arquivos.
3. Redirecione a saída dessa listagem para um arquivo de texto usando comandos apropriados no Linux.

## Parte 2: Desenvolvimento dos Programas em Python

Crie dois programas em Python (ambos desenvolvidos em um editor de texto não-gráfico do Linux, por linha de comando):

1. O primeiro deve:
   1. Ler a listagem de arquivos do arquivo de texto gerado.
   2. Implementar os algoritmos Bubble Sort, Selection Sort, Insertion Sort para ordenar a listagem.
   3. Medir e registrar o tempo de execução do algoritmo para cada execução de ordenação.
2. O segundo deve:
   1. Ler a listagem de arquivos do arquivo de texto gerado.
   2. Armazenar o conteúdo em três estruturas de dados distintas: Hashtable, pilha e fila.
   3. Recuperar o nome dos arquivos presentes nas posições 1, 100, 1000, 5000 e últimas posições da listagem para cada estrutura.
   4. Medir e registrar o tempo de execução e memória usada nas tarefas pedidas para cada estrutura testada.
   5. O programa também deve executar a adição e remoção de itens nas estruturas de dados, conforme detalhado pelo professor.
   6. Também realize a mensuração do tempo de execução e memória dessas tarefas.

## Parte 3: Análise e Relatório

1. Para cada programa implementado, explique sua lógica e funcionamento.
2. Calcule e explique a complexidade de tempo de cada algoritmo usando a notação Big O.
3. Explique os diferentes tempos de execução e memória encontrados em cada estrutura de dados usados.
4. Compare os tempos de execução observados e relate-os com suas complexidades teóricas.
5. Prepare um relatório detalhado apresentando suas descobertas, incluindo tabelas ou gráficos para comparar o desempenho dos algoritmos.

## Entrega

* Códigos-fontes dos programas em Python.
* Arquivo de texto gerado com a listagem dos arquivos.
* Relatório detalhado incluindo análise teórica e prática dos algoritmos.

Este projeto visa avaliar sua capacidade de integrar conhecimentos em diferentes áreas, como o uso de sistemas operacionais Linux, programação em Python e teoria de algoritmos. Espera-se que você aplique esses conhecimentos de forma prática e analítica para resolver o problema proposto.

Assim que terminar, salve seu trabalho em PDF nomeando o arquivo conforme a regra "nome_sobrenome_PB_TP1.PDF" e poste como resposta a este TP.

---

<p align="right"><a href="../../README.md">⬅ voltar ao README</a></p>
