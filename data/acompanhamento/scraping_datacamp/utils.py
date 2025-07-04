from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import pickle
import os
import asyncio
import nest_asyncio
import random
import numpy as np
import pandas as pd
from datetime import datetime
import venv

#para manipular google sheets
import gspread
from gspread_dataframe import get_as_dataframe, set_with_dataframe # para converter as planilhas em DataFrames e vice-versa
from oauth2client.service_account import ServiceAccountCredentials # para autenticar o acesso ao Google Sheets

#-------------------------------------------------------------------------------------------------------------------------------------


#Google Sheets API
#Google Drive API
ID_DA_PLANILHA_GOOGLE_SHEETS = '1TneLohY9QvCDMCJAS0fCdNXsqxEnVw-YsRl3DpzVDdY' #fica entre /d/ e /edit na URL.

#ARQUIVO DE PERTENCIMENTO DA FEADEV
LOCAL_CREDENCIAIS_JSON_DE_ACESSO = '../credenciais.json' #Coloque o endereço do arquivo no seu PC


# Escopos de acesso
ESCOPOS = [
    "https://spreadsheets.google.com/feeds", # acesso ao Google Sheets
    "https://www.googleapis.com/auth/spreadsheets", # acesso ao Google Sheets
    "https://www.googleapis.com/auth/drive" # acesso ao Google Drive
]



#-------------------------------------------------------------------------------------------------------------------------------------
#nome do arquivo em que está contido o banco de dados do maedev
NOME_ARQUIVO = 'arquivo.xlsx'
PASTA_TRILHAS = '../trilhas'

#Recupera o nome de cada arquivo dentro da subpasta trilhas_atualizadas (ISSO É SEMPRE ARQUIVO LOCAL, NUNCA NA NUVEM)
LISTA_DE_TRILHAS_PARA_LER = [f for f in os.listdir(PASTA_TRILHAS) if os.path.isfile(os.path.join(PASTA_TRILHAS, f))]

#Gera um cliente autenticado (para facilitar a manipulação de sessão)
def abrir_cliente_JSON():
    # Autenticação usando o JSON baixado
    credenciais = ServiceAccountCredentials.from_json_keyfile_name(LOCAL_CREDENCIAIS_JSON_DE_ACESSO, ESCOPOS) #Credenciais do JSON

    cliente = gspread.authorize(credenciais)
    return cliente

def atualizar_trilhas_com_ids(trilhas_atualizadas_datacamp, maedev_df, col_nome_trilha_atualizada="Trilha", col_df_maedev=['id_trilha', 'nome_trilha', 'url', 'tipo_trilha']):
    """
    Adiciona novas trilhas únicas de `trilhas_atualizados_datacamp` em `maedev_df`, com id incremental.
    
    Parâmetros:
        trilhas_atualizados_datacamp (pd.DataFrame): DataFrame com os cursos e suas trilhas.
        maedev_df (pd.DataFrame): DataFrame com trilhas já cadastradas.
        col_nome_trilha_atualizada (str): Nome da trilha no trilhass_atualizadas_datacamp que contém o nome das trilhas.
        col_df_maedev (list): Lista com os nomes das colunas na ordem: [id, nome, url, tipo].

    Retorna:
        pd.DataFrame: O DataFrame `maedev_df` atualizado com novas trilhas e IDs únicos.
    """
    url_padrao_trilha = 'https://app.datacamp.com/learn/career-tracks/'
    
    # Padroniza os nomes das trilhas
    trilhas_atualizadas_datacamp[col_nome_trilha_atualizada] = trilhas_atualizadas_datacamp[col_nome_trilha_atualizada].astype(str).str.strip()
    maedev_df[col_df_maedev[1]] = maedev_df[col_df_maedev[1]].astype(str).str.strip()

    # ID inicial baseado no maior ID atual
    ultimo_id = maedev_df[col_df_maedev[0]].max() if not maedev_df.empty else -1
    novas_linhas = []



# Itera cada coluna unica em cursos atualizados(apenas combinacoes unicas), depois acessa o valor nas colunas nome_curso e Duração
    for _, row in trilhas_atualizadas_datacamp[[col_nome_trilha_atualizada, 'tipo_trilha']].drop_duplicates().iterrows():
        trilha = row[col_nome_trilha_atualizada]
        tipo_da_trilha = row['tipo_trilha'] #0-> trilha oficial do datacamp, 1-> trilha personalizada

        #Se essa trilha não está inclusa no maedev, adicona ela a lista de novos trilhas
        if trilha not in maedev_df[col_df_maedev[1]].values:
            ultimo_id += 1
            novas_linhas.append({
                col_df_maedev[0]: ultimo_id, #id
                col_df_maedev[1]: trilha, #nome da trilha
                col_df_maedev[2]: url_padrao_trilha + "-".join(trilha.lower().split()), #url da trilha
                col_df_maedev[3]: tipo_da_trilha
            })
            print(f"✅ Novo curso adicionado: {trilha} (id = {ultimo_id})")

    # Adiciona as novas trilhas, se houver
    if novas_linhas:
        df_novos = pd.DataFrame(novas_linhas)
        maedev_df = pd.concat([maedev_df, df_novos], ignore_index=True)
        print("🎯 Atualização concluída com sucesso.")
    else:
        print("ℹ️ Nenhuma nova trilha encontrada.")

    return maedev_df

