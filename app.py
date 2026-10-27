import altair as alt
import pandas as pd
import streamlit as st

from src.data_loader import load_data

st.set_page_config(
    page_title="Raio-X do Brasileirão",
    page_icon="⚽",
    layout="wide",
)

# =============================================================================
# Identidade visual: cores, fontes e estilo da página
# =============================================================================

# Paleta "noite de jogo" (as cores base do tema estão em .streamlit/config.toml)
VERDE_ESTADIO = "#22b455"   # cor de destaque dos widgets
VERDE_LIMAO = "#b8f02a"     # destaque dos gráficos (vitória do mandante)
DOURADO = "#f5c518"         # detalhes, como a taça
CINZA_GRAMA = "#6f8a7b"     # classe de referência (mandante não venceu)
TEXTO = "#eef5ee"
TEXTO_SUAVE = "#9db5a6"
LINHA = "#24402f"

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow:wght@400;600;700&display=swap');

    /* Fundo com as faixas do gramado cortado */
    .stApp {{
        background:
            radial-gradient(ellipse at top, rgba(34,180,85,0.18), transparent 60%),
            repeating-linear-gradient(90deg, #0b1a12 0 120px, #0d1f15 120px 240px);
    }}
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #0f2218, #091409);
        border-right: 2px solid {LINHA};
    }}

    /* Títulos no estilo de placar de estádio */
    h1, h2, h3 {{
        font-family: 'Bebas Neue', sans-serif !important;
        letter-spacing: 1.5px;
        font-weight: 400 !important;
    }}
    h2, h3 {{ color: {TEXTO}; }}

    /* Faixa de abertura */
    .hero {{
        position: relative;
        overflow: hidden;
        padding: 28px 32px 24px;
        margin-bottom: 18px;
        border-radius: 18px;
        border: 1px solid {LINHA};
        background:
            linear-gradient(120deg, rgba(11,26,18,0.95) 35%, rgba(34,180,85,0.35)),
            repeating-linear-gradient(90deg, #12301f 0 60px, #0f2819 60px 120px);
    }}
    /* Círculo central do campo, desenhado com bordas */
    .hero::after {{
        content: "";
        position: absolute;
        right: -60px; top: 50%;
        width: 260px; height: 260px;
        transform: translateY(-50%);
        border: 3px solid rgba(255,255,255,0.12);
        border-radius: 50%;
    }}
    .hero::before {{
        content: "";
        position: absolute;
        right: 70px; top: 0; bottom: 0;
        border-left: 3px solid rgba(255,255,255,0.12);
    }}
    .hero-tag {{
        display: inline-block;
        font-family: 'Barlow', sans-serif;
        font-weight: 700;
        font-size: 12px;
        letter-spacing: 3px;
        color: #0b1a12;
        background: {VERDE_LIMAO};
        padding: 4px 12px;
        border-radius: 999px;
    }}
    .hero-titulo {{
        font-family: 'Bebas Neue', sans-serif;
        font-size: 64px;
        line-height: 1;
        margin: 14px 0 6px;
        color: {TEXTO};
    }}
    .hero-titulo span {{ color: {VERDE_LIMAO}; }}
    .hero-sub {{
        font-family: 'Barlow', sans-serif;
        color: {TEXTO_SUAVE};
        font-size: 17px;
        margin: 0 0 18px;
        max-width: 720px;
    }}

    /* Mini placar com os números do recorte */
    .placar {{ display: flex; gap: 12px; flex-wrap: wrap; position: relative; z-index: 1; }}
    .placar-item {{
        background: rgba(5,12,8,0.75);
        border: 1px solid {LINHA};
        border-top: 3px solid {VERDE_LIMAO};
        border-radius: 10px;
        padding: 8px 16px;
        min-width: 120px;
    }}
    .placar-numero {{
        font-family: 'Bebas Neue', sans-serif;
        font-size: 34px;
        line-height: 1;
        color: {TEXTO};
    }}
    .placar-rotulo {{
        font-family: 'Barlow', sans-serif;
        font-size: 12px;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: {TEXTO_SUAVE};
    }}

    /* Aviso discreto sobre a arrecadação */
    .aviso {{
        font-family: 'Barlow', sans-serif;
        color: {TEXTO_SUAVE};
        border-left: 4px solid {DOURADO};
        background: rgba(245,197,24,0.07);
        padding: 10px 14px;
        border-radius: 6px;
        margin-bottom: 14px;
    }}
    .aviso b {{ color: {DOURADO}; }}
    </style>
    """,
    unsafe_allow_html=True,
)


def estilo(grafico):
    """Aplica a identidade visual a um gráfico Altair (fundo transparente, fontes e cores do app)."""
    return (
        grafico.configure(background="transparent", font="Barlow")
        .configure_view(strokeWidth=0)
        .configure_axis(
            labelColor=TEXTO_SUAVE,
            titleColor=TEXTO,
            gridColor="#1a3325",
            domainColor=LINHA,
            tickColor=LINHA,
            labelFontSize=12,
            titleFontSize=13,
            titleFontWeight=600,
        )
        .configure_legend(labelColor=TEXTO_SUAVE, titleColor=TEXTO)
    )


# =============================================================================
# Dados
# =============================================================================

df = load_data()

# Variáveis quantitativas do estudo (mesma lista VARS_QUANT do notebook de EDA)
VARS_QUANT = ["rodata", "mandante_Placar", "visitante_Placar", "arrecadacao"]

# Nomes amigáveis para mostrar na tela (o código continua usando o nome da coluna)
ROTULOS = {
    "rodata": "Rodada",
    "mandante_Placar": "Gols do mandante",
    "visitante_Placar": "Gols do visitante",
    "arrecadacao": "Arrecadação (R$)",
}

# Variáveis discretas com poucos valores: o histograma mostra uma barra por valor (0, 1, 2 gols...)
VARS_DISCRETAS = ["mandante_Placar", "visitante_Placar"]

# Variável de classe (alvo criado na EDA) e seus valores
CLASSE = "resultado_mandante"
VALORES_CLASSE = ["Nao_Venceu", "Vitoria_Mandante"]
CORES_CLASSE = alt.Scale(domain=VALORES_CLASSE, range=[CINZA_GRAMA, VERDE_LIMAO])

# =============================================================================
# Sidebar: filtros (variáveis + intervalo)
# =============================================================================

with st.sidebar:
    st.header("⚙️ Filtros")

    variaveis = st.multiselect(
        "Variáveis quantitativas",
        options=VARS_QUANT,
        default=VARS_QUANT,
        format_func=lambda v: ROTULOS[v],
        help="Selecione as variáveis quantitativas que deseja analisar no dashboard.",
    )

    separar_por_classe = st.toggle(
        "Separar por resultado do mandante",
        value=False,
        help="Colore a distribuição pelo resultado (resultado_mandante): vitória do mandante ou não.",
    )

    st.divider()

    # Um slider de intervalo para cada variável selecionada
    intervalos = {}
    for var in variaveis:
        if pd.api.types.is_integer_dtype(df[var]):
            minimo, maximo, passo, formato = int(df[var].min()), int(df[var].max()), 1, None
        else:
            # arrecadacao vai de dezenas de milhares a milhões: passo de 1% da faixa
            minimo, maximo = float(df[var].min()), float(df[var].max())
            passo = max(round((maximo - minimo) / 100, 2), 0.01)
            formato = "R$ %.0f"
        intervalos[var] = st.slider(
            ROTULOS[var],
            min_value=minimo,
            max_value=maximo,
            value=(minimo, maximo),
            step=passo,
            format=formato,
            key=f"intervalo_{var}",
        )

# Mantém só as partidas dentro de todos os intervalos escolhidos.
# Partidas SEM valor (NaN) na variável são mantidas: arrecadacao só existe em 380 das 9.165
# partidas e, sem isso, selecionar arrecadacao jogaria fora todo o resto do dataset.
df_filtrado = df
for var, (inicio, fim) in intervalos.items():
    df_filtrado = df_filtrado[df_filtrado[var].between(inicio, fim) | df_filtrado[var].isna()]

# =============================================================================
# Abertura: faixa com o mini placar do recorte filtrado
# =============================================================================

anos = pd.to_datetime(df["data"], format="%d/%m/%Y", errors="coerce").dt.year
gols_por_jogo = (df_filtrado["mandante_Placar"] + df_filtrado["visitante_Placar"]).mean()
pct_vitoria = (df_filtrado[CLASSE] == "Vitoria_Mandante").mean()


def numero_br(valor, casas=0):
    """Formata número no padrão brasileiro (9.165 / 2,6)."""
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


st.markdown(
    f"""
    <div class="hero">
        <div class="hero-tag">⚽ CAMPEONATO BRASILEIRO · SÉRIE A · {int(anos.min())}–{int(anos.max())}</div>
        <div class="hero-titulo">Raio-X do <span>Brasileirão</span></div>
        <p class="hero-sub">Como se relacionam e como se distribuem rodada, gols e arrecadação
        das partidas do campeonato. Ajuste os filtros na lateral.</p>
        <div class="placar">
            <div class="placar-item">
                <div class="placar-numero">{numero_br(len(df_filtrado))}</div>
                <div class="placar-rotulo">partidas no filtro</div>
            </div>
            <div class="placar-item">
                <div class="placar-numero">{numero_br(gols_por_jogo, 2) if len(df_filtrado) else "–"}</div>
                <div class="placar-rotulo">gols por jogo</div>
            </div>
            <div class="placar-item">
                <div class="placar-numero">{numero_br(pct_vitoria * 100, 1) + "%" if len(df_filtrado) else "–"}</div>
                <div class="placar-rotulo">vitórias do mandante</div>
            </div>
            <div class="placar-item">
                <div class="placar-numero">{df["mandante"].nunique()}</div>
                <div class="placar-rotulo">clubes na história</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if "arrecadacao" in variaveis:
    st.markdown(
        f"""<div class="aviso">🎟️ A <b>arrecadação</b> só está registrada em
        <b>{numero_br(df_filtrado['arrecadacao'].notna().sum())}</b> dessas partidas.
        A correlação e o histograma dela usam apenas essas partidas.</div>""",
        unsafe_allow_html=True,
    )

# =============================================================================
# Dashboard 1: correlação (heatmap) à esquerda, distribuição (histogramas) à direita
# =============================================================================

col_correlacao, col_distribuicao = st.columns([1, 1.5], gap="large")

# Legenda das classes em texto, para caber no espaço livre da grade de histogramas
LEGENDA_CLASSE = (
    f"**Resultado do mandante**  \n"
    f":color[■]{{foreground=\"{VERDE_LIMAO}\"}} Venceu  \n"
    f":color[■]{{foreground=\"{CINZA_GRAMA}\"}} Não venceu (empate ou derrota)"
)

with col_correlacao:
    with st.container(border=True):
        st.subheader("🔗 Correlação (Spearman)")
        st.caption("Perto de +1 ou −1: relação forte. Perto de 0: as variáveis quase não se relacionam.")

        if len(variaveis) < 2:
            st.warning("Selecione pelo menos 2 variáveis para calcular a correlação.")
        elif len(df_filtrado) < 30:
            st.warning("Poucas partidas nos intervalos escolhidos para calcular a correlação.")
        else:
            # Matriz de correlação de Spearman, em formato longo (uma linha por célula)
            corr = (
                df_filtrado[variaveis]
                .corr(method="spearman")
                .rename_axis(index="var_y", columns="var_x")
                .stack()
                .rename("correlacao")
                .reset_index()
            )
            # Só o triângulo inferior, sem a diagonal (sempre 1): a matriz é simétrica
            ordem = {var: i for i, var in enumerate(variaveis)}
            corr = corr[corr["var_y"].map(ordem) > corr["var_x"].map(ordem)]
            corr["rotulo_x"] = corr["var_x"].map(ROTULOS)
            corr["rotulo_y"] = corr["var_y"].map(ROTULOS)

            rotulos = [ROTULOS[v] for v in variaveis]
            base = alt.Chart(corr).encode(
                x=alt.X(
                    "rotulo_x:N",
                    title=None,
                    sort=rotulos[:-1],  # a última variável só aparece nas linhas
                    axis=alt.Axis(labelAngle=-25, labelFontSize=12, orient="bottom"),
                ),
                y=alt.Y("rotulo_y:N", title=None, sort=rotulos[1:], axis=alt.Axis(labelFontSize=12)),
            )
            heatmap = base.mark_rect(cornerRadius=6, stroke="#0b1a12", strokeWidth=3).encode(
                color=alt.Color(
                    "correlacao:Q",
                    title="Spearman",
                    scale=alt.Scale(
                        domain=[-1, 0, 1],
                        range=["#ff5c7a", "#16291e", VERDE_LIMAO],
                    ),
                    legend=alt.Legend(gradientLength=220, titleFontSize=12, labelFontSize=11),
                ),
                tooltip=[
                    alt.Tooltip("rotulo_x:N", title="Variável 1"),
                    alt.Tooltip("rotulo_y:N", title="Variável 2"),
                    alt.Tooltip("correlacao:Q", title="Spearman", format=".2f"),
                ],
            )
            valores = base.mark_text(fontSize=20, font="Bebas Neue").encode(
                text=alt.Text("correlacao:Q", format=".2f"),
                color=alt.condition(
                    "abs(datum.correlacao) > 0.5", alt.value("#0b1a12"), alt.value(TEXTO)
                ),
            )

            st.altair_chart(
                estilo((heatmap + valores).properties(height=400)),
                width="stretch",
                theme=None,
                alt="Mapa de calor (triângulo inferior, sem a diagonal) da correlação de Spearman entre as variáveis quantitativas selecionadas",
            )

with col_distribuicao:
    with st.container(border=True):
        st.subheader("📊 Distribuição")
        st.caption("Quantas partidas caem em cada faixa de valor.")

        if not variaveis:
            st.warning("Selecione pelo menos 1 variável para ver a distribuição.")
        elif df_filtrado.empty:
            st.warning("Nenhuma partida dentro dos intervalos escolhidos.")
        else:
            # Com número par de variáveis não sobra espaço na grade: a legenda vai acima dela
            if separar_por_classe and len(variaveis) % 2 == 0:
                st.markdown(LEGENDA_CLASSE)

            # Um histograma por variável selecionada, em grade de 2 colunas
            for inicio in range(0, len(variaveis), 2):
                colunas = st.columns(2)
                for coluna, var in zip(colunas, variaveis[inicio : inicio + 2]):
                    # Remove as partidas sem valor nesta variável (ex.: arrecadacao ausente)
                    dados_var = df_filtrado[[var, CLASSE]].dropna(subset=[var])

                    if var in VARS_DISCRETAS:
                        # Gols: uma barra por placar (0, 1, 2...)
                        eixo_x = alt.X(f"{var}:O", title=ROTULOS[var], axis=alt.Axis(labelAngle=0))
                    elif var == "arrecadacao":
                        eixo_x = alt.X(
                            f"{var}:Q",
                            bin=alt.Bin(maxbins=20),
                            title=ROTULOS[var],
                            axis=alt.Axis(format="~s"),  # 2M em vez de 2,000,000
                        )
                    else:
                        eixo_x = alt.X(f"{var}:Q", bin=alt.Bin(maxbins=20), title=ROTULOS[var])

                    histograma = (
                        alt.Chart(dados_var)
                        .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
                        .encode(
                            x=eixo_x,
                            y=alt.Y("count()", title="Partidas"),
                            tooltip=[alt.Tooltip("count()", title="Partidas")],
                        )
                        .properties(height=210)
                    )
                    if separar_por_classe:
                        histograma = histograma.encode(
                            color=alt.Color(
                                f"{CLASSE}:N",
                                title="Resultado",
                                scale=CORES_CLASSE,
                                legend=None,
                            ),
                            tooltip=[
                                alt.Tooltip(f"{CLASSE}:N", title="Resultado"),
                                alt.Tooltip("count()", title="Partidas"),
                            ],
                        )
                    else:
                        histograma = histograma.mark_bar(
                            color=VERDE_LIMAO, cornerRadiusTopLeft=4, cornerRadiusTopRight=4
                        )

                    with coluna:
                        st.altair_chart(
                            estilo(histograma),
                            width="stretch",
                            theme=None,
                            alt=f"Histograma da variável {ROTULOS[var]}",
                        )

                # Número ímpar de variáveis: a legenda ocupa o espaço que sobrou na última linha
                if separar_por_classe and len(colunas) == 2 and len(variaveis[inicio : inicio + 2]) == 1:
                    colunas[1].markdown(LEGENDA_CLASSE)

# TODO: Dashboard 2 — KPIs (Aula 22)
