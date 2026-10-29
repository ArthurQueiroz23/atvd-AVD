# Justificativa das métricas — Dashboard 2

O Dashboard 2 responde a uma pergunta que já aparecia na minha EDA: **quanto o mando de campo pesa no resultado das partidas do Brasileirão?** Na EDA eu criei a variável de classe `resultado_mandante` (o mandante venceu ou não) e vi que ela se relaciona com o estado do mandante. Aqui eu transformei essa ideia em indicadores que dá para ler sem precisar interpretar histograma ou matriz de correlação.

O público-alvo que considerei são **torcedores e jornalistas esportivos** que acompanham o campeonato e querem números simples para comparar clubes e temporadas. A arrecadação também interessa a quem acompanha a parte financeira dos clubes.

Os indicadores são calculados sobre um **recorte** definido por três controles, todos na barra lateral:

- **Temporadas** (intervalo de 2003 a 2025, que pode ser uma temporada só), no grupo "Dashboard 2";
- **Clube mandante** (todos ou um clube específico; com um clube escolhido, entram só os jogos em que ele foi mandante), também no grupo "Dashboard 2";
- os **intervalos** de rodada, gols e arrecadação, que valem para os dois dashboards.

Cada indicador mostra também a diferença em relação a **todas as 9.165 partidas do dataset**, para o leitor saber se o recorte está acima ou abaixo do normal. Os cálculos ficam em `src/metricas.py` e têm testes em `tests/test_metricas.py`.

Uma observação sobre as temporadas: o dataset não tem uma coluna de temporada, então eu a derivei da data. A temporada 2020 foi adiada pela pandemia e terminou em fevereiro de 2021. Por isso, os jogos de janeiro e fevereiro contam para o ano anterior, e assim cada temporada a partir de 2006 fica com 380 partidas.

## Métrica 1: Partidas analisadas
- **Variável:** contagem de linhas do recorte (cada linha do dataset é uma partida).
- **Como é calculada:** número de partidas que passam pelos filtros.
- **O que mede:** o tamanho da amostra usada nos outros indicadores.
- **Por que foi escolhida:** um percentual calculado com 19 jogos (um clube em uma temporada) não tem o mesmo peso de um calculado com 9 mil. Mostrar a contagem evita que alguém leia uma variação pequena como se fosse uma tendência. Quando o recorte tem menos de 30 partidas, o app mostra um aviso.
- **Público-alvo:** qualquer pessoa usando o dashboard.
- **Qual decisão pode ser apoiada por essa métrica?** Decidir se vale a pena tirar conclusões do recorte ou se é melhor ampliar o período antes de comparar.
- **O que comunica ao público-alvo:** "estes números vêm de tantas partidas".
- **Limitações:** não é um indicador de desempenho, só de contexto.

## Métrica 2: Vitórias do mandante
- **Variável:** `resultado_mandante` (variável de classe criada na EDA: `Vitoria_Mandante` ou `Nao_Venceu`).
- **Como é calculada:** partidas com `Vitoria_Mandante` ÷ total de partidas do recorte, em %. A comparação com o dataset completo é em pontos percentuais (p.p.).
- **O que mede:** com que frequência o time da casa vence.
- **Por que foi escolhida:** é a forma mais direta de medir o fator casa, e usa exatamente a variável que eu estudei na EDA. No dataset inteiro, o mandante vence 49,6% das partidas e perde 23,9% (vitórias do visitante); o resto, 26,4%, são empates.
- **Público-alvo:** torcedores e jornalistas esportivos.
- **Qual decisão pode ser apoiada por essa métrica?** Um jornalista pode checar se a ideia de que "jogar em casa é meio caminho andado" vale para o recorte que está comentando. Um torcedor pode ver se o seu clube aproveita o mando melhor ou pior que a média do campeonato (é o que a diferença em p.p. mostra).
- **O que comunica ao público-alvo:** "o mandante ganhou X% dos jogos, Y p.p. acima ou abaixo do histórico".
- **Limitações:** junta empate e derrota no mesmo grupo (é assim que a variável da EDA foi definida). Por isso o gráfico de resultados separa as três situações. O indicador também não explica o motivo da vantagem: torcida, viagem e força dos elencos ficam misturados.

