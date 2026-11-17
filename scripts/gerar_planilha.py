"""Junta os CSVs de uma coleta em UMA planilha .xlsx NOVA, com uma aba por grupo. Não altera nada existente.

Instalar uma vez:  pip install openpyxl
Uso:
    python3 scripts/gerar_planilha.py saida/coleta_X --inicio 2026-08-16 --fim 2026-10-26 \\
        [--transcricoes saida/transcricoes_grupo_a.csv ...]

Abas geradas:
  leia_me      o que é cada aba e cada coluna, data e hora da geração
  resumo       posts, curtidas, comentários e reproduções (média e mediana) por grupo e formato
  <grupo>      uma aba por grupo, todos os posts da coleta
  transcricoes (se houver) shortcode, arquivo, texto
  dias_sem_post  dias do período sem nenhum post, por grupo
Saída: saida/planilha_<AAAA-MM-DD_HHMM>.xlsx (arquivo novo a cada geração)
"""
import argparse
import csv
import statistics as st
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from openpyxl import Workbook

DICIONARIO = [
    ("grupo", "Conjunto de perfis definido em perfis.csv"),
    ("perfil_da_captura", "Perfil que estava aberto quando o post foi capturado"),
    ("autor", "Conta que publicou o post (pode ser parceira)"),
    ("shortcode", "Código único do post no Instagram (chave para cruzar tabelas)"),
    ("url", "Endereço do post"),
    ("data_post", "Data e hora da publicação, fuso America/Sao_Paulo"),
    ("formato", "imagem, carrossel, video ou reels"),
    ("n_midias", "Quantas fotos ou vídeos o post tem (1 se não for carrossel)"),
    ("legenda", "Texto do post"),
    ("hashtags", "Hashtags da legenda, separadas por espaço"),
    ("mencoes", "@ mencionados na legenda, separados por espaço"),
    ("coautores", "@ que assinam junto (post em colaboração)"),
    ("curtidas", "Número de curtidas; vazio = curtida oculta"),
    ("comentarios", "Número de comentários (só a contagem)"),
    ("visualizacoes", "Visualizações de vídeo, quando a plataforma informa"),
    ("reproducoes", "Reproduções de vídeo; só vêm da aba Reels do perfil"),
    ("parceria_paga", "True se a plataforma marca como parceria paga"),
    ("fixado", "True se o post está fixado no topo do perfil"),
    ("data_coleta", "Quando o Zeeschuimer capturou o registro"),
    ("arquivo_origem", "Qual .ndjson originou a linha"),
]


def numero(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("pasta", type=Path, help="pasta saida/coleta_<data>")
    p.add_argument("--inicio", type=date.fromisoformat, required=True)
    p.add_argument("--fim", type=date.fromisoformat, required=True)
    p.add_argument("--transcricoes", nargs="*", type=Path, default=[])
    a = p.parse_args()

    agora = datetime.now(ZoneInfo("America/Sao_Paulo"))
    wb = Workbook()
    leia = wb.active
    leia.title = "leia_me"
    leia.append([f"Gerado em {agora:%Y-%m-%d %H:%M} (America/Sao_Paulo) a partir de {a.pasta}"])
    leia.append([f"Período: {a.inicio} a {a.fim}"])
    leia.append([])
    leia.append(["coluna", "significado"])
    for c in DICIONARIO:
        leia.append(list(c))

    por_grupo = {}
    for arq in sorted(a.pasta.glob("posts_*.csv")):
        por_grupo[arq.stem.removeprefix("posts_")] = list(csv.DictReader(open(arq, encoding="utf-8-sig")))

    resumo = wb.create_sheet("resumo")
    resumo.append(["grupo", "formato", "posts", "curtidas_media", "curtidas_mediana", "comentarios_media",
                   "comentarios_mediana", "reproducoes_media"])
    for grupo, rows in por_grupo.items():
        fmt = defaultdict(list)
        for r in rows:
            fmt[r["formato"]].append(r)
        for f, rs in fmt.items():
            cur = [numero(r["curtidas"]) for r in rs if numero(r["curtidas"]) is not None]
            com = [numero(r["comentarios"]) for r in rs if numero(r["comentarios"]) is not None]
            rep = [numero(r["reproducoes"]) for r in rs if numero(r["reproducoes"]) is not None]
            resumo.append([grupo, f, len(rs), round(st.mean(cur)) if cur else None, round(st.median(cur)) if cur else None,
                           round(st.mean(com)) if com else None, round(st.median(com)) if com else None,
                           round(st.mean(rep)) if rep else None])

    for grupo, rows in por_grupo.items():
        ws = wb.create_sheet(grupo[:31])
        if rows:
            ws.append(list(rows[0]))
            for r in rows:
                ws.append([numero(v) if k in ("curtidas", "comentarios", "visualizacoes", "reproducoes") and numero(v) is not None else v
                           for k, v in r.items()])

    if a.transcricoes:
        ws = wb.create_sheet("transcricoes")
        ws.append(["shortcode", "arquivo", "transcricao"])
        for t in a.transcricoes:
            for r in csv.DictReader(open(t, encoding="utf-8-sig")):
                ws.append([r["shortcode"], r["arquivo"], r["transcricao"]])

    dsp = wb.create_sheet("dias_sem_post")
    dsp.append(["grupo", "dia"])
    for grupo, rows in por_grupo.items():
        dias = {r["data_post"][:10] for r in rows}
        d = a.inicio
        while d <= a.fim:
            if d.isoformat() not in dias:
                dsp.append([grupo, d.isoformat()])
            d += timedelta(1)

    destino = a.pasta.parent / f"planilha_{agora:%Y-%m-%d_%H%M}.xlsx"
    wb.save(destino)
    print(f"Planilha nova: {destino}  (abas: {', '.join(wb.sheetnames)})")
