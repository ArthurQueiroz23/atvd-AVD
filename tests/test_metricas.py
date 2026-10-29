"""Testes dos cálculos do Dashboard 2 (src/metricas.py).

Rodar a partir da raiz do projeto:  python -m unittest discover -s tests -v
"""

import math
import unittest

import pandas as pd

from src.metricas import (
    EM_CASA,
    EM_CASA_E_FORA,
    FORA,
    RESULTADOS,
    ROTULOS_SALDO,
    adicionar_temporada,
    calcular_kpis,
    classificar_resultados,
    gols_por_temporada,
    partidas_analisadas,
    percentuais_resultados,
    referencia_dos_clubes,
    resultados_por_saldo,
    resultados_por_temporada,
    rotulos_dos_resultados,
    tabela_por_temporada,
)

CAMINHO_DATASET = "data/clean/dataset.csv"


def carregar_dataset():
    return adicionar_temporada(pd.read_csv(CAMINHO_DATASET))


def partidas_exemplo():
    """Quatro partidas pequenas, com resultados e arrecadação conhecidos (2 x 1, 0 x 0, 1 x 3 e 3 x 0)."""
    return adicionar_temporada(
        pd.DataFrame(
            {
                "data": ["10/05/2010", "17/05/2010", "12/06/2012", "19/06/2012"],
                "mandante": ["A", "B", "C", "D"],
                "visitante": ["B", "C", "D", "A"],
                "mandante_Placar": [2, 0, 1, 3],
                "visitante_Placar": [1, 0, 3, 0],
                "resultado_mandante": ["Vitoria_Mandante", "Nao_Venceu", "Nao_Venceu", "Vitoria_Mandante"],
                "arrecadacao": [float("nan"), 100.0, 300.0, float("nan")],
            }
        )
    )


def jogos_do_sport():
    """Os seis casos do Sport (vence, empata e perde, em casa e fora) e um jogo sem ele.

    Em 2010 e 2011 o Sport joga em casa e fora; em 2012 só há o jogo sem o Sport.
    """
    return pd.DataFrame(
        {
            "temporada": [2010, 2010, 2011, 2010, 2011, 2011, 2012],
            "mandante": ["Sport", "Sport", "Sport", "Bahia", "Ceara", "Vitoria", "Gremio"],
            "visitante": ["Bahia", "Ceara", "Vitoria", "Sport", "Sport", "Sport", "Santos"],
            "mandante_Placar": [2, 1, 0, 0, 2, 2, 1],
            "visitante_Placar": [0, 1, 1, 3, 2, 1, 0],
            "arrecadacao": [float("nan")] * 7,
        }
    )


class TestTemporada(unittest.TestCase):
    def test_jogos_de_janeiro_e_fevereiro_contam_para_o_ano_anterior(self):
        df = pd.DataFrame({"data": ["15/12/2020", "25/02/2021", "30/05/2021"]})
        self.assertEqual(adicionar_temporada(df)["temporada"].tolist(), [2020, 2020, 2021])

    def test_temporadas_do_dataset_tem_o_numero_esperado_de_partidas(self):
        temporadas = carregar_dataset()["temporada"].value_counts()
        # 24 clubes em 2003 e 2004, 22 em 2005 e 20 a partir de 2006 (380 jogos).
        # Em 2016 falta 1 partida, que não foi disputada.
        self.assertEqual(temporadas[2003], 552)
        self.assertEqual(temporadas[2004], 552)
        self.assertEqual(temporadas[2005], 462)
        self.assertEqual(temporadas[2016], 379)
        for temporada in [2006, 2015, 2019, 2020, 2021, 2025]:
            self.assertEqual(temporadas[temporada], 380, f"temporada {temporada}")