def atualizar_cursos_com_ids(cursos_atualizados_datacamp, maedev_df, col_nome_curso_atualizada="Curso", col_df_maedev=['id_curso', 'nome_curso', 'duracao', 'url']):
    """
    Adiciona novas trilhas únicas de `cursos_atualizados_datacamp` em `maedev_df`, com id incremental.
    
    Parâmetros:
        cursos_atualizados_datacamp (pd.DataFrame): DataFrame com os cursos e suas trilhas.
        maedev_df (pd.DataFrame): DataFrame com trilhas já cadastradas.
        col_nome_curso_atualizada (str): Nome da coluna no cursos_atualizados_datacamp que contém o nome das trilhas.
        col_df_maedev (list): Lista com os nomes das colunas na ordem: [id, nome, url, tipo].

    Retorna:
        pd.DataFrame: O DataFrame `maedev_df` atualizado com novas trilhas e IDs únicos.
    """
    url_padrao_trilha = 'https://app.datacamp.com/learn/courses/'
    
    # Padroniza os nomes dos cursos
    cursos_atualizados_datacamp[col_nome_curso_atualizada] = cursos_atualizados_datacamp[col_nome_curso_atualizada].astype(str).str.strip()
    maedev_df[col_df_maedev[1]] = maedev_df[col_df_maedev[1]].astype(str).str.strip()

    # ID inicial baseado no maior ID atual
    ultimo_id = maedev_df[col_df_maedev[0]].max() if not maedev_df.empty else -1
    novas_linhas = []


    # Itera cada coluna unica em cursos atualizados(apenas combinacoes unicas), depois acessa o valor nas colunas nome_curso e Duração
    for _, row in cursos_atualizados_datacamp[[col_nome_curso_atualizada, 'Duração']].drop_duplicates().iterrows():
        curso = row[col_nome_curso_atualizada]
        duracao = row['Duração']

        #Se esse curso não está incluso no maedev, adicona ele a lista de novos cursos
        if curso not in maedev_df[col_df_maedev[1]].values:
            ultimo_id += 1
            novas_linhas.append({
                col_df_maedev[0]: ultimo_id,
                col_df_maedev[1]: curso,
                col_df_maedev[2]: duracao,
                col_df_maedev[3]: url_padrao_trilha + "-".join(curso.lower().split()),
            })
            print(f"✅ Novo curso adicionado: {curso} (id = {ultimo_id})")

    # Adiciona os novos cursos, se houver
    if novas_linhas:
        df_novos = pd.DataFrame(novas_linhas)
        maedev_df = pd.concat([maedev_df, df_novos], ignore_index=True)
        print("🎯 Atualização concluída com sucesso.")
    else:
        print("ℹ️ Nenhum novo curso encontrado.")

    return maedev_df

#Para associar as trilhas com os cursos/ gerar associações
def gerar_trilhas_tem_cursos(cliente, id_key_google_sheets=ID_DA_PLANILHA_GOOGLE_SHEETS, pasta_trilhas=PASTA_TRILHAS):
    """
    Gera a sheet 'Trilhas_tem_Cursos' na planilha Google especificada pelo ID, associando cada trilha aos cursos correspondentes.

    A função percorre todos os arquivos .xlsx dentro da pasta fornecida, assumindo que cada arquivo representa uma trilha
    (coluna 'Trilha') com os cursos correspondentes (coluna 'Curso'). Com base nesses nomes, ela busca os respectivos 
    `id_trilha` e `id_curso` nas sheets 'Trilhas' e 'Cursos' da planilha Google, criando a associação com campos extras 
    padrão.

    A nova sheet gerada contém as seguintes colunas:
        - id_trilha (int)
        - id_curso (int)
        - data_final_para_assistir (str): sempre vazio ('')
        - obrigatoriedade_curso (int): sempre 1

    Parâmetros:
    ----------
    cliente : gspread.Client
    Cliente autenticado gspread para acessar a planilha Google.

    id_key_google_sheets : str
        ID da planilha Google Sheets.

    pasta_trilhas : str
        Caminho da pasta contendo os arquivos .xlsx com as trilhas e cursos atualizados.



    Retorno:
    -------
    None
        A função salva a nova sheet 'Trilhas_tem_Cursos' diretamente na planilha Google.
    """

    # Abre a planilha Google pelo ID 
    planilha = cliente.open_by_key(id_key_google_sheets) 

    # Lê os dados principais da planilha Google
    aba_trilhas = planilha.worksheet('trilhas')
    aba_cursos = planilha.worksheet('cursos')
    df_trilhas = get_as_dataframe(aba_trilhas).dropna(how='all') #Transforma em DF
    df_cursos = get_as_dataframe(aba_cursos).dropna(how='all') #Transforma em DF

    associacoes = []

    # Itera sobre os arquivos de trilha atualizada (arquivo local)
    for nome_arquivo in os.listdir(pasta_trilhas):
        if not nome_arquivo.endswith(".xlsx"):
            continue

        caminho = os.path.join(pasta_trilhas, nome_arquivo)
        df = pd.read_excel(caminho)

        # Extrai os nomes da trilha e cursos
        nome_trilha = str(df['trilha'].iloc[0]).strip()

        # Recupera o id_trilha
        linha_trilha = df_trilhas[df_trilhas['nome_trilha'].str.strip() == nome_trilha]
        if linha_trilha.empty:
            print(f"❌ trilha não encontrada: {nome_trilha}")
            continue
        id_trilha = int(linha_trilha['id_trilha'].values[0])

        for nome_curso in df['curso'].unique():
            nome_curso = str(nome_curso).strip()
            linha_curso = df_cursos[df_cursos['nome_curso'].str.strip() == nome_curso]

            if linha_curso.empty:
                print(f"⚠️ curso não encontrado: {nome_curso}")
                continue

            id_curso = int(linha_curso['id_curso'].values[0])

            associacoes.append({
                'id_trilha': id_trilha,
                'id_curso': id_curso,
                'data_final_para_assistir': '',
                'obrigatoriedade_curso': 1
            })

    # Cria dataframe da associação
    df_associacoes = pd.DataFrame(associacoes)


    # Atualiza ou cria a aba 'Trilhas_tem_Cursos' na planilha Google
    try:
        aba_assoc = planilha.worksheet('trilhas_tem_cursos')
        aba_assoc.clear()  #Limpa a aba caso ela exista
    except Exception:
        # Cria nova aba se não existir
        aba_assoc = planilha.add_worksheet(title='trilhas_tem_cursos', rows=str(len(df_associacoes)+10), cols='10')


    # Escreve o dataframe na aba
    from gspread_dataframe import set_with_dataframe
    set_with_dataframe(aba_assoc, df_associacoes, include_index=False)

