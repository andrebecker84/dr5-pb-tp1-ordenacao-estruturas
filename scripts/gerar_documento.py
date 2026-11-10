# -*- coding: utf-8 -*-
"""Gera o documento de entrega do PB-TP1 sobre o molde institucional do Infnet.

    python scripts/gerar_documento.py

Adaptado do gerador do DR1-TP1: reaproveita do molde (docs/molde/andre_becker_DR3_TP1.docx) a capa,
os estilos, o tema, o cabecalho, os rodapes, a faixa decorativa dos titulos e a tabela de links. O
texto vem de docs/RELATORIO_TP1.md e e de proposito curto: apresentacao, links do repositorio e
referencias. O relatorio completo e o notebook andre_becker_PB_TP1.ipynb, publicado no repositorio.

O molde nao e versionado (.gitignore): e a entrega de outra disciplina e traz a identidade visual
do Infnet. Para gerar o documento, coloque-o em docs/molde/ ou passe o caminho como argumento.

Convencoes do markdown:
  ##              titulo de secao, com faixa decorativa
  [rotulo](url)   linhas seguidas de links viram a tabela de links do molde
  paragrafos      corpo; na secao Referencias, sem recuo (ABNT)
"""
import glob, io, os, re, shutil, struct, sys, tempfile, zipfile


RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOLDE = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    RAIZ, 'docs', 'molde', 'andre_becker_DR3_TP1.docx')
SAIDA = os.path.join(RAIZ, 'andre_becker_PB_TP1.docx')
# Fora do projeto de proposito: um diretorio temporario dentro do OneDrive fica
# travado pela sincronizacao no meio do build.
TRAB = os.path.join(tempfile.gettempdir(), '_pacote_docx_pb_tp1')
SRC = os.path.join(RAIZ, 'src')

# Codigo da entrega e dados da disciplina (capa e cabecalho). O molde e o TP1 do DR3.
TP = 'TP1'
DR = 'DR5'
DISCIPLINA = 'Projeto de Bloco: Ciência da Computação'
PROFESSOR = 'Ricardo Pires Mesquita'
DISCIPLINA_MOLDE = 'Microsserviços e DevOps com Spring Boot e Spring Cloud'
PROFESSOR_MOLDE = 'Wesley Bruno Barbosa Silva'

# Data que aparece no cabecalho de todas as paginas depois da capa.
DATA_ENTREGA = '12/11/2026'
# Mesma data em ISO. O cabecalho nao guarda a data como texto simples: ela vive num controle de
# conteudo ligado por data binding a customXml/item1.xml, e o Word reavalia esse vinculo ao abrir
# o arquivo. Trocar so o texto nao adianta — ele volta para a data do molde na primeira abertura.
_dia, _mes, _ano = DATA_ENTREGA.split('/')
DATA_ISO = '%s-%s-%sT00:00:00' % (_ano, _mes, _dia)

# Texto do documento: docs/RELATORIO_TP1.md, sem os comentarios HTML.
def carregar_conteudo():
    texto = io.open(os.path.join(RAIZ, 'docs', 'RELATORIO_TP1.md'), encoding='utf-8').read()
    return re.sub(r'<!--.*?-->', '', texto, flags=re.S)


def trecho_funcoes(nome, funcoes):
    return []


CONTEUDO = carregar_conteudo()

# Link do video de defesa no Google Drive institucional ("qualquer pessoa com o link"): vem do bloco
# "<!-- video: URL -->" do docs/RELATORIO_TP1.md. Enquanto estiver vazio, o documento mostra a caixa.
_video = re.search(r'^@@video[ \t]*(\S*)', CONTEUDO, re.M)
VIDEO_URL = _video.group(1) if _video else ''


# ---------------------------------------------------------------- desempacota
if os.path.isdir(TRAB):
    shutil.rmtree(TRAB)
if os.path.isdir(MOLDE):
    # Aceita o molde ja desempacotado: o .docx original fica travado quando aberto
    # no Word ou enquanto o OneDrive sincroniza.
    shutil.copytree(MOLDE, TRAB)
else:
    with zipfile.ZipFile(MOLDE) as z:
        z.extractall(TRAB)

doc_path = os.path.join(TRAB, 'word', 'document.xml')
d = io.open(doc_path, encoding='utf-8').read()
inicio_body = d.index('<w:body>') + len('<w:body>')

# ------------------------------------------- formatacao extraida do molde
# O corpo do TP1 quase nao usa estilos nomeados: ele formata direto no paragrafo.
# Os valores abaixo foram medidos no proprio documento, para o TP2 sair identico.
TEMA = ('<w:rFonts w:asciiTheme="majorHAnsi" w:hAnsiTheme="majorHAnsi" '
        'w:cstheme="majorHAnsi"/>')
