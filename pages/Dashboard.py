import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import plotly.express as px
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Análise Futebolística Avançada",
    page_icon="⚽",
    layout="wide"
)

# Dicionário com as URLs das bases de dados
data_sources = {
    "Argentina Primera División": "https://github.com/futpythontrader/YouTube/raw/refs/heads/main/Bases_de_Dados/FootyStats/Bases_de_Dados_(2022-2025)/Argentina%20Primera%20Divisi%C3%B3n_2025.xlsx",
    "Belgium Pro League": "https://github.com/futpythontrader/YouTube/raw/refs/heads/main/Bases_de_Dados/FootyStats/Bases_de_Dados_(2022-2025)/Belgium%20Pro%20League_20242025.xlsx",
    "Brasil Serie A": "https://github.com/futpythontrader/YouTube/raw/refs/heads/main/Bases_de_Dados/FootyStats/Bases_de_Dados_(2022-2025)/Brazil%20Serie%20A_2025.xlsx",
    '''"England Championship": "https://github.com/futpythontrader/YouTube/raw/refs/heads/main/Bases_de_Dados/FootyStats/Bases_de_Dados_(2022-2025)/England%20Championship_20242025.xlsx",'''
    "England EFL League One": "https://github.com/futpythontrader/YouTube/raw/refs/heads/main/Bases_de_Dados/FootyStats/Bases_de_Dados_(2022-2025)/England%20EFL%20League%20One_20242025.xlsx",
    "England Premier League": "https://github.com/futpythontrader/YouTube/raw/refs/heads/main/Bases_de_Dados/FootyStats/Bases_de_Dados_(2022-2025)/England%20Premier%20League_20242025.xlsx",
    "France Ligue 1": "https://github.com/futpythontrader/YouTube/raw/refs/heads/main/Bases_de_Dados/FootyStats/Bases_de_Dados_(2022-2025)/France%20Ligue%201_20242025.xlsx",
    "France Ligue 2": "https://github.com/futpythontrader/YouTube/raw/refs/heads/main/Bases_de_Dados/FootyStats/Bases_de_Dados_(2022-2025)/France%20Ligue%202_20242025.xlsx",
    "Germany 2. Bundesliga": "https://github.com/futpythontrader/YouTube/raw/refs/heads/main/Bases_de_Dados/FootyStats/Bases_de_Dados_(2022-2025)/Germany%202.%20Bundesliga_20242025.xlsx",
    "Germany Bundesliga": "https://github.com/futpythontrader/YouTube/raw/refs/heads/main/Bases_de_Dados/FootyStats/Bases_de_Dados_(2022-2025)/Germany%20Bundesliga_20242025.xlsx",
    "Italy Serie A": "https://github.com/futpythontrader/YouTube/raw/refs/heads/main/Bases_de_Dados/FootyStats/Bases_de_Dados_(2022-2025)/Italy%20Serie%20A_20232024.xlsx",
    "Japan J1 League": "https://github.com/futpythontrader/YouTube/raw/refs/heads/main/Bases_de_Dados/FootyStats/Bases_de_Dados_(2022-2025)/Japan%20J1%20League_2024.xlsx",
    "Netherlands Eerste Divisie": "https://github.com/futpythontrader/YouTube/raw/refs/heads/main/Bases_de_Dados/FootyStats/Bases_de_Dados_(2022-2025)/Netherlands%20Eredivisie_20242025.xlsx",
    "Norway First Division": "https://github.com/futpythontrader/YouTube/raw/refs/heads/main/Bases_de_Dados/FootyStats/Bases_de_Dados_(2022-2025)/Norway%20First%20Division_2025.xlsx",
    "Norway Eliteserien": "https://github.com/futpythontrader/YouTube/raw/refs/heads/main/Bases_de_Dados/FootyStats/Bases_de_Dados_(2022-2025)/Norway%20Eliteserien_2025.xlsx",
    "Portugal Liga NOS": "https://github.com/futpythontrader/YouTube/raw/refs/heads/main/Bases_de_Dados/FootyStats/Bases_de_Dados_(2022-2025)/Portugal%20Liga%20NOS_20242025.xlsx",
    "Portugal LigaPro": "https://github.com/futpythontrader/YouTube/raw/refs/heads/main/Bases_de_Dados/FootyStats/Bases_de_Dados_(2022-2025)/Portugal%20LigaPro_20242025.xlsx",
    "Spain La Liga": "https://github.com/futpythontrader/YouTube/raw/refs/heads/main/Bases_de_Dados/FootyStats/Bases_de_Dados_(2022-2025)/Spain%20La%20Liga_20242025.xlsx",
    "Turkey Süper Lig": "https://github.com/futpythontrader/YouTube/raw/refs/heads/main/Bases_de_Dados/FootyStats/Bases_de_Dados_(2022-2025)/Turkey%20S%C3%BCper%20Lig_20242025.xlsx",
    "USA MLS": "https://github.com/futpythontrader/YouTube/raw/refs/heads/main/Bases_de_Dados/FootyStats/Bases_de_Dados_(2022-2025)/USA%20MLS_2025.xlsx"

    # Adicione todas as outras ligas aqui
}

