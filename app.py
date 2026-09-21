
import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="Candidatas SP 2026",
    page_icon="🗳️",
    layout="wide",
)

BASE = Path(__file__).parent
ARQ = BASE / "data" / "candidatas_base.csv"

PAUTAS = [
    "Direitos das mulheres",
    "Igualdade racial",
    "Meio ambiente e clima",
    "Educação",
    "Saúde e SUS",
    "Moradia",
    "Trabalho e renda",
    "Assistência social",
    "Cultura",
    "Direitos LGBTQIA+",
    "Povos indígenas",
    "Agricultura familiar e reforma agrária",
    "Ciência e tecnologia",
    "Mobilidade",
    "Direitos das pessoas com deficiência",
]

@st.cache_data
def carregar_dados():
    if not ARQ.exists():
        return pd.DataFrame()
    df = pd.read_csv(ARQ, dtype=str).fillna("")
    return df

def lista_pautas(valor):
    return [x.strip() for x in valor.split("|") if x.strip()]

def card_candidata(row):
    with st.container(border=True):
        c1, c2 = st.columns([1, 3])
        with c1:
            if row.get("foto_url"):
                st.image(row["foto_url"], width=150)
            else:
                st.caption("Foto oficial ainda não vinculada")
        with c2:
            st.subheader(row.get("nome_urna", ""))
            partido = row.get("partido", "")
            numero = row.get("numero", "")
            cargo = row.get("cargo", "")
            st.write(f"**{cargo}** · {partido} · nº {numero}")
            if row.get("regiao_atuacao"):
                st.caption(f"Atuação: {row['regiao_atuacao']}")
            pautas = lista_pautas(row.get("pautas", ""))
            if pautas:
                st.write(" · ".join([f"`{p}`" for p in pautas]))
            if row.get("resumo_trajetoria"):
                st.write(row["resumo_trajetoria"])
            if row.get("fonte_principal"):
                st.link_button("Ver fonte principal", row["fonte_principal"])

st.title("Candidatas de São Paulo — Eleições 2026")
st.caption(
    "Plataforma informativa baseada em dados oficiais e fontes públicas. "
    "Não classifica, recomenda ou ranqueia candidatas."
)

with st.expander("Metodologia e critérios", expanded=False):
    st.markdown("""
    **Escopo inicial:** candidaturas femininas a deputada federal e deputada estadual
    no estado de São Paulo, pertencentes aos partidos/federações definidos na metodologia editorial.

    **Fontes eleitorais:** dados oficiais do TSE.

    **Trajetórias e pautas:** somente informações documentadas em fontes públicas.
    O site diferencia dados oficiais, trajetória declarada e atuação documentada.

    **Sem ranking:** os filtros servem para localizar candidatas por cargo, partido,
    território e temas. A plataforma não atribui notas nem indica voto.
    """)

df = carregar_dados()

if df.empty:
    st.warning(
        "A base ainda está vazia. Execute scripts/atualizar_tse.py e depois preencha "
        "os campos editoriais em data/candidatas_base.csv."
    )
    st.stop()

st.sidebar.header("Filtros")

cargo_opts = sorted([x for x in df["cargo"].unique() if x])
cargo_sel = st.sidebar.multiselect("Cargo", cargo_opts, default=cargo_opts)

partido_opts = sorted([x for x in df["partido"].unique() if x])
partido_sel = st.sidebar.multiselect("Partido", partido_opts, default=partido_opts)

pauta_sel = st.sidebar.multiselect("Pautas", PAUTAS)

busca = st.sidebar.text_input("Buscar por nome ou trajetória")

f = df.copy()

if cargo_sel:
    f = f[f["cargo"].isin(cargo_sel)]
if partido_sel:
    f = f[f["partido"].isin(partido_sel)]
if pauta_sel:
    f = f[f["pautas"].apply(lambda x: any(p in lista_pautas(x) for p in pauta_sel))]
if busca:
    q = busca.lower().strip()
    f = f[
        f["nome_urna"].str.lower().str.contains(q, na=False)
        | f["resumo_trajetoria"].str.lower().str.contains(q, na=False)
    ]

st.write(f"**{len(f)} candidatas encontradas**")

for _, row in f.sort_values(["cargo", "nome_urna"]).iterrows():
    card_candidata(row)
