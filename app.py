import altair as alt
import pandas as pd
import streamlit as st

from src.data_loader import load_data
from src.metricas import (
    RESULTADOS,
    adicionar_temporada,
    calcular_kpis,
    gols_por_temporada,
    resultados_por_temporada,
    tabela_por_temporada,
)

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
CINZA_GRAMA = "#6f8a7b"     # classe de referência (mandante não venceu) e empate
AZUL_VISITANTE = "#4cc9f0"  # vitória do visitante (distinguível do cinza também por daltônicos)
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


def numero_br(valor, casas=0):
    """Formata número no padrão brasileiro (9.165 / 2,6)."""
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def reais(valor):
    """Valor em reais de forma curta: R$ 996 mil, R$ 1,25 mi."""
    if abs(valor) >= 1_000_000:
        return f"R$ {numero_br(valor / 1_000_000, 2)} mi"
    return f"R$ {numero_br(valor / 1_000)} mil"


def variacao(diferenca, casas=1, sufixo=""):
    """Texto do delta do st.metric, com sinal (ex.: "+1,2 p.p.").

    Uma diferença que arredonda para zero volta como o número 0, que o st.metric mostra sem seta.
    """
    if round(diferenca, casas) == 0:
        return 0
    sinal = "+" if diferenca > 0 else "-"
    return f"{sinal}{numero_br(abs(diferenca), casas)}{sufixo}"


def variacao_reais(diferenca):
    """Delta em reais para o st.metric (ex.: "+R$ 120 mil"); menos de R$ 1 mil conta como zero."""
    if abs(diferenca) < 1_000:
        return 0
    sinal = "+" if diferenca > 0 else "-"
    return f"{sinal}{reais(abs(diferenca))}"


# =============================================================================
# Dados
# =============================================================================

df = adicionar_temporada(load_data())

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

# Resultado da partida em três categorias, usado no Dashboard 2
CORES_RESULTADO = alt.Scale(domain=RESULTADOS, range=[VERDE_LIMAO, CINZA_GRAMA, AZUL_VISITANTE])

# Abaixo disso, correlações e percentuais ficam instáveis demais para serem lidos com confiança
MIN_PARTIDAS = 30

TODOS_CLUBES = "Todos os clubes"

# A arrecadação só foi registrada em parte das temporadas (no dataset atual, só em 2025)
TEMPORADAS_ARRECADACAO = ", ".join(
    str(t) for t in sorted(df.loc[df["arrecadacao"].notna(), "temporada"].unique())
)

# =============================================================================
# Sidebar: filtros (variáveis + intervalo)
# =============================================================================

with st.sidebar:
    st.header("Filtros")

    variaveis = st.multiselect(
        "Variáveis quantitativas",
        options=VARS_QUANT,
        default=VARS_QUANT,
        format_func=lambda v: ROTULOS[v],
        help="Selecione as variáveis quantitativas que deseja analisar no Dashboard 1.",
    )

    separar_por_classe = st.toggle(
        "Separar por resultado do mandante",
        value=False,
        help="Dashboard 1: colore os histogramas pelo resultado (resultado_mandante), vitória do mandante ou não.",
    )

    st.divider()

    if variaveis:
        st.caption("Os intervalos abaixo valem para os dois dashboards.")

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

