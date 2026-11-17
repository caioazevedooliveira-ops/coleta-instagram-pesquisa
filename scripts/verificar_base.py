"""Confere um CSV de posts e lista os dias sem post. Só leitura: não grava nada.

Uso, de dentro da pasta do projeto:
    python3 scripts/verificar_base.py saida/coleta_X/posts_grupo.csv --inicio 2026-01-01 --fim 2026-03-31
    python3 scripts/verificar_base.py saida/coleta_Y/posts_grupo.csv --inicio ... --fim ... --anterior saida/coleta_X/posts_grupo.csv

Mostra: linhas, shortcodes repetidos, posts fora do período, curtidas e comentários vazios,
vídeos sem reproduções, posts por perfil de captura, dias sem post e, com --anterior,
o que mudou em relação à coleta anterior (posts novos, posts que sumiram, reproduções recuperadas).
"""
import argparse
import csv
from collections import Counter
from datetime import date, timedelta
from pathlib import Path


def ler(caminho: Path) -> list:
    with open(caminho, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def vazio(valor) -> bool:
    return valor is None or str(valor).strip() in ("", "None")


def main() -> None:
    p = argparse.ArgumentParser(description="Confere um CSV de posts (só leitura)")
    p.add_argument("csv", type=Path)
    p.add_argument("--inicio", type=date.fromisoformat, required=True)
    p.add_argument("--fim", type=date.fromisoformat, required=True)
    p.add_argument("--anterior", type=Path, help="CSV da coleta anterior, para comparar")
    a = p.parse_args()

    linhas = ler(a.csv)
    codigos = [r["shortcode"] for r in linhas]
    repetidos = [c for c, n in Counter(codigos).items() if n > 1]
    ini, fim = a.inicio.isoformat(), a.fim.isoformat()
    fora = [r["shortcode"] for r in linhas if not (ini <= r["data_post"][:10] <= fim)]
    videos = [r for r in linhas if r["formato"] in ("video", "reels")]
    sem_rep = [r for r in videos if vazio(r["reproducoes"]) and vazio(r["visualizacoes"])]

    dias_com_post = {r["data_post"][:10] for r in linhas}
    sem_post, d = [], a.inicio
    while d <= a.fim:
        if d.isoformat() not in dias_com_post:
            sem_post.append(d.isoformat())
        d += timedelta(days=1)

    print(f"Arquivo: {a.csv}")
    print(f"Linhas: {len(linhas)} | shortcodes repetidos: {len(repetidos)}"
          + (f" ({' '.join(repetidos[:10])})" if repetidos else ""))
    print(f"Fora do período {ini} a {fim}: {len(fora)}" + (f" ({' '.join(fora[:10])})" if fora else ""))
    print(f"Curtidas vazias: {sum(vazio(r['curtidas']) for r in linhas)} | "
          f"comentários vazios: {sum(vazio(r['comentarios']) for r in linhas)}")
    print(f"Vídeos: {len(videos)} | sem reproduções nem visualizações: {len(sem_rep)}")
    por_perfil = Counter(r["perfil_da_captura"] for r in linhas)
    print("Posts por perfil de captura: " + ", ".join(f"{k}={v}" for k, v in por_perfil.most_common()))
    por_formato = Counter(r["formato"] for r in linhas)
    print("Posts por formato: " + ", ".join(f"{k}={v}" for k, v in por_formato.most_common()))
    print(f"Dias sem post ({len(sem_post)} de {(a.fim - a.inicio).days + 1}): {' '.join(sem_post) or 'nenhum'}")

    if a.anterior:
        antes = {r["shortcode"]: r for r in ler(a.anterior)}
        agora = {r["shortcode"]: r for r in linhas}
        novos = [c for c in agora if c not in antes]
        sumiram = [c for c in antes if c not in agora]
        recuperadas = [c for c in agora if c in antes and vazio(antes[c]["reproducoes"]) and not vazio(agora[c]["reproducoes"])]
        print(f"\nComparação com {a.anterior.name}: {len(novos)} posts novos | {len(sumiram)} que estavam antes e não estão agora "
              f"| {len(recuperadas)} reproduções recuperadas")
        if sumiram:
            print("  Sumiram (post excluído ou rolagem mais curta): " + " ".join(sumiram[:20]))

    problemas = bool(repetidos or fora)
    print("\nVeredito: " + ("há repetidos ou posts fora do período; corrija antes de seguir." if problemas
                           else "estrutura ok. Agora classifique cada dia sem post (passo 7)."))


if __name__ == "__main__":
    main()
