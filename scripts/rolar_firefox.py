"""Abre um perfil do Instagram no Firefox e rola a página sozinho, para o Zeeschuimer capturar os posts.

Funciona em macOS, Windows e Linux (Linux precisa do xdotool: sudo apt install xdotool).

Uso, de dentro da pasta do projeto:
    python3 scripts/rolar_firefox.py nome_do_perfil                 # feed, 40 rolagens
    python3 scripts/rolar_firefox.py nome_do_perfil/reels           # aba de vídeos (traz as reproduções)
    python3 scripts/rolar_firefox.py nome_do_perfil --rolagens 100  # mais fundo no perfil

Antes de rodar: Firefox aberto, conta de pesquisa logada, chave do Instagram ligada no Zeeschuimer.
macOS: Ajustes > Privacidade e Segurança > Acessibilidade > ligar o Terminal. O script confere se o
Firefox está na frente e para se ele sair. Windows e Linux: o script não consegue conferir isso;
deixe o Firefox na frente e não toque no computador enquanto roda.
Ao terminar: no Zeeschuimer, Download (ndjson), mover para dados_brutos/, Delete.
"""
import argparse
import platform
import random
import shutil
import subprocess
import sys
import time

PAUSA_PADRAO = (3.0, 7.0)  # segundos entre rolagens: ritmo de pessoa lendo, não de robô
SISTEMA = platform.system()  # Darwin, Windows ou Linux

# macOS: aperta Page Down só se o Firefox estiver na frente; devolve "fora" se não estiver.
APERTAR_MAC = '''
tell application "System Events"
    set naFrente to name of (first application process whose frontmost is true)
    if naFrente is not "firefox" then return "fora"
    key code 121
end tell
return "ok"
'''


def osascript(codigo: str) -> str:
    r = subprocess.run(["osascript", "-e", codigo], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(
            f"\nO Mac não deixou controlar o teclado: {r.stderr.strip()}\n"
            "Ligue a permissão em Ajustes > Privacidade e Segurança > Acessibilidade para o app\n"
            "de onde você roda o script (Terminal), feche e abra esse app e rode de novo."
        )
    return r.stdout.strip()


def abrir(url: str) -> None:
    if SISTEMA == "Darwin":
        subprocess.run(["open", "-a", "Firefox", url], check=True)
    elif SISTEMA == "Windows":
        subprocess.run(["cmd", "/c", "start", "", "firefox", url], check=True)
    else:
        if not shutil.which("firefox"):
            raise SystemExit("Não achei o comando 'firefox'. Abra o perfil à mão e rode de novo com --sem-abrir.")
        subprocess.Popen(["firefox", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def trazer_firefox_para_frente() -> None:
    if SISTEMA == "Darwin":
        osascript('tell application "Firefox" to activate')
    elif SISTEMA == "Linux" and shutil.which("xdotool"):
        subprocess.run(["xdotool", "search", "--onlyvisible", "--class", "firefox", "windowactivate"],
                       capture_output=True)
    # Windows: sem jeito simples e confiável só com a biblioteca padrão; a pessoa deixa o Firefox na frente.


def apertar_page_down() -> str:
    """Devolve 'ok' ou 'fora' (só o Mac sabe dizer 'fora')."""
    if SISTEMA == "Darwin":
        return osascript(APERTAR_MAC)
    if SISTEMA == "Windows":
        import ctypes
        VK_NEXT, KEYUP = 0x22, 0x0002
        ctypes.windll.user32.keybd_event(VK_NEXT, 0, 0, 0)
        ctypes.windll.user32.keybd_event(VK_NEXT, 0, KEYUP, 0)
        return "ok"
    if not shutil.which("xdotool"):
        raise SystemExit("No Linux este script precisa do xdotool: sudo apt install xdotool")
    subprocess.run(["xdotool", "key", "Next"], check=True)
    return "ok"


def main() -> None:
    p = argparse.ArgumentParser(description="Rola um perfil do Instagram no Firefox para o Zeeschuimer")
    p.add_argument("perfil", help="o @ sem arroba, ex.: nome_do_perfil ou nome_do_perfil/reels")
    p.add_argument("--rolagens", type=int, default=40, help="quantas vezes apertar Page Down (padrão: 40)")
    p.add_argument("--pausa", type=float, nargs=2, default=PAUSA_PADRAO, metavar=("MIN", "MAX"),
                   help="pausa entre rolagens em segundos (padrão: 3 7). Não diminua.")
    p.add_argument("--sem-abrir", action="store_true", help="não abre a URL; usa a aba que já está aberta")
    a = p.parse_args()

    caminho = a.perfil.strip("@/ ")
    url = f"https://www.instagram.com/{caminho}/"
    if a.sem_abrir:
        print(f"Vou rolar a aba que está aberta no Firefox. Deixe {url} na frente.")
    else:
        abrir(url)
        print(f"Abrindo {url} no Firefox...")
    print("Começo em 10 segundos. Não toque no computador até terminar.", flush=True)
    time.sleep(10)  # tempo de a página carregar e de a pessoa tirar as mãos
    trazer_firefox_para_frente()
    time.sleep(2)

    tentativas_de_voltar = 3  # o Mac às vezes devolve o foco ao Terminal; mais que isso é a pessoa usando
    for n in range(1, a.rolagens + 1):
        while apertar_page_down() == "fora":
            if not tentativas_de_voltar:
                raise SystemExit(f"\nO Firefox saiu da frente. Parei na rolagem {n - 1} de {a.rolagens}.")
            tentativas_de_voltar -= 1
            trazer_firefox_para_frente()
            time.sleep(2)
        print(f"  rolagem {n}/{a.rolagens}", end="\r", flush=True)
        time.sleep(random.uniform(*a.pausa))

    print(f"\nPronto: {a.rolagens} rolagens em {url}")
    print("Agora: clique no Z, Download (formato ndjson), mova o arquivo para dados_brutos/ e clique em Delete.")


if __name__ == "__main__":
    if sys.version_info < (3, 9):
        raise SystemExit("Precisa de Python 3.9 ou mais novo.")
    main()
