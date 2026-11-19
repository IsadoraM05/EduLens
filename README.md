# EduLens — Infraestrutura escolar em São Paulo

## Objetivo

O EduLens compara a presença de recursos de infraestrutura nas escolas públicas paulistas entre 2023 e 2025. A pergunta orientadora é: **em quais recursos e territórios a cobertura avançou, recuou ou permaneceu desigual?** O painel pode apoiar a identificação de recortes que merecem investigação e planejamento público; não mede a qualidade do serviço nem define, sozinho, a alocação de recursos.

O IDEB entra como análise complementar. Os resultados são associativos e não permitem afirmar que a infraestrutura causou mudanças no desempenho escolar.

## Recorte e dados

- Escolas públicas de São Paulo que oferecem anos finais do ensino fundamental e aparecem nos dois Censos Escolares.
- Coorte pareada: **5.445 escolas**.
- Escolas com IDEB numérico em 2023 e 2025: **4.437**.
- Pareamento pelo código `CO_ENTIDADE` do Censo, harmonizado com `ID_ESCOLA` no arquivo do IDEB.
- Localização e rede administrativa são referenciadas em 2023.
- A comparação usa duas edições, 2023 e 2025; não representa uma série anual.

### Arquivos de origem

Coloque os arquivos abaixo em `Dados/Brutos/`. O grupo os compartilha pelo [Drive do projeto](https://drive.google.com/file/d/1waGbFi3OLdM5zsVgWNjmzyv-BOb7qK0v/view?usp=sharing):

- `Tabela_Escola_2025_V2.csv` — Censo Escolar 2025.
- `microdados_ed_basica_2023.csv` — Censo Escolar 2023.
- `divulgacao_anos_finais_escolas_2025.xlsx` — resultados observados do IDEB para 2023 e 2025.

Os dados brutos e tratados estão excluídos do Git pelo `.gitignore`. Para reproduzir o fluxo em outro computador, obtenha as fontes compartilhadas e gere as bases tratadas novamente.

## Como executar

Python **3.13 é a versão usada no desenvolvimento**. No PowerShell, abra a pasta do projeto e instale as dependências:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

No VS Code, selecione o kernel `.venv` (com `ipykernel`) e execute:

1. `Notebooks/01_exploracao_dados.ipynb` — lê e trata os microdados, pareia as escolas e integra o IDEB. Gera `Dados/Tratados/painel_escolas_sp_2023_2025_com_ideb.csv`.
2. `Notebooks/02_teste_hipotese.ipynb` — usa a base integrada para cinco comparações de transições de infraestrutura com `ΔIDEB` e um teste de associação entre localização e expansão da internet para alunos.
3. `Notebooks/03_preparacao_dashboard.ipynb` — prepara as tabelas do dashboard a partir da base integrada.

Os notebooks 02 e 03 dependem da base criada pelo 01. Para abrir apenas o dashboard, execute o notebook 01 e depois o 03; o notebook 02 documenta a análise estatística complementar.

Inicie o app na raiz do projeto:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Abra `http://localhost:8501`. Para encerrar o servidor, volte ao terminal e pressione `Ctrl+C`. A primeira execução do notebook 01 pode levar mais tempo por ler os arquivos brutos; caches em `Dados/Tratados/` aceleram execuções posteriores.

## Dashboard

O app lê `Dados/Tratados/dashboard_infraestrutura_escolas_long.csv`. Permite filtrar categoria, indicador, localização, rede administrativa e município. As telas apresentam um panorama, o ranking e a tabela municipal, além do detalhe por escola e exportação do recorte em CSV. O filtro territorial usa as características de 2023; o mínimo de escolas por município é ajustável.

Os **14 indicadores** estão agrupados em serviços básicos, espaços de aprendizagem, conectividade e equipamentos para alunos. Para cada ano, a cobertura é a proporção de registros válidos com valor 1; valores ausentes não entram no denominador. A variação é expressa em pontos percentuais. Biblioteca e sala de leitura são indicadores separados.

As transições entre os anos são: `0→1` (ganhou registro), `1→0` (perdeu registro), `0→0` (permaneceu sem o recurso) e `1→1` (manteve o recurso). Quando falta o valor em qualquer ano, a transição é classificada como sem comparação completa. A versão atual apresenta rankings e tabelas; uma visualização em mapa requer dados de limites geográficos municipais e ainda não está incluída.

O notebook 03 também gera `Dados/Tratados/dashboard_infraestrutura_municipios.csv`, com agregações por município, localização e rede. Essa tabela serve para análises e exportações; o app atual monta os recortes municipais a partir da tabela detalhada.

## Resultados exploratórios atuais

- Nos cinco testes de Mann–Whitney que comparam `ΔIDEB` entre escolas que passaram de `0→1` e as que permaneceram em `0→0`, não houve evidência estatística suficiente após o ajuste conjunto de Holm aplicado aos seis testes.
- Entre as escolas sem internet disponível aos alunos em 2023, ganharam acesso **40 de 72 escolas rurais (55,6%)** e **372 de 1.138 urbanas (32,7%)**. A diferença permaneceu estatisticamente significativa após o ajuste de Holm conjunto dos seis testes (`p-Holm = 0,0009`). É uma associação exploratória; não indica que a localização causou a expansão.

## Limitações

- A análise longitudinal observa somente dois anos e escolas presentes nas duas edições; a análise de IDEB inclui apenas escolas com valores numéricos nos dois anos.
- Os testes não isolam outros fatores que podem influenciar o IDEB ou a expansão dos recursos.
- A equivalência das definições dos indicadores entre as edições do Censo precisa ser conferida nos dicionários oficiais antes da interpretação final.
- `1→0` indica perda de registro entre edições e pode refletir mudança de preenchimento ou definição, além de mudança física na escola.
- A coorte pareada não explica, por si só, por que 93 escolas aparecem apenas em 2023 e 58 apenas em 2025 no recorte inicial.

## Arquivos principais

```text
app.py
requirements.txt
Notebooks/
  01_exploracao_dados.ipynb
  02_teste_hipotese.ipynb
  03_preparacao_dashboard.ipynb
Dados/
  Brutos/       # fontes; não versionadas
  Tratados/     # bases intermediárias e saídas; não versionadas
```

## Entrega técnica

Para montar o ZIP técnico:

- Salve os notebooks executados com as células e resultados visíveis.
- Inclua `Dados/Tratados/painel_escolas_sp_2023_2025_com_ideb.csv`, usado pelos notebooks 02 e 03.
- Inclua `Dados/Tratados/dashboard_infraestrutura_escolas_long.csv`, lido pelo `app.py`, e a tabela agregada `dashboard_infraestrutura_municipios.csv` como saída complementar do notebook 03.
- Para permitir o reprocessamento completo do notebook 01, inclua também em `Dados/Brutos/` os três arquivos de origem listados acima. Se uma base for grande demais para anexar, inclua no ZIP um TXT com seu link de download direto, conforme a orientação da disciplina.
- Inclua `app.py` e `requirements.txt` para que o painel possa ser reproduzido.

Como `Dados/` é ignorada pelo Git, copie manualmente os CSVs e as fontes necessárias para o ZIP.
