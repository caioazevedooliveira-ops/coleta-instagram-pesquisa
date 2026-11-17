"""Transforma as exportações do Zeeschuimer (.ndjson) em CSV, um arquivo por grupo, numa pasta nova.

Uso, de dentro da pasta do projeto:
    python3 scripts/importar_ndjson.py dados_brutos/*.ndjson --perfis perfis.csv --inicio 2026-01-01 --fim 2026-03-31

Saída: saida/coleta_<AAAA-MM-DD>_<HHMM>/posts_<grupo>.csv  +  resumo.txt
Cada rodada cria uma pasta nova. Nada é sobrescrito. Os .ndjson não são tocados.

O mesmo post costuma aparecer duas vezes: no feed (sem reproduções) e na aba Reels (com reproduções).
As duas versões são juntadas: campo vazio numa é preenchido pela outra.

Só usa a biblioteca padrão do Python (3.9+).
"""
import argparse
import csv
import json
import re
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

COLUNAS = [
    "grupo", "perfil_da_captura", "autor", "shortcode", "url", "data_post", "formato", "n_midias",
    "legenda", "hashtags", "mencoes", "coautores", "curtidas", "comentarios", "visualizacoes",
    "reproducoes", "parceria_paga", "fixado", "data_coleta", "arquivo_origem",
]
FORMATOS = {1: "imagem", 2: "video", 8: "carrossel"}
URL_PERFIL = re.compile(r"https://www\.instagram\.com/([\w.]+)/?")