@st.cache_data(show_spinner="Carregando dados das ligas...")
def load_all_data():
    dfs = []
    for league, url in data_sources.items():
        try:
            response = requests.get(url)
            file = BytesIO(response.content)
            df = pd.read_excel(file)
            df['League'] = league
            dfs.append(df)
        except Exception as e:
            st.error(f"Erro na liga {league}: {str(e)}")
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

data = load_all_data()

# Pré-processamento
if not data.empty:
    data['Date'] = pd.to_datetime(data['Date']).dt.date
    data['Resultado'] = data.apply(lambda x: 
        'Vitória Casa' if x['Goals_H_FT'] > x['Goals_A_FT'] else
        'Vitória Fora' if x['Goals_H_FT'] < x['Goals_A_FT'] else
        'Empate', axis=1)
    data['TotalGoals_FT'] = pd.to_numeric(data['TotalGoals_FT'], errors='coerce').fillna(0)

# Interface principal
st.title("⚽ Painel de Análise Futebolística")
st.markdown("---")

# Sidebar com controles
with st.sidebar:
    st.header("⚙ Filtros")
    times = sorted(set(data['Home'].unique()).union(set(data['Away'].unique())))
    selecionados = st.multiselect(
        'Selecione times para análise:',
        options=times,
        max_selections=2
    )
    
    if not data.empty:
        min_date = data['Date'].min()
        max_date = data['Date'].max()
        date_range = st.date_input(
            "Período de análise:",
            [min_date, max_date],
            min_value=min_date,
            max_value=max_date
        )