## Métrica 3: Gols por partida
- **Variáveis:** `mandante_Placar` e `visitante_Placar`.
- **Como é calculada:** média de (gols do mandante + gols do visitante) nas partidas do recorte. A comparação é com a média do dataset completo (2,56 gols por partida).
- **O que mede:** se os jogos do recorte costumam ter muitos ou poucos gols.
- **Por que foi escolhida:** completa o indicador de vitórias, porque mostra o tipo de jogo e não só quem ganhou. Na EDA vi que os placares se concentram em valores baixos e que poucos jogos têm placar alto. A média por partida é a forma mais comum de resumir isso no futebol.
- **Público-alvo:** torcedores e jornalistas esportivos.
- **Qual decisão pode ser apoiada por essa métrica?** Comparar temporadas e clubes antes de afirmar que o campeonato "está com menos gols". Por exemplo, de 2003 a 2009 todas as temporadas tiveram mais de 2,7 gols por partida, e de 2012 a 2025 todas ficaram abaixo de 2,6.
- **O que comunica ao público-alvo:** "neste recorte saem X gols por jogo, mais ou menos que o normal do campeonato".
- **Limitações:** a média esconde a distribuição (um 5 x 4 e um 0 x 0 dão média 4,5). A distribuição dos placares fica no Dashboard 1.

## Métrica 4: Arrecadação mediana
- **Variável:** `arrecadacao` (renda da partida, em R$).
- **Como é calculada:** mediana da arrecadação das partidas do recorte que têm esse valor registrado. A comparação é com a mediana de todas as partidas com registro (R$ 996 mil).
- **O que mede:** quanto um jogo do recorte costuma arrecadar.
- **Por que foi escolhida:** é a única variável financeira do dataset. Usei a mediana e não a média porque, como mostrei na EDA, a arrecadação é assimétrica à direita (skewness de 1,29): poucos jogos com renda muito alta puxam a média para cima. A média é R$ 1,36 milhão, mas metade dos jogos arrecadou menos de R$ 996 mil.
- **Público-alvo:** jornalistas e pessoas que acompanham as finanças dos clubes.
- **Qual decisão pode ser apoiada por essa métrica?** Comparar a renda típica por jogo de um clube jogando em casa com a do campeonato, por exemplo para contextualizar uma notícia sobre bilheteria.
- **O que comunica ao público-alvo:** "um jogo típico deste recorte arrecadou R$ X".
- **Limitações:** a arrecadação só existe na **temporada 2025** (380 das 9.165 partidas). Fora dela o indicador aparece como "–" e o app explica o motivo. Os valores também não estão corrigidos pela inflação, mas como são todos do mesmo ano isso não atrapalha a comparação.

## Gráficos do Dashboard 2

- **Resultado das partidas por temporada** (barras empilhadas em 100%): mostra, para cada temporada, a parte de vitórias do mandante, empates e derrotas do mandante (vitórias do visitante), calculadas pelo placar de cada partida. As três partes somam o total de jogos da temporada no recorte (isso é conferido nos testes), e o texto acima do gráfico traz a divisão do recorte inteiro. Complementa a Métrica 2: o indicador mostra só as vitórias, e o gráfico mostra também empates e derrotas e se isso mudou de uma temporada para outra (no dataset completo, as vitórias do mandante variam de 43,9% em 2017 a 54,7% em 2008). Clicar numa cor da legenda destaca esse resultado, e um novo clique volta a mostrar todos.
- **Gols por partida por temporada** (linha): complementa a Métrica 3 mostrando a evolução ano a ano, com uma linha tracejada na média do recorte. Quando o clube escolhido não estava na Série A em alguma temporada, a linha fica interrompida em vez de ligar anos distantes.
- **Por quanto o mandante vence ou perde** (barras por saldo de gols): mostra a parte das partidas do recorte que terminou com cada saldo de gols do mandante, de "−3 ou menos" a "+3 ou mais", com as barras coloridas pelo resultado. Os traços dourados mostram o mesmo percentual em todas as partidas, para comparar o recorte com o histórico.
  - **Por que este gráfico:** ele junta o desempenho do mandante em campo (o saldo de gols) com o resultado final, o que os outros dois não mostram. Dá para ver, por exemplo, se um clube vence em casa por margens maiores que a média ou se perde mais jogos por um gol. No dataset completo, 26,0% das partidas terminam com vitória do mandante por um gol e 9,6% com vitória por três ou mais.
  - **Por que não outro gráfico por temporada:** um segundo gráfico de vitórias, empates e derrotas por temporada repetiria o primeiro.
  - **Limitação:** o gráfico soma as temporadas do recorte. Para comparar períodos, é preciso mudar o filtro de temporadas.
- **Tabela "Ver os números por temporada"**: traz os mesmos números dos gráficos por temporada, para quem prefere ler os valores ou não consegue distinguir as cores.

As cores seguem a identidade do app: verde-limão para a vitória do mandante (a mesma cor do Dashboard 1), cinza para o empate e azul para a derrota do mandante. O azul foi escolhido depois de testar a paleta para daltonismo: um vermelho, que seria a escolha óbvia, ficava quase igual ao cinza para quem tem protanopia. O dourado marca referências (a média no gráfico de gols e o histórico no gráfico de saldo).
