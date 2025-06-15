# Introdução ao Streamlit: Guia Completo para Desenvolvimento de Aplicações de Dados

## Sumário

1. [O que é Streamlit](#o-que-é-streamlit)
2. [Estrutura Básica de uma Aplicação](#estrutura-básica-de-uma-aplicação)
    - [Anatomia de um Script Streamlit](#anatomia-de-um-script-streamlit)
    - [Padrões de Organização](#padrões-de-organização)
    - [Gerenciamento de Estado](#gerenciamento-de-estado)
    - [Tratamento de Erros e Validação](#tratamento-de-erros-e-validação)
3. [Componentes Essenciais](#componentes-essenciais)
    - [Elementos de Texto e Markdown](#elementos-de-texto-e-markdown)
    - [Widgets de Entrada](#widgets-de-entrada)
    - [Exibição de Dados](#exibição-de-dados)
    - [Visualizações](#visualizações)
    - [Layout e Organização](#layout-e-organização)

---

## O que é Streamlit

- **Documentação Oficial**: [docs.streamlit.io](https://docs.streamlit.io)

Streamlit é uma biblioteca Python de código aberto que facilita a criação de aplicações web interativas para dados. Com ela, é possível transformar scripts Python em dashboards e interfaces elegantes sem precisar saber HTML, CSS ou JavaScript. Focada em ciência de dados, a ferramenta oferece componentes prontos para visualização, manipulação de dados e prototipagem rápida de modelos, tornando-se ideal para análises, demonstrações e relatórios interativos.

## Estrutura Básica de uma Aplicação

### Anatomia de um Script Streamlit

Uma aplicação Streamlit básica consiste em um script Python que utiliza a API do Streamlit para criar elementos de interface. A estrutura fundamental segue um padrão simples mas poderoso:

```python
import streamlit as st
import pandas as pd
import numpy as np

# Configuração da página
st.set_page_config(
    page_title="Minha Aplicação",
    page_icon="📊",
    layout="wide"
)

# Título principal
st.title("Sistema de Análise de Dados")

# Sidebar para controles
st.sidebar.header("Configurações")
opcao = st.sidebar.selectbox("Escolha uma opção:", ["Análise", "Visualização"])

# Conteúdo principal
if opcao == "Análise":
    st.header("Análise de Dados")
    # Lógica de análise aqui
else:
    st.header("Visualização")
    # Lógica de visualização aqui
```

### Padrões de Organização

Para aplicações mais complexas, é essencial adotar padrões de organização que promovam reutilização de código e facilitem manutenção. O padrão de funções modulares é particularmente efetivo:

```python
def load_data():
    """Carrega e processa dados"""
    return pd.read_csv("data.csv")

def create_sidebar():
    """Cria controles da sidebar"""
    st.sidebar.header("Filtros")
    return st.sidebar.multiselect("Categorias:", ["A", "B", "C"])

def main_content(data, filters):
    """Renderiza conteúdo principal"""
    filtered_data = data[data['category'].isin(filters)]
    st.dataframe(filtered_data)

def main():
    """Função principal da aplicação"""
    data = load_data()
    filters = create_sidebar()
    main_content(data, filters)

if __name__ == "__main__":
    main()
```

### Gerenciamento de Estado

O gerenciamento eficaz do estado é crucial para criar aplicações responsivas e eficientes. O Streamlit oferece várias estratégias para gerenciar estado:

```python
# Inicialização do estado
if 'data' not in st.session_state:
    st.session_state.data = load_initial_data()

if 'user_preferences' not in st.session_state:
    st.session_state.user_preferences = {
        'theme': 'light',
        'language': 'pt'
    }

# Uso do estado
data = st.session_state.data
preferences = st.session_state.user_preferences

# Atualização do estado
if st.button("Atualizar Dados"):
    st.session_state.data = fetch_new_data()
    st.rerun()
```

### Tratamento de Erros e Validação

Aplicações robustas devem incluir tratamento adequado de erros e validação de entrada. O Streamlit oferece componentes nativos para feedback ao usuário:

```python
try:
    uploaded_file = st.file_uploader("Escolha um arquivo CSV")
    
    if uploaded_file is not None:
        # Validação do arquivo
        if not uploaded_file.name.endswith('.csv'):
            st.error("Por favor, faça upload de um arquivo CSV válido.")
            st.stop()
        
        # Processamento do arquivo
        df = pd.read_csv(uploaded_file)
        
        # Validação dos dados
        if df.empty:
            st.warning("O arquivo está vazio.")
        elif len(df.columns) < 2:
            st.warning("O arquivo deve ter pelo menos 2 colunas.")
        else:
            st.success(f"Arquivo carregado com sucesso! {len(df)} linhas encontradas.")
            st.dataframe(df)
            
except Exception as e:
    st.error(f"Erro ao processar arquivo: {str(e)}")
    st.info("Verifique se o arquivo está no formato correto e tente novamente.")
```


## Componentes Essenciais

### Elementos de Texto e Markdown

O Streamlit oferece uma rica variedade de elementos para apresentação de texto e conteúdo formatado. Estes componentes formam a base da comunicação com usuários e estruturação de informações:

```python
# Títulos e cabeçalhos
st.title("Título Principal")
st.header("Cabeçalho de Seção")
st.subheader("Subcabeçalho")

# Texto formatado
st.markdown("**Texto em negrito** e *itálico*")
st.markdown("---")  # Linha horizontal

# Texto com código
st.code("print('Hello, Streamlit!')", language='python')

# Citações e alertas
st.info("Informação importante")
st.success("Operação realizada com sucesso")
st.warning("Atenção: verifique os dados")
st.error("Erro encontrado")
```

### Widgets de Entrada

Os widgets de entrada são fundamentais para criar interatividade. Cada widget retorna um valor que pode ser usado imediatamente na lógica da aplicação:

```python
# Entrada de texto
nome = st.text_input("Digite seu nome:")
descricao = st.text_area("Descrição:", height=100)

# Seletores
opcao = st.selectbox("Escolha uma opção:", ["A", "B", "C"])
multiplas = st.multiselect("Múltiplas escolhas:", ["X", "Y", "Z"])

# Controles numéricos
idade = st.number_input("Idade:", min_value=0, max_value=120, value=25)
valor = st.slider("Valor:", 0.0, 100.0, 50.0)

# Controles de data e tempo
data = st.date_input("Selecione uma data:")
hora = st.time_input("Selecione um horário:")

# Controles booleanos
ativo = st.checkbox("Ativo")
confirmacao = st.radio("Confirma?", ["Sim", "Não"])
```

### Exibição de Dados

O Streamlit excel na apresentação de dados estruturados, oferecendo componentes otimizados para diferentes tipos de conteúdo:

```python
# DataFrames interativos
df = pd.DataFrame(data)
st.dataframe(df)  # Tabela interativa
st.table(df.head())  # Tabela estática

# Métricas e KPIs
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Vendas", "R$ 1.234.567", "12%")
with col2:
    st.metric("Clientes", "1.234", "-2%")
with col3:
    st.metric("Conversão", "3.45%", "0.5%")

# JSON e dados estruturados
st.json({"chave": "valor", "lista": [1, 2, 3]})
```

### Visualizações

O framework suporta nativamente as principais bibliotecas de visualização Python:

```python
# Gráficos nativos do Streamlit
st.line_chart(df)
st.bar_chart(df)
st.area_chart(df)

# Matplotlib
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
ax.plot(x, y)
st.pyplot(fig)

# Plotly
import plotly.express as px
fig = px.scatter(df, x='x', y='y', color='category')
st.plotly_chart(fig)

# Mapas
st.map(df_with_coordinates)
```

### Layout e Organização

O controle de layout permite criar interfaces sofisticadas e bem organizadas:

```python
# Colunas
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.write("Coluna principal")
with col2:
    st.write("Coluna lateral")
with col3:
    st.write("Outra coluna")

# Containers e expansores
with st.container():
    st.write("Conteúdo agrupado")

with st.expander("Clique para expandir"):
    st.write("Conteúdo oculto")

# Abas
tab1, tab2, tab3 = st.tabs(["Aba 1", "Aba 2", "Aba 3"])
with tab1:
    st.write("Conteúdo da aba 1")

# Sidebar
st.sidebar.title("Controles")
st.sidebar.slider("Parâmetro:", 0, 100, 50)
```
---