# Visualização principal
if selecionados:
    df_filtrado = data[
        (data['Home'].isin(selecionados)) | 
        (data['Away'].isin(selecionados))
    ]
    
    if len(date_range) == 2:
        df_filtrado = df_filtrado[
            (df_filtrado['Date'] >= date_range[0]) & 
            (df_filtrado['Date'] <= date_range[1])
        ]

    if not df_filtrado.empty:
        # Seção de Métricas Rápidas
        st.subheader("📊 Visão Geral Instantânea")
        col1, col2, col3, col4 = st.columns(4)
        metricas = {
            'Partidas Analisadas': len(df_filtrado),
            'Média de Gols/Partida': df_filtrado['TotalGoals_FT'].mean().round(2),
            'Jogos Over 2.5': f"{len(df_filtrado[df_filtrado['TotalGoals_FT'] > 2.5])} ({len(df_filtrado[df_filtrado['TotalGoals_FT'] > 2.5])/len(df_filtrado)*100:.1f}%)",
            'Escanteios/Jogo': df_filtrado['TotalCorners_FT'].mean().round(1)
        }
        for (key, value), col in zip(metricas.items(), [col1, col2, col3, col4]):
            with col:
                st.metric(key, value)

        # Abas Principais
        tab1, tab2, tab3 = st.tabs(["📈 Desempenho", "📋 Estatísticas Detalhadas", "🔄 Evolução Temporal"])
        
        with tab1:
            st.subheader("Análise de Desempenho")
            col1, col2 = st.columns([3,2])
            
            with col1:
                fig = px.bar(
                    df_filtrado,
                    x='Date',
                    y=['Goals_H_FT', 'Goals_A_FT'],
                    title='Gols por Partida',
                    labels={'value': 'Gols', 'variable': 'Equipe'},
                    color_discrete_map={'Goals_H_FT': '#2A9D8F', 'Goals_A_FT': '#E76F51'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("Distribuição de Resultados")
                resultado_counts = df_filtrado['Resultado'].value_counts()
                fig = px.pie(
                    names=resultado_counts.index,
                    values=resultado_counts.values,
                    color=resultado_counts.index,
                    color_discrete_map={
                        'Vitória Casa': '#2A9D8F',
                        'Empate': '#E9C46A',
                        'Vitória Fora': '#E76F51'
                    }
                )
                fig.update_layout(showlegend=True)
                st.plotly_chart(fig, use_container_width=True)

        with tab2:
            st.subheader("🔍 Comparativo Detalhado")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🏠 Desempenho como Mandante**")
                home_stats = df_filtrado.groupby('Home').agg({
                    'TotalGoals_FT': 'mean',
                    'Shots_H': 'mean',
                    'Corners_H_FT': 'mean'
                }).rename(columns={
                    'TotalGoals_FT': 'Média Gols',
                    'Shots_H': 'Chutes por Jogo',
                    'Corners_H_FT': 'Escanteios por Jogo'
                }).round(2)
                
                if selecionados:
                    home_stats = home_stats.loc[selecionados]
                
                st.dataframe(
                    home_stats.style
                    .background_gradient(subset=['Média Gols'], cmap='Greens')
                    .background_gradient(subset=['Chutes por Jogo'], cmap='Blues')
                    .format("{:.2f}")
                    .set_properties(**{'text-align': 'center'}),
                    height=400
                )

            with col2:
                st.markdown("**✈️ Desempenho como Visitante**")
                away_stats = df_filtrado.groupby('Away').agg({
                    'TotalGoals_FT': 'mean',
                    'Shots_A': 'mean',
                    'Corners_A_FT': 'mean'
                }).rename(columns={
                    'TotalGoals_FT': 'Média Gols',
                    'Shots_A': 'Chutes por Jogo',
                    'Corners_A_FT': 'Escanteios por Jogo'
                }).round(2)
                
                if selecionados:
                    away_stats = away_stats.loc[selecionados]
                
                st.dataframe(
                    away_stats.style
                    .background_gradient(subset=['Média Gols'], cmap='Oranges')
                    .bar(subset=['Chutes por Jogo'], color='#5A9BD4')
                    .format("{:.2f}")
                    .set_properties(**{'text-align': 'center'}),
                    height=400
                )

            st.markdown("---")
            st.subheader("📌 Comparação Direta de Desempenho")
            
            if len(selecionados) == 2:
                try:
                    times_selecionados = selecionados
                    
                    # Estatísticas como mandante (com colunas explícitas)
                    home_stats = (
                        df_filtrado[df_filtrado['Home'].isin(times_selecionados)]
                        .groupby('Home')
                        .agg({
                            'TotalGoals_FT': 'mean',
                            'Shots_H': 'mean',
                            'Corners_H_FT': 'mean'
                        })
                        .rename(columns={
                            'TotalGoals_FT': 'TotalGoals_Home',
                            'Shots_H': 'Shots_Home',
                            'Corners_H_FT': 'Corners_Home'
                        })
                        .reindex(times_selecionados)
                        .fillna(0)
                    )
                    
                    # Estatísticas como visitante (com colunas explícitas)
                    away_stats = (
                        df_filtrado[df_filtrado['Away'].isin(times_selecionados)]
                        .groupby('Away')
                        .agg({
                            'TotalGoals_FT': 'mean',
                            'Shots_A': 'mean',
                            'Corners_A_FT': 'mean'
                        })
                        .rename(columns={
                            'TotalGoals_FT': 'TotalGoals_Away',
                            'Shots_A': 'Shots_Away',
                            'Corners_A_FT': 'Corners_Away'
                        })
                        .reindex(times_selecionados)
                        .fillna(0)
                    )
                    
                    # Combinar dados
                    comparison_data = pd.concat([home_stats, away_stats], axis=1).reset_index()
                    
                    # Selecionar colunas relevantes
                    colunas_relevantes = [
                        'index',
                        'TotalGoals_Home', 'Shots_Home', 'Corners_Home',
                        'TotalGoals_Away', 'Shots_Away', 'Corners_Away'
                    ]
                    comparison_data = comparison_data[colunas_relevantes]
                    
                    # Reformatar para o gráfico
                    comparison_data = comparison_data.melt(
                        id_vars='index', 
                        var_name='variable',
                        value_name='value'
                    )
                    
                    # Extrair estatística e tipo
                    comparison_data[['Estatística', 'Tipo']] = (
                        comparison_data['variable']
                        .str.split('_', n=1, expand=True)
                    )
                    
                    # Criar gráfico
                    fig = px.bar(
                        comparison_data,
                        x='Estatística',
                        y='value',
                        color='index',
                        barmode='group',
                        facet_row='Tipo',
                        labels={'value': 'Valor Médio', 'index': 'Time'},
                        color_discrete_sequence=['#2A9D8F', '#E76F51'],
                        text_auto='.2f'
                    )
                    
                    # Ajustar layout
                    fig.update_layout(
                        xaxis_title="Estatísticas",
                        hovermode="x unified",
                        showlegend=True,
                        height=600
                    )
                    
                    # Remover títulos redundantes
                    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                except Exception as e:
                    st.error(f"Erro na geração da comparação: {str(e)}")
            else:
                st.info("Selecione 2 times para ver a comparação direta")

        with tab3:
            st.subheader("Linha do Tempo de Desempenho")
            col1, col2 = st.columns([3, 2])
            
            with col1:
                # Gráfico de Gols
                fig_goals = px.line(
                    df_filtrado.sort_values('Date'),
                    x='Date',
                    y='TotalGoals_FT',
                    markers=True,
                    title='Evolução de Gols Totais por Partida',
                    labels={'TotalGoals_FT': 'Gols'},
                    color_discrete_sequence=['#2A9D8F']
                )
                fig_goals.update_layout(
                    height=400,
                    xaxis_title="Data",
                    yaxis_title="Total de Gols",
                    hovermode="x unified"
                )
                st.plotly_chart(fig_goals, use_container_width=True)
                
                # Gráfico de Escanteios
                fig_corners = px.bar(
                    df_filtrado.sort_values('Date'),
                    x='Date',
                    y=['Corners_H_FT', 'Corners_A_FT'],
                    title='Escanteios por Partida',
                    labels={'value': 'Escanteios', 'variable': 'Equipe'},
                    color_discrete_map={'Corners_H_FT': '#2A9D8F', 'Corners_A_FT': '#E76F51'}
                )
                fig_corners.update_layout(
                    height=400,
                    xaxis_title="Data",
                    yaxis_title="Total de Escanteios",
                    barmode='group'
                )
                st.plotly_chart(fig_corners, use_container_width=True)
            
            with col2:
                st.subheader("Últimos 10 Jogos")
                ultimos_jogos = df_filtrado.sort_values('Date', ascending=False).head(10)[[
                    'Date', 'Home', 'Away', 'Goals_H_FT', 'Goals_A_FT', 'TotalCorners_FT'
                ]]
                # Formatação de datas e estilização
                ultimos_jogos['Date'] = pd.to_datetime(ultimos_jogos['Date']).dt.strftime('%Y-%m-%d')
                
                # Ajuste de altura e largura
                st.dataframe(
                    ultimos_jogos.style
                    .format({'TotalCorners_FT': '{:.0f} ⚪'})
                    .background_gradient(subset=['Goals_H_FT', 'Goals_A_FT'], cmap='YlGnBu')
                    .set_properties(**{
                        'text-align': 'center',
                        'min-width': '150px',  # Largura mínima das colunas
                        'white-space': 'nowrap'  # Evita quebra de texto
                    })
                    .set_table_styles([{
                        'selector': 'table',
                        'props': [('height', '600px'), ('overflow-y', 'auto')]  # Altura fixa com rolagem
        }]),
        height=600  # Altura do container no Streamlit
    )

    else:
        st.warning("⚠️ Nenhum dado encontrado para os critérios selecionados")

else:
    st.info("ℹ️ Selecione times no menu lateral para iniciar a análise")

# Rodapé
st.markdown("---")
st.markdown("**Desenvolvido por Gui Santos** • Dados atualizados em: " + datetime.today().strftime('%d/%m/%Y'))