#Para marcar que um usuário x esteve presente ou ausente no evento y, também serve para atualizar o registro
#Essa função cria se necessário e atualiza o registro caso já exista
def registrar_participacao_evento(id_key_google_sheets, cliente, id_membro, id_evento, presenca=1):
    """
    Registra a participação de um membro da Feadev em um evento na planilha Google.

    A função acessa a aba 'membro_feadev_participa_eventos', e atualiza ou adiciona a participação,
    e salva de volta na mesma aba.

    Parâmetros:
    -----------
    id_key_google_sheets : str
        ID da planilha Google Sheets.

    cliente : gspread.Client
        Cliente gspread autenticado.

    id_membro : int
        ID do membro participante.

    id_evento : int
        ID do evento.

    presenca : int, opcional (padrão=1)
        1 para presente, 0 para ausente.

    Retorno:
    --------
    None
    """
    # Abre a planilha
    planilha = cliente.open_by_key(id_key_google_sheets)

    # Tenta abrir a aba, ou cria uma nova se não existir
    try:
        aba = planilha.worksheet('membro_feadev_participa_eventos')
        df_participacoes = get_as_dataframe(aba).dropna(how='all')
    except:
        aba = planilha.add_worksheet(title='membro_feadev_participa_eventos', rows='100', cols='5')
        df_participacoes = pd.DataFrame(columns=['id_membro', 'id_evento', 'presença'])

    # Garante os tipos certos
    df_participacoes['id_membro'] = pd.to_numeric(df_participacoes['id_membro'], errors='coerce').fillna(-1).astype(int)
    df_participacoes['id_evento'] = pd.to_numeric(df_participacoes['id_evento'], errors='coerce').fillna(-1).astype(int)

    # Verifica se já existe
    existe = (
        (df_participacoes['id_membro'] == id_membro) &
        (df_participacoes['id_evento'] == id_evento)
    )

    if existe.any():
        df_participacoes.loc[existe, 'presença'] = presenca
    else:
        nova_linha = pd.DataFrame([{
            'id_membro': id_membro,
            'id_evento': id_evento,
            'presença': presenca
        }])
        df_participacoes = pd.concat([df_participacoes, nova_linha], ignore_index=True)

    # Salva de volta na aba (substitui tudo)
    aba.clear()
    set_with_dataframe(aba, df_participacoes, include_index=False)

#Essa função cria se necessário e atualiza o registro caso já exista
def registrar_membro_faz_curso(id_key_google_sheets, cliente, id_membro, id_curso, data_inicio='', data_fim='', finalizado=0):
    """
    Registra que um membro da Feadev iniciou ou finalizou um curso.

    A função acessa (ou cria) a aba 'membro_feadev_faz_cursos', atualiza ou adiciona o registro,
    e salva de volta na mesma aba.

    Parâmetros:
    -----------
    id_key_google_sheets : str
        ID da planilha Google Sheets.

    cliente : gspread.Client
        Cliente gspread autenticado.

    id_membro : int
        ID do membro.

    id_curso : int
        ID do curso.

    data_inicio : str ou datetime
        Data de início do curso.

    data_fim : str ou datetime
        Data de término do curso.

    finalizado : int, opcional (default=0)
        1 para curso finalizado, 0 para não finalizado.

    Retorno:
    --------
    None
    """
    planilha = cliente.open_by_key(id_key_google_sheets)

    # Tenta abrir ou criar a aba
    try:
        aba = planilha.worksheet('membro_feadev_faz_cursos')
        df = get_as_dataframe(aba).dropna(how='all')
    except:
        aba = planilha.add_worksheet(title='membro_feadev_faz_cursos', rows='100', cols='6')
        df = pd.DataFrame(columns=[
            'id_membro', 'id_curso', 'data_inicio', 'data_fim', 'finalizado'
        ])

    # Garante tipos numéricos
    df['id_membro'] = pd.to_numeric(df['id_membro'], errors='coerce').fillna(-1).astype(int)
    df['id_curso'] = pd.to_numeric(df['id_curso'], errors='coerce').fillna(-1).astype(int)

    # Converte as datas para datetime (caso venham como string)
    if isinstance(data_inicio, str):
        data_inicio = pd.to_datetime(data_inicio)
    if isinstance(data_fim, str):
        data_fim = pd.to_datetime(data_fim)

    # Verifica se já existe esse registro
    existe = (
        (df['id_membro'] == id_membro) &
        (df['id_curso'] == id_curso)
    )

    if existe.any():
        # Atualiza o registro existente
        df.loc[existe, 'data_inicio'] = data_inicio
        df.loc[existe, 'data_fim'] = data_fim
        df.loc[existe, 'finalizado'] = finalizado
    else:
        nova_linha = pd.DataFrame([{
            'id_membro': id_membro,
            'id_curso': id_curso,
            'data_inicio': data_inicio,
            'data_fim': data_fim,
            'finalizado': finalizado
        }])
        df = pd.concat([df, nova_linha], ignore_index=True)

    # Salva de volta
    aba.clear()
    set_with_dataframe(aba, df, include_index=False)

#Essa função cria se necessário e atualiza o registro caso já exista
def registrar_membro_faz_trilha(id_key_google_sheets, cliente, id_membro, id_trilha, data_inicio='', data_fim='', finalizado=0):
    """
    Registra que um membro da Feadev iniciou ou finalizou uma trilha.

    A função acessa (ou cria) a aba 'membro_feadev_faz_trilhas', atualiza ou adiciona o registro,
    e salva de volta na mesma aba.

    Parâmetros:
    -----------
    id_key_google_sheets : str
        ID da planilha Google Sheets.

    cliente : gspread.Client
        Cliente gspread autenticado.

    id_membro : int
        ID do membro.

    id_trilha : int
        ID da trilha.

    data_inicio : str ou datetime
        Data de início da trilha.

    data_fim : str ou datetime
        Data de término da trilha.

    finalizado : int, opcional (default=0)
        1 para trilha finalizada, 0 para não finalizada.

    Retorno:
    --------
    None
    """
    planilha = cliente.open_by_key(id_key_google_sheets)

    # Tenta abrir ou criar a aba
    try:
        aba = planilha.worksheet('membro_feadev_faz_trilhas')
        df = get_as_dataframe(aba).dropna(how='all')
    except:
        aba = planilha.add_worksheet(title='membro_feadev_faz_trilhas', rows='100', cols='6')
        df = pd.DataFrame(columns=[
            'id_membro', 'id_trilha', 'data_inicio', 'data_fim', 'finalizado'
        ])

    # Garante tipos numéricos
    df['id_membro'] = pd.to_numeric(df['id_membro'], errors='coerce').fillna(-1).astype(int)
    df['id_trilha'] = pd.to_numeric(df['id_trilha'], errors='coerce').fillna(-1).astype(int)

    # Converte as datas para datetime (caso venham como string)
    if isinstance(data_inicio, str):
        data_inicio = pd.to_datetime(data_inicio)
    if isinstance(data_fim, str):
        data_fim = pd.to_datetime(data_fim)

    # Verifica se já existe esse registro
    existe = (
        (df['id_membro'] == id_membro) &
        (df['id_trilha'] == id_trilha)
    )

    if existe.any():
        df.loc[existe, 'data_inicio'] = data_inicio
        df.loc[existe, 'data_fim'] = data_fim
        df.loc[existe, 'finalizado'] = finalizado
    else:
        nova_linha = pd.DataFrame([{
            'id_membro': id_membro,
            'id_trilha': id_trilha,
            'data_inicio': data_inicio,
            'data_fim': data_fim,
            'finalizado': finalizado
        }])
        df = pd.concat([df, nova_linha], ignore_index=True)

    # Salva de volta
    aba.clear()
    set_with_dataframe(aba, df, include_index=False)

