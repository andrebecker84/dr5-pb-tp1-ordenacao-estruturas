# -*- coding: utf-8 -*-
"""Executa o PB-TP1 no WezTerm (Ubuntu/WSL2, shell fish) e captura cada tela da janela real.

    uv run --no-project --with pillow python scripts/capturar_wezterm.py

1. Copia os fontes de src/ para ~/PB_TP1 no Ubuntu (estado limpo).
2. Abre uma janela nova do WezTerm com o ~/.wezterm.lua do usuario (tema, fonte, prompt starship).
3. Digita cada comando no fish pelo `wezterm cli send-text` e espera o prompt voltar.
4. Captura a janela com PrintWindow (scripts/capturar_janela.ps1) e corta a area vazia de baixo.
5. Traz de volta a listagem, os resultados (JSON) e o texto puro das telas dos dois programas.

Com --so-estruturas, refaz apenas as telas do Programa 2 (04, 06 e 07) sobre a listagem ja gerada:
o /usr/lib muda a cada atualizacao de pacotes, e um novo `find` trocaria N e todas as outras figuras.
"""
import os
import subprocess
import sys
import time

from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TELAS = os.path.join(RAIZ, 'evidencias', 'telas')
RESULTADOS = os.path.join(RAIZ, 'resultados')
WEZ = r'C:\Program Files\WezTerm'
SOCKETS = os.path.join(os.path.expanduser('~'), '.local', 'share', 'wezterm')
DIR_LISTADO = '/usr/lib'
LINHAS, COLUNAS = 54, 150
PROMPT = '❯'

RAIZ_WSL = '/mnt/c' + RAIZ[2:].replace('\\', '/')
env = dict(os.environ)
fig = 0


def wsl(cmd):
    subprocess.run(['wsl', '-d', 'Ubuntu', '--exec', 'bash', '-c', cmd], check=True)


def cli(*args):
    r = subprocess.run([os.path.join(WEZ, 'wezterm.exe'), 'cli', *args], env=env,
                       capture_output=True, text=True, encoding='utf-8')
    if r.returncode:
        raise RuntimeError(r.stderr)
    return r.stdout


def texto():
    linhas = cli('get-text', '--start-line', '-2000').rstrip().split('\n')
    return [l.rstrip() for l in linhas]


def prompts(linhas):
    return sum(1 for l in linhas if l.startswith(PROMPT))


def ocioso(linhas):
    return bool(linhas) and linhas[-1].strip() == PROMPT


def esperar(condicao, limite=900):
    fim = time.time() + limite
    while time.time() < fim:
        if condicao(texto()):
            time.sleep(0.6)            # deixa o starship terminar de desenhar o prompt
            return
        time.sleep(0.5)
    raise TimeoutError('o prompt nao voltou')


def digita(comando):
    cli('send-text', '--no-paste', comando + '\r')


def cmd(comando):
    antes = prompts(texto())
    digita(comando)
    esperar(lambda l: ocioso(l) and prompts(l) > antes)


def limpa():
    digita('clear')
    time.sleep(1)
    esperar(lambda l: ocioso(l) and prompts(l) == 1)


def tela(nome):
    global fig
    fig += 1
    destino = os.path.join(TELAS, f'{fig:02d}-{nome}.png')
    time.sleep(0.8)
    subprocess.run(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
                    os.path.join(RAIZ, 'scripts', 'capturar_janela.ps1'), '-Hwnd', str(hwnd), '-Saida', destino],
                   check=True)
    cortar(destino)
    return destino


def cortar(caminho):
    """Corta a parte de baixo sem texto. Texto tem brilho alto; o fundo e o fantasma do tema, nao."""
    img = Image.open(caminho).convert('RGB')
    w, h = img.size
    px = img.load()
    ultima = 0
    for y in range(h - 1, 0, -1):
        if any(sum(px[x, y]) > 330 for x in range(0, w - 40, 2)):
            ultima = y
            break
    img.crop((0, 0, w, min(h, ultima + 34))).save(caminho, optimize=True)


def executa(nome, *comandos):
    limpa()
    for c in comandos:
        cmd(c)
    tela(nome)


def editor(nome, arquivo, linha):
    limpa()
    digita(f'nano --linenumbers +{linha} {arquivo}')
    time.sleep(2.5)
    tela(nome)
    cli('send-text', '--no-paste', '\x18')         # Ctrl-X: sai do nano sem alterar nada
    esperar(ocioso)


