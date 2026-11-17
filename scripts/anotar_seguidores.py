"""Anota o número de seguidores de cada perfil no dia. Só acrescenta linhas; nunca apaga nem altera.

Uso, de dentro da pasta do projeto, uma vez por dia:
    python3 scripts/anotar_seguidores.py nome_do_perfil=1234567 outro_perfil=98765

Onde ver o número exato: abra o perfil no Firefox e passe o mouse sobre "seguidores".
Grava em dados_brutos/seguidores.csv (data, perfil, seguidores). Se o perfil já tem linha hoje, avisa e não repete.
"""
import argparse
import csv
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

COLUNAS = ["data", "perfil", "seguidores"]


def main() -> None:
    p = argparse.ArgumentParser(description="Anota seguidores do dia (só acrescenta)")
    p.add_argument("pares", nargs="+", help="perfil=numero, ex.: nome_do_perfil=1234567")
    p.add_argument("--arquivo", type=Path, default=Path("dados_brutos/seguidores.csv"))
    p.add_argument("--fuso", default="America/Sao_Paulo")
    a = p.parse_args()

    hoje = datetime.now(ZoneInfo(a.fuso)).strftime("%Y-%m-%d")
    a.arquivo.parent.mkdir(parents=True, exist_ok=True)
    ja_hoje = set()
    if a.arquivo.exists():
        with open(a.arquivo, encoding="utf-8-sig", newline="") as f:
            ja_hoje = {r["perfil"] for r in csv.DictReader(f) if r["data"] == hoje}

    novas = []
    for par in a.pares:
        perfil, _, valor = par.partition("=")
        perfil = perfil.strip().lstrip("@").lower()
        numero = re.sub(r"[.\s,]", "", valor)
        if not perfil or not numero.isdigit():
            raise SystemExit(f"Não entendi '{par}'. Use perfil=numero, com o número exato (sem 'mil' ou 'mi').")
        if perfil in ja_hoje:
            print(f"  {perfil}: já tem registro hoje ({hoje}); não repeti.")
            continue
        novas.append({"data": hoje, "perfil": perfil, "seguidores": int(numero)})

    if novas:
        existe = a.arquivo.exists()
        with open(a.arquivo, "a", encoding="utf-8-sig" if not existe else "utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=COLUNAS)
            if not existe:
                w.writeheader()
            w.writerows(novas)
        for n in novas:
            print(f"  {n['perfil']}: {n['seguidores']:,} seguidores em {hoje}".replace(",", "."))
    print(f"Arquivo: {a.arquivo}")


if __name__ == "__main__":
    main()