def registrar_membro(id_key_google_sheets, cliente, nome, email, tipo_ingresso, conta_github='', conta_datacamp='', xp_datacamp='', ativo=1):
    """
    Registra um novo membro da Feadev na planilha Google na aba 'membros_feadev'.

    Se a aba não existir, ela será criada.

    Parâmetros:
    -----------
    id_key_google_sheets : str
        ID da planilha Google Sheets.

    cliente : gspread.Client
        Cliente gspread autenticado.

    nome : str
        Nome do membro.

    email : str
        E-mail do membro.

    tipo_ingresso : str, 2 letras maiusculas (tipo de processo) e 2 números (ano)
        PS - Processo Seletivo
        PY - curso de PYthon

    conta_github : str, opcional
        Nome de usuário no GitHub.

    conta_datacamp : str, opcional
        URL ou identificador da conta no DataCamp.

    xp_datacamp : str, opcional
        Experiência acumulada no DataCamp.

    ativo : int, opcional (default=1)
        Status do membro: 1 para ativo, 0 para inativo.

    Retorno:
    --------
    None
    """
    # Abre a planilha
    planilha = cliente.open_by_key(id_key_google_sheets)

    # Tenta abrir a aba ou cria uma nova se não existir
    try:
        aba = planilha.worksheet('membros_feadev')
        df_membros = get_as_dataframe(aba).dropna(how='all')
    except:
        aba = planilha.add_worksheet(title='membros_feadev', rows='100', cols='8')
        df_membros = pd.DataFrame(columns=[
            'id_membro', 'nome', 'email', 'conta_github',
            'conta_datacamp', 'xp_datacamp', 'ativo', 'tipo_ingresso'
        ])

    # Garante que os IDs sejam inteiros
    df_membros['id_membro'] = pd.to_numeric(df_membros['id_membro'], errors='coerce').fillna(-1).astype(int)

    # Define o novo ID
    novo_id = df_membros['id_membro'].max() + 1 if not df_membros.empty else 0

    # Cria nova linha
    novo_membro = pd.DataFrame([{
        'id_membro': novo_id,
        'nome': nome,
        'email': email,
        'conta_github': conta_github,
        'conta_datacamp': conta_datacamp,
        'xp_datacamp': xp_datacamp,
        'ativo': ativo,
        'tipo_ingresso': tipo_ingresso
    }])

    # Adiciona e salva
    df_membros = pd.concat([df_membros, novo_membro], ignore_index=True)
    aba.clear()
    set_with_dataframe(aba, df_membros, include_index=False)

def atualizar_registro_membro(id_key_google_sheets, cliente, id_membro, nome='', email='', conta_github='', conta_datacamp='',
       xp_datacamp='', ativo=1, tipo_ingresso='') -> None | Exception:
    '''
    Troca as informações atuais do membro de id fornecido pelas informações nos kwargs
    Caso não exista a aba um erro é retornado

    Criada com a ideia de corrigir eventuais erros passados a frente para a DB

    Parâmetros:
    -----------
    id_key_google_sheets : str
        ID da planilha Google Sheets.

    cliente : gspread.Client
        Cliente gspread autenticado.

    id_membro : Int
        ID do membro.

    nome : str, opcional
        Nome do membro.

    email : str, opcional
        E-mail do membro.

    tipo_ingresso : str, opcional
        2 letras maiusculas (tipo de processo) e 2 números (ano)
        PS - Processo Seletivo
        PY - curso de PYthon

    conta_github : str, opcional
        Nome de usuário no GitHub.

    conta_datacamp : str, opcional
        URL ou identificador da conta no DataCamp.

    xp_datacamp : str, opcional
        Experiência acumulada no DataCamp.

    ativo : int, opcional (default=1)
        Status do membro: 1 para ativo, 0 para inativo.

    Retorno:
    --------
    None
    """

    '''
    # Abre a planilha
    planilha = cliente.open_by_key(id_key_google_sheets)

    # Tenta abrir a aba ou cria uma nova se não existir
    try:
        aba = planilha.worksheet('membros_feadev')
        df_membros = get_as_dataframe(aba).dropna(how='all')
    except:
        print('falha ao abrir aba da planilha')
        raise ConnectionError
    
    # Garante que os IDs sejam inteiros
    df_membros['id_membro'] = pd.to_numeric(df_membros['id_membro'], errors='coerce').fillna(-1).astype(int)
    
    cadastro_antigo = df_membros[df_membros['id_membro']==id_membro]
    # cria a nova linha 
    novo_cadastro = pd.DataFrame([{
        'id_membro': int(id_membro),
        'nome': nome if nome else cadastro_antigo['nome'].values[0],
        'email': email if email else cadastro_antigo['email'].values[0],
        'conta_github': conta_github if conta_github else cadastro_antigo['conta_github'].values[0],
        'conta_datacamp': conta_datacamp if conta_datacamp else cadastro_antigo['conta_datacamp'].values[0],
        'xp_datacamp': xp_datacamp if xp_datacamp else cadastro_antigo['xp_datacamp'].values[0],
        'ativo': ativo if ativo!=1 else 1,
        'tipo_ingresso': tipo_ingresso if tipo_ingresso else cadastro_antigo['tipo_ingresso'].values[0]
    }])
    novo_cadastro_ = np.copy(novo_cadastro)

    # substitui a linha
    df_membros[df_membros['id_membro']==id_membro] = novo_cadastro_

    # salva
    aba.clear()
    set_with_dataframe(aba, df_membros, include_index=False)
    # print(f'membro id {id_membro} modificado com sucesso')

