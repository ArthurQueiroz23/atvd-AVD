"""Cálculos do Dashboard 2 (indicadores do fator casa).

As funções recebem e devolvem DataFrames do pandas, sem nada de Streamlit,
para poderem ser testadas separadamente (ver tests/test_metricas.py).
"""

import numpy as np
import pandas as pd

# Resultado da partida do ponto de vista do mandante, na ordem usada nos gráficos
RESULTADOS = ["Vitória do mandante", "Empate", "Vitória do visitante"]


def adicionar_temporada(df):
    """Acrescenta a coluna `temporada`, derivada da data da partida.

    Quase todas as edições começam e terminam no mesmo ano. A exceção é a de 2020,
    adiada pela pandemia, que terminou em fevereiro de 2021. Como nenhuma outra
    edição do dataset tem jogos em janeiro ou fevereiro, as partidas desses meses
    contam para a temporada do ano anterior.
    """
    datas = pd.to_datetime(df["data"], format="%d/%m/%Y")
    return df.assign(temporada=datas.dt.year - (datas.dt.month <= 2).astype(int))


def classificar_resultados(df):
    """Resultado de cada partida (uma das categorias de RESULTADOS), a partir do placar."""
    diferenca = df["mandante_Placar"] - df["visitante_Placar"]
    resultado = np.select([diferenca > 0, diferenca == 0], RESULTADOS[:2], default=RESULTADOS[2])
    return pd.Series(resultado, index=df.index)


def calcular_kpis(recorte):
    """Indicadores do Dashboard 2 para um recorte de partidas.

    Indicadores que não podem ser calculados (recorte vazio ou sem arrecadação
    registrada) voltam como None, para o app mostrar "–" em vez de um número errado.
    """
    partidas = len(recorte)
    arrecadacao = recorte["arrecadacao"].dropna()
    vitorias = (recorte["resultado_mandante"] == "Vitoria_Mandante").mean()
    gols = (recorte["mandante_Placar"] + recorte["visitante_Placar"]).mean()
    return {
        "partidas": partidas,
        "pct_vitorias_mandante": float(vitorias) if partidas else None,
        "gols_por_partida": float(gols) if partidas else None,
        "partidas_com_arrecadacao": len(arrecadacao),
        "arrecadacao_mediana": float(arrecadacao.median()) if len(arrecadacao) else None,
    }


def resultados_por_temporada(recorte):
    """Quantidade e percentual de cada resultado por temporada (formato longo, para o Altair)."""
    contagem = (
        recorte.assign(resultado=classificar_resultados(recorte))
        .groupby(["temporada", "resultado"])
        .size()
        .rename("partidas")
        .reset_index()
    )
    contagem["percentual"] = contagem["partidas"] / contagem.groupby("temporada")["partidas"].transform("sum")
    contagem["ordem"] = contagem["resultado"].map(RESULTADOS.index)
    return contagem


def gols_por_temporada(recorte, primeira, ultima):
    """Média de gols por partida em cada temporada do intervalo.

    Temporadas sem partidas no recorte (por exemplo, quando o clube escolhido não
    estava na Série A) ficam com valor vazio, e o gráfico de linha mostra a lacuna.
    """
    gols = recorte["mandante_Placar"] + recorte["visitante_Placar"]
    return (
        gols.groupby(recorte["temporada"])
        .agg(gols_por_partida="mean", partidas="size")
        .reindex(range(primeira, ultima + 1))
        .rename_axis("temporada")
        .reset_index()
    )


def tabela_por_temporada(recorte):
    """Tabela com os mesmos números dos gráficos, uma linha por temporada."""
    percentuais = (
        resultados_por_temporada(recorte)
        .pivot(index="temporada", columns="resultado", values="percentual")
        .reindex(columns=RESULTADOS)
        .fillna(0)
        * 100
    )
    gols = recorte["mandante_Placar"] + recorte["visitante_Placar"]
    resumo = gols.groupby(recorte["temporada"]).agg(partidas="size", gols_por_partida="mean")
    return resumo.join(percentuais).reset_index()
