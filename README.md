# Dashboard de Análise do Catálogo da Netflix

Aplicação **low code** desenvolvida em **Streamlit** como parte do Projeto Integrador do 2º semestre do curso de Analise e Desenvolvimento de Sistemas — Senac EAD.

# Objetivo

Permitir a análise interativa do catálogo da Netflix, com indicadores sobre filmes, séries, países produtores, classificações indicativas, evolução do catálogo ao longo dos anos e gêneros mais frequentes.

# Tecnologias utilizadas

- **Python 3.10+**
- **Streamlit** — framework low code para construção da interface web
- **Pandas** — manipulação e transformação dos dados
- **Plotly Express** — visualizações interativas

# Estrutura do projeto

```
pi_netflix/
├── app.py                 # Aplicação principal Streamlit
├── netflix_titles.csv     # Dataset (baixar do Kaggle)
├── requirements.txt       # Dependências
└── README.md              # Este arquivo
```

# Como executar localmente

1. Clonar o repositório
   ```bash
   git clone <url-do-repositorio>
   cd pi_netflix
   ```
2. Baixar o dataset `netflix_titles.csv` em https://www.kaggle.com/datasets/shivamb/netflix-shows e colocar na raiz do projeto.
3. Instalar as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Executar a aplicação:
   ```bash
   streamlit run app.py
   ```

A aplicação abrirá no navegador em `http://localhost:8501`.

# Publicação no Streamlit Community Cloud

A aplicação está publicada em: `https://<seu-usuario>-pi-netflix.streamlit.app`

# Autor

Projeto desenvolvido por **Wagner R De Souza** — Senac EAD, 2026.
[README.md](https://github.com/user-attachments/files/27863141/README.md)