def excluir_membro(id_key_google_sheets, cliente, id_membro) -> None | Exception:
    '''
    Remove o membro de mesmo ID e todas as suas menções na DB (falta implementar a remoção nas outras abas)

    Parâmetros:
    -----------
    id_key_google_sheets : str
        ID da planilha Google Sheets.

    cliente : gspread.Client
        Cliente gspread autenticado.

    id_membro : Int
        ID do membro a ser removido.

    Retorno:
    --------
    None
    '''
    # Abre a planilha
    planilha = cliente.open_by_key(id_key_google_sheets)

    # Tenta abrir a aba ou cria uma nova se não existir
    try:
        aba = planilha.worksheet('membros_feadev')
        df_membros = get_as_dataframe(aba).dropna(how='all')
    except:
        print('falha ao abrir aba da planilha')
        raise ConnectionError
    
    # Garante que os IDs sejam inteiros
    df_membros['id_membro'] = pd.to_numeric(df_membros['id_membro'], errors='coerce').fillna(-1).astype(int)
    # Garante que IDs correspondam ao index
    df_membros.set_index(df_membros['id_membro'], drop=False, inplace=True)
    # exclui a linha referente ao membro
    df_membros = df_membros.drop(index=id_membro, axis=0)
    # salva
    aba.clear()
    set_with_dataframe(aba, df_membros, include_index=False)
    # print(f'membro {id_membro} removido')


def registrar_evento(id_key_google_sheets, cliente, nome_evento, tipo_evento_id='', tipo_evento_nome='', descricao='', data_inicio='', data_fim=''):
    """
    Registra um novo evento da Feadev na aba 'eventos' da planilha Google.

    Se a aba não existir, ela será criada.

    Parâmetros:
    -----------
    id_key_google_sheets : str
        ID da planilha Google Sheets.

    cliente : gspread.Client
        Cliente gspread autenticado.

    nome_evento : str
        Nome do evento.

    tipo_evento_id : str
        ID do tipo do evento (chave estrangeira).

    tipo_evento_nome : str
        Nome do tipo do evento (chave estrangeira).

    descricao : str
        Descrição do evento.

    data_inicio : datetime.datetime
        Data e hora de início do evento.

    data_fim : datetime.datetime
        Data e hora de fim do evento.

    Retorno:
    --------
    None
    """
    planilha = cliente.open_by_key(id_key_google_sheets)

    # Tenta abrir ou cria a aba
    try:
        aba = planilha.worksheet('eventos')
        df_eventos = get_as_dataframe(aba).dropna(how='all')
    except:
        aba = planilha.add_worksheet(title='eventos', rows='100', cols='7')
        df_eventos = pd.DataFrame(columns=[
            'id_evento', 'nome_evento', 'tipo_evento_id', 'tipo_evento_nome',
            'descricao', 'data_inicio', 'data_fim'
        ])

    # Garante que os IDs sejam inteiros
    df_eventos['id_evento'] = pd.to_numeric(df_eventos['id_evento'], errors='coerce').fillna(-1).astype(int)

    # Define o novo ID
    novo_id = df_eventos['id_evento'].max() + 1 if not df_eventos.empty else 0

    # Cria nova linha
    novo_evento = pd.DataFrame([{
        'id_evento': novo_id,
        'nome_evento': nome_evento,
        'tipo_evento_id': tipo_evento_id,
        'tipo_evento_nome': tipo_evento_nome,
        'descricao': descricao,
        'data_inicio': pd.to_datetime(data_inicio),
        'data_fim': pd.to_datetime(data_fim)
    }])

    # Adiciona, limpa e salva de volta
    df_eventos = pd.concat([df_eventos, novo_evento], ignore_index=True)
    aba.clear()
    set_with_dataframe(aba, df_eventos, include_index=False)

def listar_membros(id_key_google_sheets, cliente):
    """
    Retorna um DataFrame com todos os membros registrados na aba 'membros_feadev' da planilha Google.

    Parâmetros:
    -----------
    id_key_google_sheets : str
        ID da planilha Google Sheets.

    cliente : gspread.Client
        Cliente gspread autenticado.

    Retorno:
    --------
    pd.DataFrame
        DataFrame com os dados dos membros.
    """
    planilha = cliente.open_by_key(id_key_google_sheets)

    try:
        aba = planilha.worksheet('membros_feadev')
        df_membros = get_as_dataframe(aba).dropna(how='all')
        return df_membros
    except Exception as e:
        print(f"Erro ao acessar a aba 'membros_feadev': {e}")
        return pd.DataFrame()

def listar_cursos(id_key_google_sheets, cliente):
    """
    Retorna um DataFrame com todos os cursos registrados na aba 'cursos' da planilha Google.

    Parâmetros:
    -----------
    id_key_google_sheets : str
        ID da planilha Google Sheets.

    cliente : gspread.Client
        Cliente gspread autenticado.

    Retorno:
    --------
    pd.DataFrame
        DataFrame com os dados dos cursos.
    """
    planilha = cliente.open_by_key(id_key_google_sheets)

    try:
        aba = planilha.worksheet('cursos')
        df_cursos = get_as_dataframe(aba).dropna(how='all')
        return df_cursos
    except Exception as e:
        print(f"Erro ao acessar a aba 'cursos': {e}")
        return pd.DataFrame()
    
def listar_trilhas(id_key_google_sheets, cliente):
    """
    Retorna um DataFrame com todos as trilhas registrados na aba 'trilhas' da planilha Google.

    Parâmetros:
    -----------
    id_key_google_sheets : str
        ID da planilha Google Sheets.

    cliente : gspread.Client
        Cliente gspread autenticado.

    Retorno:
    --------
    pd.DataFrame
        DataFrame com os dados dos cursos.
    """
    planilha = cliente.open_by_key(id_key_google_sheets)

    try:
        aba = planilha.worksheet('trilhas')
        df_cursos = get_as_dataframe(aba).dropna(how='all')
        return df_cursos
    except Exception as e:
        print(f"Erro ao acessar a aba 'trilhas': {e}")
        return pd.DataFrame()
    
