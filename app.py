import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import math
import difflib

# CSS personalizado
css = """
<style>
/* Cor de fundo da aplicação */
.stApp {
    background-color: #0f0d09;
}

/* Estilo para os títulos */
h1, h2, h3 {
    font-family: 'Arial', sans-serif;
    color: #333333;
}
</style>
"""

# Incorpora o CSS no aplicativo
st.markdown(css, unsafe_allow_html=True)

# Dicionário com as URLs das bases de dados de diversas ligas
data_sources = {
    "Argentina Primera División": "https://github.com/futpythontrader/YouTube/raw/refs/heads/main/Bases_de_Dados/FootyStats/Bases_de_Dados_(2022-2025)/Argentina%20Primera%20Divisi%C3%B3n_2025.xlsx",
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
    "USA MLS": "https://github.com/futpythontrader/YouTube/raw/refs/heads/main/Bases_de_Dados/FootyStats/Bases_de_Dados_(2022-2025)/USA%20MLS_2025.xlsx"
}

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
        return pd.DataFrame()  # retorna DataFrame vazio se não carregar nada

data = load_all_data()

# Cria uma lista de todos os times disponíveis (tanto de casa quanto visitantes)
teams = set(data['Home'].unique()).union(set(data['Away'].unique()))
# Cria um conjunto e um mapeamento para comparação case insensitive
teams_lower = {team.lower() for team in teams}
team_map = {team.lower(): team for team in teams}

st.title("Análise de Futebol - Predição de Partidas")
st.write("Insira os nomes dos times para análise:")

# Entrada dos times e das odds reais do mercado
input_home = st.text_input("Time da Casa").strip()
input_away = st.text_input("Time Visitante").strip()
market_odd_input = st.text_input("Odd Real do Mercado para Over 2.5 gols", value="")
market_odd_back = st.text_input("Odd Real do Mercado para Back Favorito", value="")
market_odd_lay = st.text_input("Odd Real do Mercado para Lay Zebra", value="")
# Nova entrada para o mercado de Ambas Marcam
market_odd_both = st.text_input("Odd Real do Mercado para Ambas Marcam", value="")

# Função para buscar times similares (usando cutoff=0.4)
def find_similar_team(input_team, teams_set, cutoff=0.4):
    matches = difflib.get_close_matches(input_team.lower(), teams_set, n=5, cutoff=cutoff)
    return [team_map.get(match, match) for match in matches]

