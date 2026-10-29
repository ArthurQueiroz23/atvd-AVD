"""Cálculos do Dashboard 2 (indicadores do fator casa).

As funções recebem e devolvem DataFrames do pandas, sem nada de Streamlit,
para poderem ser testadas separadamente (ver tests/test_metricas.py).

Todo resultado é contado do ponto de vista de um "time analisado":
- fator casa geral (nenhum clube escolhido): o time analisado é sempre o mandante;
- clube escolhido: o time analisado é o próprio clube, jogando em casa ou fora.
A função `partidas_analisadas` monta essa visão (colunas gols_pro e gols_contra),
e todo o resto do módulo trabalha sobre ela.
"""

import numpy as np
import pandas as pd

# Resultado do ponto de vista do time analisado, na ordem usada nos gráficos
RESULTADOS = ["Vitória", "Empate", "Derrota"]

# Em que jogos de um clube escolhido a análise considera
EM_CASA, FORA, EM_CASA_E_FORA = "Em casa", "Fora", "Em casa e fora"
LOCAIS = [EM_CASA, FORA, EM_CASA_E_FORA]

# Faixas de saldo de gols do time analisado: placares mais elásticos ficam nas pontas
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


def ponto_de_vista(partidas, em_casa):
    """Acrescenta local, gols_pro e gols_contra do time analisado.

    `em_casa` diz, partida a partida, se o time analisado era o mandante.
    """
    return partidas.assign(
        local=np.where(em_casa, "casa", "fora"),
        gols_pro=np.where(em_casa, partidas["mandante_Placar"], partidas["visitante_Placar"]),
        gols_contra=np.where(em_casa, partidas["visitante_Placar"], partidas["mandante_Placar"]),
    )


def partidas_analisadas(partidas, clube=None, local=EM_CASA_E_FORA):
    """Partidas do recorte vistas pelo time analisado, uma linha por partida.

    Sem clube: todas as partidas, vistas pelo mandante (fator casa geral).
    Com clube: só as partidas dele no local escolhido, vistas pelo clube.
    Um clube nunca é mandante e visitante da mesma partida, então nada é contado duas vezes.
    """
    if clube is None:
        return ponto_de_vista(partidas, np.ones(len(partidas), dtype=bool))
    em_casa = partidas["mandante"] == clube
    fora = partidas["visitante"] == clube
    filtro = {EM_CASA: em_casa, FORA: fora, EM_CASA_E_FORA: em_casa | fora}[local]
    return ponto_de_vista(partidas[filtro], em_casa[filtro])


def referencia_dos_clubes(partidas, local):
    """Base de comparação para um clube: todas as partidas vistas por um clube qualquer no mesmo local.

    Em casa usa o ponto de vista do mandante; fora, o do visitante; em casa e fora junta
    os dois (cada partida entra uma vez para cada time), como a média de um clube da liga.
    """
    casa = ponto_de_vista(partidas, np.ones(len(partidas), dtype=bool))
    fora = ponto_de_vista(partidas, np.zeros(len(partidas), dtype=bool))
    return {EM_CASA: casa, FORA: fora, EM_CASA_E_FORA: pd.concat([casa, fora], ignore_index=True)}[local]


def rotulos_dos_resultados(clube=None):
    """Nomes das três categorias de RESULTADOS para mostrar na tela."""
    if clube is None:
        return ["Mandante venceu", "Empate", "Visitante venceu"]
    return [f"{clube} venceu", "Empate", f"{clube} perdeu"]


def saldo_do_time(analisadas):
    """Gols a favor menos gols contra do time analisado, partida a partida."""
    return analisadas["gols_pro"] - analisadas["gols_contra"]


def resultado_pelo_saldo(saldo):
    """Categoria de RESULTADOS a partir do saldo do time analisado (positivo, zero ou negativo)."""
    resultado = np.select([saldo > 0, saldo == 0], RESULTADOS[:2], default=RESULTADOS[2])
    return pd.Series(resultado, index=saldo.index)


def classificar_resultados(analisadas):
    """Resultado de cada partida (uma das categorias de RESULTADOS) para o time analisado."""
    return resultado_pelo_saldo(saldo_do_time(analisadas))