def listar_eventos(id_key_google_sheets, cliente):
    """
    Retorna um DataFrame com todos os eventos registrados na aba 'eventos' da planilha Google.

    Parâmetros:
    -----------
    id_key_google_sheets : str
        ID da planilha Google Sheets.

    cliente : gspread.Client
        Cliente gspread autenticado.

    Retorno:
    --------
    pd.DataFrame
        DataFrame com os dados dos cursos.
    """
    planilha = cliente.open_by_key(id_key_google_sheets)

    try:
        aba = planilha.worksheet('eventos')
        df_cursos = get_as_dataframe(aba).dropna(how='all')
        return df_cursos
    except Exception as e:
        print(f"Erro ao acessar a aba 'eventos': {e}")
        return pd.DataFrame()
    
#Listar/Ler google sheets

#MEMBROS X EVENTOS
def listar_eventos_de_um_usuario(id_key_google_sheets, cliente, id_membro):
    """
    Retorna um DataFrame com os eventos que um membro participou, incluindo o campo presença.

    Parâmetros:
    -----------
    id_key_google_sheets : str
        ID da planilha Google Sheets.

    cliente : gspread.Client
        Cliente gspread autenticado.

    id_membro : int
        ID do membro para filtrar os eventos.

    Retorno:
    --------
    pd.DataFrame
        DataFrame com os eventos em que o membro participou, contendo também a coluna 'presença'.
    """
    planilha = cliente.open_by_key(id_key_google_sheets)

    try:
        # Lê participações do membro
        aba_participacoes = planilha.worksheet('membro_feadev_participa_eventos')
        df_participacoes = get_as_dataframe(aba_participacoes).dropna(how='all')

        # Garantir tipos corretos
        df_participacoes['id_membro'] = pd.to_numeric(df_participacoes['id_membro'], errors='coerce').fillna(-1).astype(int)
        df_participacoes['id_evento'] = pd.to_numeric(df_participacoes['id_evento'], errors='coerce').fillna(-1).astype(int)
        df_participacoes['presença'] = pd.to_numeric(df_participacoes['presença'], errors='coerce').fillna(0).astype(int)

        # Filtra participações do usuário
        participacoes_usuario = df_participacoes[df_participacoes['id_membro'] == id_membro]

        if participacoes_usuario.empty:
            return pd.DataFrame()

        # Lê os eventos
        aba_eventos = planilha.worksheet('eventos')
        df_eventos = get_as_dataframe(aba_eventos).dropna(how='all')
        df_eventos['id_evento'] = pd.to_numeric(df_eventos['id_evento'], errors='coerce').fillna(-1).astype(int)

        # Filtra eventos correspondentes
        eventos_filtrados = df_eventos[df_eventos['id_evento'].isin(participacoes_usuario['id_evento'].unique())]

        # Junta com presença (merge pela coluna id_evento)
        resultado = pd.merge(eventos_filtrados, participacoes_usuario[['id_evento', 'presença']], on='id_evento', how='left')

        return resultado.reset_index(drop=True)

    except Exception as e:
        print(f"Erro ao listar eventos do usuário {id_membro}: {e}")
        return pd.DataFrame()

def listar_participantes_de_um_evento(id_key_google_sheets, cliente, id_evento):
    """
    Retorna um DataFrame com os membros que participaram de um evento, incluindo o campo presença.

    Parâmetros:
    -----------
    id_key_google_sheets : str
        ID da planilha Google Sheets.

    cliente : gspread.Client
        Cliente gspread autenticado.

    id_evento : int
        ID do evento para filtrar os participantes.

    Retorno:
    --------
    pd.DataFrame
        DataFrame com os membros que participaram do evento, contendo também a coluna 'presença'.
    """
    planilha = cliente.open_by_key(id_key_google_sheets)

    try:
        # Lê participações do evento
        aba_participacoes = planilha.worksheet('membro_feadev_participa_eventos')
        df_participacoes = get_as_dataframe(aba_participacoes).dropna(how='all')

        # Garantir tipos corretos
        df_participacoes['id_membro'] = pd.to_numeric(df_participacoes['id_membro'], errors='coerce').fillna(-1).astype(int)
        df_participacoes['id_evento'] = pd.to_numeric(df_participacoes['id_evento'], errors='coerce').fillna(-1).astype(int)
        df_participacoes['presença'] = pd.to_numeric(df_participacoes['presença'], errors='coerce').fillna(0).astype(int)

        # Filtra participações do evento
        participacoes_evento = df_participacoes[df_participacoes['id_evento'] == id_evento]

        if participacoes_evento.empty:
            return pd.DataFrame()

        # Lê os membros
        aba_membros = planilha.worksheet('Membros_feadev')
        df_membros = get_as_dataframe(aba_membros).dropna(how='all')
        df_membros['id_membro'] = pd.to_numeric(df_membros['id_membro'], errors='coerce').fillna(-1).astype(int)

        # Filtra membros correspondentes
        membros_filtrados = df_membros[df_membros['id_membro'].isin(participacoes_evento['id_membro'].unique())]

        # Junta com presença (merge pela coluna id_membro)
        resultado = pd.merge(membros_filtrados, participacoes_evento[['id_membro', 'presença']], on='id_membro', how='left')

        return resultado.reset_index(drop=True)

    except Exception as e:
        print(f"Erro ao listar participantes do evento {id_evento}: {e}")
        return pd.DataFrame()

