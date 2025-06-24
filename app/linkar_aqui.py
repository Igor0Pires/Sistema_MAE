import gspread as gs
from dotenv import load_dotenv
import os

load_dotenv()


auth = gs.api_key(os.getenv("API-KEY"))
# Criar um dot file .env com as seguintes variáveis:
# API-KEY = chave da API do Google Sheets
# SHEET_acompanhamento = link
# SHEET_membros = link



# Podemos usar um config.json também, mas aqui vamos usar as variáveis de ambiente
acompanhamento = auth.open_by_url(os.getenv("SHEET_acompanhamento"))
membros = auth.open_by_url(os.getenv("SHEET_membros"))


if __name__ == "__main__":
    # testing the connection
    try:
        acompanhamento.sheet1.get_all_records()
        membros.sheet1.get_all_records()
        print("Conexão bem-sucedida com o Google Sheets.")
    except Exception as e:
        print(f"Erro ao conectar com o Google Sheets: {e}")