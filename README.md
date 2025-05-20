```markdown
# FarmTech Solutions — Pipeline de Previsão de Fertilizantes

**Autor:** Rafael Lima Jordão (RM 563855)  
**Data:** 20/05/2025

---

## Visão Geral

Este projeto implementa um pipeline completo de Ciência de Dados para prever o tipo de fertilizante ideal, a partir de variáveis de solo e clima. O fluxo abrange:

1. Importação e limpeza dos dados brutos  
2. Análise exploratória (EDA) com gráficos e estatísticas descritivas  
3. Cálculo do perfil ideal do solo/clima e comparação com fertilizantes selecionados  
4. Feature engineering (label encoding, one-hot, normalização)  
5. Treinamento e avaliação de seis modelos distintos  
6. Comparação final de acurácias e seleção de modelo  
7. Automação via script Python (`main.py`)

---

## Estrutura de Diretórios

```

PythonProject3/
├── data/
│   ├── Atividade\_Cap\_14\_produtos\_agricolas.csv
│   └── fertilizer\_prediction.csv
│
├── notebooks/
│   └── RafaelLimaJordao\_RM563855\_fase3\_cap14.ipynb
│
├── src/
│   ├── **init**.py
│   ├── data\_processing.py
│   ├── feature\_engineering.py
│   ├── modeling.py
│   └── visualization.py
│
├── main.py
├── requirements.txt
├── .gitignore
└── README.md

````

---

## Configuração do Ambiente

1. **Clone o repositório**  
   ```bash
   git clone https://github.com/rafaelljordao/PythonProject-Farmtech-Fase3.git
   cd PythonProject-Farmtech-Fase3
````

2. **Crie e ative um ambiente virtual**

   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS / Linux
   source .venv/bin/activate
   ```

3. **Instale as dependências**

   ```bash
   pip install -r requirements.txt
   ```

---

## Execução

### 1. Via Jupyter Notebook

* Inicie o Jupyter Lab/Notebook:

  ```bash
  jupyter lab
  ```
* Abra e execute todas as células em
  `notebooks/RafaelLimaJordao_RM563855_fase3_cap14.ipynb`.

### 2. Via Script Python

* Execute no terminal:

  ```bash
  python main.py
  ```
* O script irá:

  1. Carregar e limpar os dados (`fertilizer_prediction.csv`)
  2. Gerar gráficos de EDA e perfil ideal
  3. Preparar features, treinar seis modelos e plotar comparação de acurácias
  4. Imprimir as acurácias finais no console

---

## Observação sobre reprodutibilidade

> Os resultados de acurácia obtidos interativamente no notebook (4×100 %, 95 %, 90 %) podem diferir daqueles gerados ao executar `main.py` (80 %, 25 %, 90 %, etc.). Isso ocorre porque o particionamento (train/test split) no notebook e no script não usam exatamente os mesmos índices ou aleatoriedades.
>
> Para avaliações mais estáveis em produção, recomenda-se usar validação cruzada (k-fold) ou “congelar” o split salvando e recarregando os índices usados no notebook.

---

## Descrição dos Módulos (`src/`)

* **`data_processing.py`**

  * `load_and_clean(path)` — lê o CSV, remove duplicatas e faz strip nos nomes de coluna.
  * `prepare_profile(df)` — calcula as médias globais e por fertilizante para gerar o perfil ideal.

* **`feature_engineering.py`**

  * `prepare_features(df)` — label encoding do target, one-hot das variáveis categóricas, split treino/teste e normalização.

* **`modeling.py`**

  * `train_all_models(X_train, y_train, X_test, y_test)` — treina e avalia seis algoritmos:

    * Regressão Logística
    * K-Nearest Neighbors
    * Decision Tree
    * Random Forest
    * Support Vector Machine
    * XGBoost

* **`visualization.py`**

  * Funções para plotar boxplot, countplot, heatmap de correlação, perfil ideal vs. fertilizantes e comparação de acurácias.

---

## Principais Resultados

* **Perfil Ideal Geral** das variáveis numéricas e comparação com fertilizantes **Urea**, **DAP** e **28-28**.
* **Modelos**: quatro alcançaram 100 % de acurácia (Regressão Logística, Decision Tree, SVM, XGBoost); Random Forest 95 %; KNN 90 %.
* **Modelo recomendado**: **XGBoost** (robusto, alta acurácia e interpretabilidade via importância de features).

---

## Próximos Passos

* Aplicar validação cruzada (k-fold) para confirmar estabilidade.
* Realizar tuning de hiperparâmetros (GridSearch/RandomizedSearch).
* Explorar explicabilidade (SHAP, feature importances).
* Coletar mais dados para reduzir overfitting.

---

## Como Contribuir

1. Faça um fork deste repositório.
2. Crie uma branch:

   ```bash
   git checkout -b feature/minha-ideia
   ```
3. Implemente e teste suas alterações.
4. Abra um Pull Request detalhando suas contribuições.

---

## Licença

Este é um projeto acadêmico da FIAP, desenvolvido como parte das atividades da disciplina de Modelagem de IA da FarmTech Solutions (empresa fictícia).  
Uso e redistribuição são permitidos apenas para fins educacionais, com crédito ao autor.

