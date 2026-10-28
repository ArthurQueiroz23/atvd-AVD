# Declaração de Uso de IA

**Nome:** Arthur Queiroz Silva\
**Data:** 27/10/2026 e 28/10/2026

## Ferramenta

- Claude (claude.ai, modelo Claude Opus 5.5), em conversa no navegador.
- Claude Code (extensão do VS Code, modelo Claude Opus 5.5), que editou os arquivos do projeto, rodou os testes e conferiu o estado do Git. Os commits e o push foram feitos por mim.

## Prompt usado

Os pedidos foram feitos em conversa, em várias etapas. Os principais foram:

1. "Analise todo esse projeto (repositório da disciplina) e me diga um passo a passo de como fazer a entrega."
2. Envio do notebook de EDA da Aula 11 (Campeonato Brasileiro) pedindo ajuda para gerar o `data/clean/dataset.csv` e adaptar o `app.py` às colunas do meu dataset.
3. "O app está rodando, mas está feio visualmente. Quero um visual que remeta a futebol."
4. Pedido ao Claude Code para aplicar o `app.py` e o `config.toml` gerados na conversa e preencher esta declaração, sem fazer commits.
5. "Preciso que você confira se o meu repositório Git está certo e se meus commits chegaram no GitHub", só com comandos de leitura, e que abrisse o app localmente.
6. "Veja se falta algo para entregar que eu não tenha feito; caso eu tenha feito tudo, me diga como entregar para a professora."
7. "Tarefa: concluir, revisar e preparar toda a atividade de AVD para entrega": revisar o Dashboard 1, implementar o Dashboard 2 com `st.metric` e gráficos Altair, separar os dashboards com `st.tabs`, preencher a justificativa das métricas, completar esta declaração, atualizar o README, preparar o deploy e testar tudo. Tudo sem commits, sem push e sem gerar os rascunhos de layout.

### O que o Claude Code produziu na etapa final (28/10/2026)

- Dashboard 2 no `app.py`:
  - filtros de temporadas e de clube mandante;
  - quatro indicadores com `st.metric` (partidas analisadas, vitórias do mandante, gols por partida e arrecadação mediana);
  - gráficos Altair de resultado por temporada e de gols por partida por temporada;
  - tabela com os números por temporada;
  - separação dos dois dashboards em abas com `st.tabs`.
- `src/metricas.py`, com os cálculos dos indicadores e a criação da coluna de temporada a partir da data, e os testes automatizados em `tests/`.
- Correção no Dashboard 1: cada par da correlação de Spearman só aparece com pelo menos 30 partidas que tenham os dois valores. Antes, ao filtrar a arrecadação, o mapa mostrava correlações calculadas com 4 partidas.
- Ajustes de interface:
  - a faixa de abertura deixou de repetir números que viraram indicadores;
  - o aviso da arrecadação passou a dizer que ela só existe em 2025;
  - os emojis saíram dos títulos.
- Texto de `entregas/justificativa-metricas.md`, escrito pela IA a partir do que foi implementado, inclusive a proposta de público-alvo e de decisões apoiadas por cada métrica.
- Atualização do `README.md` e do `requirements.txt` (versões mínimas testadas de `streamlit` e `altair`, e o `kagglehub`, que os notebooks usam para baixar o dataset).
- Rascunho desta declaração. Os campos que dependem da minha opinião ficaram para eu completar.

## O que foi aceito, modificado ou rejeitado e por quê

- **Aceito:**
  - Passo a passo de configuração (ambiente virtual, publicação do repositório no GitHub, execução do app).
  - Notebook `eda-com-downloads.ipynb`: minha EDA da Aula 11 sem alterações, com a seção final de exportação dos datasets sugerida pela IA, seguindo o modelo do notebook da professora.
  - Adaptação do `app.py` ao meu dataset: `VARS_QUANT` com as variáveis da minha EDA (`rodata`, `mandante_Placar`, `visitante_Placar`, `arrecadacao`) e `resultado_mandante` como classe.
  - Manter no filtro as partidas sem `arrecadacao` (só 380 de 9.165 têm esse valor), para o filtro não descartar quase todo o dataset.
  - `@st.cache_data` no `src/data_loader.py`.
  - Identidade visual proposta pela IA (tema escuro com cores de gramado, fontes de placar, rótulos em português) no `app.py` e no `.streamlit/config.toml`.
  - Correções de sintaxe Python e revisão ortográfica dos textos.
  - <!-- depois de revisar, indique aqui o que da etapa final (lista acima) você aceitou -->
- **Modificado:**
  - <!-- descreva aqui o que você mudou por conta própria depois de testar (cores, textos, filtros, ordem dos gráficos etc.) -->
- **Rejeitado:**
  - <!-- descreva aqui sugestões que você não usou e por quê -->

## O que foi feito por mim

- Escolha do dataset e EDA da Aula 11 (tratamento de ausentes, decisão de manter outliers, escolha das variáveis quantitativas e da variável de classe).
- Testes do app nos casos de borda (0, 1 e 2+ variáveis, filtros apertados, separação por classe) e conferência dos resultados.
- Revisão das alterações, commits e envio para o GitHub.
- <!-- complete com outras decisões suas -->