def ler_perfis(caminho: Path) -> dict:
    """Devolve {usuario_ou_alias (minúsculo): grupo}."""
    mapa = {}
    with open(caminho, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            nomes = [r["perfil"], *(r.get("aliases") or "").split(";")]
            for nome in nomes:
                nome = nome.strip().lstrip("@").lower()
                if nome:
                    mapa[nome] = r["grupo"].strip()
    if not mapa:
        raise SystemExit(f"{caminho}: nenhum perfil encontrado. Veja modelos/perfis.csv.")
    return mapa


def montar_linha(registro: dict, grupo: str, perfil: str, origem: str, fuso: ZoneInfo) -> dict:
    d = registro["data"]
    video = d.get("media_type") == 2
    legenda = ((d.get("caption") or {}).get("text") or "")
    curtidas = None if d.get("like_and_view_counts_disabled") else d.get("like_count")
    formato = "reels" if video and d.get("product_type") == "clips" else FORMATOS.get(d.get("media_type"), "imagem")
    ids_do_perfil = {str(u.get("pk")) for u in [d.get("user") or {}, *(d.get("coauthor_producers") or [])]
                     if (u.get("username") or "").lower() == perfil}
    fixado = bool(ids_do_perfil & {str(i) for i in d.get("timeline_pinned_user_ids") or []})
    return {
        "grupo": grupo,
        "perfil_da_captura": perfil,
        "autor": (d.get("user") or {}).get("username", ""),
        "shortcode": d["code"],
        "url": f"https://www.instagram.com/p/{d['code']}/",
        "data_post": datetime.fromtimestamp(d["taken_at"], fuso).strftime("%Y-%m-%d %H:%M"),
        "formato": formato,
        "n_midias": d.get("carousel_media_count") or len(d.get("carousel_media") or []) or 1,
        "legenda": legenda.replace("\r", " ").replace("\n", " "),
        "hashtags": " ".join(re.findall(r"#(\w+)", legenda)),
        "mencoes": " ".join(re.findall(r"@([\w.]+)", legenda)),
        "coautores": " ".join(u.get("username", "") for u in d.get("coauthor_producers") or []),
        "curtidas": curtidas,
        "comentarios": d.get("comment_count"),
        "visualizacoes": d.get("view_count") if video else None,
        "reproducoes": (d.get("play_count") or d.get("ig_play_count")) if video else None,
        "parceria_paga": bool(d.get("is_paid_partnership")),
        "fixado": fixado,
        "data_coleta": datetime.fromtimestamp(registro["timestamp_collected"] / 1000, fuso).strftime("%Y-%m-%d %H:%M"),
        "arquivo_origem": origem,
    }


def juntar(antiga: dict, nova: dict) -> dict:
    """Campo vazio numa versão é preenchido pela outra. Em conflito, fica a captura mais recente."""
    mais_nova, mais_antiga = (nova, antiga) if nova["data_coleta"] >= antiga["data_coleta"] else (antiga, nova)
    return {k: mais_nova[k] if mais_nova[k] not in (None, "") else mais_antiga[k] for k in COLUNAS}


def main() -> None:
    p = argparse.ArgumentParser(description="Importa .ndjson do Zeeschuimer para CSV (pasta nova por coleta)")
    p.add_argument("arquivos", nargs="+", type=Path, help="um ou mais .ndjson")
    p.add_argument("--perfis", type=Path, required=True, help="CSV com grupo, perfil, aliases")
    p.add_argument("--inicio", type=date.fromisoformat, required=True, help="AAAA-MM-DD")
    p.add_argument("--fim", type=date.fromisoformat, required=True, help="AAAA-MM-DD")
    p.add_argument("--fuso", default="America/Sao_Paulo", help="fuso das datas (padrão: America/Sao_Paulo)")
    p.add_argument("--saida", type=Path, default=Path("saida"), help="pasta base das coletas (padrão: saida/)")
    a = p.parse_args()

    fuso = ZoneInfo(a.fuso)
    mapa = ler_perfis(a.perfis)
    posts = defaultdict(dict)  # grupo -> shortcode -> linha
    contagem = {"lidos": 0, "sem_perfil": 0, "fora_do_periodo": 0, "invalidos": 0}

    for arquivo in a.arquivos:
        with open(arquivo, encoding="utf-8") as f:
            for texto in f:
                if not texto.strip():
                    continue
                contagem["lidos"] += 1
                try:
                    reg = json.loads(texto)
                except json.JSONDecodeError:
                    contagem["invalidos"] += 1
                    continue
                d = reg.get("data") or {}
                if not d.get("code") or not d.get("taken_at"):
                    contagem["invalidos"] += 1
                    continue
                achado = URL_PERFIL.match(reg.get("source_platform_url") or "")
                perfil = achado.group(1).lower() if achado else ""
                autor = ((d.get("user") or {}).get("username") or "").lower()
                grupo = mapa.get(perfil) or mapa.get(autor)
                if not grupo:
                    contagem["sem_perfil"] += 1  # capturado fora dos perfis da lista (feed, explorar...)
                    continue
                dia = datetime.fromtimestamp(d["taken_at"], fuso).date()
                if not (a.inicio <= dia <= a.fim):
                    contagem["fora_do_periodo"] += 1
                    continue
                nova = montar_linha(reg, grupo, perfil or autor, arquivo.name, fuso)
                antiga = posts[grupo].get(d["code"])
                posts[grupo][d["code"]] = juntar(antiga, nova) if antiga else nova

    pasta = a.saida / f"coleta_{datetime.now(fuso):%Y-%m-%d_%H%M}"
    pasta.mkdir(parents=True, exist_ok=False)  # nunca escreve numa pasta que já existe

    linhas_resumo = [f"Coleta importada em {datetime.now(fuso):%Y-%m-%d %H:%M} ({a.fuso})",
                     f"Período pedido: {a.inicio} a {a.fim}",
                     f"Arquivos: {', '.join(x.name for x in a.arquivos)}",
                     f"Itens lidos: {contagem['lidos']} | fora dos perfis: {contagem['sem_perfil']} | "
                     f"fora do período: {contagem['fora_do_periodo']} | inválidos: {contagem['invalidos']}", ""]
    for grupo in sorted(posts):
        ordenados = sorted(posts[grupo].values(), key=lambda x: x["data_post"])
        with open(pasta / f"posts_{grupo}.csv", "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=COLUNAS)
            w.writeheader()
            w.writerows(ordenados)
        primeiro, ultimo = ordenados[0]["data_post"][:10], ordenados[-1]["data_post"][:10]
        videos = [x for x in ordenados if x["formato"] in ("video", "reels")]
        com_rep = sum(1 for x in videos if x["reproducoes"] not in (None, ""))
        linhas_resumo.append(f"{grupo}: {len(ordenados)} posts, de {primeiro} a {ultimo}; "
                             f"vídeos com reproduções: {com_rep} de {len(videos)}")
        if primeiro > a.inicio.isoformat():
            linhas_resumo.append(f"  AVISO: ainda não chegou no início do período ({a.inicio}). "
                                 f"Role mais fundo o perfil e importe de novo.")
    if not posts:
        linhas_resumo.append("Nenhum post entrou. Confira se o @ em perfis.csv é igual ao da URL do perfil.")

    resumo = "\n".join(linhas_resumo)
    (pasta / "resumo.txt").write_text(resumo + "\n", encoding="utf-8")
    print(resumo)
    print(f"\nSaída: {pasta}")


if __name__ == "__main__":
    main()
