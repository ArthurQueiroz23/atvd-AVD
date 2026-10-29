# AVD-20262-pratica-streamlit

Repositório utilizado para aula prática relacionada a Streamlit na disciplina Análise e Visualização de Dados da Cesar School no período de 2026.2.

Repositório-modelo das Aulas 21, 22 e 23: construção de dois dashboards em Streamlit a partir da EDA desenvolvida em sala. O deploy dos dashboards ocorrerá via Streamlit Community Cloud e serão os seguintes:

- Dashboard 1 = correlação + distribuição das variáveis quantitativas
- Dashboard 2 = KPIs

## Meu projeto: Raio-X do Brasileirão

**Aluno:** Arthur Queiroz Silva

**Link do app (Aula 23):** <https://raio-x-brasileirao.streamlit.app/>

**Dataset:** [Campeonato Brasileiro de Futebol](https://www.kaggle.com/datasets/adaoduque/campeonato-brasileiro-de-futebol) (Kaggle, arquivo `campeonato-brasileiro-full.csv`), com as 9.165 partidas da Série A de 2003 a 2025.
- `notebooks/eda.ipynb` é a minha EDA original da Aula 11.
- `notebooks/eda-com-downloads.ipynb` é a mesma EDA com a exportação no final, que gera o `data/clean/dataset.csv` lido pelo app.

O app tem duas abas:

| Aba | O que mostra | Controles |
| --- | --- | --- |
| **Dashboard 1 · Correlação e distribuição** | Mapa de calor da correlação de Spearman entre rodada, gols do mandante, gols do visitante e arrecadação, e um histograma de cada variável, com a opção de colorir pelo resultado do mandante (`resultado_mandante`, a variável de classe da EDA). | Na barra lateral: escolha das variáveis, intervalo de cada uma e a opção de separar por resultado. |
| **Dashboard 2 · Indicadores do fator casa** | Duas análises. Com "Todos os clubes", o **fator casa geral** (cada partida vista pelo mandante). Com um clube escolhido, o **desempenho do clube** em casa, fora ou nos dois (cada partida vista pelo clube). Quatro indicadores com `st.metric` (partidas analisadas, vitórias, gols por partida e arrecadação mediana), comparados com todas as partidas ou com a média dos clubes nas mesmas condições. Três gráficos: resultados por temporada (vitória, empate e derrota), gols por partida por temporada e saldo de gols (por quanto vence ou perde). Também traz uma tabela por temporada. | Na barra lateral, no grupo "Dashboard 2": intervalo de temporadas, clube e "Jogos do clube" (em casa, fora ou os dois). Os intervalos da barra lateral também valem aqui. |

A justificativa de cada métrica do Dashboard 2 está em [entregas/justificativa-metricas.md](entregas/justificativa-metricas.md).

Observações sobre os dados:

- A **arrecadação** só foi registrada na temporada 2025 (380 das 9.165 partidas). Fora dela, o histograma e o indicador de arrecadação ficam sem dados, e o app avisa.
- O dataset não tem coluna de **temporada**, então ela é calculada a partir da data. A temporada 2020 terminou em fevereiro de 2021 (pandemia), por isso jogos de janeiro e fevereiro contam para o ano anterior.

Organização do código:

- `app.py`: a interface, com os dois dashboards em abas.
- `src/data_loader.py`: leitura do dataset tratado, com `@st.cache_data`.
- `src/metricas.py`: cálculos dos indicadores do Dashboard 2.
- `tests/`: testes automatizados dos cálculos e do app.

Para rodar o app e os testes (com o ambiente virtual ativo, na raiz do projeto; o Setup está logo abaixo):

```bash
streamlit run app.py
python -m unittest discover -s tests -v
```

## Setup

Requer **Python 3.11 a 3.15**. Confira a sua versão antes de começar:

| Sistema | Verificar versão |
| --- | --- |
| macOS / Linux | `python3 --version` |
| Windows | `py --version` |

### 1. Criar e ativar o ambiente virtual

O nome do comando do Python muda por sistema (em muitas máquinas `python` nem existe). Use a linha do seu sistema:

| Sistema | Criar | Ativar |
| --- | --- | --- |
| macOS / Linux | `python3 -m venv .venv` | `source .venv/bin/activate` |
| Windows (PowerShell) | `py -m venv .venv` | `.venv\Scripts\Activate.ps1` |
| Windows (cmd) | `py -m venv .venv` | `.venv\Scripts\activate.bat` |

Se você tem várias versões instaladas, escolha uma compatível, por exemplo `python3.12 -m venv .venv` (macOS/Linux) ou `py -3.12 -m venv .venv` (Windows).

Com o ambiente ativo, o terminal mostra `(.venv)` no início da linha. **A partir daqui os comandos são iguais em todos os sistemas**, porque dentro do venv `python` e `pip` sempre existem.

### 2. Instalar, configurar a IA e rodar

```bash
python -m pip install -r requirements.txt

# Skills de IA do Streamlit (ver seção "IA neste projeto")
streamlit skills --yes

streamlit run app.py
```

### Problemas comuns

- **`python: command not found` / `python` não é reconhecido:** use `python3` (macOS/Linux) ou `py` (Windows) só para criar o venv; depois de ativado, `python` funciona.
- **Linux (Debian/Ubuntu): `ensurepip is not available` ou `No module named venv`:** instale `sudo apt install python3-venv` (ou `python3.X-venv` para a sua versão).
- **Windows: "a execução de scripts foi desabilitada" ao ativar no PowerShell:** rode uma vez `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, ou use o cmd.
- **Python fora de 3.11–3.15:** instale uma versão compatível em [python.org](https://www.python.org/downloads/) e crie o venv com ela, como no exemplo acima.
- **Apareceu `ModuleNotFoundError` ou `streamlit: command not found`:** o venv provavelmente não está ativo. Ative de novo e confira o `(.venv)` no prompt.
- **Erro de certificado no `pip install` (macOS, Python do python.org):** rode `Install Certificates.command`, na pasta Python 3.X em Aplicativos.
- **Erro de SSL ou `DatasetNotFoundError` ao baixar o dataset no notebook (macOS, Python do python.org):** é o mesmo problema de certificado SSL. Rode `Install Certificates.command` e reinicie o kernel. Neste projeto o dataset vem do Kaggle, pelo `kagglehub` (já incluído no `requirements.txt`).

## Estrutura de dados: `data/raw` vs `data/clean`

- `data/raw/`: o dataset **bruto**, como foi baixado. Nunca é editado à mão.
- `data/clean/`: o dataset **já tratado**, exportado na última célula do notebook de EDA (ex.: `df.to_csv("data/clean/dataset.csv", index=False)`). O `app.py` lê **somente** desta pasta, via `src/data_loader.py`.

### O que vai para o Git

| Pasta | Versionada? | Por quê |
| --- | --- | --- |
| `data/raw/` | **Não** (só o `.gitkeep`) | O bruto pode ser grande ou ter dados sensíveis, e o app não o usa. |
| `data/clean/` | **Sim** | O Streamlit Community Cloud faz deploy a partir do GitHub e só enxerga o que está no repositório. Sem o CSV tratado no repo, o app funciona na sua máquina e **quebra no deploy**. |

### Antes de dar `git push` com o dado tratado

- **O dado é público ou pode ser compartilhado?** Se não for claramente público, use um **repositório privado** (o Community Cloud permite conectar repositórios privados ao autorizar o GitHub; confirme na hora do deploy). Nesse caso, dê acesso de leitura ao professor (como colaborador ou pela organização).
- **Dado sensível** (nomes, CPF, e-mail, telefone, localização exata etc.): remova ou anonimize na EDA, antes de exportar para `data/clean/`. Isso vale mesmo em repositório privado.
- **Tamanho:** o GitHub rejeita arquivos acima de **100 MB**. Se o CSV tratado for grande, reduza colunas e linhas na EDA ou exporte em Parquet (`df.to_parquet(...)`, exige `pyarrow`).
- **Lembre de commitar o arquivo:** confira com `git status` que `data/clean/dataset.csv` aparece como novo arquivo.

## Passo a passo

O passo a passo detalhado de cada aula (Aulas 21, 22 e 23), com pré-requisitos e objetivos, está em [ROTEIRO.md](ROTEIRO.md). Comece por ele depois do Setup.

O link do app publicado fica no início deste README, na seção "Meu projeto".

## IA neste projeto

Este projeto usa o **streamlit skills**: um conjunto de instruções (arquivos `SKILL.md`) que a ferramenta de IA lê para escrever código Streamlit seguindo boas práticas (estrutura de layout, cache, widgets, etc.).

**Como instalar:** depois do `pip install -r requirements.txt`, rode na raiz do projeto:

```bash
streamlit skills        # interativo
streamlit skills --yes  # sem confirmações
```

O comando cria *symlinks* para as skills que acompanham a sua instalação do Streamlit, então elas se atualizam sozinhas quando você atualiza o pacote. (A opção `--global` instala para todos os projetos, em vez de só este.)

**Onde fica instalado:**

- `.claude/skills/`: lido pelo Claude Code.
- `.agents/skills/`: lido pelo Gemini CLI, que já encontra essa pasta sozinho.

Essas pastas **não são versionadas** (ver `.gitignore`): os symlinks apontam para o seu ambiente virtual e não funcionam em outra máquina. Cada pessoa roda `streamlit skills` no próprio clone.

**Se você usa outra ferramenta** (ChatGPT, Copilot Chat, etc.): abra o `SKILL.md` correspondente em `.agents/skills/` e cole o conteúdo manualmente no início do chat, antes do seu pedido.

O uso de IA deve ser declarado conforme a seção abaixo.

## Pasta `prompts/`

A pasta [prompts/](prompts) guarda só o que é sobre **uso de IA**: o template de prompt para transformar o rascunho de layout em esqueleto de código e a **Declaração de Uso de IA** exigida pelo Plano de Ensino. Veja [prompts/README.md](prompts/README.md).

## Pasta `entregas/`

A pasta [entregas/](entregas) guarda os artefatos de entrega que não são sobre IA: os rascunhos de layout de cada dashboard (`.jpg` ou `.png`) e a justificativa das métricas do Dashboard 2. Veja [entregas/README.md](entregas/README.md) para o detalhe de cada arquivo e o checklist por aula. Não coloque esses arquivos no `.gitignore`.