class TestPontoDeVista(unittest.TestCase):
    """Os casos do enunciado: o resultado é sempre do time analisado, em casa ou fora."""

    def test_clube_em_casa_e_fora(self):
        sport = partidas_analisadas(jogos_do_sport(), "Sport", EM_CASA_E_FORA)
        self.assertEqual(sport.index.tolist(), [0, 1, 2, 3, 4, 5])  # o jogo sem o Sport fica de fora
        self.assertEqual(sport["local"].tolist(), ["casa"] * 3 + ["fora"] * 3)
        # Em casa: 2 x 0, 1 x 1, 0 x 1. Fora: 0 x 3, 2 x 2, 2 x 1 (placar mandante x visitante)
        self.assertEqual(
            classificar_resultados(sport).tolist(),
            ["Vitória", "Empate", "Derrota", "Vitória", "Empate", "Derrota"],
        )
        self.assertEqual(sport["gols_pro"].tolist(), [2, 1, 0, 3, 2, 1])
        self.assertEqual(sport["gols_contra"].tolist(), [0, 1, 1, 0, 2, 2])

    def test_so_em_casa_ou_so_fora(self):
        em_casa = partidas_analisadas(jogos_do_sport(), "Sport", EM_CASA)
        fora = partidas_analisadas(jogos_do_sport(), "Sport", FORA)
        self.assertEqual(em_casa.index.tolist(), [0, 1, 2])
        self.assertEqual(fora.index.tolist(), [3, 4, 5])
        self.assertEqual(classificar_resultados(em_casa).tolist(), ["Vitória", "Empate", "Derrota"])
        self.assertEqual(classificar_resultados(fora).tolist(), ["Vitória", "Empate", "Derrota"])

    def test_fator_casa_geral_ve_cada_partida_pelo_mandante(self):
        geral = partidas_analisadas(jogos_do_sport())
        self.assertEqual(len(geral), 7)
        self.assertEqual(
            classificar_resultados(geral).tolist(),
            ["Vitória", "Empate", "Derrota", "Derrota", "Empate", "Vitória", "Vitória"],
        )
        # A mesma partida (Bahia 0 x 3 Sport) muda de categoria conforme a análise
        sport = partidas_analisadas(jogos_do_sport(), "Sport", EM_CASA_E_FORA)
        self.assertEqual(classificar_resultados(geral)[3], "Derrota")  # derrota do mandante (Bahia)
        self.assertEqual(classificar_resultados(sport)[3], "Vitória")  # vitória do Sport

    def test_temporada_sem_jogos_do_clube(self):
        sport = partidas_analisadas(jogos_do_sport(), "Sport", EM_CASA_E_FORA)
        self.assertEqual(sorted(resultados_por_temporada(sport)["temporada"].unique()), [2010, 2011])
        gols = gols_por_temporada(sport, 2010, 2012)
        self.assertTrue(math.isnan(gols.loc[gols["temporada"] == 2012, "gols_por_partida"].iloc[0]))

    def test_casa_e_fora_na_mesma_temporada(self):
        sport = partidas_analisadas(jogos_do_sport(), "Sport", EM_CASA_E_FORA)
        tabela = resultados_por_temporada(sport).set_index(["temporada", "resultado"])
        # 2010: vitória em casa, empate em casa e vitória fora
        self.assertEqual(tabela.loc[(2010, "Vitória"), "partidas"], 2)
        self.assertEqual(tabela.loc[(2010, "Empate"), "partidas"], 1)
        # 2011: derrota em casa, empate fora e derrota fora
        self.assertEqual(tabela.loc[(2011, "Derrota"), "partidas"], 2)
        self.assertEqual(tabela.loc[(2011, "Empate"), "partidas"], 1)
        self.assertTrue((tabela["total"] == 3).all())
        for soma in tabela.groupby(level="temporada")["percentual"].sum():
            self.assertAlmostEqual(soma, 1.0)

    def test_nenhuma_partida_contada_duas_vezes(self):
        df = carregar_dataset()
        for clube in sorted(set(df["mandante"]) | set(df["visitante"])):
            em_casa = partidas_analisadas(df, clube, EM_CASA)
            fora = partidas_analisadas(df, clube, FORA)
            todos = partidas_analisadas(df, clube, EM_CASA_E_FORA)
            self.assertTrue(todos.index.is_unique, clube)
            self.assertEqual(len(todos), len(em_casa) + len(fora), clube)
            self.assertEqual(len(todos), ((df["mandante"] == clube) | (df["visitante"] == clube)).sum(), clube)

    def test_sport_no_dataset_real(self):
        df = carregar_dataset()
        sport = partidas_analisadas(df[df["temporada"] == 2016], "Sport", EM_CASA_E_FORA)
        self.assertEqual(len(sport), 38)  # 19 em casa e 19 fora
        self.assertEqual((sport["local"] == "casa").sum(), 19)
        contagem = resultados_por_temporada(sport)
        self.assertEqual(contagem["partidas"].sum(), 38)

    def test_referencia_dos_clubes(self):
        df = carregar_dataset()
        vitorias_casa = (df["mandante_Placar"] > df["visitante_Placar"]).sum()
        vitorias_fora = (df["mandante_Placar"] < df["visitante_Placar"]).sum()
        casa = calcular_kpis(referencia_dos_clubes(df, EM_CASA))["pct_vitorias"]
        fora = calcular_kpis(referencia_dos_clubes(df, FORA))["pct_vitorias"]
        ambos = referencia_dos_clubes(df, EM_CASA_E_FORA)
        self.assertAlmostEqual(casa, vitorias_casa / len(df))
        self.assertAlmostEqual(fora, vitorias_fora / len(df))
        self.assertEqual(len(ambos), 2 * len(df))  # cada partida uma vez para cada time
        self.assertAlmostEqual(calcular_kpis(ambos)["pct_vitorias"], (vitorias_casa + vitorias_fora) / (2 * len(df)))

    def test_rotulos(self):
        self.assertEqual(rotulos_dos_resultados(), ["Mandante venceu", "Empate", "Visitante venceu"])
        self.assertEqual(rotulos_dos_resultados("Sport"), ["Sport venceu", "Empate", "Sport perdeu"])