#MEMBROS X TRILHAS
def listar_trilhas_feitas_por_um_membro(id_key_google_sheets, cliente, id_membro):
    """
    Retorna um DataFrame com as trilhas que um membro está fazendo ou já fez,
    incluindo informações de progresso como data de início, data de fim e se foi finalizado.

    Parâmetros:
    -----------
    id_key_google_sheets : str
        ID da planilha Google Sheets.

    cliente : gspread.Client
        Cliente gspread autenticado.

    id_membro : int
        ID do membro.

    Retorno:
    --------
    pd.DataFrame
        DataFrame com as trilhas associadas ao membro e suas informações de progresso.
    """
    planilha = cliente.open_by_key(id_key_google_sheets)

    try:
        # Lê registros da aba de membros fazendo trilhas
        aba_faz_trilhas = planilha.worksheet('membro_feadev_faz_trilhas')
        df_faz_trilhas = get_as_dataframe(aba_faz_trilhas).dropna(how='all')

        df_faz_trilhas['id_membro'] = pd.to_numeric(df_faz_trilhas['id_membro'], errors='coerce').fillna(-1).astype(int)
        df_faz_trilhas['id_trilha'] = pd.to_numeric(df_faz_trilhas['id_trilha'], errors='coerce').fillna(-1).astype(int)

        # Filtra somente os registros do membro
        trilhas_do_membro = df_faz_trilhas[df_faz_trilhas['id_membro'] == id_membro]

        if trilhas_do_membro.empty:
            return pd.DataFrame()

        # Lê os dados das trilhas
        aba_trilhas = planilha.worksheet('trilhas')
        df_trilhas = get_as_dataframe(aba_trilhas).dropna(how='all')
        df_trilhas['id_trilha'] = pd.to_numeric(df_trilhas['id_trilha'], errors='coerce').fillna(-1).astype(int)

        # Junta os dados da trilha com os dados de progresso do membro
        resultado = trilhas_do_membro.merge(df_trilhas, on='id_trilha', how='left')

        # Organiza as colunas com prioridade para info de progresso
        colunas_base = ['id_trilha', 'nome_trilha', 'url', 'tipo_trilha']
        colunas_progresso = ['data_inicio', 'data_fim', 'finalizado']
        colunas_outros = [c for c in resultado.columns if c not in colunas_base + colunas_progresso + ['id_membro']]

        colunas_final = colunas_base + colunas_progresso + colunas_outros
        return resultado[colunas_final].reset_index(drop=True)

    except Exception as e:
        print(f"Erro ao listar trilhas do membro {id_membro}: {e}")
        return pd.DataFrame()

def listar_membros_de_uma_trilha(id_key_google_sheets, cliente, id_trilha):
    """
    Retorna um DataFrame com os membros que estão fazendo ou fizeram uma trilha específica.

    Parâmetros:
    -----------
    id_key_google_sheets : str
        ID da planilha Google Sheets.

    cliente : gspread.Client
        Cliente gspread autenticado.

    id_trilha : int
        ID da trilha para filtrar os membros.

    Retorno:
    --------
    pd.DataFrame
        DataFrame com os membros associados à trilha.
    """
    planilha = cliente.open_by_key(id_key_google_sheets)

    try:
        # Lê registros da aba de membros fazendo trilhas
        aba_faz_trilhas = planilha.worksheet('membro_feadev_faz_trilhas')
        df_faz_trilhas = get_as_dataframe(aba_faz_trilhas).dropna(how='all')

        df_faz_trilhas['id_membro'] = pd.to_numeric(df_faz_trilhas['id_membro'], errors='coerce').fillna(-1).astype(int)
        df_faz_trilhas['id_trilha'] = pd.to_numeric(df_faz_trilhas['id_trilha'], errors='coerce').fillna(-1).astype(int)

        membros_da_trilha = df_faz_trilhas[df_faz_trilhas['id_trilha'] == id_trilha]

        if membros_da_trilha.empty:
            return pd.DataFrame()

        # Lê os dados dos membros
        aba_membros = planilha.worksheet('membros_feadev')
        df_membros = get_as_dataframe(aba_membros).dropna(how='all')
        df_membros['id_membro'] = pd.to_numeric(df_membros['id_membro'], errors='coerce').fillna(-1).astype(int)

        # Junta os dados dos membros
        membros_completos = df_membros[df_membros['id_membro'].isin(membros_da_trilha['id_membro'].unique())]

        return membros_completos.reset_index(drop=True)

    except Exception as e:
        print(f"Erro ao listar membros da trilha {id_trilha}: {e}")
        return pd.DataFrame()


#MEMBROS X CURSOS
def listar_cursos_feitos_por_um_membro(id_key_google_sheets, cliente, id_membro):
    """
    Retorna um DataFrame com os cursos que um membro está fazendo ou já fez,
    incluindo informações de progresso como data de início, data de fim e se foi finalizado.

    Parâmetros:
    -----------
    id_key_google_sheets : str
        ID da planilha Google Sheets.

    cliente : gspread.Client
        Cliente gspread autenticado.

    id_membro : int
        ID do membro.

    Retorno:
    --------
    pd.DataFrame
        DataFrame com os cursos associados ao membro e suas informações de progresso.
    """
    planilha = cliente.open_by_key(id_key_google_sheets)

    try:
        # Lê registros da aba de membros fazendo cursos
        aba_faz_cursos = planilha.worksheet('membro_feadev_faz_cursos')
        df_faz_cursos = get_as_dataframe(aba_faz_cursos).dropna(how='all')

        df_faz_cursos['id_membro'] = pd.to_numeric(df_faz_cursos['id_membro'], errors='coerce').fillna(-1).astype(int)
        df_faz_cursos['id_curso'] = pd.to_numeric(df_faz_cursos['id_curso'], errors='coerce').fillna(-1).astype(int)

        # Filtra somente os registros do membro
        cursos_do_membro = df_faz_cursos[df_faz_cursos['id_membro'] == id_membro]

        if cursos_do_membro.empty:
            return pd.DataFrame()

        # Lê os dados dos cursos
        aba_cursos = planilha.worksheet('cursos')
        df_cursos = get_as_dataframe(aba_cursos).dropna(how='all')
        df_cursos['id_curso'] = pd.to_numeric(df_cursos['id_curso'], errors='coerce').fillna(-1).astype(int)

        # Junta os dados do curso com os dados de progresso do membro
        resultado = cursos_do_membro.merge(df_cursos, on='id_curso', how='left')

        # Organiza as colunas com prioridade para info de progresso
        colunas_base = ['id_curso', 'nome_curso', 'duracao', 'url']
        colunas_progresso = ['data_inicio', 'data_fim', 'finalizado']
        colunas_outros = [c for c in resultado.columns if c not in colunas_base + colunas_progresso + ['id_membro']]

        colunas_final = colunas_base + colunas_progresso + colunas_outros
        return resultado[colunas_final].reset_index(drop=True)

    except Exception as e:
        print(f"Erro ao listar cursos do membro {id_membro}: {e}")
        return pd.DataFrame()