PPR_TITULO = ('<w:spacing w:before="40" w:after="0" w:line="240" w:lineRule="auto"/>'
              '<w:ind w:left="113" w:firstLine="0"/>')
RPR_TITULO = TEMA + '<w:b/><w:bCs/><w:sz w:val="24"/><w:szCs w:val="24"/>'
PPR_CORPO = ('<w:spacing w:before="80" w:after="0" w:line="336" w:lineRule="auto"/>'
             '<w:ind w:left="113" w:firstLine="596"/><w:contextualSpacing/>')
# Item numerado: o numero vai no proprio texto, seguido de tabulacao ate o recuo. A numeracao
# automatica do Word reiniciava a contagem depois de quebras de pagina.
PPR_ITEM_NUMERADO = ('<w:pStyle w:val="PargrafodaLista"/>'
                     '<w:spacing w:before="0" w:after="0" w:line="336" w:lineRule="auto"/>'
                     '<w:ind w:left="1066" w:hanging="357"/>')
# Item com marcador: numeracao 8 do molde, que e um bullet.
PPR_ITEM_MARCADOR = PPR_ITEM_NUMERADO.replace(
    '<w:spacing', '<w:numPr><w:ilvl w:val="0"/><w:numId w:val="8"/></w:numPr><w:spacing', 1)
PPR_REF = ('<w:spacing w:before="0" w:after="100" w:line="240" w:lineRule="auto"/>'
           '<w:ind w:left="113" w:firstLine="0"/><w:jc w:val="left"/>')
PPR_LEGENDA = ('<w:spacing w:before="0" w:after="0" w:line="312" w:lineRule="auto"/>'
               '<w:ind w:firstLine="0"/><w:jc w:val="center"/>')
RPR_LEGENDA = TEMA + ('<w:i/><w:iCs/><w:color w:val="404040"/>'
                      '<w:sz w:val="18"/><w:szCs w:val="18"/>')

# ------------------------------------------------- moldes tirados do TP1
# O molde monta cada secao como uma TABELA de uma celula contendo uma faixa com
# o titulo, e reune os links numa tabela de duas colunas: a estreita leva o
# icone, a larga leva a URL dentro de uma caixa de texto. Em vez de recriar essa
# estrutura, extraimos as tabelas do proprio TP1 e trocamos texto e ids.
def _tabelas(xml):
    return [m.group(0) for m in re.finditer(r'<w:tbl>.*?</w:tbl>', xml, re.S)]

_TABS = _tabelas(d)
_tab_titulo = next((t for t in _TABS if 'rio do Projeto' in ''.join(
    re.findall(r'<w:t(?:\s[^>]*)?>([^<]*)</w:t>', t))), None)
_tab_links = next((t for t in _TABS if t.count('<w:hyperlink') >= 2), None)
_linhas_link = (re.findall(r'<w:tr\b.*?</w:tr>', _tab_links, re.S)
                if _tab_links else [])

_seq = [0]

def _unico(x, base_doc, base_alt, prefixo):
    """Renumera identificadores para o Word nao ver duplicatas."""
    _seq[0] += 1
    n = _seq[0]
    x = re.sub(r'<wp:docPr id="\d+"', lambda mm: '<wp:docPr id="%d"' % (base_doc + n * 7), x)
    x = re.sub(r'relativeHeight="\d+"', 'relativeHeight="%d"' % (base_alt + n * 2048), x)
    x = re.sub(r'w14:paraId="[0-9A-Fa-f]+"', 'w14:paraId="%s%04X"' % (prefixo, n), x)
    return x.replace('<w:lastRenderedPageBreak/>', '')

def titulo(texto):
    """Tabela de uma celula com a faixa do titulo dentro, como no molde."""
    if not _tab_titulo:
        return para(texto, PPR_TITULO, RPR_TITULO)
    x = re.sub(r'(<w:t(?:\s[^>]*)?>)[^<]*(</w:t>)',
               lambda mm: mm.group(1) + esc(texto) + mm.group(2), _tab_titulo)
    x = re.sub(r'<a:t>[^<]*</a:t>', '<a:t>%s</a:t>' % esc(texto), x)
    # "Manter com o proximo" nos paragrafos da faixa: o titulo nao fica sozinho no pe da pagina.
    x = re.sub(r'(<w:pPr>(?:<w:pStyle [^>]*/>)?)(?!<w:keepNext/>)', lambda mm: mm.group(1) + '<w:keepNext/>', x)
    return _unico(x, 1900000000, 251800000, '6A10')