if st.button("Analisar Partida"):
    if not input_home or not input_away:
        st.error("Por favor, insira os nomes dos dois times.")
    else:
        input_home_lower = input_home.lower()
        input_away_lower = input_away.lower()
        
        # Verifica se o time da casa existe; se não, tenta sugestões automáticas
        if input_home_lower not in teams_lower:
            similar_home = find_similar_team(input_home, teams_lower)
            if similar_home:
                if len(similar_home) == 1:
                    home_team = similar_home[0]
                    st.info(f"Time da Casa não encontrado exatamente. Usando a sugestão: {home_team}")
                else:
                    st.error(f"Time da Casa não encontrado. Você quis dizer: {', '.join(similar_home)}?")
                    st.stop()
            else:
                st.error("Time da Casa não encontrado e nenhuma sugestão foi encontrada.")
                st.stop()
        else:
            home_team = team_map[input_home_lower]
        
        # Verifica se o time visitante existe; se não, tenta sugestões automáticas
        if input_away_lower not in teams_lower:
            similar_away = find_similar_team(input_away, teams_lower)
            if similar_away:
                if len(similar_away) == 1:
                    away_team = similar_away[0]
                    st.info(f"Time Visitante não encontrado exatamente. Usando a sugestão: {away_team}")
                else:
                    st.error(f"Time Visitante não encontrado. Você quis dizer: {', '.join(similar_away)}?")
                    st.stop()
            else:
                st.error("Time Visitante não encontrado e nenhuma sugestão foi encontrada.")
                st.stop()
        else:
            away_team = team_map[input_away_lower]
        
        # Filtra os dados para cada time
        home_matches = data[data['Home'] == home_team]
        away_matches = data[data['Away'] == away_team]
        
        if home_matches.empty or away_matches.empty:
            st.error("Não foram encontrados dados suficientes para um ou ambos os times. Verifique a disponibilidade dos dados.")
        else:
            # Estatísticas do time da casa
            home_avg_goals_scored = home_matches['Goals_H_FT'].mean()
            home_avg_goals_conceded = home_matches['Goals_A_FT'].mean()
            
            # Estatísticas do time visitante
            away_avg_goals_scored = away_matches['Goals_A_FT'].mean()
            away_avg_goals_conceded = away_matches['Goals_H_FT'].mean()
            
            st.subheader(f"Estatísticas de {home_team} (Casa)")
            st.write(f"Média de Gols Marcados: {home_avg_goals_scored:.2f}")
            st.write(f"Média de Gols Sofridos: {home_avg_goals_conceded:.2f}")
            
            st.subheader(f"Estatísticas de {away_team} (Fora)")
            st.write(f"Média de Gols Marcados: {away_avg_goals_scored:.2f}")
            st.write(f"Média de Gols Sofridos: {away_avg_goals_conceded:.2f}")
            
            # Cálculo dos gols esperados na partida
            expected_home_goals = home_avg_goals_scored
            expected_away_goals = away_avg_goals_scored
            lambda_total = expected_home_goals + expected_away_goals
            st.subheader("Previsão de Gols")
            st.write(f"Gols esperados na partida (total): {lambda_total:.2f}")
            
            # Cálculo da probabilidade de over 2.5 gols via distribuição de Poisson
            p0 = math.exp(-lambda_total)
            p1 = lambda_total * math.exp(-lambda_total)
            p2 = (lambda_total**2 / 2) * math.exp(-lambda_total)
            prob_under_2_5 = p0 + p1 + p2
            prob_over_2_5 = 1 - prob_under_2_5
            fair_odd = 1 / prob_over_2_5 if prob_over_2_5 > 0 else None
            
            st.subheader("Cálculo da Odd Justa para Over 2.5 Gols")
            st.write(f"Probabilidade de over 2.5 gols: {prob_over_2_5*100:.2f}%")
            if fair_odd:
                st.write(f"Odd Justa: {fair_odd:.2f}")
            else:
                st.error("Não foi possível calcular a odd justa.")
            
            # Comparação com a odd real do mercado para Over 2.5 gols
            try:
                market_odd = float(market_odd_input)
                st.subheader("Análise de Valor da Aposta para Over 2.5 Gols")
                if fair_odd:
                    if market_odd > fair_odd:
                        st.success("A aposta pode ter valor (valor esperado positivo).")
                    else:
                        st.warning("A aposta pode não ter valor.")
                else:
                    st.error("Não foi possível comparar, pois a odd justa não pôde ser calculada.")
            except ValueError:
                st.error("Por favor, insira uma odd real válida para Over 2.5 gols.")
            
            # ---- Adição dos mercados Back Favorito e Lay Zebra ----
            def poisson_probability(k, lambd):
                return (lambd**k) * math.exp(-lambd) / math.factorial(k)
            
            def compute_match_probabilities(lambda_home, lambda_away, max_goals=10):
                home_win = 0
                draw = 0
                away_win = 0
                for x in range(max_goals+1):
                    for y in range(max_goals+1):
                        p = poisson_probability(x, lambda_home) * poisson_probability(y, lambda_away)
                        if x > y:
                            home_win += p
                        elif x == y:
                            draw += p
                        else:
                            away_win += p
                return {'home_win': home_win, 'draw': draw, 'away_win': away_win}
            
            # Calcula as probabilidades de vitória, empate e derrota
            probs = compute_match_probabilities(expected_home_goals, expected_away_goals)
            
            # Determina o favorito com base nos gols esperados
            if expected_home_goals > expected_away_goals:
                favorite = home_team
                underdog = away_team
                back_favorito_prob = probs['home_win']
                lay_zebra_prob = probs['away_win']
            elif expected_home_goals < expected_away_goals:
                favorite = away_team
                underdog = home_team
                back_favorito_prob = probs['away_win']
                lay_zebra_prob = probs['home_win']
            else:
                favorite = 'Indefinido (times iguais)'
                underdog = 'Indefinido (times iguais)'
                back_favorito_prob = probs['home_win']
                lay_zebra_prob = probs['away_win']
            
            fair_odd_back = 1 / back_favorito_prob if back_favorito_prob > 0 else None
            fair_odd_lay = 1 / lay_zebra_prob if lay_zebra_prob > 0 else None
            
            st.subheader("Cálculo da Odd Justa para Back Favorito e Lay Zebra")
            st.write(f"Probabilidade de vitória do favorito ({favorite}): {back_favorito_prob*100:.2f}%")
            if fair_odd_back:
                st.write(f"Odd Justa para Back Favorito: {fair_odd_back:.2f}")
            else:
                st.error("Não foi possível calcular a odd justa para Back Favorito.")
            
            st.write(f"Probabilidade de vitória do azarão ({underdog}): {lay_zebra_prob*100:.2f}%")
            if fair_odd_lay:
                st.write(f"Odd Justa para Lay Zebra: {fair_odd_lay:.2f}")
            else:
                st.error("Não foi possível calcular a odd justa para Lay Zebra.")
            
            # Comparação com as odds reais do mercado para Back Favorito e Lay Zebra
            try:
                market_odd_back_val = float(market_odd_back)
                market_odd_lay_val = float(market_odd_lay)
                
                st.subheader("Análise de Valor da Aposta para Back Favorito")
                if fair_odd_back:
                    if market_odd_back_val > fair_odd_back:
                        st.success("A aposta no Back Favorito pode ter valor (valor esperado positivo).")
                    else:
                        st.warning("A aposta no Back Favorito pode não ter valor.")
                else:
                    st.error("Não foi possível comparar, pois a odd justa para Back Favorito não pôde ser calculada.")
                
                st.subheader("Análise de Valor da Aposta para Lay Zebra")
                if fair_odd_lay:
                    if market_odd_lay_val > fair_odd_lay:
                        st.success("A aposta no Lay Zebra pode ter valor (valor esperado positivo).")
                    else:
                        st.warning("A aposta no Lay Zebra pode não ter valor.")
                else:
                    st.error("Não foi possível comparar, pois a odd justa para Lay Zebra não pôde ser calculada.")
            except ValueError:
                st.error("Por favor, insira odds reais válidas para Back Favorito e Lay Zebra.")
            
            # ---- Adição do mercado de Ambas Marcam ----
            # Cálculo da probabilidade de ambas as equipes marcarem
            prob_both = (1 - math.exp(-expected_home_goals)) * (1 - math.exp(-expected_away_goals))
            fair_odd_both = 1 / prob_both if prob_both > 0 else None
            
            st.subheader("Cálculo da Odd Justa para Ambas Marcam")
            st.write(f"Probabilidade de ambas marcarem: {prob_both*100:.2f}%")
            if fair_odd_both:
                st.write(f"Odd Justa para Ambas Marcam: {fair_odd_both:.2f}")
            else:
                st.error("Não foi possível calcular a odd justa para Ambas Marcam.")
            
            # Comparação com a odd real do mercado para Ambas Marcam
            try:
                market_odd_both_val = float(market_odd_both)
                st.subheader("Análise de Valor da Aposta para Ambas Marcam")
                if fair_odd_both:
                    if market_odd_both_val > fair_odd_both:
                        st.success("A aposta para Ambas Marcam pode ter valor (valor esperado positivo).")
                    else:
                        st.warning("A aposta para Ambas Marcam pode não ter valor.")
                else:
                    st.error("Não foi possível comparar, pois a odd justa para Ambas Marcam não pôde ser calculada.")
            except ValueError:
                st.error("Por favor, insira uma odd real válida para Ambas Marcam.")