def listar_membros_de_um_curso(id_key_google_sheets, cliente, id_curso):
    """
    Retorna um DataFrame com os membros que estão fazendo ou fizeram um curso específico.

    Parâmetros:
    -----------
    id_key_google_sheets : str
        ID da planilha Google Sheets.

    cliente : gspread.Client
        Cliente gspread autenticado.

    id_curso : int
        ID do curso para filtrar os membros.

    Retorno:
    --------
    pd.DataFrame
        DataFrame com os membros associados ao curso.
    """
    planilha = cliente.open_by_key(id_key_google_sheets)

    try:
        # Lê registros da aba de membros fazendo cursos
        aba_faz_cursos = planilha.worksheet('membro_feadev_faz_cursos')
        df_faz_cursos = get_as_dataframe(aba_faz_cursos).dropna(how='all')

        df_faz_cursos['id_membro'] = pd.to_numeric(df_faz_cursos['id_membro'], errors='coerce').fillna(-1).astype(int)
        df_faz_cursos['id_curso'] = pd.to_numeric(df_faz_cursos['id_curso'], errors='coerce').fillna(-1).astype(int)

        membros_do_curso = df_faz_cursos[df_faz_cursos['id_curso'] == id_curso]

        if membros_do_curso.empty:
            return pd.DataFrame()

        # Lê os dados dos membros
        aba_membros = planilha.worksheet('membros_feadev')
        df_membros = get_as_dataframe(aba_membros).dropna(how='all')
        df_membros['id_membro'] = pd.to_numeric(df_membros['id_membro'], errors='coerce').fillna(-1).astype(int)

        # Junta os dados dos membros
        membros_completos = df_membros[df_membros['id_membro'].isin(membros_do_curso['id_membro'].unique())]

        return membros_completos.reset_index(drop=True)

    except Exception as e:
        print(f"Erro ao listar membros do curso {id_curso}: {e}")
        return pd.DataFrame()

#CURSOS X TRILHAS
def listar_cursos_de_uma_trilha(id_key_google_sheets, cliente, id_trilha):
    """
    Retorna um DataFrame com todos os cursos associados a uma trilha.

    Parâmetros:
    -----------
    id_key_google_sheets : str
        ID da planilha Google Sheets.

    cliente : gspread.Client
        Cliente gspread autenticado.

    id_trilha : int
        ID da trilha para filtrar os cursos.

    Retorno:
    --------
    pd.DataFrame
        DataFrame com os cursos associados à trilha.
    """
    planilha = cliente.open_by_key(id_key_google_sheets)

    try:
        # Lê associação trilhas -> cursos
        aba_assoc = planilha.worksheet('trilhas_tem_cursos')
        df_assoc = get_as_dataframe(aba_assoc).dropna(how='all')

        # Filtra associações para o id_trilha
        df_assoc['id_trilha'] = pd.to_numeric(df_assoc['id_trilha'], errors='coerce').fillna(-1).astype(int)
        df_assoc['id_curso'] = pd.to_numeric(df_assoc['id_curso'], errors='coerce').fillna(-1).astype(int)
        assoc_filtrada = df_assoc[df_assoc['id_trilha'] == id_trilha]

        if assoc_filtrada.empty:
            print(f"Nenhum curso encontrado para a trilha id {id_trilha}")
            return pd.DataFrame()

        # Lê dados dos cursos
        aba_cursos = planilha.worksheet('cursos')
        df_cursos = get_as_dataframe(aba_cursos).dropna(how='all')
        df_cursos['id_curso'] = pd.to_numeric(df_cursos['id_curso'], errors='coerce').fillna(-1).astype(int)

        # Filtra os cursos que estão associados à trilha
        cursos_trilha = df_cursos[df_cursos['id_curso'].isin(assoc_filtrada['id_curso'].unique())]

        return cursos_trilha.reset_index(drop=True)

    except Exception as e:
        print(f"Erro ao listar cursos da trilha {id_trilha}: {e}")
        return pd.DataFrame()
    
def listar_trilhas_de_um_curso(id_key_google_sheets, cliente, id_curso):
    """
    Retorna um DataFrame com todas as trilhas associadas a um curso.

    Parâmetros:
    -----------
    id_key_google_sheets : str
        ID da planilha Google Sheets.

    cliente : gspread.Client
        Cliente gspread autenticado.

    id_curso : int
        ID do curso para filtrar as trilhas.

    Retorno:
    --------
    pd.DataFrame
        DataFrame com as trilhas associadas ao curso.
    """
    planilha = cliente.open_by_key(id_key_google_sheets)

    try:
        # Lê associação trilhas -> cursos
        aba_assoc = planilha.worksheet('trilhas_tem_cursos')
        df_assoc = get_as_dataframe(aba_assoc).dropna(how='all')

        # Garante que as colunas numéricas estejam corretas
        df_assoc['id_trilha'] = pd.to_numeric(df_assoc['id_trilha'], errors='coerce').fillna(-1).astype(int)
        df_assoc['id_curso'] = pd.to_numeric(df_assoc['id_curso'], errors='coerce').fillna(-1).astype(int)

        # Filtra associações para o id_curso
        assoc_filtrada = df_assoc[df_assoc['id_curso'] == id_curso]

        if assoc_filtrada.empty:
            print(f"Nenhuma trilha encontrada para o curso id {id_curso}")
            return pd.DataFrame()

        # Lê dados das trilhas
        aba_trilhas = planilha.worksheet('trilhas')
        df_trilhas = get_as_dataframe(aba_trilhas).dropna(how='all')
        df_trilhas['id_trilha'] = pd.to_numeric(df_trilhas['id_trilha'], errors='coerce').fillna(-1).astype(int)

        # Filtra as trilhas associadas ao curso
        trilhas_curso = df_trilhas[df_trilhas['id_trilha'].isin(assoc_filtrada['id_trilha'].unique())]

        return trilhas_curso.reset_index(drop=True)

    except Exception as e:
        print(f"Erro ao listar trilhas do curso {id_curso}: {e}")
        return pd.DataFrame()