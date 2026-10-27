# Declaração de Uso de IA

**Nome:** <!-- preencher -->\
**Data:** 27/10/2026

## Ferramenta

- Claude (claude.ai, modelo Claude Opus 5.5), em conversa no navegador.
- Claude Code, extensão no VS Code, para aplicar as alterações nos arquivos.

## Prompt usado

Os pedidos foram feitos em conversa, em várias etapas. Os principais foram:

1. "Analise todo esse projeto (repositório da disciplina) e me diga um passo a passo de como fazer a entrega."
2. Envio do notebook de EDA da Aula 11 (Campeonato Brasileiro) pedindo ajuda para gerar o `data/clean/dataset.csv` e adaptar o `app.py` às colunas do meu dataset.
3. "O app está rodando, mas está feio visualmente. Quero um visual que remeta a futebol."
4. Pedido ao Claude Code para aplicar o `app.py` e o `config.toml` gerados na conversa e preencher esta declaração, sem fazer commits.

## O que foi aceito, modificado ou rejeitado e por quê

- **Aceito:**
  - Passo a passo de configuração (ambiente virtual, publicação do repositório no GitHub, execução do app).
  - Notebook `eda-com-downloads.ipynb`: minha EDA da Aula 11 sem alterações, com a seção final de exportação dos datasets sugerida pela IA, seguindo o modelo do notebook da professora.
  - Adaptação do `app.py` ao meu dataset: `VARS_QUANT` com as variáveis da minha EDA (`rodata`, `mandante_Placar`, `visitante_Placar`, `arrecadacao`) e `resultado_mandante` como classe.
  - Manter no filtro as partidas sem `arrecadacao` (só 380 de 9.165 têm esse valor), para o filtro não descartar quase todo o dataset.
  - `@st.cache_data` no `src/data_loader.py`.
  - Identidade visual proposta pela IA (tema escuro com cores de gramado, fontes de placar, rótulos em português) no `app.py` e no `.streamlit/config.toml`.
  - Correções de sintaxe Python e revisão ortográfica dos textos.
- **Modificado:**
  - <!-- descreva aqui o que você mudou por conta própria depois de testar (cores, textos, filtros, ordem dos gráficos etc.) -->
- **Rejeitado:**
  - <!-- descreva aqui sugestões que você não usou e por quê -->

## O que foi feito por mim

- Escolha do dataset e EDA da Aula 11 (tratamento de ausentes, decisão de manter outliers, escolha das variáveis quantitativas e da variável de classe).
- Testes do app nos casos de borda (0, 1 e 2+ variáveis, filtros apertados, separação por classe) e conferência dos resultados.
- <!-- complete com outras decisões suas -->