st.markdown(
    f"""
    <div class="hero">
        <div class="hero-tag">⚽ CAMPEONATO BRASILEIRO · SÉRIE A · {df["temporada"].min()}–{df["temporada"].max()}</div>
        <div class="hero-titulo">Raio-X do <span>Brasileirão</span></div>
        <p class="hero-sub">Dois painéis sobre as partidas do campeonato: como rodada, gols e
        arrecadação se relacionam e se distribuem, e quanto o mando de campo pesa no resultado.
        Os intervalos da barra lateral valem para os dois.</p>
        <div class="placar">
            <div class="placar-item">
                <div class="placar-numero">{numero_br(len(df_filtrado))}</div>
                <div class="placar-rotulo">partidas no filtro</div>
            </div>
            <div class="placar-item">
                <div class="placar-numero">{df["temporada"].nunique()}</div>
                <div class="placar-rotulo">temporadas</div>
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

aba_dashboard1, aba_dashboard2 = st.tabs(
    ["Dashboard 1 · Correlação e distribuição", "Dashboard 2 · Indicadores do fator casa"]
)

# =============================================================================
# Dashboard 1: correlação (heatmap) à esquerda, distribuição (histogramas) à direita
# =============================================================================

# Legenda das classes em texto, para caber no espaço livre da grade de histogramas
LEGENDA_CLASSE = (
    f"**Resultado do mandante**  \n"
    f":color[■]{{foreground=\"{VERDE_LIMAO}\"}} Venceu  \n"
    f":color[■]{{foreground=\"{CINZA_GRAMA}\"}} Não venceu (empate ou derrota)"
)

with aba_dashboard1:
    st.header("Correlação e distribuição das variáveis quantitativas")

    if "arrecadacao" in variaveis:
        st.markdown(
            f"""<div class="aviso">A <b>arrecadação</b> só foi registrada nas partidas de
            <b>{TEMPORADAS_ARRECADACAO}</b>: são <b>{numero_br(df_filtrado['arrecadacao'].notna().sum())}</b>
            das partidas do filtro. A correlação e o histograma dela usam apenas essas partidas.</div>""",
            unsafe_allow_html=True,
        )

    col_correlacao, col_distribuicao = st.columns([1, 1.5], gap="large")

    with col_correlacao:
        with st.container(border=True):
            st.subheader("Correlação (Spearman)")
            st.caption("Perto de +1 ou −1: relação forte. Perto de 0: as variáveis quase não se relacionam.")

            if len(variaveis) < 2:
                st.warning("Selecione pelo menos 2 variáveis para calcular a correlação.")
            elif len(df_filtrado) < MIN_PARTIDAS:
                st.warning("Poucas partidas nos intervalos escolhidos para calcular a correlação.")
            else:
                # Matriz de correlação de Spearman, em formato longo (uma linha por célula).
                # Um par só é calculado com pelo menos MIN_PARTIDAS partidas com os dois valores
                # preenchidos; os outros viram NaN e saem da tabela. Sem isso, filtrar a arrecadação
                # mostraria correlações calculadas com 3 ou 4 partidas como se fossem confiáveis.
                corr = (
                    df_filtrado[variaveis]
                    .corr(method="spearman", min_periods=MIN_PARTIDAS)
                    .rename_axis(index="var_y", columns="var_x")
                    .stack(future_stack=True)
                    .dropna()
                    .rename("correlacao")
                    .reset_index()
                )
                # Só o triângulo inferior, sem a diagonal (sempre 1): a matriz é simétrica
                ordem = {var: i for i, var in enumerate(variaveis)}
                corr = corr[corr["var_y"].map(ordem) > corr["var_x"].map(ordem)]
                corr["rotulo_x"] = corr["var_x"].map(ROTULOS)
                corr["rotulo_y"] = corr["var_y"].map(ROTULOS)

                pares_possiveis = len(variaveis) * (len(variaveis) - 1) // 2
                if corr.empty:
                    st.warning(
                        f"Nenhum par de variáveis tem pelo menos {MIN_PARTIDAS} partidas com os dois "
                        "valores preenchidos (e variando) nos intervalos escolhidos."
                    )
                else:
                    if len(corr) < pares_possiveis:
                        st.caption(
                            f"Pares com menos de {MIN_PARTIDAS} partidas em comum, ou com uma variável "
                            "constante no filtro, ficaram de fora."
                        )

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
            st.subheader("Distribuição")
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

# =============================================================================
# Dashboard 2: KPIs do fator casa (st.metric) + gráficos por temporada
# =============================================================================

with aba_dashboard2:
    st.header("Indicadores do fator casa")
    st.caption(
        "Quanto o mando de campo pesa no resultado? Os indicadores comparam o recorte escolhido "
        "com todas as partidas do dataset. Os intervalos da barra lateral também valem aqui."
    )

    primeira_temporada, ultima_temporada = int(df["temporada"].min()), int(df["temporada"].max())
    col_periodo, col_clube = st.columns([2, 1], gap="large")
    with col_periodo:
        primeira, ultima = st.slider(
            "Temporadas",
            min_value=primeira_temporada,
            max_value=ultima_temporada,
            value=(primeira_temporada, ultima_temporada),
            key="kpi_temporadas",
        )
    with col_clube:
        clube = st.selectbox(
            "Clube mandante",
            [TODOS_CLUBES] + sorted(df["mandante"].unique()),
            key="kpi_clube",
            help="Escolha um clube para ver só as partidas em que ele jogou em casa.",
        )

    recorte = df_filtrado[df_filtrado["temporada"].between(primeira, ultima)]
    if clube != TODOS_CLUBES:
        recorte = recorte[recorte["mandante"] == clube]

    if recorte.empty:
        st.warning(
            "Nenhuma partida no recorte. O clube escolhido pode não ter jogado em casa na Série A "
            "nessas temporadas, ou os intervalos da barra lateral excluíram as partidas."
        )
    else:
        kpis = calcular_kpis(recorte)
        geral = calcular_kpis(df)

        col_partidas, col_vitorias, col_gols, col_arrecadacao = st.columns(4)
        col_partidas.metric(
            "Partidas analisadas",
            numero_br(kpis["partidas"]),
            help="Base de cálculo dos outros indicadores. Com poucas partidas, os percentuais oscilam muito.",
            border=True,
            height="stretch",
        )
        col_vitorias.metric(
            "Vitórias do mandante",
            f"{numero_br(kpis['pct_vitorias_mandante'] * 100, 1)}%",
            delta=variacao((kpis["pct_vitorias_mandante"] - geral["pct_vitorias_mandante"]) * 100, 1, " p.p."),
            delta_color="off",
            delta_description="vs. todas as partidas",
            help="Percentual das partidas em que o mandante venceu (variável resultado_mandante da EDA). "
            "A comparação é em pontos percentuais.",
            border=True,
            height="stretch",
        )
        col_gols.metric(
            "Gols por partida",
            numero_br(kpis["gols_por_partida"], 2),
            delta=variacao(kpis["gols_por_partida"] - geral["gols_por_partida"], 2),
            delta_color="off",
            delta_description="vs. todas as partidas",
            help="Média de gols marcados (mandante + visitante) por partida.",
            border=True,
            height="stretch",
        )
        if kpis["arrecadacao_mediana"] is None:
            col_arrecadacao.metric(
                "Arrecadação mediana",
                "–",
                help=f"A arrecadação só foi registrada nas partidas de {TEMPORADAS_ARRECADACAO}, "
                "e nenhuma delas está no recorte.",
                border=True,
                height="stretch",
            )
        else:
            col_arrecadacao.metric(
                "Arrecadação mediana",
                reais(kpis["arrecadacao_mediana"]),
                delta=variacao_reais(kpis["arrecadacao_mediana"] - geral["arrecadacao_mediana"]),
                delta_color="off",
                delta_description=f"vs. todas as partidas de {TEMPORADAS_ARRECADACAO}",
                help=f"Mediana da arrecadação por partida, calculada com as {kpis['partidas_com_arrecadacao']} "
                f"partidas do recorte que têm esse registro (só existe em {TEMPORADAS_ARRECADACAO}). "
                "A mediana é usada porque poucos jogos com arrecadação muito alta puxam a média para cima.",
                border=True,
                height="stretch",
            )

        if kpis["partidas"] < MIN_PARTIDAS:
            st.caption(
                f"Recorte com menos de {MIN_PARTIDAS} partidas: com tão poucos jogos, "
                "os percentuais mudam bastante de uma partida para outra."
            )

        # Todas as temporadas do intervalo aparecem no eixo, mesmo sem partidas no recorte
        eixo_temporada = alt.X(
            "temporada:O",
            title="Temporada",
            scale=alt.Scale(domain=list(range(primeira, ultima + 1))),
            axis=alt.Axis(labelAngle=-45),
        )

        col_resultados, col_gols_temporada = st.columns([1.3, 1], gap="large")

        with col_resultados:
            with st.container(border=True):
                st.subheader("Resultado das partidas por temporada")
                st.caption("Clique em um item da legenda para destacar um resultado.")

                destaque = alt.selection_point(fields=["resultado"], bind="legend")
                grafico_resultados = (
                    alt.Chart(resultados_por_temporada(recorte))
                    .mark_bar(stroke="#0b1a12", strokeWidth=2)
                    .encode(
                        x=eixo_temporada,
                        y=alt.Y(
                            "partidas:Q",
                            stack="normalize",
                            title="Partidas da temporada",
                            axis=alt.Axis(format="%"),
                        ),
                        color=alt.Color(
                            "resultado:N",
                            title=None,
                            scale=CORES_RESULTADO,
                            legend=alt.Legend(orient="top"),
                        ),
                        order=alt.Order("ordem:Q"),
                        opacity=alt.condition(destaque, alt.value(1), alt.value(0.25)),
                        tooltip=[
                            alt.Tooltip("temporada:O", title="Temporada"),
                            alt.Tooltip("resultado:N", title="Resultado"),
                            alt.Tooltip("partidas:Q", title="Partidas"),
                            alt.Tooltip("percentual:Q", title="Percentual", format=".1%"),
                        ],
                    )
                    .add_params(destaque)
                    .properties(height=320)
                )
                st.altair_chart(
                    estilo(grafico_resultados),
                    width="stretch",
                    theme=None,
                    alt="Barras empilhadas com o percentual de vitórias do mandante, empates e vitórias do visitante em cada temporada",
                )

        with col_gols_temporada:
            with st.container(border=True):
                st.subheader("Gols por partida por temporada")
                st.caption(
                    f"A linha tracejada marca a média do recorte: {numero_br(kpis['gols_por_partida'], 2)} gols por partida."
                )

                base_gols = alt.Chart(gols_por_temporada(recorte, primeira, ultima)).encode(
                    x=eixo_temporada,
                    y=alt.Y("gols_por_partida:Q", title="Gols por partida", scale=alt.Scale(zero=False)),
                )
                # Temporadas sem partidas (valor vazio) quebram a linha em vez de ligar anos distantes
                linha = base_gols.mark_line(
                    color=VERDE_LIMAO,
                    strokeWidth=2,
                    invalid="break-paths-show-domains",
                    point=alt.OverlayMarkDef(color=VERDE_LIMAO, size=60, filled=True),
                )
                # Pontos invisíveis maiores, só para facilitar o hover do tooltip
                alvo_tooltip = base_gols.mark_point(size=400, opacity=0).encode(
                    tooltip=[
                        alt.Tooltip("temporada:O", title="Temporada"),
                        alt.Tooltip("gols_por_partida:Q", title="Gols por partida", format=".2f"),
                        alt.Tooltip("partidas:Q", title="Partidas"),
                    ]
                )
                media = (
                    alt.Chart(pd.DataFrame({"media": [kpis["gols_por_partida"]]}))
                    .mark_rule(color=DOURADO, strokeDash=[6, 4], strokeWidth=1.5)
                    .encode(y="media:Q")
                )
                st.altair_chart(
                    estilo((linha + media + alvo_tooltip).properties(height=320)),
                    width="stretch",
                    theme=None,
                    alt="Linha com a média de gols por partida em cada temporada, com a média do recorte como referência",
                )

        with st.expander("Ver os números por temporada"):
            st.dataframe(
                tabela_por_temporada(recorte),
                hide_index=True,
                column_config={
                    "temporada": st.column_config.NumberColumn("Temporada", format="%d"),
                    "partidas": st.column_config.NumberColumn("Partidas"),
                    "gols_por_partida": st.column_config.NumberColumn("Gols por partida", format="%.2f"),
                    **{r: st.column_config.NumberColumn(f"{r} (%)", format="%.1f") for r in RESULTADOS},
                },
                alt="Tabela por temporada com partidas, gols por partida e percentual de cada resultado",
            )