def calcular_kpis(analisadas):
    """Indicadores do Dashboard 2 para as partidas analisadas.

    Indicadores que não podem ser calculados (recorte vazio ou sem arrecadação
    registrada) voltam como None, para o app mostrar "–" em vez de um número errado.
    """
    partidas = len(analisadas)
    arrecadacao = analisadas["arrecadacao"].dropna()
    vitorias = (classificar_resultados(analisadas) == "Vitória").mean()
    gols = (analisadas["gols_pro"] + analisadas["gols_contra"]).mean()
    return {
        "partidas": partidas,
        "pct_vitorias": float(vitorias) if partidas else None,
        "gols_por_partida": float(gols) if partidas else None,
        "partidas_com_arrecadacao": len(arrecadacao),
        "arrecadacao_mediana": float(arrecadacao.median()) if len(arrecadacao) else None,
    }


def percentuais_resultados(analisadas):
    """Fração das partidas em cada resultado, na ordem de RESULTADOS."""
    return classificar_resultados(analisadas).value_counts(normalize=True).reindex(RESULTADOS, fill_value=0.0)


def resultados_por_temporada(analisadas):
    """Quantidade e percentual de cada resultado por temporada (formato longo, para o Altair).

    `total` é o número de partidas da temporada no recorte; as três categorias somam esse valor.
    """
    contagem = (
        analisadas.assign(resultado=classificar_resultados(analisadas))
        .groupby(["temporada", "resultado"])
        .size()
        .rename("partidas")
        .reset_index()
    )
    contagem["total"] = contagem.groupby("temporada")["partidas"].transform("sum")
    contagem["percentual"] = contagem["partidas"] / contagem["total"]
    contagem["ordem"] = contagem["resultado"].map(RESULTADOS.index)
    return contagem


def resultados_por_saldo(analisadas, referencia):
    """Partidas por saldo de gols do time analisado, no recorte e numa referência.

    Todas as faixas de ROTULOS_SALDO aparecem, mesmo sem partidas, cada uma com o resultado
    que representa. O saldo é limitado a ±3: uma vitória por 5 x 0 entra em "+3 ou mais".
    """
    saldos = pd.Series(list(ROTULOS_SALDO))
    no_recorte = saldo_do_time(analisadas).clip(-3, 3).value_counts()
    na_referencia = saldo_do_time(referencia).clip(-3, 3).value_counts(normalize=True)
    tabela = pd.DataFrame(
        {
            "saldo": saldos,
            "faixa": saldos.map(ROTULOS_SALDO),
            "resultado": resultado_pelo_saldo(saldos),
            "partidas": saldos.map(no_recorte).fillna(0).astype(int),
            "percentual_referencia": saldos.map(na_referencia).fillna(0.0),
        }
    )
    tabela["percentual"] = tabela["partidas"] / len(analisadas) if len(analisadas) else 0.0
    return tabela


def gols_por_temporada(analisadas, primeira, ultima):
    """Média de gols por partida (dos dois times) em cada temporada do intervalo.

    Temporadas sem partidas no recorte (por exemplo, quando o clube escolhido não
    estava na Série A) ficam com valor vazio, e o gráfico de linha mostra a lacuna.
    """
    gols = analisadas["gols_pro"] + analisadas["gols_contra"]
    return (
        gols.groupby(analisadas["temporada"])
        .agg(gols_por_partida="mean", partidas="size")
        .reindex(range(primeira, ultima + 1))
        .rename_axis("temporada")
        .reset_index()
    )


def tabela_por_temporada(analisadas):
    """Tabela com os mesmos números dos gráficos, uma linha por temporada."""
    percentuais = (
        resultados_por_temporada(analisadas)
        .pivot(index="temporada", columns="resultado", values="percentual")
        .reindex(columns=RESULTADOS)
        .fillna(0)
        * 100
    )
    gols = analisadas["gols_pro"] + analisadas["gols_contra"]
    resumo = gols.groupby(analisadas["temporada"]).agg(partidas="size", gols_por_partida="mean")
    return resumo.join(percentuais).reset_index()