def tabela_links(urls):
    """Tabela de duas colunas: icone na estreita, link na larga."""
    if not _linhas_link:
        return ''.join(link_simples(u if isinstance(u, str) else u[1]) for u in urls)
    cabeca = _tab_links[:_tab_links.index('<w:tr')]
    corpo_linhas = []
    for k, item in enumerate(urls):
        # Uma URL longa nao cabe na caixa do molde; nesses casos o texto visivel e um rotulo.
        rotulo, url = item if isinstance(item, tuple) else (item, item)
        # Usa os icones do molde (linha 0 = documento, linha 1 = GitHub): o repositorio e as
        # pastas levam o do GitHub; arquivos e o notebook no nbviewer levam o de documento.
        e_github = 'github.com' in url and '/blob/' not in url
        tr = _linhas_link[(1 if e_github else 0) % len(_linhas_link)]
        _prox[0] += 1
        rid = 'rId%d' % _prox[0]
        links.append((rid, url))
        tr = re.sub(r'(<w:t(?:\s[^>]*)?>)[^<]*(</w:t>)',
                    lambda mm: mm.group(1) + esc(rotulo) + mm.group(2), tr)
        tr = re.sub(r'<w:hyperlink r:id="rId\d+"', '<w:hyperlink r:id="%s"' % rid, tr)
        corpo_linhas.append(_unico(tr, 1920000000, 251900000, '6B20'))
    return cabeca + ''.join(corpo_linhas) + '</w:tbl>'

# ------------------------------------------- fim da capa, no ponto balanceado
def balanceado(frag):
    pilha = []
    for m in re.finditer(r'<(/?)([A-Za-z0-9:._-]+)([^>]*?)(/?)>', frag):
        fecha, nome, resto, auto = m.groups()
        if auto == '/' or resto.startswith('?') or nome[0] in '?!':
            continue
        if fecha:
            if not pilha or pilha[-1] != nome:
                return False
            pilha.pop()
        else:
            pilha.append(nome)
    return not pilha

paras = [(m.start(), m.end()) for m in re.finditer(r'<w:p [^>]*>.*?</w:p>|<w:p/>', d, re.S)]
alvo = next(a for a, b in paras
            if 'rio do Projeto' in ''.join(re.findall(r'<w:t(?:\s[^>]*)?>([^<]*)</w:t>', d[a:b])))

# O molde envolve o conteudo numa tabela de uma celula; cortar no paragrafo do
# titulo fatiaria o <w:tc>. Recuamos ate o ultimo ponto com as tags fechadas.
cand = sorted({a for a, _ in paras if a <= alvo} |
              {m.start() for m in re.finditer(r'<w:tbl>', d) if m.start() <= alvo})
corte = max(c for c in cand if balanceado(d[inicio_body:c]))
capa = d[inicio_body:corte]

# capa: disciplina, bloco, professor, codigo e mes da entrega ("A" e "gosto/2026" vem em runs
# separados). O molde ja e um "Teste de Performance", TP1, entao esses dois textos ficam.
capa = (capa.replace(DISCIPLINA_MOLDE, DISCIPLINA).replace('DR3', DR)
            .replace(PROFESSOR_MOLDE, PROFESSOR).replace('TP1', TP))
_MESES = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto',
          'Setembro', 'Outubro', 'Novembro', 'Dezembro']
_mes_capa = _MESES[int(_mes) - 1]
capa = re.sub(r'>A</w:t>', '>%s</w:t>' % _mes_capa[0], capa)
capa = capa.replace('gosto/2026', '%s/%s' % (_mes_capa[1:], _ano))

sect = re.search(r'<w:sectPr[^>]*>.*?</w:sectPr>', d, re.S).group(0)

