"""Testes dos cálculos do Dashboard 2 (src/metricas.py).

Rodar a partir da raiz do projeto:  python -m unittest discover -s tests -v
"""

import math
import unittest

import pandas as pd

from src.metricas import (
    RESULTADOS,
    adicionar_temporada,
    calcular_kpis,
    classificar_resultados,
    gols_por_temporada,
    resultados_por_temporada,
    tabela_por_temporada,
)

CAMINHO_DATASET = "data/clean/dataset.csv"


def partidas_exemplo():
    """Quatro partidas pequenas, com resultados e arrecadação conhecidos."""
    return pd.DataFrame(
        {
            "data": ["10/05/2010", "17/05/2010", "12/06/2012", "19/06/2012"],
            "mandante_Placar": [2, 0, 1, 3],
            "visitante_Placar": [1, 0, 3, 0],
            "resultado_mandante": ["Vitoria_Mandante", "Nao_Venceu", "Nao_Venceu", "Vitoria_Mandante"],
            "arrecadacao": [float("nan"), 100.0, 300.0, float("nan")],
        }
    )


class TestTemporada(unittest.TestCase):
    def test_jogos_de_janeiro_e_fevereiro_contam_para_o_ano_anterior(self):
        df = pd.DataFrame({"data": ["15/12/2020", "25/02/2021", "30/05/2021"]})
        self.assertEqual(adicionar_temporada(df)["temporada"].tolist(), [2020, 2020, 2021])

    def test_temporadas_do_dataset_tem_o_numero_esperado_de_partidas(self):
        temporadas = adicionar_temporada(pd.read_csv(CAMINHO_DATASET))["temporada"].value_counts()
        # 24 clubes em 2003 e 2004, 22 em 2005 e 20 a partir de 2006 (380 jogos).
        # Em 2016 falta 1 partida, que não foi disputada.
        self.assertEqual(temporadas[2003], 552)
        self.assertEqual(temporadas[2004], 552)
        self.assertEqual(temporadas[2005], 462)
        self.assertEqual(temporadas[2016], 379)
        for temporada in [2006, 2015, 2019, 2020, 2021, 2025]:
            self.assertEqual(temporadas[temporada], 380, f"temporada {temporada}")


class TestResultados(unittest.TestCase):
    def test_classificacao_pelo_placar(self):
        df = partidas_exemplo()
        self.assertEqual(
            classificar_resultados(df).tolist(),
            ["Vitória do mandante", "Empate", "Vitória do visitante", "Vitória do mandante"],
        )

    def test_classificacao_bate_com_a_variavel_de_classe_da_eda(self):
        df = pd.read_csv(CAMINHO_DATASET)
        venceu_pelo_placar = classificar_resultados(df) == "Vitória do mandante"
        venceu_na_eda = df["resultado_mandante"] == "Vitoria_Mandante"
        self.assertTrue((venceu_pelo_placar == venceu_na_eda).all())

    def test_percentuais_de_cada_temporada_somam_1(self):
        resultados = resultados_por_temporada(adicionar_temporada(partidas_exemplo()))
        somas = resultados.groupby("temporada")["percentual"].sum()
        for soma in somas:
            self.assertAlmostEqual(soma, 1.0)
        self.assertEqual(set(resultados["resultado"]), set(RESULTADOS))


class TestKpis(unittest.TestCase):
    def test_valores_calculados_a_mao(self):
        kpis = calcular_kpis(partidas_exemplo())
        self.assertEqual(kpis["partidas"], 4)
        self.assertAlmostEqual(kpis["pct_vitorias_mandante"], 0.5)  # 2 vitórias em 4 jogos
        self.assertAlmostEqual(kpis["gols_por_partida"], 2.5)  # (3 + 0 + 4 + 3) / 4
        self.assertEqual(kpis["partidas_com_arrecadacao"], 2)
        self.assertAlmostEqual(kpis["arrecadacao_mediana"], 200.0)  # mediana de 100 e 300

    def test_recorte_vazio_nao_gera_numero(self):
        kpis = calcular_kpis(partidas_exemplo().iloc[0:0])
        self.assertEqual(kpis["partidas"], 0)
        self.assertIsNone(kpis["pct_vitorias_mandante"])
        self.assertIsNone(kpis["gols_por_partida"])
        self.assertIsNone(kpis["arrecadacao_mediana"])

    def test_recorte_sem_arrecadacao(self):
        kpis = calcular_kpis(partidas_exemplo().iloc[[0, 3]])
        self.assertEqual(kpis["partidas_com_arrecadacao"], 0)
        self.assertIsNone(kpis["arrecadacao_mediana"])

    def test_dataset_completo(self):
        df = pd.read_csv(CAMINHO_DATASET)
        kpis = calcular_kpis(df)
        self.assertEqual(kpis["partidas"], 9165)
        self.assertAlmostEqual(kpis["pct_vitorias_mandante"], 4550 / 9165)
        gols_esperados = (df["mandante_Placar"].sum() + df["visitante_Placar"].sum()) / len(df)
        self.assertAlmostEqual(kpis["gols_por_partida"], gols_esperados)
        self.assertEqual(kpis["partidas_com_arrecadacao"], 380)
        self.assertAlmostEqual(kpis["arrecadacao_mediana"], df["arrecadacao"].median())


class TestTabelasPorTemporada(unittest.TestCase):
    def test_temporada_sem_partidas_fica_vazia(self):
        gols = gols_por_temporada(adicionar_temporada(partidas_exemplo()), 2010, 2012)
        self.assertEqual(gols["temporada"].tolist(), [2010, 2011, 2012])
        self.assertAlmostEqual(gols.loc[0, "gols_por_partida"], 1.5)  # (3 + 0) / 2
        self.assertTrue(math.isnan(gols.loc[1, "gols_por_partida"]))
        self.assertAlmostEqual(gols.loc[2, "gols_por_partida"], 3.5)  # (4 + 3) / 2

    def test_tabela_tem_percentuais_que_somam_100(self):
        tabela = tabela_por_temporada(adicionar_temporada(partidas_exemplo()))
        self.assertEqual(tabela["partidas"].tolist(), [2, 2])
        for _, linha in tabela.iterrows():
            self.assertAlmostEqual(sum(linha[r] for r in RESULTADOS), 100.0)


if __name__ == "__main__":
    unittest.main()
