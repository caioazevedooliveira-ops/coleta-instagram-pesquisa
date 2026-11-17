"""Baixa imagens e vídeos dos posts de um .ndjson, para análise e transcrição. Não sobrescreve nada.

Uso, de dentro da pasta do projeto:
    python3 scripts/baixar_midia.py dados_brutos/*.ndjson --perfis perfis.csv \
        --inicio 2026-01-01 --fim 2026-03-31 --so-videos

Grava em midia/<grupo>/<AAAA-MM-DD_HH-MM>_<shortcode>[_<n>].mp4 (ou .jpg). Pula o que já existe.
Os links do Instagram expiram em horas ou dias: baixe logo depois de capturar.
Registro: midia/registro_download.csv (shortcode, arquivo, status). Só usa a biblioteca padrão.
"""
import argparse
import csv
import json
import random
import time
import urllib.request
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from importar_ndjson import URL_PERFIL, ler_perfis


def baixar(url: str, destino: Path) -> str:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as r, open(destino, "wb") as f:
            f.write(r.read())
        return "ok"
    except Exception as erro:  # link expirado, rede etc.
        destino.unlink(missing_ok=True)
        return f"erro:{type(erro).__name__}"


def itens_do_post(d: dict) -> list:
    """(sufixo, extensão, url) de cada mídia; carrossel gera uma por filho."""
    filhos = d.get("carousel_media") or [d]
    saida = []
    for n, f in enumerate(filhos, 1):
        sufixo = "" if len(filhos) == 1 else f"_{n}"
        video = (f.get("video_versions") or [{}])[0].get("url")
        imagem = ((f.get("image_versions2") or {}).get("candidates") or [{}])[0].get("url")
        if video:
            saida.append((sufixo, "mp4", video))
        elif imagem:
            saida.append((sufixo, "jpg", imagem))
    return saida


def main() -> None:
    p = argparse.ArgumentParser(description="Baixa mídia dos posts de um .ndjson")
    p.add_argument("arquivos", nargs="+", type=Path)
    p.add_argument("--perfis", type=Path, required=True)
    p.add_argument("--inicio", type=date.fromisoformat, required=True)
    p.add_argument("--fim", type=date.fromisoformat, required=True)
    p.add_argument("--fuso", default="America/Sao_Paulo")
    p.add_argument("--saida", type=Path, default=Path("midia"))
    p.add_argument("--so-videos", action="store_true", help="não baixa imagens")
    a = p.parse_args()

    fuso, mapa, vistos = ZoneInfo(a.fuso), ler_perfis(a.perfis), set()
    a.saida.mkdir(exist_ok=True)
    registro = a.saida / "registro_download.csv"
    novo = not registro.exists()
    with open(registro, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        if novo:
            w.writerow(["shortcode", "arquivo", "status"])
        for arq in a.arquivos:
            for texto in arq.read_text(encoding="utf-8").splitlines():
                try:
                    reg = json.loads(texto)
                except json.JSONDecodeError:
                    continue
                d = reg.get("data") or {}
                achado = URL_PERFIL.match(reg.get("source_platform_url") or "")
                autor = ((d.get("user") or {}).get("username") or "").lower()
                grupo = mapa.get(achado.group(1).lower() if achado else "") or mapa.get(autor)
                if not grupo or not d.get("code") or not d.get("taken_at") or d["code"] in vistos:
                    continue
                quando = datetime.fromtimestamp(d["taken_at"], fuso)
                if not (a.inicio <= quando.date() <= a.fim):
                    continue
                vistos.add(d["code"])
                pasta = a.saida / grupo
                pasta.mkdir(exist_ok=True)
                for sufixo, ext, url in itens_do_post(d):
                    if a.so_videos and ext != "mp4":
                        continue
                    destino = pasta / f"{quando:%Y-%m-%d_%H-%M}_{d['code']}{sufixo}.{ext}"
                    if destino.exists():
                        continue
                    status = baixar(url, destino)
                    w.writerow([d["code"], destino.name, status])
                    f.flush()
                    print(f"{destino.name}: {status}")
                    time.sleep(random.uniform(0.5, 1.5))


if __name__ == "__main__":
    main()
