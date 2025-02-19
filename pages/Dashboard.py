import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import plotly.express as px

# Dicionário com as URLs das bases de dados de diversas ligas
data_sources = { "Argentina Primera División": "https://github.com/futpythontrader/YouTube/raw/refs/heads/main/Bases_de_Dados/FootyStats/Bases_de_Dados_(2022-2025)/Argentina%20Primera%20Divisi%C3%B3n_2025.xlsx",
    "Belgium Pro League": "https://github.com/futpythontrader/YouTube/raw/refs/heads/main/Bases_de_Dados/FootyStats/Bases_de_Dados_(2022-2025)/Belgium%20Pro%20League_20242025.xlsx",
    "Brasil Serie A": "https://github.com/futpythontrader/YouTube/raw/refs/heads/main/Bases_de_Dados/FootyStats/Bases_de_Dados_(2022-2025)/Brazil%20Serie%20A_2025.xlsx",
    "England Championship": "https://github.com/futpythontrader/YouTube/raw/refs/heads/main/Bases_de_Dados/FootyStats/Bases_de_Dados_(2022-2025)/England%20Championship_20242025.xlsx",
    "England EFL League One": "https://github.com/futpythontrader/YouTube/raw/refs/heads/main/Bases_de_Dados/FootyStats/Bases_de_Dados_(2022-2025)/England%20EFL%20League%20One_20242025.xlsx",
    "England Premier League": "https://github.com/futpythontrader/YouTube/raw/refs/heads/main/Bases_de_Dados/FootyStats/Bases_de_Dados_(2022-2025)/England%20Premier%20League_20242025.xlsx",
    "France Ligue 1": "https://github.com/futpythontrader/YouTube/raw/refs/heads/main/Bases_de_Dados/FootyStats/Bases_de_Dados_(2022-2025)/France%20Ligue%201_20242025.xlsx",
    "France Ligue 2": "https://github.com/futpythontrader/YouTube/raw/refs/heads/main/Bases_de_Dados/FootyStats/Bases_de_Dados_(2022-2025)/France%20Ligue%202_20242025.xlsx",
    "Germany 2. Bundesliga": "https://github.com/futpythontrader/YouTube/raw/refs/heads/main/Bases_de_Dados/FootyStats/Bases_de_Dados_(2022-2025)/Germany%202.%20Bundesliga_20242025.xlsx",
    "Germany Bundesliga": "https://github.com/futpythontrader/YouTube/raw/refs/heads/main/Bases_de_Dados/FootyStats/Bases_de_Dados_(2022-2025)/Germany%20Bundesliga_20242025.xlsx",
    "Italy Serie A": "https://github.com/futpythontrader/YouTube/raw/refs/heads/main/Bases_de_Dados/FootyStats/Bases_de_Dados_(2022-2025)/Italy%20Serie%20A_20232024.xlsx",
    "Japan J1 League": "https://github.com/futpythontrader/YouTube/raw/refs/heads/main/Bases_de_Dados/FootyStats/Bases_de_Dados_(2022-2025)/Japan%20J1%20League_2024.xlsx",
    "Netherlands Eerste Divisie": "https://github.com/futpythontrader/YouTube/raw/refs/heads/main/Bases_de_Dados/FootyStats/Bases_de_Dados_(2022-2025)/Netherlands%20Eredivisie_20242025.xlsx",
    "Portugal Liga NOS": "https://github.com/futpythontrader/YouTube/raw/refs/heads/main/Bases_de_Dados/FootyStats/Bases_de_Dados_(2022-2025)/Portugal%20Liga%20NOS_20242025.xlsx",
    "Portugal LigaPro": "https://github.com/futpythontrader/YouTube/raw/refs/heads/main/Bases_de_Dados/FootyStats/Bases_de_Dados_(2022-2025)/Portugal%20LigaPro_20242025.xlsx",
    "Spain La Liga": "https://github.com/futpythontrader/YouTube/raw/refs/heads/main/Bases_de_Dados/FootyStats/Bases_de_Dados_(2022-2025)/Spain%20La%20Liga_20242025.xlsx",
    "Turkey Süper Lig": "https://github.com/futpythontrader/YouTube/raw/refs/heads/main/Bases_de_Dados/FootyStats/Bases_de_Dados_(2022-2025)/Turkey%20S%C3%BCper%20Lig_20242025.xlsx",
    "USA MLS": "https://github.com/futpythontrader/YouTube/raw/refs/heads/main/Bases_de_Dados/FootyStats/Bases_de_Dados_(2022-2025)/USA%20MLS_2025.xlsx" }  # Mantendo o dicionário original

# Função para carregar e concatenar os dados de todas as ligas
@st.cache_data(show_spinner=True)
def load_all_data():
    dfs = []
    for league, url in data_sources.items():
        try:
            response = requests.get(url)
            file = BytesIO(response.content)
            df = pd.read_excel(file)
            df['League'] = league  # adiciona a coluna com o nome da liga
            dfs.append(df)
        except Exception as e:
            st.error(f"Erro ao carregar dados da liga {league}: {e}")
    if dfs:
        return pd.concat(dfs, ignore_index=True)
    else:
        return pd.DataFrame()

data = load_all_data()

st.title("Dashboard de Análise de Futebol")

# Seleção de times
times = sorted(set(data['Home'].unique()).union(set(data['Away'].unique())))
selecionados = st.multiselect('Selecione um ou dois times para comparar', times)

if selecionados:
    df_selecionado = data[(data['Home'].isin(selecionados)) | (data['Away'].isin(selecionados))]
    
    # Estatísticas de gols
    st.subheader("Estatísticas de Gols")
    fig_goals = px.histogram(df_selecionado, x='TotalGoals_FT', title='Distribuição de Gols por Partida')
    st.plotly_chart(fig_goals)
    
    # Odds Over/Under
    st.subheader("Odds Over/Under 2.5 FT")
    fig_odds = px.box(df_selecionado, y=['Odd_Over25_FT', 'Odd_Under25_FT'], title='Odds Over/Under 2.5 FT')
    st.plotly_chart(fig_odds)
    
    # Estatísticas de Chutes
    st.subheader("Estatísticas de Chutes")
    fig_shots = px.bar(df_selecionado, x='Date', y=['Shots_H', 'Shots_A'], title='Chutes por Jogo', barmode='group')
    st.plotly_chart(fig_shots)
    
    # Escanteios
    st.subheader("Escanteios")
    fig_corners = px.line(df_selecionado, x='Date', y='TotalCorners_FT', title='Número de Escanteios por Jogo')
    st.plotly_chart(fig_corners)
    
else:
    st.write("Selecione um ou dois times para visualizar as estatísticas.")