# --- cabecalho e rodapes: o molde traz a data e a disciplina do DR3 ---
# Sem isto, todas as paginas depois da capa exibem 21/08/2026 e a disciplina do molde. O nome da
# disciplina vem quebrado em quatro runs; o primeiro recebe o nome novo e os outros ficam vazios.
for parte in ('header1', 'header2', 'header3', 'footer1', 'footer2', 'footer3'):
    caminho = os.path.join(TRAB, 'word', parte + '.xml')
    if not os.path.exists(caminho):
        continue
    x = io.open(caminho, encoding='utf-8').read()
    x = re.sub(r'\d{2}/\d{2}/2026', DATA_ENTREGA, x)
    x = re.sub(r'w:fullDate="[^"]*"', 'w:fullDate="%sZ"' % DATA_ISO, x)
    x = x.replace('>Microsserviços e </w:t>', '>%s</w:t>' % DISCIPLINA)
    for resto in ('>DevOps</w:t>', '> com Spring Boot</w:t>', '> e Spring Cloud</w:t>'):
        x = x.replace(resto, '></w:t>')
    # O rodape do molde traz uma declaracao de uso de IA que esta disciplina nao exige.
    x = x.replace('>Elaborado com o auxílio de inteligência artificial, conforme orientação '
                  'docente.</w:t>', '></w:t>')
    io.open(caminho, 'w', encoding='utf-8').write(x)

# Propriedades do arquivo (Arquivo > Informacoes no Word): titulo e assunto da entrega.
core = os.path.join(TRAB, 'docProps', 'core.xml')
x = io.open(core, encoding='utf-8').read()
x = x.replace(DISCIPLINA_MOLDE, DISCIPLINA)
x = re.sub(r'<dc:subject>[^<]*</dc:subject>',
           '<dc:subject>%s - PB-%s - Teste de Performance</dc:subject>' % (DR, TP), x)
# O molde e a entrega do DR3: limpa a descricao, as revisoes e as datas herdadas dele.
x = re.sub(r'<dc:description>[^<]*</dc:description>', '<dc:description></dc:description>', x)
x = re.sub(r'<cp:revision>[^<]*</cp:revision>', '<cp:revision>1</cp:revision>', x)
x = re.sub(r'<cp:lastPrinted>[^<]*</cp:lastPrinted>', '', x)
x = re.sub(r'(<dcterms:(?:created|modified)[^>]*>)[^<]*', r'\g<1>%sZ' % DATA_ISO, x)
io.open(core, 'w', encoding='utf-8').write(x)

app = os.path.join(TRAB, 'docProps', 'app.xml')
x = io.open(app, encoding='utf-8').read()
x = re.sub(r'(<TitlesOfParts>.*?<vt:lpstr>)[^<]*', r'\g<1>%s' % DISCIPLINA, x, flags=re.S)
x = re.sub(r'<TotalTime>\d+</TotalTime>', '<TotalTime>0</TotalTime>', x)
io.open(app, 'w', encoding='utf-8').write(x)

# A fonte do data binding. Sem trocar aqui, o Word restaura a data do molde ao abrir o documento,
# desfazendo as substituicoes acima.
custom = os.path.join(TRAB, 'customXml')
if os.path.isdir(custom):
    for nome in os.listdir(custom):
        if not nome.endswith('.xml'):
            continue
        caminho = os.path.join(custom, nome)
        x = io.open(caminho, encoding='utf-8').read()
        if 'PublishDate' not in x:
            continue
        x = re.sub(r'(<PublishDate>)[^<]*(</PublishDate>)',
                   lambda mm: mm.group(1) + DATA_ISO + mm.group(2), x)
        io.open(caminho, 'w', encoding='utf-8').write(x)

