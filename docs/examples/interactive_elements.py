"""
Exemplo 1: Introdução a elementos no Streamlit

Para executar, digite no terminal: 
    cd docs/examples
    streamlit run interactive_elements.py

Conceitos:
- Widgets interativos avançados
- Estado de sessão (session state)
- Callbacks e reatividade
- Layouts responsivos
- Componentes customizados
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

def main():
    st.title("🎛️ Streamlit Título")
    st.markdown("---")
    
    # Inicializar estado da sessão
    inicializar_session_state()
    
    # Sidebar com navegação
    st.sidebar.title("🧭 Navegação")
    secao = st.sidebar.radio(
        "Escolha uma seção:",
        [
            "🎮 Widgets",
            "📊 Dashboard", 
            "🔄 Estado de Sessão",
            "📱 Layouts Responsivos",
            "⚡ Tempo Real"
        ]
    )
    
    if secao == "🎮 Widgets":
        secao_widgets()
    elif secao == "📊 Dashboard":
        secao_dashboard()
    elif secao == "🔄 Estado de Sessão":
        secao_session_state()
    elif secao == "📱 Layouts Responsivos":
        secao_layouts()
    else:
        secao_tempo_real()

def inicializar_session_state():
    """Inicializa variáveis do estado da sessão"""
    if 'contador' not in st.session_state:
        st.session_state.contador = 0
    if 'historico_clicks' not in st.session_state:
        st.session_state.historico_clicks = []
    if 'configuracoes' not in st.session_state:
        st.session_state.configuracoes = {
            'tema': 'Claro',
            'idioma': 'Português',
            'notificacoes': True
        }
    if 'dados_dashboard' not in st.session_state:
        st.session_state.dados_dashboard = gerar_dados_dashboard()

def secao_widgets():
    """Demonstra widgets interativos avançados"""
    
    st.header("🎮 Widgets Interativos")
    
    # Seção 1: Widgets básicos com callbacks
    st.subheader("1. Widgets com Feedback Dinâmico")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Slider com feedback visual
        valor_slider = st.slider(
            "Ajuste o valor:",
            min_value=0,
            max_value=100,
            value=50,
            help="Arraste para ver o feedback em tempo real"
        )
        
        # Feedback visual baseado no valor
        if valor_slider < 30:
            st.error(f"⚠️ Valor baixo: {valor_slider}")
        elif valor_slider < 70:
            st.warning(f"⚡ Valor médio: {valor_slider}")
        else:
            st.success(f"✅ Valor alto: {valor_slider}")
        
        # Barra de progresso dinâmica
        st.progress(valor_slider / 100)
    
    with col2:
        # Seletor múltiplo com validação
        opcoes_disponiveis = ['Python', 'JavaScript', 'Java', 'C++', 'Go', 'Rust']
        linguagens = st.multiselect(
            "Selecione suas linguagens favoritas:",
            opcoes_disponiveis,
            default=['Python']
        )
        
        if linguagens:
            st.info(f"🎯 Você selecionou {len(linguagens)} linguagem(ns)")
            for lang in linguagens:
                st.write(f"• {lang}")
        else:
            st.warning("⚠️ Selecione pelo menos uma linguagem")
    
    # Seção 2: Widgets condicionais
    st.subheader("2. Widgets Condicionais")
    
    tipo_analise = st.selectbox(
        "Tipo de análise:",
        ["Análise Simples", "Análise Avançada", "Análise Personalizada"]
    )
    
    if tipo_analise == "Análise Simples":
        st.info("📊 Configuração básica selecionada")
        metrica = st.radio("Métrica:", ["Média", "Mediana", "Moda"])
        
    elif tipo_analise == "Análise Avançada":
        st.info("🔬 Configuração avançada selecionada")
        col1, col2 = st.columns(2)
        with col1:
            metrica = st.selectbox("Métrica:", ["Média", "Mediana", "Desvio Padrão", "Variância"])
        with col2:
            intervalo_confianca = st.slider("Intervalo de Confiança:", 90, 99, 95)
        
    else:  # Análise Personalizada
        st.info("⚙️ Configuração personalizada selecionada")
        with st.expander("Configurações Avançadas"):
            metrica = st.text_input("Métrica personalizada:", "custom_metric")
            parametros = st.text_area("Parâmetros (JSON):", '{"param1": "value1"}')
            usar_cache = st.checkbox("Usar cache", True)
    
    # Seção 3: Formulários dinâmicos
    st.subheader("3. Formulário Dinâmico")
    
    with st.form("formulario_dinamico"):
        st.write("**Configuração de Relatório**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            tipo_relatorio = st.selectbox("Tipo:", ["Vendas", "Financeiro", "Operacional"])
            periodo = st.selectbox("Período:", ["Diário", "Semanal", "Mensal"])
        
        with col2:
            incluir_graficos = st.checkbox("Incluir gráficos", True)
            incluir_tabelas = st.checkbox("Incluir tabelas", True)
            incluir_resumo = st.checkbox("Incluir resumo executivo", False)
        
        with col3:
            formato_saida = st.radio("Formato:", ["PDF", "Excel", "PowerPoint"])
            enviar_email = st.checkbox("Enviar por email")
        
        if enviar_email:
            email_destinatario = st.text_input("Email do destinatário:")
        
        submitted = st.form_submit_button("🚀 Gerar Relatório")
        
        if submitted:
            st.success("✅ Relatório configurado com sucesso!")
            config = {
                "tipo": tipo_relatorio,
                "periodo": periodo,
                "graficos": incluir_graficos,
                "tabelas": incluir_tabelas,
                "resumo": incluir_resumo,
                "formato": formato_saida
            }
            st.json(config)

def secao_dashboard():
    """Dashboard dinâmico com múltiplas visualizações"""
    
    st.header("📊 Dashboard Dinâmico")
    
    # Controles do dashboard
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔄 Atualizar Dados"):
            st.session_state.dados_dashboard = gerar_dados_dashboard()
            st.rerun()
    
    with col2:
        auto_refresh = st.checkbox("Auto-refresh (5s)")
    
    with col3:
        mostrar_detalhes = st.checkbox("Mostrar detalhes", True)
    
    with col4:
        tema_grafico = st.selectbox("Tema:", ["plotly", "plotly_white", "plotly_dark"])
    
    # Auto-refresh
    if auto_refresh:
        time.sleep(5)
        st.session_state.dados_dashboard = gerar_dados_dashboard()
        st.rerun()
    
    df = st.session_state.dados_dashboard
    
    # KPIs principais
    st.subheader("📈 KPIs Principais")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_vendas = df['Vendas'].sum()
        st.metric(
            "Total de Vendas",
            f"R$ {total_vendas:,.2f}",
            delta=f"{np.random.randint(-10, 15)}%"
        )
    
    with col2:
        media_vendas = df['Vendas'].mean()
        st.metric(
            "Média de Vendas",
            f"R$ {media_vendas:,.2f}",
            delta=f"{np.random.randint(-5, 10)}%"
        )
    
    with col3:
        total_clientes = df['Cliente_ID'].nunique()
        st.metric(
            "Clientes Únicos",
            total_clientes,
            delta=f"{np.random.randint(0, 20)}"
        )
    
    with col4:
        ticket_medio = total_vendas / len(df)
        st.metric(
            "Ticket Médio",
            f"R$ {ticket_medio:,.2f}",
            delta=f"{np.random.randint(-8, 12)}%"
        )
    
    # Gráficos interativos
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de vendas por categoria
        vendas_categoria = df.groupby('Categoria')['Vendas'].sum().reset_index()
        fig_bar = px.bar(
            vendas_categoria,
            x='Categoria',
            y='Vendas',
            title="Vendas por Categoria",
            template=tema_grafico
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col2:
        # Gráfico de tendência temporal
        vendas_tempo = df.groupby('Data')['Vendas'].sum().reset_index()
        fig_line = px.line(
            vendas_tempo,
            x='Data',
            y='Vendas',
            title="Tendência de Vendas",
            template=tema_grafico
        )
        st.plotly_chart(fig_line, use_container_width=True)
    
    # Detalhes condicionais
    if mostrar_detalhes:
        st.subheader("📋 Detalhes dos Dados")
        
        # Filtros interativos
        col1, col2 = st.columns(2)
        
        with col1:
            categorias_selecionadas = st.multiselect(
                "Filtrar por categoria:",
                df['Categoria'].unique(),
                default=df['Categoria'].unique()
            )
        
        with col2:
            faixa_vendas = st.slider(
                "Faixa de vendas:",
                float(df['Vendas'].min()),
                float(df['Vendas'].max()),
                (float(df['Vendas'].min()), float(df['Vendas'].max()))
            )
        
        # Aplicar filtros
        df_filtrado = df[
            (df['Categoria'].isin(categorias_selecionadas)) &
            (df['Vendas'] >= faixa_vendas[0]) &
            (df['Vendas'] <= faixa_vendas[1])
        ]
        
        st.dataframe(df_filtrado, use_container_width=True)

def secao_session_state():
    """Demonstra o uso do estado de sessão"""
    
    st.header("🔄 Estado de Sessão")
    
    st.write("O estado de sessão permite manter dados entre interações do usuário.")
    
    # Contador simples
    st.subheader("1. Contador Simples")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("➕ Incrementar"):
            st.session_state.contador += 1
    
    with col2:
        if st.button("➖ Decrementar"):
            st.session_state.contador -= 1
    
    with col3:
        if st.button("🔄 Reset"):
            st.session_state.contador = 0
    
    st.metric("Contador atual:", st.session_state.contador)
    
    # Histórico de cliques
    st.subheader("2. Histórico de Ações")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📝 Registrar Ação"):
            timestamp = datetime.now().strftime("%H:%M:%S")
            st.session_state.historico_clicks.append(f"Ação registrada às {timestamp}")
    
    with col2:
        if st.button("🗑️ Limpar Histórico"):
            st.session_state.historico_clicks = []
    
    if st.session_state.historico_clicks:
        st.write("**Histórico de ações:**")
        for i, acao in enumerate(reversed(st.session_state.historico_clicks[-10:]), 1):
            st.write(f"{i}. {acao}")
    else:
        st.info("Nenhuma ação registrada ainda.")
    
    # Configurações persistentes
    st.subheader("3. Configurações Persistentes")
    
    with st.expander("⚙️ Configurações"):
        st.session_state.configuracoes['tema'] = st.selectbox(
            "Tema:",
            ["Claro", "Escuro", "Auto"],
            index=["Claro", "Escuro", "Auto"].index(st.session_state.configuracoes['tema'])
        )
        
        st.session_state.configuracoes['idioma'] = st.selectbox(
            "Idioma:",
            ["Português", "Inglês", "Espanhol"],
            index=["Português", "Inglês", "Espanhol"].index(st.session_state.configuracoes['idioma'])
        )
        
        st.session_state.configuracoes['notificacoes'] = st.checkbox(
            "Receber notificações",
            value=st.session_state.configuracoes['notificacoes']
        )
    
    st.write("**Configurações atuais:**")
    st.json(st.session_state.configuracoes)

def secao_layouts():
    """Demonstra layouts responsivos"""
    
    st.header("📱 Layouts Responsivos")
    
    # Layout em colunas
    st.subheader("1. Layout em Colunas")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.write("**Coluna Principal (50%)**")
        st.area_chart(np.random.randn(20, 3))
    
    with col2:
        st.write("**Coluna Lateral (25%)**")
        st.metric("Métrica 1", "123")
        st.metric("Métrica 2", "456")
    
    with col3:
        st.write("**Coluna Lateral (25%)**")
        st.metric("Métrica 3", "789")
        st.metric("Métrica 4", "012")
    
    # Layout com containers
    st.subheader("2. Containers e Expansores")
    
    with st.container():
        st.write("**Container Principal**")
        
        with st.expander("📊 Gráficos"):
            tab1, tab2, tab3 = st.tabs(["Linha", "Barra", "Pizza"])
            
            with tab1:
                st.line_chart(np.random.randn(20, 3))
            
            with tab2:
                st.bar_chart(np.random.randn(20, 3))
            
            with tab3:
                data = pd.DataFrame({
                    'Categoria': ['A', 'B', 'C', 'D'],
                    'Valores': np.random.randint(10, 100, 4)
                })
                fig = px.pie(data, values='Valores', names='Categoria')
                st.plotly_chart(fig, use_container_width=True)
    
    # Layout em abas
    st.subheader("3. Layout em Abas")
    
    tab1, tab2, tab3 = st.tabs(["📈 Análise", "📊 Dados", "⚙️ Configurações"])
    
    with tab1:
        st.write("Conteúdo da análise...")
        st.line_chart(np.random.randn(30, 2))
    
    with tab2:
        st.write("Tabela de dados...")
        df_exemplo = pd.DataFrame(np.random.randn(10, 4), columns=['A', 'B', 'C', 'D'])
        st.dataframe(df_exemplo)
    
    with tab3:
        st.write("Configurações do sistema...")
        st.slider("Parâmetro 1", 0, 100, 50)
        st.selectbox("Parâmetro 2", ["Opção 1", "Opção 2", "Opção 3"])

def secao_tempo_real():
    """Demonstra elementos em tempo real"""
    
    st.header("⚡ Elementos em Tempo Real")
    
    # Placeholder para atualizações
    placeholder = st.empty()
    
    col1, col2 = st.columns(2)
    
    with col1:
        iniciar_simulacao = st.button("▶️ Iniciar Simulação")
        parar_simulacao = st.button("⏹️ Parar Simulação")
    
    with col2:
        velocidade = st.slider("Velocidade (segundos):", 0.1, 2.0, 1.0)
    
    if iniciar_simulacao:
        st.session_state.simulacao_ativa = True
    
    if parar_simulacao:
        st.session_state.simulacao_ativa = False
    
    # Simulação em tempo real
    if st.session_state.get('simulacao_ativa', False):
        for i in range(10):
            with placeholder.container():
                # Dados simulados em tempo real
                dados_tempo_real = pd.DataFrame({
                    'Tempo': pd.date_range('now', periods=20, freq='1min'),
                    'Valor': np.random.randn(20).cumsum()
                })
                
                # Métricas em tempo real
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Valor Atual", f"{dados_tempo_real['Valor'].iloc[-1]:.2f}")
                
                with col2:
                    variacao = dados_tempo_real['Valor'].iloc[-1] - dados_tempo_real['Valor'].iloc[-2]
                    st.metric("Variação", f"{variacao:.2f}")
                
                with col3:
                    st.metric("Máximo", f"{dados_tempo_real['Valor'].max():.2f}")
                
                # Gráfico em tempo real
                fig = px.line(
                    dados_tempo_real,
                    x='Tempo',
                    y='Valor',
                    title="Dados em Tempo Real"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Barra de progresso
                st.progress((i + 1) / 10)
                
                time.sleep(velocidade)
        
        st.session_state.simulacao_ativa = False
        st.success("✅ Simulação concluída!")

def gerar_dados_dashboard():
    """Gera dados simulados para o dashboard"""
    np.random.seed(int(time.time()) % 1000)  # Seed baseado no tempo para variação
    
    dates = pd.date_range('2023-01-01', periods=30, freq='D')
    
    df = pd.DataFrame({
        'Data': np.random.choice(dates, 100),
        'Cliente_ID': np.random.randint(1000, 9999, 100),
        'Categoria': np.random.choice(['Eletrônicos', 'Roupas', 'Casa', 'Livros'], 100),
        'Vendas': np.random.uniform(50, 1000, 100),
        'Quantidade': np.random.randint(1, 10, 100)
    })
    
    return df.sort_values('Data')

if __name__ == "__main__":
    main()

