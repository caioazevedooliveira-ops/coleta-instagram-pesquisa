"""Transcreve o áudio dos vídeos baixados (local, sem internet depois do modelo, sem custo).

Instalar uma vez:  pip install faster-whisper      (baixa o modelo ~500 MB na 1ª execução)
Uso:
    python3 scripts/transcrever.py midia/grupo_a --idioma pt --saida saida/transcricoes_grupo_a.csv

Só transcreve vídeos que ainda não estão no CSV de saída (pode parar e retomar).
Vídeo sem fala (só música) ou sem áudio sai com texto vazio: o script não separa o motivo.
Nome do vídeo esperado: <AAAA-MM-DD_HH-MM>_<shortcode>[_<n>].mp4  (vem de baixar_midia.py).
"""
import argparse
import csv
import os
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
from faster_whisper import WhisperModel  # noqa: E402

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("pasta", type=Path)
    p.add_argument("--saida", type=Path, required=True)
    p.add_argument("--idioma", default="pt")
    p.add_argument("--modelo", default="small", help="small (rápido) ou medium (melhor, mais lento)")
    a = p.parse_args()

    feitos = set()
    if a.saida.exists():
        feitos = {r["arquivo"] for r in csv.DictReader(open(a.saida, encoding="utf-8-sig"))}
    videos = [v for v in sorted(a.pasta.glob("*.mp4")) if v.name not in feitos]
    print(f"{len(videos)} vídeos a transcrever (modelo {a.modelo})")
    modelo = WhisperModel(a.modelo, device="cpu", compute_type="int8",
                          cpu_threads=int(os.environ.get("TRANSCREVER_THREADS", "4")))
    novo = not a.saida.exists()
    a.saida.parent.mkdir(parents=True, exist_ok=True)
    with open(a.saida, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        if novo:
            w.writerow(["shortcode", "arquivo", "transcricao"])
        for n, v in enumerate(videos, 1):
            shortcode = v.stem.split("_", 2)[-1]
            try:
                segmentos, _ = modelo.transcribe(str(v), language=a.idioma, vad_filter=True)
                texto = " ".join(s.text.strip() for s in segmentos)
            except Exception as erro:
                print(f"  [{n}/{len(videos)}] {v.name}: sem áudio legível ({type(erro).__name__})")
                texto = ""
            w.writerow([shortcode, v.name, texto])
            f.flush()
            print(f"  [{n}/{len(videos)}] {v.name}: {texto[:60]}")