def saida_texto(nome):
    linhas = texto()
    with open(os.path.join(RESULTADOS, f'saida_{nome}.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(linhas) + '\n')


SO_ESTRUTURAS = '--so-estruturas' in sys.argv
REFEITAS = ('04-', '06-', '07-')

if __name__ == '__main__':
    os.makedirs(TELAS, exist_ok=True)
    os.makedirs(RESULTADOS, exist_ok=True)
    for f in os.listdir(TELAS):
        if f.endswith('.png') and (not SO_ESTRUTURAS or f.startswith(REFEITAS)):
            os.remove(os.path.join(TELAS, f))

    # estado limpo no Ubuntu: so os tres fontes, sem permissao de execucao (o chmod +x aparece na tela)
    wsl(f'rm -rf ~/PB_TP1 && mkdir -p ~/PB_TP1 && cp "{RAIZ_WSL}"/src/gerar_listagem.sh '
        f'"{RAIZ_WSL}"/src/ordenacao.py "{RAIZ_WSL}"/src/estruturas.py ~/PB_TP1/ && chmod 644 ~/PB_TP1/*')
    if SO_ESTRUTURAS:
        # a listagem e os resultados do Programa 1 da execucao original, com as datas preservadas
        wsl(f'chmod 755 ~/PB_TP1/gerar_listagem.sh && mkdir -p ~/PB_TP1/resultados && '
            f'cp -p "{RAIZ_WSL}"/listagem_arquivos.txt ~/PB_TP1/ && '
            f'cp -p "{RAIZ_WSL}"/resultados/ordenacao.json "{RAIZ_WSL}"/resultados/listagem_ordenada.txt '
            f'~/PB_TP1/resultados/ && chmod 644 ~/PB_TP1/listagem_arquivos.txt ~/PB_TP1/resultados/*')

    gui = subprocess.Popen([os.path.join(WEZ, 'wezterm-gui.exe'), '--config', f'initial_rows={LINHAS}',
                            '--config', f'initial_cols={COLUNAS}', 'start', '--always-new-process',
                            '--class', 'pbtp1'])
    socket = os.path.join(SOCKETS, f'gui-sock-{gui.pid}')
    for _ in range(60):
        if os.path.exists(socket):
            break
        time.sleep(0.5)
    env['WEZTERM_UNIX_SOCKET'] = socket
    hwnd = 0
    for _ in range(60):
        r = subprocess.run(['powershell', '-NoProfile', '-Command', f'(Get-Process -Id {gui.pid}).MainWindowHandle'],
                           capture_output=True, text=True)
        hwnd = int(r.stdout.strip() or 0)
        if hwnd:
            break
        time.sleep(0.5)
    esperar(ocioso, 60)

    try:
        if SO_ESTRUTURAS:
            fig = 3
            cmd('cd ~/PB_TP1')
            editor('nano-estruturas', 'estruturas.py', 70)
            fig = 5
            executa('estruturas', 'python3 estruturas.py listagem_arquivos.txt')
            saida_texto('estruturas')
            executa('artefatos', 'ls -l ~/PB_TP1 ~/PB_TP1/resultados')
        else:
            executa('diretorio-listado',
                    'cat /etc/os-release | head -2 && uname -sr',
                    f'cd {DIR_LISTADO} && pwd',
                    'ls | head -12',
                    'find . -type d | wc -l      # subdiretorios aninhados',
                    'find . -type f | wc -l      # arquivos regulares',
                    'cd ~/PB_TP1')
            executa('listagem',
                    'cat gerar_listagem.sh',
                    f'chmod +x gerar_listagem.sh && ./gerar_listagem.sh {DIR_LISTADO} listagem_arquivos.txt',
                    'head -5 listagem_arquivos.txt',
                    'tail -3 listagem_arquivos.txt',
                    'ls -lh listagem_arquivos.txt && file listagem_arquivos.txt')
            editor('nano-ordenacao', 'ordenacao.py', 64)
            editor('nano-estruturas', 'estruturas.py', 70)
            executa('ordenacao',
                    'python3 ordenacao.py listagem_arquivos.txt',
                    "LC_ALL=C sort listagem_arquivos.txt | cmp - resultados/listagem_ordenada.txt && echo 'identica ao sort do Linux'")
            saida_texto('ordenacao')
            executa('estruturas', 'python3 estruturas.py listagem_arquivos.txt')
            saida_texto('estruturas')
            executa('artefatos', 'ls -l ~/PB_TP1 ~/PB_TP1/resultados')
    finally:
        try:
            cli('kill-pane')                         # fecha a janela de captura (sem confirmacao)
        except Exception:
            gui.terminate()

    if SO_ESTRUTURAS:
        wsl(f'cp ~/PB_TP1/resultados/estruturas.json "{RAIZ_WSL}/resultados/"')
    else:
        wsl(f'cp ~/PB_TP1/listagem_arquivos.txt "{RAIZ_WSL}/" && cp ~/PB_TP1/resultados/* "{RAIZ_WSL}/resultados/"')
    print(f'telas capturadas: {fig}')
