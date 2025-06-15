import streamlit as st

st.set_page_config(page_title = "MAE", layout = "wide")
with st.sidebar:
    st.markdown(
    """
    <style>
    :root {
        --primary-foreground-color: oklch(98.5% 0 0);
        --primary-color: oklch(20.5% 0 0);
        --radius: .625rem;
        --spacing: 0.25rem;
        --font-weight-bold: 700;
        --text-2xl: 1.5rem;
        --radius: .625rem;
        }

    .st-emotion-cache-jx6q2s {
        flex-direction: column;
        display: flex;
    }/* Sidebar container */

    .st-emotion-cache-1xgtwnd {
        display: none;
    }/* Hide the default sidebar padding */

    .st-emotion-cache-79elbk {
        order: 2;
    }/* Sidebar Navigation Container */

    .st-emotion-cache-1b4num7 {
        order: 1;
        padding-top: 0px;
        padding-left: calc(2px + .7rem);
    }/* Sidebar title container */

    .title-sidebar {
        position: absolute;
        top: 0;
        font-size: 1.2rem !important;
        display: flex;
    }/* Sidebar title */

    .M-style {
        color: var(--primary-foreground-color);
        background-color: var(--primary-color);
        border-radius: calc(var(--radius) - 2px);
        width: calc(var(--spacing) * 6);
        justify-content: center;
        display: flex;
        margin-right: 0.5rem;
        height: calc(var(--spacing) -2px);
    }

    </style>
    <h1 class="title-sidebar"><span class="M-style">M</span> MAE </h1>
    """,
    
    unsafe_allow_html=True
    )
    

pg = st.navigation([st.Page("Dashboard.py", icon=":material/dashboard:"), st.Page("Ativos.py", icon=":material/person:"), st.Page("Projetos.py", icon=":material/calendar_today:"), st.Page("Relatorios.py", icon=":material/equalizer:"), st.Page("Configuracoes.py", icon=":material/settings:")])

st.markdown("""
            <style>

            .main-title {
                position: fixed;
                z-index: 999991;
                top: 0;
                padding: 1.25rem 0px 1rem !important;
                font-size: 1.2rem !important;
                left: 17rem;
            }

            </style>

            <h1 class="main-title">MAE</h1>

        """, 
        unsafe_allow_html=True
        )



pg.run()