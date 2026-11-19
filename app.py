from html import escape
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "Dados" / "Tratados" / "dashboard_infraestrutura_escolas_long.csv"

st.set_page_config(
    page_title="EduLens | Infraestrutura escolar",
    page_icon="🏫",
    layout="wide",
)

st.markdown(
    """
    <style>
    :root {
        --ink: #17343b;
        --muted: #667b80;
        --teal: #087f75;
        --teal-soft: #e2f2ef;
        --blue: #3979a8;
        --amber: #d69a35;
        --red: #c55d57;
        --line: #dce6e6;
        --surface: #ffffff;
        --canvas: #f3f7f6;
    }
    .stApp { background: var(--canvas); color: var(--ink); }
    .block-container { max-width: 1500px; padding-top: 1.4rem; padding-bottom: 3rem; }
    section[data-testid="stSidebar"] { background: #eaf1f0; border-right: 1px solid var(--line); }
    section[data-testid="stSidebar"] h2 { color: var(--ink); font-size: 1.05rem; }
    .edulens-hero {
        background: linear-gradient(112deg, #123b46 0%, #176c6b 68%, #24877b 100%);
        border-radius: 20px;
        padding: 28px 34px;
        margin: 0 0 22px 0;
        color: #f6fbfa;
        box-shadow: 0 12px 30px rgba(23, 52, 59, .12);
    }
    .edulens-hero .eyebrow {
        color: #bce7df; font-size: .76rem; font-weight: 700;
        letter-spacing: .13em; text-transform: uppercase; margin-bottom: 8px;
    }
    .edulens-hero h1 { color: #fff; font-size: clamp(1.8rem, 3vw, 2.6rem); margin: 0; line-height: 1.12; }
    .edulens-hero p { color: #e1f0ed; max-width: 850px; margin: 10px 0 0 0; font-size: 1rem; }
    .metric-card {
        min-height: 128px; background: var(--surface); border: 1px solid var(--line);
        border-radius: 16px; padding: 17px 19px; box-shadow: 0 5px 16px rgba(23, 52, 59, .045);
    }
    .metric-label { color: var(--muted); font-size: .82rem; font-weight: 600; margin-bottom: 9px; }
    .metric-value { color: var(--ink); font-size: 1.85rem; font-weight: 750; letter-spacing: -.035em; line-height: 1.1; }
    .metric-note { color: var(--muted); font-size: .76rem; margin-top: 9px; }
    .section-kicker { color: var(--teal); font-size: .76rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; margin: 12px 0 4px 0; }
    .small-note { color: var(--muted); font-size: .83rem; }
    div[data-testid="stTabs"] button[role="tab"] { color: var(--muted); font-weight: 650; }
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] { color: var(--teal); }
    div[data-testid="stTabs"] [data-baseweb="tab-highlight"] { background-color: var(--teal); }
    div[data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 12px; overflow: hidden; }
    .stDownloadButton button { background: var(--teal); color: white; border: 0; border-radius: 9px; }
    .stDownloadButton button:hover { background: #06685f; color: white; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def carregar_dados(caminho: str) -> pd.DataFrame:
    """Carrega e mantém em cache a base longa preparada pelo notebook 03."""
    return pd.read_csv(
        caminho,
        encoding="utf-8-sig",
        dtype={"CO_ENTIDADE": "string", "CO_MUNICIPIO": "string"},
    )


def formatar_percentual(valor):
    return f"{valor:.1f}%" if pd.notna(valor) else "Sem dados"


def criar_card(rotulo, valor, nota):
    return f"""
    <div class="metric-card">
      <div class="metric-label">{escape(str(rotulo))}</div>
      <div class="metric-value">{escape(str(valor))}</div>
      <div class="metric-note">{escape(str(nota))}</div>
    </div>
    """


def estilizar_figura(fig, altura=340):
    fig.update_layout(
        template="plotly_white",
        height=altura,
        margin=dict(l=12, r=18, t=28, b=16),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial, sans-serif", color="#17343b", size=12),
        hoverlabel=dict(bgcolor="#17343b", font_color="white"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    return fig


st.markdown(
    """
    <div class="edulens-hero">
      <div class="eyebrow">EduLens · São Paulo · Censo Escolar 2023–2025</div>
      <h1>Infraestrutura escolar</h1>
      <p>Explore onde os recursos estão presentes, onde houve avanço e onde ainda existem lacunas nas escolas públicas paulistas.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if not DATA_PATH.exists():
    st.error("A base do dashboard ainda não foi gerada.")
    st.write("Execute a célula de `Notebooks/03_preparacao_dashboard.ipynb` e abra o app novamente.")
    st.stop()

df = carregar_dados(str(DATA_PATH))

with st.sidebar:
    st.markdown("## Refine a análise")
    st.caption("Os filtros territoriais usam a classificação de 2023.")
    categorias = ["Todas"] + sorted(df["CATEGORIA"].dropna().unique().tolist())
    categoria = st.selectbox(
        "Categoria de infraestrutura",
        categorias,
        index=categorias.index("Conectividade") if "Conectividade" in categorias else 0,
    )

    base_indicadores = df if categoria == "Todas" else df.loc[df["CATEGORIA"].eq(categoria)]
    indicadores = sorted(base_indicadores["INDICADOR"].dropna().unique().tolist())
    indicador_preferido = "Internet para alunos" if "Internet para alunos" in indicadores else indicadores[0]
    indicador = st.selectbox("Recurso", indicadores, index=indicadores.index(indicador_preferido))
    dados = base_indicadores.loc[base_indicadores["INDICADOR"].eq(indicador)].copy()

    localizacoes = ["Todas"] + sorted(dados["LOCALIZACAO_2023"].dropna().unique().tolist())
    localizacao = st.selectbox("Localização", localizacoes)
    redes = ["Todas"] + sorted(dados["REDE_ADMINISTRATIVA_2023"].dropna().unique().tolist())
    rede = st.selectbox("Rede administrativa", redes)

    if localizacao != "Todas":
        dados = dados.loc[dados["LOCALIZACAO_2023"].eq(localizacao)]
    if rede != "Todas":
        dados = dados.loc[dados["REDE_ADMINISTRATIVA_2023"].eq(rede)]

    municipios = ["Todos"] + sorted(dados["NO_MUNICIPIO"].dropna().unique().tolist())
    municipio = st.selectbox("Município", municipios)
    if municipio != "Todos":
        dados = dados.loc[dados["NO_MUNICIPIO"].eq(municipio)]

    minimo_municipio = st.number_input(
        "Mínimo de escolas por município",
        min_value=1,
        value=5,
        step=1,
        help="O denominador fica visível para contextualizar cada taxa municipal.",
    )

if dados.empty:
    st.warning("Não há escolas para essa combinação de filtros.")
    st.stop()

n_escolas = dados["CO_ENTIDADE"].nunique()
n_validos_2023 = int(dados["VALOR_2023"].notna().sum())
n_validos_2025 = int(dados["VALOR_2025"].notna().sum())
cobertura_2023 = dados["VALOR_2023"].mean() * 100
cobertura_2025 = dados["VALOR_2025"].mean() * 100
variacao_pp = cobertura_2025 - cobertura_2023 if pd.notna(cobertura_2023) and pd.notna(cobertura_2025) else None
transicoes = dados["TRANSICAO"].value_counts()
ganharam = int(transicoes.get("Ganhou recurso", 0))
perderam = int(transicoes.get("Perdeu registro do recurso", 0))
permaneceram_sem = int(transicoes.get("Permaneceu sem recurso", 0))
sem_comparacao = int(transicoes.get("Sem comparação completa", 0))

st.markdown(f"<div class='section-kicker'>{escape(categoria if categoria != 'Todas' else 'Todas as categorias')}</div>", unsafe_allow_html=True)
st.subheader(indicador)
st.markdown(
    f"<div class='small-note'>{n_escolas:,} escolas no recorte · "
    f"dados válidos: {n_validos_2023:,} em 2023 e {n_validos_2025:,} em 2025</div>",
    unsafe_allow_html=True,
)

colunas_cards = st.columns(4, gap="medium")
with colunas_cards[0]:
    st.markdown(criar_card("Cobertura em 2023", formatar_percentual(cobertura_2023), f"{n_validos_2023:,} registros válidos"), unsafe_allow_html=True)
with colunas_cards[1]:
    st.markdown(criar_card("Cobertura em 2025", formatar_percentual(cobertura_2025), f"{n_validos_2025:,} registros válidos"), unsafe_allow_html=True)
with colunas_cards[2]:
    valor_variacao = f"{variacao_pp:+.1f} p.p." if variacao_pp is not None else "Sem dados"
    nota_variacao = "Aumento da cobertura" if variacao_pp is not None and variacao_pp > 0 else "Redução da cobertura" if variacao_pp is not None and variacao_pp < 0 else "Sem variação" if variacao_pp == 0 else "Sem dados comparáveis"
    st.markdown(criar_card("Variação da cobertura", valor_variacao, nota_variacao), unsafe_allow_html=True)
with colunas_cards[3]:
    st.markdown(criar_card("Ganhos / perdas", f"{ganharam:,} / {perderam:,}", "escolas que ganharam / perderam registro"), unsafe_allow_html=True)

aba_visao, aba_municipios, aba_escolas = st.tabs(["Panorama", "Municípios", "Escolas"])

with aba_visao:
    coluna_a, coluna_b = st.columns(2, gap="large")
    with coluna_a:
        st.markdown("#### Cobertura por ano")
        fig_cobertura = go.Figure()
        fig_cobertura.add_trace(go.Bar(
            x=["2023", "2025"],
            y=[cobertura_2023, cobertura_2025],
            marker_color=["#9fc9c3", "#087f75"],
            text=[formatar_percentual(cobertura_2023), formatar_percentual(cobertura_2025)],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="Ano: %{x}<br>Cobertura: %{y:.1f}%<extra></extra>",
        ))
        fig_cobertura.update_yaxes(title="Escolas com o recurso (%)", range=[0, 100], ticksuffix="%", gridcolor="#e6eeee", zeroline=False)
        fig_cobertura.update_xaxes(title=None, showgrid=False)
        fig_cobertura.update_layout(showlegend=False, bargap=0.55)
        st.plotly_chart(estilizar_figura(fig_cobertura), use_container_width=True, config={"displayModeBar": False})

    with coluna_b:
        st.markdown("#### O que mudou nas escolas")
        ordem_transicoes = [
            "Ganhou recurso",
            "Perdeu registro do recurso",
            "Permaneceu sem recurso",
            "Manteve recurso",
            "Sem comparação completa",
        ]
        contagem = dados["TRANSICAO"].value_counts().reindex(ordem_transicoes, fill_value=0)
        cores = ["#087f75", "#c55d57", "#d69a35", "#3979a8", "#b8c7c9"]
        fig_transicoes = go.Figure(go.Bar(
            x=contagem.values,
            y=contagem.index,
            orientation="h",
            marker_color=cores,
            text=[f"{v:,}" for v in contagem.values],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{y}: %{x:,} escolas<extra></extra>",
        ))
        fig_transicoes.update_xaxes(title="Número de escolas", rangemode="tozero", gridcolor="#e6eeee")
        fig_transicoes.update_yaxes(title=None, autorange="reversed", showgrid=False)
        fig_transicoes.update_layout(showlegend=False, margin=dict(l=10, r=40, t=24, b=10))
        st.plotly_chart(estilizar_figura(fig_transicoes), use_container_width=True, config={"displayModeBar": False})

    st.markdown("#### Cobertura por localização")
    por_local = dados.groupby("LOCALIZACAO_2023", dropna=False)[["VALOR_2023", "VALOR_2025"]].mean() * 100
    fig_local = go.Figure()
    for coluna, ano, cor in [("VALOR_2023", "2023", "#9fc9c3"), ("VALOR_2025", "2025", "#087f75")]:
        fig_local.add_trace(go.Bar(
            name=ano,
            x=por_local.index.astype(str),
            y=por_local[coluna],
            marker_color=cor,
            text=[formatar_percentual(v) for v in por_local[coluna]],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="Localização: %{x}<br>Cobertura: %{y:.1f}%<extra></extra>",
        ))
    fig_local.update_yaxes(title="Escolas com o recurso (%)", range=[0, 100], ticksuffix="%", gridcolor="#e6eeee", zeroline=False)
    fig_local.update_xaxes(title=None, showgrid=False)
    fig_local.update_layout(barmode="group", bargap=0.28, bargroupgap=0.12)
    st.plotly_chart(estilizar_figura(fig_local, altura=360), use_container_width=True, config={"displayModeBar": False})
    st.caption(f"Sem comparação completa entre os anos: {sem_comparacao:,} escolas. Ausência de registro não é convertida em zero.")

with aba_municipios:
    st.markdown("#### Onde a cobertura está mais baixa?")
    municipal = dados.groupby(["CO_MUNICIPIO", "NO_MUNICIPIO"], dropna=False).agg(
        N_ESCOLAS=("CO_ENTIDADE", "nunique"),
        N_COM_DADO_2023=("VALOR_2023", "count"),
        N_COM_DADO_2025=("VALOR_2025", "count"),
        MEDIA_2023=("VALOR_2023", "mean"),
        MEDIA_2025=("VALOR_2025", "mean"),
        GANHARAM=("TRANSICAO", lambda s: (s == "Ganhou recurso").sum()),
        PERDERAM=("TRANSICAO", lambda s: (s == "Perdeu registro do recurso").sum()),
    ).reset_index()
    municipal["COBERTURA_2023_PCT"] = municipal["MEDIA_2023"] * 100
    municipal["COBERTURA_2025_PCT"] = municipal["MEDIA_2025"] * 100
    municipal["VARIACAO_PP"] = municipal["COBERTURA_2025_PCT"] - municipal["COBERTURA_2023_PCT"]
    municipal = municipal.loc[municipal["N_COM_DADO_2025"].ge(minimo_municipio)].copy()
    municipal = municipal.sort_values(["COBERTURA_2025_PCT", "NO_MUNICIPIO"], na_position="last")
    if municipal.empty:
        st.info("Nenhum município atende ao mínimo de escolas selecionado.")
    else:
        top_municipios = municipal.head(12).sort_values("COBERTURA_2025_PCT", ascending=True)
        fig_municipios = go.Figure(go.Bar(
            x=top_municipios["COBERTURA_2025_PCT"],
            y=top_municipios["NO_MUNICIPIO"],
            orientation="h",
            marker_color="#087f75",
            text=[formatar_percentual(v) for v in top_municipios["COBERTURA_2025_PCT"]],
            textposition="outside",
            cliponaxis=False,
            customdata=top_municipios["N_COM_DADO_2025"],
            hovertemplate="%{y}<br>Cobertura: %{x:.1f}%<br>Escolas com dado: %{customdata}<extra></extra>",
        ))
        fig_municipios.update_xaxes(title="Cobertura em 2025 (%)", range=[0, 100], ticksuffix="%", gridcolor="#e6eeee")
        fig_municipios.update_yaxes(title=None, showgrid=False)
        fig_municipios.update_layout(showlegend=False, margin=dict(l=10, r=45, t=20, b=10))
        st.plotly_chart(estilizar_figura(fig_municipios, altura=430), use_container_width=True, config={"displayModeBar": False})

        tabela = municipal.rename(columns={
            "CO_MUNICIPIO": "Código IBGE",
            "NO_MUNICIPIO": "Município",
            "N_ESCOLAS": "Escolas na coorte",
            "N_COM_DADO_2025": "Escolas com dado em 2025",
            "COBERTURA_2023_PCT": "Cobertura 2023 (%)",
            "COBERTURA_2025_PCT": "Cobertura 2025 (%)",
            "VARIACAO_PP": "Variação (p.p.)",
            "GANHARAM": "Ganharam recurso",
            "PERDERAM": "Perderam registro",
        })
        st.dataframe(
            tabela[["Código IBGE", "Município", "Escolas na coorte", "Escolas com dado em 2025", "Cobertura 2023 (%)", "Cobertura 2025 (%)", "Variação (p.p.)", "Ganharam recurso", "Perderam registro"]],
            hide_index=True,
            use_container_width=True,
        )
        st.caption("A tabela completa respeita o mínimo de escolas e os filtros selecionados.")

with aba_escolas:
    st.markdown("#### Consulte a transição de cada escola")
    opcoes_transicao = ["Todas", "Ganhou recurso", "Perdeu registro do recurso", "Permaneceu sem recurso", "Manteve recurso", "Sem comparação completa"]
    transicao = st.selectbox("Situação entre 2023 e 2025", opcoes_transicao, key="filtro_transicao")
    detalhe = dados if transicao == "Todas" else dados.loc[dados["TRANSICAO"].eq(transicao)]
    detalhe = detalhe.assign(
        **{
            "Registro em 2023": detalhe["VALOR_2023"].map({0: "Não", 1: "Sim"}).fillna("Sem dado"),
            "Registro em 2025": detalhe["VALOR_2025"].map({0: "Não", 1: "Sim"}).fillna("Sem dado"),
        }
    )
    colunas_detalhe = [
        "CO_ENTIDADE", "NO_ENTIDADE", "CO_MUNICIPIO", "NO_MUNICIPIO",
        "LOCALIZACAO_2023", "REDE_ADMINISTRATIVA_2023",
        "Registro em 2023", "Registro em 2025", "TRANSICAO",
    ]
    st.dataframe(detalhe[colunas_detalhe], hide_index=True, use_container_width=True)
    st.download_button(
        "Baixar escolas deste recorte (CSV)",
        data=detalhe[colunas_detalhe].to_csv(index=False).encode("utf-8-sig"),
        file_name="edulens_escolas_filtradas.csv",
        mime="text/csv",
    )

st.markdown("<div class='small-note'>Fonte: Censo Escolar 2023 e 2025 · Coorte pareada de escolas públicas de São Paulo · Indicadores descritivos, sem inferência causal.</div>", unsafe_allow_html=True)
