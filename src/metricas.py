"""Cálculos do Dashboard 2 (indicadores do fator casa).

As funções recebem e devolvem DataFrames do pandas, sem nada de Streamlit,
para poderem ser testadas separadamente (ver tests/test_metricas.py).
"""

import numpy as np
import pandas as pd

# Resultado da partida do ponto de vista do mandante, na ordem usada nos gráficos.
# "Derrota do mandante" é o mesmo que vitória do visitante.
RESULTADOS = ["Vitória do mandante", "Empate", "Derrota do mandante"]

# Faixas de saldo de gols do mandante no gráfico de margens: placares mais elásticos ficam nas pontas
ROTULOS_SALDO = {-3: "−3 ou menos", -2: "−2", -1: "−1", 0: "0", 1: "+1", 2: "+2", 3: "+3 ou mais"}


def adicionar_temporada(df):
    """Acrescenta a coluna `temporada`, derivada da data da partida.

    Quase todas as edições começam e terminam no mesmo ano. A exceção é a de 2020,
    adiada pela pandemia, que terminou em fevereiro de 2021. Como nenhuma outra
    edição do dataset tem jogos em janeiro ou fevereiro, as partidas desses meses
    contam para a temporada do ano anterior.
    """
    datas = pd.to_datetime(df["data"], format="%d/%m/%Y")
    return df.assign(temporada=datas.dt.year - (datas.dt.month <= 2).astype(int))


def saldo_do_mandante(df):
    """Gols do mandante menos gols do visitante, partida a partida."""
    return df["mandante_Placar"] - df["visitante_Placar"]


def resultado_pelo_saldo(saldo):
    """Categoria de RESULTADOS a partir do saldo de gols do mandante.

    Saldo positivo é vitória do mandante, zero é empate e negativo é derrota do mandante.
    """
    resultado = np.select([saldo > 0, saldo == 0], RESULTADOS[:2], default=RESULTADOS[2])
    return pd.Series(resultado, index=saldo.index)


def classificar_resultados(df):
    """Resultado de cada partida (uma das categorias de RESULTADOS), a partir do placar."""
    return resultado_pelo_saldo(saldo_do_mandante(df))


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


def percentuais_resultados(recorte):
    """Fração das partidas do recorte em cada resultado, na ordem de RESULTADOS."""
    return classificar_resultados(recorte).value_counts(normalize=True).reindex(RESULTADOS, fill_value=0.0)


def resultados_por_temporada(recorte):
    """Quantidade e percentual de cada resultado por temporada (formato longo, para o Altair).

    `total` é o número de partidas da temporada no recorte; as três categorias somam esse valor.
    """
    contagem = (
        recorte.assign(resultado=classificar_resultados(recorte))
        .groupby(["temporada", "resultado"])
        .size()
        .rename("partidas")
        .reset_index()
    )
    contagem["total"] = contagem.groupby("temporada")["partidas"].transform("sum")
    contagem["percentual"] = contagem["partidas"] / contagem["total"]
    contagem["ordem"] = contagem["resultado"].map(RESULTADOS.index)
    return contagem


def resultados_por_saldo(recorte, referencia):
    """Partidas por saldo de gols do mandante, no recorte e numa referência (o dataset completo).

    Todas as faixas de ROTULOS_SALDO aparecem, mesmo sem partidas, cada uma com o resultado
    que representa. O saldo é limitado a ±3: uma vitória por 5 x 0 entra em "+3 ou mais".
    """
    saldos = pd.Series(list(ROTULOS_SALDO))
    no_recorte = saldo_do_mandante(recorte).clip(-3, 3).value_counts()
    na_referencia = saldo_do_mandante(referencia).clip(-3, 3).value_counts(normalize=True)
    tabela = pd.DataFrame(
        {
            "saldo": saldos,
            "faixa": saldos.map(ROTULOS_SALDO),
            "resultado": resultado_pelo_saldo(saldos),
            "partidas": saldos.map(no_recorte).fillna(0).astype(int),
            "percentual_referencia": saldos.map(na_referencia).fillna(0.0),
        }
    )
    tabela["percentual"] = tabela["partidas"] / len(recorte) if len(recorte) else 0.0
    return tabela


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