# ------------------------------------------------------------------ helpers
def esc(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def runs(texto, extra=''):
    """**negrito**, *italico*, `codigo` e [texto](url) -> runs WordprocessingML."""
    texto = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', texto)
    out = []
    # O negrito vem antes do italico na alternancia: com a ordem trocada, `\*[^*]+\*`
    # casaria os dois primeiros asteriscos de **negrito** e produziria italico vazio.
    for p in [x for x in re.split(r'(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)', texto) if x]:
        if p.startswith('**') and p.endswith('**'):
            rpr, txt = extra + '<w:b/><w:bCs/>', p[2:-2]
        elif p.startswith('*') and p.endswith('*'):
            rpr, txt = extra + '<w:i/><w:iCs/>', p[1:-1]
        elif p.startswith('`') and p.endswith('`'):
            rpr = ('<w:rFonts w:ascii="Consolas" w:hAnsi="Consolas"/>'
                   '<w:sz w:val="19"/><w:szCs w:val="19"/>')
            txt = p[1:-1]
        else:
            rpr, txt = extra, p
        out.append('<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r>'
                   % ('<w:rPr>%s</w:rPr>' % rpr if rpr else '', esc(txt)))
    return ''.join(out)

def para(texto, ppr=PPR_CORPO, rpr=TEMA):
    return '<w:p><w:pPr>%s</w:pPr>%s</w:p>' % (ppr, runs(texto, rpr))

def subtitulo(texto):
    return '<w:p><w:pPr><w:keepNext/>%s</w:pPr>%s</w:p>' % (
        '<w:spacing w:before="160" w:after="40" w:line="240" w:lineRule="auto"/>'
        '<w:ind w:left="113" w:firstLine="0"/>',
        runs(texto, TEMA + '<w:b/><w:bCs/>'))

def codigo(linhas, tam=17, recuo=454):
    # Consolas tambem para os caracteres fora do ASCII (acentos, desenho de caixa da arvore).
    return ''.join(
        '<w:p><w:pPr><w:shd w:val="clear" w:color="auto" w:fill="F2F2F2"/>'
        '<w:spacing w:before="0" w:after="0" w:line="240" w:lineRule="auto"/>'
        '<w:ind w:left="%d" w:firstLine="0"/>'
        # Marca de paragrafo no mesmo tamanho do codigo: sem isto, linhas vazias ficam com a altura
        # da fonte padrao e parecem duplas.
        '<w:rPr><w:sz w:val="%d"/><w:szCs w:val="%d"/></w:rPr></w:pPr>'
        '<w:r><w:rPr><w:rFonts w:ascii="Consolas" w:hAnsi="Consolas" w:cs="Consolas" '
        'w:eastAsia="Consolas"/>'
        '<w:sz w:val="%d"/><w:szCs w:val="%d"/></w:rPr>'
        '<w:t xml:space="preserve">%s</w:t></w:r></w:p>'
        % (recuo, tam, tam, tam, tam, esc(l if l else ' '))
        for l in linhas)

def trecho(nome, funcoes):
    """Rotulo + so as funcoes pedidas de src/<nome>, sem docstring (o arquivo inteiro fica em src/)."""
    return (subtitulo('Trecho de `src/%s`' % nome)
            + codigo(trecho_funcoes(nome, funcoes), tam=15, recuo=113))

def caixa_video():
    return caixa_figura().replace('[ INSERIR AQUI A IMAGEM DA FIGURA ]',
                                  '[ INSERIR AQUI O LINK DO VÍDEO NO GOOGLE DRIVE ]')

def caixa_figura():
    return ('<w:p><w:pPr><w:jc w:val="center"/>'
            '<w:shd w:val="clear" w:color="auto" w:fill="FFF4E5"/><w:pBdr>'
            '<w:top w:val="single" w:sz="6" w:color="E0A800"/>'
            '<w:bottom w:val="single" w:sz="6" w:color="E0A800"/>'
            '<w:left w:val="single" w:sz="6" w:color="E0A800"/>'
            '<w:right w:val="single" w:sz="6" w:color="E0A800"/></w:pBdr>'
            '<w:spacing w:before="240" w:after="0"/><w:ind w:firstLine="0"/></w:pPr>'
            '<w:r><w:rPr>%s<w:i/><w:b/><w:color w:val="B00020"/></w:rPr>'
            '<w:t>[ INSERIR AQUI A IMAGEM DA FIGURA ]</w:t></w:r></w:p>' % TEMA)

def legenda(texto):
    return '<w:p><w:pPr>%s</w:pPr>%s</w:p>' % (
        PPR_LEGENDA + '<w:spacing w:before="80" w:after="240" w:line="312" '
                      'w:lineRule="auto"/>',
        runs(texto, RPR_LEGENDA))

LARG = 9360  # Carta com margens de 1" = 6,5"

def tabela(linhas_md):
    cels = lambda l: [c.strip() for c in l.strip().strip('|').split('|')]
    cab, corpo_tab = cels(linhas_md[0]), [cels(l) for l in linhas_md[2:]]
    n = len(cab)
    # Largura de cada coluna proporcional ao texto mais longo dela (entre 6 e 45 caracteres), para
    # uma coluna curta como "Ex." nao ocupar o mesmo espaco que uma descricao.
    texto = lambda c: re.sub(r'[*`]', '', c)
    peso = [min(45, max(6, max(len(texto(l[k])) for l in [cab] + corpo_tab if k < len(l))))
            for k in range(n)]
    larg = [LARG * p // sum(peso) for p in peso]
    larg[-1] = LARG - sum(larg[:-1])

    def linha(vals, is_cab):
        tcs = ''.join(
            '<w:tc><w:tcPr><w:tcW w:w="%d" w:type="dxa"/>%s</w:tcPr>'
            '<w:p><w:pPr><w:spacing w:before="40" w:after="40" w:line="240" '
            'w:lineRule="auto"/><w:ind w:firstLine="0"/><w:jc w:val="left"/></w:pPr>%s</w:p></w:tc>'
            % (larg[i],
               '<w:shd w:val="clear" w:color="auto" w:fill="323E4F"/>' if is_cab else '',
               runs(v, TEMA + ('<w:b/><w:color w:val="FFFFFF"/>' if is_cab else '')
                    + '<w:sz w:val="20"/><w:szCs w:val="20"/>'))
            for i, v in enumerate(vals[:n]))
        return '<w:tr>%s%s</w:tr>' % (
            '<w:trPr><w:tblHeader/></w:trPr>' if is_cab else '', tcs)

    return ('<w:tbl><w:tblPr><w:tblStyle w:val="Tabelacomgrade"/>'
            '<w:tblW w:w="%d" w:type="dxa"/><w:tblBorders>'
            '<w:top w:val="single" w:sz="4" w:color="BFBFBF"/>'
            '<w:left w:val="single" w:sz="4" w:color="BFBFBF"/>'
            '<w:bottom w:val="single" w:sz="4" w:color="BFBFBF"/>'
            '<w:right w:val="single" w:sz="4" w:color="BFBFBF"/>'
            '<w:insideH w:val="single" w:sz="4" w:color="BFBFBF"/>'
            '<w:insideV w:val="single" w:sz="4" w:color="BFBFBF"/>'
            '</w:tblBorders></w:tblPr><w:tblGrid>%s</w:tblGrid>%s</w:tbl>'
            '<w:p><w:pPr><w:spacing w:after="0"/></w:pPr></w:p>'
            % (LARG, ''.join('<w:gridCol w:w="%d"/>' % x for x in larg),
               linha(cab, True) + ''.join(linha(c, False) for c in corpo_tab)))

# --- hyperlinks externos: cada URL vira um Relationship novo no pacote ---
links = []
_prox = [9000]

# ------------------------------------------------------------------- figuras
# As capturas vivem em evidencias/telas com nome "NN-descricao.png", NN na ordem em que foram
# tiradas, que e a ordem dos exercicios (Figura N = Exercicio N). Quando falta a imagem, fica a
# caixa de marcacao.
EVIDENCIAS = os.path.join(RAIZ, 'evidencias', 'telas')
TELAS = sorted(glob.glob(os.path.join(EVIDENCIAS, '[0-9][0-9]-*.png')))
imagens = []  # (rid, nome no pacote, caminho de origem)

def png_dim(caminho):
    """Largura e altura de um PNG, lidas direto do IHDR — sem depender do Pillow."""
    with open(caminho, 'rb') as f:
        cab = f.read(24)
    if len(cab) < 24 or cab[:8] != b'\x89PNG\r\n\x1a\n':
        return None
    return struct.unpack('>II', cab[16:24])

def figura(numero, texto_legenda):
    """Imagem e legenda num UNICO paragrafo (quebra de linha entre as duas), com keepLines.

    Imagem e legenda em paragrafos separados exigiriam "manter com o proximo" na imagem; com 28
    figuras e os blocos longos dos .txt, essa cadeia de keepNext deixava o Word em laco infinito
    de paginacao ao exportar o PDF. Num paragrafo so, as duas ficam juntas sem cadeia nenhuma.
    """
    achados = TELAS[numero - 1:numero]
    dim = png_dim(achados[0]) if achados else None
    if not dim:
        return caixa_figura() + legenda(texto_legenda)
    larg_px, alt_px = dim
    # 1 twip = 635 EMU. A largura ocupa a area util da pagina; a altura acompanha a proporcao
    # real do arquivo — fixar as duas independentemente e o que deixa a figura esticada.
    # Em 88% da largura util a tela continua legivel e cabe mais vezes no resto da pagina, o que
    # evita os buracos deixados quando a figura inteira pula para a pagina seguinte.
    cx = int(LARG * 0.88) * 635
    cy = int(round(cx * float(alt_px) / larg_px))
    _prox[0] += 1
    rid = 'rId%d' % _prox[0]
    nome = 'figura%02d.png' % numero
    imagens.append((rid, nome, achados[0]))
    ident = 3000 + numero
    return (
        '<w:p><w:pPr><w:keepLines/><w:jc w:val="center"/>'
        '<w:spacing w:before="240" w:after="240" w:line="240" w:lineRule="auto"/>'
        '<w:ind w:firstLine="0"/></w:pPr><w:r><w:drawing>'
        '<wp:inline distT="0" distB="0" distL="0" distR="0">'
        '<wp:extent cx="%d" cy="%d"/><wp:effectExtent l="0" t="0" r="0" b="0"/>'
        '<wp:docPr id="%d" name="Figura %d"/><wp:cNvGraphicFramePr>'
        '<a:graphicFrameLocks xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"'
        ' noChangeAspect="1"/></wp:cNvGraphicFramePr>'
        '<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
        '<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        '<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        '<pic:nvPicPr><pic:cNvPr id="%d" name="%s"/><pic:cNvPicPr/></pic:nvPicPr>'
        '<pic:blipFill><a:blip r:embed="%s"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
        '<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="%d" cy="%d"/></a:xfrm>'
        '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>'
        '</pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r>'
        '<w:r><w:br/></w:r>%s</w:p>'
        % (cx, cy, ident, numero, ident, nome, rid, cx, cy, runs(texto_legenda, RPR_LEGENDA)))

def link_simples(url):
    """Reserva: link como paragrafo, se o molde nao trouxer a tabela."""
    _prox[0] += 1
    rid = 'rId%d' % _prox[0]
    links.append((rid, url))
    return ('<w:p><w:pPr><w:spacing w:before="0" w:after="0" w:line="240" '
            'w:lineRule="auto"/><w:ind w:left="113" w:firstLine="0"/></w:pPr>'
            '<w:hyperlink r:id="%s"><w:r><w:rPr><w:rStyle w:val="Hyperlink"/>%s'
            '<w:sz w:val="18"/><w:szCs w:val="18"/></w:rPr>'
            '<w:t xml:space="preserve">%s</w:t></w:r></w:hyperlink></w:p>'
            % (rid, TEMA, esc(url)))

# --------------------------------------------------------------- markdown
linhas = CONTEUDO.split('\n')
i = 0
while i < len(linhas) and not linhas[i].startswith('## '):
    i += 1

corpo, buf_tab, buf_url = [], [], []
secao = ''

# Linha que comeca outro bloco (titulo, item, tabela, codigo, figura...) e nao continua o paragrafo.
INICIO_DE_BLOCO = r'^(#{2,3} |[-*] |\d+\. |\||```|> |https?://|Figura \d+\.|@@|---$)'

def juntar_continuacao(i, primeira):
    """Junta as linhas seguintes que continuam o mesmo paragrafo. Devolve (texto, ultimo indice lido)."""
    partes = [primeira]
    while i + 1 < len(linhas) and linhas[i + 1].strip() and not re.match(INICIO_DE_BLOCO, linhas[i + 1].strip()):
        i += 1
        partes.append(linhas[i].strip())
    return ' '.join(partes), i

def despeja_tabela():
    global buf_tab
    if len(buf_tab) >= 2:
        corpo.append(tabela(buf_tab))
    buf_tab = []

def despeja_links():
    """URLs consecutivas viram UMA tabela, como no molde.

    Linhas em branco entre elas nao encerram o bloco — se encerrassem, cada link
    viraria uma tabela propria, que foi o defeito da primeira versao.
    """
    global buf_url
    if buf_url:
        corpo.append(tabela_links(buf_url))
    buf_url = []

def despeja():
    despeja_tabela()
    despeja_links()

while i < len(linhas):
    l = linhas[i]
    if l.strip().startswith('|'):
        buf_tab.append(l.strip()); i += 1; continue
    despeja_tabela()
    LINK_MD = re.match(r'^\[([^\]]+)\]\((https?://\S+)\)$', l.strip())
    if l.strip() and not re.match(r'^https?://\S+$', l.strip()) and not LINK_MD:
        despeja_links()

    if l.startswith('```'):
        buf = []; i += 1
        while i < len(linhas) and not linhas[i].startswith('```'):
            buf.append(linhas[i]); i += 1
        corpo.append(codigo(buf)); i += 1; continue

    if l.startswith('@@trecho '):
        _, arquivo, funcoes = l.split()
        corpo.append(trecho(arquivo, funcoes.split(',')))
    elif l.strip().startswith('@@video'):
        if VIDEO_URL:
            buf_url.append(VIDEO_URL)       # o enunciado pede o link: o endereço fica visível
        else:
            corpo.append(caixa_video())
    elif l.startswith('## '):
        secao = l[3:].strip()
        corpo.append(titulo(secao))
    elif l.startswith('### '):
        corpo.append(subtitulo(l[4:]))
    elif re.match(r'^Figura \d+\.', l.strip()):
        corpo.append(figura(int(re.match(r'^Figura (\d+)\.', l.strip()).group(1)), l.strip()))
    elif re.match(r'^https?://\S+$', l.strip()):
        buf_url.append(l.strip())
    elif LINK_MD:
        buf_url.append((LINK_MD.group(1), LINK_MD.group(2)))
    elif re.match(r'^[-*] ', l.strip()):
        texto, i = juntar_continuacao(i, l.strip()[2:])
        corpo.append(para(texto, PPR_ITEM_MARCADOR))
    elif re.match(r'^\d+\. ', l.strip()):
        numero, resto = l.strip().split(' ', 1)
        texto, i = juntar_continuacao(i, resto)
        corpo.append('<w:p><w:pPr>%s</w:pPr><w:r><w:rPr>%s</w:rPr><w:t>%s</w:t></w:r><w:r><w:tab/></w:r>%s</w:p>'
                     % (PPR_ITEM_NUMERADO, TEMA, numero, runs(texto, TEMA)))
    elif l.startswith('> '):
        corpo.append(para(l[2:].strip().strip('*')))
    elif l.strip() in ('---', ''):
        pass
    else:
        # Linhas consecutivas formam um unico paragrafo, como no markdown. Nas Referencias (ABNT):
        # alinhado a esquerda, sem recuo e com uma linha de espaco entre as obras.
        texto, i = juntar_continuacao(i, l.strip())
        corpo.append(para(texto, PPR_REF) if secao == 'Referências' else para(texto))
    i += 1
despeja()

# ------------------------------------------------------------------ escreve
novo = d[:inicio_body] + capa + ''.join(corpo) + sect + '</w:body></w:document>'
io.open(doc_path, 'w', encoding='utf-8').write(novo)

# --- remove imagens e links do molde que o novo corpo nao referencia ---
rels_path = os.path.join(TRAB, 'word', '_rels', 'document.xml.rels')
rels = io.open(rels_path, encoding='utf-8').read()
usados = set(re.findall(r'r:(?:embed|id|link)="(rId\d+)"', novo))
mantidos, removidos = [], []
for m in re.finditer(r'<Relationship [^>]*/>', rels):
    tag = m.group(0)
    rid = re.search(r'Id="(rId\d+)"', tag).group(1)
    alvo_rel = re.search(r'Target="([^"]+)"', tag).group(1)
    if rid not in usados and (alvo_rel.startswith('media/') or 'hyperlink' in tag):
        removidos.append(alvo_rel)
    else:
        mantidos.append(tag)
novos = ''.join(
    '<Relationship Id="%s" Type="http://schemas.openxmlformats.org/officeDocument/'
    '2006/relationships/hyperlink" Target="%s" TargetMode="External"/>' % (rid, url)
    for rid, url in links)
novos += ''.join(
    '<Relationship Id="%s" Type="http://schemas.openxmlformats.org/officeDocument/'
    '2006/relationships/image" Target="media/%s"/>' % (rid, nome)
    for rid, nome, _ in imagens)
rels_novo = re.sub(r'<Relationship [^>]*/>', '', rels)
rels_novo = rels_novo.replace('</Relationships>', ''.join(mantidos) + novos + '</Relationships>')
io.open(rels_path, 'w', encoding='utf-8').write(rels_novo)
for alvo_rel in removidos:
    caminho = os.path.join(TRAB, 'word', alvo_rel.replace('/', os.sep))
    if os.path.exists(caminho):
        os.remove(caminho)

# Copia as capturas para dentro do pacote. Depois da limpeza acima, para nao serem varridas
# junto com as imagens herdadas do molde.
if imagens:
    media = os.path.join(TRAB, 'word', 'media')
    if not os.path.isdir(media):
        os.makedirs(media)
    for _, nome, origem in imagens:
        shutil.copyfile(origem, os.path.join(media, nome))

# ---------------------------------------------------------------- reempacota
if os.path.exists(SAIDA):
    try:
        os.remove(SAIDA)
    except PermissionError:
        shutil.rmtree(TRAB)
        sys.exit('ERRO: %s esta aberto (Word?). Feche-o e rode de novo.' % SAIDA)
with zipfile.ZipFile(SAIDA, 'w', zipfile.ZIP_DEFLATED) as z:
    z.write(os.path.join(TRAB, '[Content_Types].xml'), '[Content_Types].xml')
    for raiz_dir, _, arqs in os.walk(TRAB):
        for a in arqs:
            full = os.path.join(raiz_dir, a)
            rel = os.path.relpath(full, TRAB).replace(os.sep, '/')
            if rel != '[Content_Types].xml':
                z.write(full, rel)
shutil.rmtree(TRAB)
print('gerado: %s (%.0f KB) | figuras inseridas: %d | relacionamentos do molde removidos: %d'
      % (SAIDA, os.path.getsize(SAIDA) / 1024, len(imagens), len(removidos)))
