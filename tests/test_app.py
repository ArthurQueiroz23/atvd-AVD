"""Testes do app inteiro com o AppTest do Streamlit (roda o app.py sem abrir o navegador).

Rodar a partir da raiz do projeto:  python -m unittest discover -s tests -v
"""

import unittest

import pandas as pd
from streamlit.testing.v1 import AppTest

from src.metricas import adicionar_temporada

CAMINHO_APP = "../app.py"  # relativo a este arquivo, como o AppTest espera


def abrir_app():
    return AppTest.from_file(CAMINHO_APP, default_timeout=60).run()


def percentual_br(valor):
    return f"{valor * 100:.1f}%".replace(".", ",")


class TestAbertura(unittest.TestCase):
    def test_abre_sem_erro_com_as_duas_abas(self):
        at = abrir_app()
        self.assertFalse(at.exception)
        self.assertEqual(
            [aba.label for aba in at.tabs],
            ["Dashboard 1 · Correlação e distribuição", "Dashboard 2 · Indicadores do fator casa"],
        )
        self.assertFalse(at.warning)

    def test_dashboard2_mostra_os_quatro_kpis_com_st_metric(self):
        at = abrir_app()
        self.assertEqual(
            [m.label for m in at.metric],
            ["Partidas analisadas", "Vitórias do mandante", "Gols por partida", "Arrecadação mediana"],
        )
        self.assertEqual(at.metric[0].value, "9.165")
        self.assertEqual(at.metric[1].value, percentual_br(4550 / 9165))
        self.assertEqual(at.metric[3].value, "R$ 996 mil")


class TestDashboard1(unittest.TestCase):
    def test_nenhuma_variavel(self):
        at = abrir_app()
        at.multiselect[0].set_value([]).run()
        self.assertFalse(at.exception)
        self.assertEqual(
            [w.value for w in at.warning],
            [
                "Selecione pelo menos 2 variáveis para calcular a correlação.",
                "Selecione pelo menos 1 variável para ver a distribuição.",
            ],
        )

    def test_uma_variavel(self):
        at = abrir_app()
        at.multiselect[0].set_value(["rodata"]).run()
        self.assertFalse(at.exception)
        self.assertEqual(
            [w.value for w in at.warning],
            ["Selecione pelo menos 2 variáveis para calcular a correlação."],
        )

    def test_tres_variaveis_separando_por_classe(self):
        at = abrir_app()
        at.multiselect[0].set_value(["rodata", "mandante_Placar", "arrecadacao"]).run()
        at.toggle[0].set_value(True).run()
        self.assertFalse(at.exception)
        self.assertFalse(at.warning)

    def test_correlacao_ignora_pares_com_poucas_partidas(self):
        # Com arrecadação acima de R$ 5 milhões sobram só 4 partidas com esse valor:
        # os pares com arrecadação não podem aparecer no mapa de correlação.
        at = abrir_app()
        slider = at.slider(key="intervalo_arrecadacao")
        slider.set_range(5_000_000.0, slider.max).run()
        self.assertFalse(at.exception)
        self.assertTrue(any("ficaram de fora" in c.value for c in at.caption))


class TestDashboard2(unittest.TestCase):
    def test_filtros_ficam_so_na_barra_lateral(self):
        at = abrir_app()
        self.assertIn("kpi_temporadas", [s.key for s in at.sidebar.slider])
        self.assertIn("kpi_clube", [s.key for s in at.sidebar.selectbox])
        self.assertNotIn("kpi_temporadas", [s.key for s in at.main.slider])
        self.assertNotIn("kpi_clube", [s.key for s in at.main.selectbox])

    def test_aba_tem_tres_graficos(self):
        at = abrir_app()
        self.assertEqual(len(at.tabs[1].get("vega_lite_chart")), 3)

    def test_uma_temporada_so(self):
        df = adicionar_temporada(pd.read_csv("data/clean/dataset.csv"))
        at = abrir_app()
        at.slider(key="kpi_temporadas").set_range(2017, 2017).run()
        self.assertFalse(at.exception)
        self.assertEqual(at.metric[0].value, str((df["temporada"] == 2017).sum()))
        self.assertTrue(any("temporada 2017 ·" in c.value for c in at.caption))
        self.assertEqual(len(at.tabs[1].get("vega_lite_chart")), 3)

    def test_trocar_o_clube_varias_vezes(self):
        df = adicionar_temporada(pd.read_csv("data/clean/dataset.csv"))
        at = abrir_app()
        at.slider(key="kpi_temporadas").set_range(2010, 2015).run()
        for clube in ["Flamengo", "Vasco", "Gremio", "Todos os clubes"]:
            at.selectbox(key="kpi_clube").select(clube).run()
            self.assertFalse(at.exception, clube)
            recorte = df[df["temporada"].between(2010, 2015)]
            if clube != "Todos os clubes":
                recorte = recorte[recorte["mandante"] == clube]
            self.assertEqual(at.metric[0].value.replace(".", ""), str(len(recorte)), clube)
            # A tabela por temporada soma as mesmas partidas do indicador
            self.assertEqual(at.dataframe[0].value["partidas"].sum(), len(recorte), clube)

    def test_clube_e_temporada(self):
        df = adicionar_temporada(pd.read_csv("data/clean/dataset.csv"))
        esperado = df[(df["temporada"] == 2025) & (df["mandante"] == "Flamengo")]

        at = abrir_app()
        at.slider(key="kpi_temporadas").set_range(2025, 2025).run()
        at.selectbox(key="kpi_clube").select("Flamengo").run()

        self.assertFalse(at.exception)
        self.assertEqual(at.metric[0].value, str(len(esperado)))
        vitorias = (esperado["resultado_mandante"] == "Vitoria_Mandante").mean()
        self.assertEqual(at.metric[1].value, percentual_br(vitorias))

    def test_arrecadacao_fora_de_2025_fica_sem_valor(self):
        at = abrir_app()
        at.slider(key="kpi_temporadas").set_range(2003, 2024).run()
        self.assertFalse(at.exception)
        self.assertEqual(at.metric[3].value, "–")

    def test_recorte_vazio_mostra_aviso(self):
        # O Barueri não jogou a Série A entre 2020 e 2025
        at = abrir_app()
        at.slider(key="kpi_temporadas").set_range(2020, 2025).run()
        at.selectbox(key="kpi_clube").select("Barueri").run()
        self.assertFalse(at.exception)
        self.assertEqual(len(at.metric), 0)
        self.assertTrue(any("Nenhuma partida no recorte" in w.value for w in at.warning))


if __name__ == "__main__":
    unittest.main()