class TestResultados(unittest.TestCase):
    def test_classificacao_pelo_placar(self):
        geral = partidas_analisadas(partidas_exemplo())
        # Placares: 2 x 1, 0 x 0, 1 x 3 (o visitante venceu, ou seja, derrota do mandante) e 3 x 0
        self.assertEqual(classificar_resultados(geral).tolist(), ["Vitória", "Empate", "Derrota", "Vitória"])

    def test_classificacao_bate_com_a_variavel_de_classe_da_eda(self):
        df = carregar_dataset()
        venceu_pelo_placar = classificar_resultados(partidas_analisadas(df)) == "Vitória"
        venceu_na_eda = df["resultado_mandante"] == "Vitoria_Mandante"
        self.assertTrue((venceu_pelo_placar == venceu_na_eda).all())

    def test_as_tres_categorias_somam_as_partidas_de_cada_temporada(self):
        df = carregar_dataset()
        resultados = resultados_por_temporada(partidas_analisadas(df))
        partidas_por_temporada = df.groupby("temporada").size()
        soma_das_categorias = resultados.groupby("temporada")["partidas"].sum()
        self.assertTrue((soma_das_categorias == partidas_por_temporada).all())
        self.assertTrue((resultados["total"] == resultados["temporada"].map(partidas_por_temporada)).all())
        # Nenhuma partida é contada em duas categorias: no máximo uma linha por (temporada, resultado)
        self.assertFalse(resultados.duplicated(["temporada", "resultado"]).any())

    def test_percentuais_do_recorte_na_ordem_dos_resultados(self):
        percentuais = percentuais_resultados(partidas_analisadas(partidas_exemplo()))
        self.assertEqual(list(percentuais.index), RESULTADOS)
        self.assertEqual(percentuais.tolist(), [0.5, 0.25, 0.25])

    def test_resultado_sem_partidas_aparece_como_zero(self):
        so_vitorias = partidas_analisadas(partidas_exemplo().iloc[[0, 3]])
        self.assertEqual(percentuais_resultados(so_vitorias).tolist(), [1.0, 0.0, 0.0])


class TestResultadosPorSaldo(unittest.TestCase):
    def test_faixas_e_resultado_de_cada_saldo(self):
        exemplo = partidas_analisadas(partidas_exemplo())  # saldos do mandante: +1, 0, -2 e +3
        saldos = resultados_por_saldo(exemplo, exemplo)
        self.assertEqual(saldos["faixa"].tolist(), list(ROTULOS_SALDO.values()))
        self.assertEqual(saldos["partidas"].tolist(), [0, 1, 0, 1, 1, 0, 1])
        self.assertEqual(saldos["resultado"].tolist(), ["Derrota"] * 3 + ["Empate"] + ["Vitória"] * 3)
        self.assertAlmostEqual(saldos["percentual"].sum(), 1.0)
        self.assertAlmostEqual(saldos["percentual_referencia"].sum(), 1.0)

    def test_saldo_do_clube_fora_de_casa(self):
        fora = partidas_analisadas(jogos_do_sport(), "Sport", FORA)  # 0 x 3, 2 x 2 e 2 x 1 para o mandante
        saldos = resultados_por_saldo(fora, fora).set_index("saldo")
        self.assertEqual(saldos.loc[3, "partidas"], 1)  # venceu por 3 fora de casa
        self.assertEqual(saldos.loc[0, "partidas"], 1)
        self.assertEqual(saldos.loc[-1, "partidas"], 1)  # perdeu por 1 fora de casa

    def test_placares_elasticos_ficam_nas_pontas(self):
        goleadas = partidas_analisadas(pd.DataFrame({"mandante_Placar": [5, 0, 3], "visitante_Placar": [0, 4, 0]}))
        saldos = resultados_por_saldo(goleadas, goleadas).set_index("saldo")
        self.assertEqual(saldos.loc[3, "partidas"], 2)  # 5 x 0 e 3 x 0
        self.assertEqual(saldos.loc[-3, "partidas"], 1)  # 0 x 4

    def test_bate_com_os_kpis_e_com_o_grafico_por_temporada(self):
        df = carregar_dataset()
        flamengo = partidas_analisadas(df[df["temporada"].between(2010, 2025)], "Flamengo", EM_CASA_E_FORA)
        saldos = resultados_por_saldo(flamengo, referencia_dos_clubes(df, EM_CASA_E_FORA))
        kpis = calcular_kpis(flamengo)
        self.assertEqual(saldos["partidas"].sum(), kpis["partidas"])
        vitorias = saldos.loc[saldos["resultado"] == "Vitória", "percentual"].sum()
        self.assertAlmostEqual(vitorias, kpis["pct_vitorias"])
        por_temporada = resultados_por_temporada(flamengo).groupby("resultado")["partidas"].sum()
        por_saldo = saldos.groupby("resultado")["partidas"].sum()
        self.assertTrue((por_temporada.reindex(RESULTADOS) == por_saldo.reindex(RESULTADOS)).all())


