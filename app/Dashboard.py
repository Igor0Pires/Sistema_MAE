import gspread as gs
import streamlit as st
import pandas as pd
import time

st.markdown(
    '''
    <style>
    #root > div:nth-child(1) > div.withScreencast > div > div > section.stMain.st-emotion-cache-bm2z3a.en45cdb1 > div.stMainBlockContainer.block-container.st-emotion-cache-zy6yx3.en45cdb4 > div > div > div.st-emotion-cache-1khiglm.e1lln2w84 {
        padding: calc(var(--spacing) * 6);
        background: var(--primary-color);
    }
    .saudacao {
        font-weight: var(--font-weight-bold) !important;
        font-size: var(--text-2xl) !important;
        padding: 0rem 0px 0.5rem !important;
        color: var(--primary-foreground-color) !important;
    }
    
    p.apresent {
        color: #C8C8C8;
    }

    </style>

    ''',
unsafe_allow_html=True
)
try:
    auth = gs.api_key(st.secrets["google"]["API-KEY"])
    sheet = auth.open_by_key(st.secrets["sheets"]["code"])
    pagina_presenca = sheet.sheet1.get_all_records()
    df_presenca = pd.DataFrame(pagina_presenca)

    hour = time.strftime("%H:%M")

    mensagem = """Bom dia!""" * (hour < "12:00" and hour >= "05:00") + """Boa tarde!""" * (hour < "18:00" and hour >= "12:00") + """Boa noite!""" * (hour < "05:00" or hour >= "18:00")

    with st.container(height=100):
        st.markdown(
    f"""
        <h2 class="saudacao">{mensagem}</h2>
        <p class="apresent">Como a MAE pode te ajudar hoje?</p>

    """,
    unsafe_allow_html=True
        )

    # Processing the data
    df_presenca["Data"] = pd.to_datetime(df_presenca["Data"], format="%d/%m/%Y")
    df_presenca["Presença"] = 1

    frequencia = df_presenca.groupby("Nome")["Presença"].sum().reset_index()
    frequencia = frequencia.rename(columns={"Presença": "Frequência"})
    frequencia = frequencia.sort_values(by="Frequência", ascending=False)

    # Displaying the data
    st.subheader("Frequência de Presença")
    st.dataframe(frequencia, use_container_width=True)

    st.subheader("Destaques")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Mais presente", frequencia.iloc[0]["Nome"], f"{int(frequencia.iloc[0]['Frequência'])} presenças")
    with col2:
        media = frequencia["Frequência"].mean()
        st.metric("Média de presença", f"{media:.1f} eventos")

    st.subheader("Eventos até agora")
    st.dataframe(df_presenca.sort_values(by="Data", ascending=False), use_container_width=True)



except Exception as e:
    st.error(e)