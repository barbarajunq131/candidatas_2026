
"""
Baixa automaticamente o conjunto 'Candidatos - 2026' pelo catálogo CKAN do TSE,
identifica o CSV principal e produz uma base inicial para SP.

Uso:
    python scripts/atualizar_tse.py

Observação:
    O Portal de Dados Abertos do TSE pode alterar nomes de recursos.
    O script procura o recurso pelo título em vez de depender de uma URL fixa.
"""

from pathlib import Path
import io
import zipfile
import requests
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "candidatas_base.csv"

CKAN_API = "https://dadosabertos.tse.jus.br/api/3/action/package_show"
DATASET_ID = "candidatos-2026"

# Recorte inicial objetivo: federações registradas no TSE que incluem
# PT, PCdoB, PV, PSOL e REDE. A metodologia pode ampliar o conjunto depois.
PARTIDOS_INICIAIS = {"PT", "PCdoB", "PC DO B", "PV", "PSOL", "REDE"}

CARGOS = {"DEPUTADO FEDERAL", "DEPUTADO ESTADUAL"}

COLUNAS_EDITORIAIS = [
    "regiao_atuacao",
    "resumo_trajetoria",
    "trajetoria_declarada",
    "atuacao_documentada",
    "pautas",
    "fonte_principal",
    "fonte_2",
    "fonte_3",
    "ultima_revisao_editorial",
]

def obter_metadados():
    r = requests.get(CKAN_API, params={"id": DATASET_ID}, timeout=60)
    r.raise_for_status()
    payload = r.json()
    if not payload.get("success"):
        raise RuntimeError("O catálogo CKAN não retornou sucesso.")
    return payload["result"]

def escolher_recurso_csv(recursos):
    candidatos = []
    for r in recursos:
        nome = (r.get("name") or "").lower()
        formato = (r.get("format") or "").lower()
        if "candidato" in nome and "complement" not in nome and "social" not in nome:
            if formato in {"csv", "zip"} or "csv" in nome:
                candidatos.append(r)
    if not candidatos:
        raise RuntimeError("Não localizei o CSV principal de candidatos no catálogo do TSE.")
    return candidatos[0]

def ler_recurso(url):
    r = requests.get(url, timeout=180)
    r.raise_for_status()
    content = r.content

    if url.lower().endswith(".zip") or content[:2] == b"PK":
        with zipfile.ZipFile(io.BytesIO(content)) as z:
            csvs = [n for n in z.namelist() if n.lower().endswith(".csv")]
            if not csvs:
                raise RuntimeError("ZIP sem arquivo CSV.")
            with z.open(csvs[0]) as f:
                return pd.read_csv(f, sep=";", encoding="latin1", dtype=str)
    return pd.read_csv(io.BytesIO(content), sep=";", encoding="latin1", dtype=str)

def achar_coluna(df, candidatos):
    normalizadas = {c.upper(): c for c in df.columns}
    for c in candidatos:
        if c.upper() in normalizadas:
            return normalizadas[c.upper()]
    return None

def main():
    meta = obter_metadados()
    recurso = escolher_recurso_csv(meta["resources"])
    df = ler_recurso(recurso["url"]).fillna("")

    col_uf = achar_coluna(df, ["SG_UF"])
    col_cargo = achar_coluna(df, ["DS_CARGO"])
    col_genero = achar_coluna(df, ["DS_GENERO"])
    col_partido = achar_coluna(df, ["SG_PARTIDO"])
    col_nome = achar_coluna(df, ["NM_URNA_CANDIDATO"])
    col_numero = achar_coluna(df, ["NR_CANDIDATO"])
    col_seq = achar_coluna(df, ["SQ_CANDIDATO"])
    col_status = achar_coluna(df, ["DS_SITUACAO_CANDIDATURA", "DS_SITUACAO_CANDIDATO"])

    obrigatorias = [col_uf, col_cargo, col_genero, col_partido, col_nome, col_numero, col_seq]
    if any(c is None for c in obrigatorias):
        faltantes = [x for x, c in zip(
            ["UF","cargo","gênero","partido","nome","número","sequencial"],
            obrigatorias
        ) if c is None]
        raise RuntimeError(f"Colunas esperadas não encontradas: {faltantes}")

    sp = df[
        (df[col_uf].str.upper() == "SP")
        & (df[col_cargo].str.upper().isin(CARGOS))
        & (df[col_genero].str.upper().str.contains("FEMIN", na=False))
        & (df[col_partido].str.upper().isin({p.upper() for p in PARTIDOS_INICIAIS}))
    ].copy()

    out = pd.DataFrame({
        "sq_candidato": sp[col_seq],
        "nome_urna": sp[col_nome],
        "numero": sp[col_numero],
        "cargo": sp[col_cargo].str.title(),
        "partido": sp[col_partido],
        "situacao_candidatura": sp[col_status] if col_status else "",
        "foto_url": "",
    })

    for c in COLUNAS_EDITORIAIS:
        out[c] = ""

    if OUT.exists():
        antiga = pd.read_csv(OUT, dtype=str).fillna("")
        editoriais = ["sq_candidato"] + COLUNAS_EDITORIAIS + ["foto_url"]
        antiga = antiga[[c for c in editoriais if c in antiga.columns]]
        out = out.merge(antiga, on="sq_candidato", how="left", suffixes=("", "_antiga"))
        for c in COLUNAS_EDITORIAIS + ["foto_url"]:
            antiga_c = f"{c}_antiga"
            if antiga_c in out.columns:
                out[c] = out[antiga_c].fillna(out[c])
                out.drop(columns=[antiga_c], inplace=True)

    out = out.drop_duplicates("sq_candidato").sort_values(["cargo", "nome_urna"])
    out.to_csv(OUT, index=False, encoding="utf-8-sig")
    print(f"Base criada: {OUT}")
    print(f"{len(out)} candidatas no recorte inicial.")

if __name__ == "__main__":
    main()