class TestKpis(unittest.TestCase):
    def test_valores_calculados_a_mao(self):
        kpis = calcular_kpis(partidas_analisadas(partidas_exemplo()))
        self.assertEqual(kpis["partidas"], 4)
        self.assertAlmostEqual(kpis["pct_vitorias"], 0.5)  # 2 vitórias do mandante em 4 jogos
        self.assertAlmostEqual(kpis["gols_por_partida"], 2.5)  # (3 + 0 + 4 + 3) / 4
        self.assertEqual(kpis["partidas_com_arrecadacao"], 2)
        self.assertAlmostEqual(kpis["arrecadacao_mediana"], 200.0)  # mediana de 100 e 300

    def test_vitorias_do_clube_em_casa_e_fora(self):
        kpis = calcular_kpis(partidas_analisadas(jogos_do_sport(), "Sport", EM_CASA_E_FORA))
        self.assertEqual(kpis["partidas"], 6)
        self.assertAlmostEqual(kpis["pct_vitorias"], 2 / 6)  # venceu 1 em casa e 1 fora
        self.assertAlmostEqual(kpis["gols_por_partida"], (2 + 2 + 1 + 3 + 4 + 3) / 6)

    def test_recorte_vazio_nao_gera_numero(self):
        kpis = calcular_kpis(partidas_analisadas(partidas_exemplo().iloc[0:0]))
        self.assertEqual(kpis["partidas"], 0)
        self.assertIsNone(kpis["pct_vitorias"])
        self.assertIsNone(kpis["gols_por_partida"])
        self.assertIsNone(kpis["arrecadacao_mediana"])

    def test_recorte_sem_arrecadacao(self):
        kpis = calcular_kpis(partidas_analisadas(partidas_exemplo().iloc[[0, 3]]))
        self.assertEqual(kpis["partidas_com_arrecadacao"], 0)
        self.assertIsNone(kpis["arrecadacao_mediana"])

    def test_dataset_completo(self):
        df = carregar_dataset()
        kpis = calcular_kpis(partidas_analisadas(df))
        self.assertEqual(kpis["partidas"], 9165)
        self.assertAlmostEqual(kpis["pct_vitorias"], 4550 / 9165)
        gols_esperados = (df["mandante_Placar"].sum() + df["visitante_Placar"].sum()) / len(df)
        self.assertAlmostEqual(kpis["gols_por_partida"], gols_esperados)
        self.assertEqual(kpis["partidas_com_arrecadacao"], 380)
        self.assertAlmostEqual(kpis["arrecadacao_mediana"], df["arrecadacao"].median())


class TestTabelasPorTemporada(unittest.TestCase):
    def test_temporada_sem_partidas_fica_vazia(self):
        gols = gols_por_temporada(partidas_analisadas(partidas_exemplo()), 2010, 2012)
        self.assertEqual(gols["temporada"].tolist(), [2010, 2011, 2012])
        self.assertAlmostEqual(gols.loc[0, "gols_por_partida"], 1.5)  # (3 + 0) / 2
        self.assertTrue(math.isnan(gols.loc[1, "gols_por_partida"]))
        self.assertAlmostEqual(gols.loc[2, "gols_por_partida"], 3.5)  # (4 + 3) / 2

    def test_tabela_tem_percentuais_que_somam_100(self):
        tabela = tabela_por_temporada(partidas_analisadas(partidas_exemplo()))
        self.assertEqual(tabela["partidas"].tolist(), [2, 2])
        for _, linha in tabela.iterrows():
            self.assertAlmostEqual(sum(linha[r] for r in RESULTADOS), 100.0)


if __name__ == "__main__":
    unittest.main()
