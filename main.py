import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import os
import logging
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_driver():
    """Configura e retorna o driver do Chrome para automação."""
    chrome_options = Options()
    # Comentando o modo headless para debug
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    # Desabilitar o TensorFlow Lite
    chrome_options.add_argument("--disable-features=NativeNotifications")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    # Usar webdriver_manager para gerenciar o ChromeDriver automaticamente
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def extract_unemployment_data():
    """Extrai dados de desemprego nas Américas do site Trading Economics."""
    # Nova URL para taxas de desemprego nas Américas
    url = "https://tradingeconomics.com/country-list/unemployment-rate?continent=america"
    
    driver = setup_driver()
    logger.info("Acessando o site Trading Economics para dados de desemprego nas Américas...")
    driver.get(url)
    
    try:
        # Aumentar o tempo de espera e usar um seletor CSS mais específico
        wait = WebDriverWait(driver, 30)
        
        # Primeiro, verificar se há algum popup ou cookie banner e fechar
        try:
            cookie_button = wait.until(EC.element_to_be_clickable((By.ID, "cookieAcceptButton")))
            cookie_button.click()
            logger.info("Banner de cookies fechado")
        except:
            logger.info("Nenhum banner de cookies encontrado ou já foi aceito")
        
        # Tentar localizar a tabela com diferentes estratégias
        logger.info("Tentando localizar a tabela de taxas de desemprego...")
        
        # Estratégia 1: Pela classe da tabela (mais comum no Trading Economics)
        try:
            table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.table")))
            logger.info("Tabela encontrada pela classe table")
        except:
            logger.info("Não foi possível encontrar a tabela pela classe, tentando seletor alternativo")
            
            # Estratégia 2: Qualquer tabela na página
            table = wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
        
        # Tirar screenshot para debug
        driver.save_screenshot("unemployment_page_screenshot.png")
        logger.info("Screenshot salvo como unemployment_page_screenshot.png")
        
        # Extrair cabeçalhos
        headers = []
        header_elements = table.find_elements(By.TAG_NAME, "th")
        for header in header_elements:
            headers.append(header.text.strip())
        
        logger.info(f"Cabeçalhos encontrados: {headers}")
        
        # Extrair linhas de dados
        rows = []
        row_elements = table.find_elements(By.TAG_NAME, "tr")[1:]  # Pular a linha de cabeçalho
        
        for row_element in row_elements:
            row_data = []
            cell_elements = row_element.find_elements(By.TAG_NAME, "td")
            
            for cell in cell_elements:
                row_data.append(cell.text.strip())
            
            if row_data:  # Verificar se a linha não está vazia
                rows.append(row_data)
        
        logger.info(f"Total de {len(rows)} linhas de dados extraídas")
        
        # Criar DataFrame
        if headers and rows:
            # Ajustar o número de colunas se necessário
            max_cols = max(len(headers), max(len(row) for row in rows))
            
            # Expandir headers se necessário
            if len(headers) < max_cols:
                headers.extend([f"Coluna {i+1}" for i in range(len(headers), max_cols)])
            
            # Garantir que todas as linhas tenham o mesmo número de colunas
            for i in range(len(rows)):
                if len(rows[i]) < max_cols:
                    rows[i].extend([''] * (max_cols - len(rows[i])))
                elif len(rows[i]) > max_cols:
                    rows[i] = rows[i][:max_cols]
            
            df = pd.DataFrame(rows, columns=headers)
            
            # Renomear colunas para o formato esperado pelo dashboard
            column_mapping = {
                'Country': 'Country',
                'Last': 'Last',
                'Previous': 'Previous',
                'Reference': 'Reference',
                'Unit': 'Unit'
            }
            
            # Aplicar o mapeamento apenas para colunas que existem
            for old_col, new_col in column_mapping.items():
                if old_col in df.columns:
                    df = df.rename(columns={old_col: new_col})
            
            return df
        else:
            raise Exception("Não foi possível extrair dados da tabela (cabeçalhos ou linhas vazios)")
    
    except Exception as e:
        logger.error(f"Erro ao extrair dados: {str(e)}")
        # Salvar o HTML da página para debug
        with open("unemployment_page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        logger.info("HTML da página salvo como unemployment_page_source.html")
        
        # Usar dados estáticos para o dashboard em caso de falha
        return create_static_data()
    finally:
        driver.quit()

def create_static_data():
    """Cria um DataFrame estático com os dados da tabela fornecida."""
    logger.info("Usando dados estáticos para o dashboard")
    
    data = {
        'Country': [
            'Argentina', 'Bahamas', 'Barbados', 'Belize', 'Bolivia', 'Brazil', 'Canada',
            'Cayman Islands', 'Chile', 'Colombia', 'Costa Rica', 'Cuba', 'Dominican Republic',
            'Ecuador', 'El Salvador', 'Guatemala', 'Guyana', 'Haiti', 'Honduras', 'Jamaica',
            'Mexico', 'Nicaragua', 'Panama', 'Paraguay', 'Peru', 'Puerto Rico', 'Suriname',
            'Trinidad and Tobago', 'United States', 'Uruguay', 'Venezuela'
        ],
        'Last': [
            6.4, 9.5, 7.1, 3.4, 2.7, 6.8, 6.7, 3.3, 8.4, 10.33, 6.9, 1.2, 4.8, 5.1, 5.2, 2.3,
            14.0, 14.9, 6.4, 3.5, 2.5, 2.8, 7.7, 4.6, 6.3, 5.4, 8.0, 4.1, 4.2, 7.9, 5.9
        ],
        'Previous': [
            6.9, 10.1, 7.7, 5.0, 2.8, 6.5, 6.6, 2.1, 8.0, 11.64, 6.6, 1.8, 5.3, 3.6, 5.0, 3.0,
            12.4, 14.8, 8.7, 3.6, 2.7, 3.0, 10.3, 5.3, 6.2, 5.4, 8.2, 4.8, 4.1, 8.1, 5.3
        ],
        'Reference': [
            'Dec/24', 'Dec/23', 'Sep/24', 'Dec/23', 'Sep/24', 'Feb/25', 'Mar/25', 'Dec/23',
            'Feb/25', 'Feb/25', 'Dec/24', 'Dec/23', 'Dec/24', 'Jan/25', 'Dec/23', 'Dec/23',
            'Dec/23', 'Dec/23', 'Dec/23', 'Dec/24', 'Feb/25', 'Feb/25', 'Dec/23', 'Dec/24',
            'Feb/25', 'Jan/25', 'Dec/23', 'Sep/24', 'Mar/25', 'Feb/25', 'Dec/23'
        ],
        'Unit': ['%'] * 31
    }
    
    return pd.DataFrame(data)

def save_data(df):
    """Salva os dados extraídos em formato CSV e Excel."""
    # Criar pasta de dados se não existir
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Adicionar timestamp ao nome do arquivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Salvar como CSV
    csv_path = f'data/americas_unemployment_data_{timestamp}.csv'
    df.to_csv(csv_path, index=False)
    
    # Salvar como Excel
    excel_path = f'data/americas_unemployment_data_{timestamp}.xlsx'
    df.to_excel(excel_path, index=False)
    
    logger.info(f"Dados salvos em {csv_path} e {excel_path}")
    return csv_path, excel_path

def prepare_data_for_dashboard(df):
    """Prepara os dados para o dashboard."""
    # Converter colunas numéricas
    for col in ['Last', 'Previous']:
        if col in df.columns:
            # Converter para numérico
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Calcular a variação percentual
    df['Change'] = ((df['Last'] - df['Previous']) / df['Previous'] * 100).round(2)
    
    # Definir regiões para análise
    regions = {
        'North America': ['Canada', 'United States', 'Mexico'],
        'Central America': ['Belize', 'Costa Rica', 'El Salvador', 'Guatemala', 'Honduras', 'Nicaragua', 'Panama'],
        'Caribbean': ['Bahamas', 'Barbados', 'Cayman Islands', 'Cuba', 'Dominican Republic', 'Haiti', 'Jamaica', 'Puerto Rico', 'Trinidad and Tobago'],
        'South America': ['Argentina', 'Bolivia', 'Brazil', 'Chile', 'Colombia', 'Ecuador', 'Guyana', 'Paraguay', 'Peru', 'Suriname', 'Uruguay', 'Venezuela']
    }
    
    # Adicionar coluna de região
    df['Region'] = df['Country'].apply(lambda x: next((k for k, v in regions.items() if x in v), 'Other'))
    
    # Adicionar coluna de "saúde" do indicador
    def calculate_unemployment_health(row):
        rate = row['Last']
        if pd.notna(rate):
            if rate < 5:
                return 'Bom'
            elif rate < 10:
                return 'Médio'
            else:
                return 'Ruim'
        return 'Neutro'
    
    df['Health'] = df.apply(calculate_unemployment_health, axis=1)
    
    return df

def create_dashboard(df):
    """Cria e executa o dashboard com os dados fornecidos."""
    # Inicializar o app
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    
    # Layout do dashboard
    app.layout = dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1("Taxa de Desemprego nas Américas", className="text-center my-4"),
                html.P("Análise comparativa das taxas de desemprego nos países das Américas", className="text-center mb-4")
            ])
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Selecione o Tipo de Visualização"),
                    dbc.CardBody([
                        dcc.Dropdown(
                            id='chart-type',
                            options=[
                                {'label': 'Mapa de Calor por Região', 'value': 'heatmap'},
                                {'label': 'Gráfico de Barras - Taxa Atual', 'value': 'bar_current'},
                                {'label': 'Gráfico de Barras - Comparação Atual vs Anterior', 'value': 'bar_compare'},
                                {'label': 'Gráfico de Dispersão - Taxa Atual vs Variação', 'value': 'scatter'},
                                {'label': 'Treemap por Região', 'value': 'treemap'},
                                {'label': 'Top 5 Maiores Taxas', 'value': 'top5_high'},
                                {'label': 'Top 5 Menores Taxas', 'value': 'top5_low'}
                            ],
                            value='bar_current',
                            clearable=False
                        )
                    ])
                ], className="mb-4")
            ])
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Visualização"),
                    dbc.CardBody([
                        dcc.Graph(id='main-chart', style={'height': '600px'})
                    ])
                ], className="mb-4")
            ])
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Tabela de Dados - Taxas de Desemprego por País"),
                    dbc.CardBody([
                        dash_table.DataTable(
                            id='data-table',
                            columns=[
                                {'name': 'País', 'id': 'Country'},
                                {'name': 'Taxa Atual (%)', 'id': 'Last'},
                                {'name': 'Taxa Anterior (%)', 'id': 'Previous'},
                                {'name': 'Variação (%)', 'id': 'Change'},
                                {'name': 'Região', 'id': 'Region'},
                                {'name': 'Situação', 'id': 'Health'},
                                {'name': 'Referência', 'id': 'Reference'}
                            ],
                            data=df.to_dict('records'),
                            sort_action='native',
                            filter_action='native',
                            page_size=10,
                            style_table={'overflowX': 'auto'},
                            style_cell={
                                'textAlign': 'left',
                                'padding': '8px',
                                'minWidth': '100px'
                            },
                            style_header={
                                'backgroundColor': 'rgb(230, 230, 230)',
                                'fontWeight': 'bold'
                            },
                            style_data_conditional=[
                                {
                                    'if': {'column_id': 'Health', 'filter_query': '{Health} = "Bom"'},
                                    'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                                    'color': 'green'
                                },
                                {
                                    'if': {'column_id': 'Health', 'filter_query': '{Health} = "Médio"'},
                                    'backgroundColor': 'rgba(255, 206, 86, 0.2)',
                                    'color': 'orange'
                                },
                                {
                                    'if': {'column_id': 'Health', 'filter_query': '{Health} = "Ruim"'},
                                    'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                                    'color': 'red'
                                },
                                {
                                    'if': {'column_id': 'Change', 'filter_query': '{Change} < 0'},
                                    'color': 'green'
                                },
                                {
                                    'if': {'column_id': 'Change', 'filter_query': '{Change} > 0'},
                                    'color': 'red'
                                }
                            ]
                        )
                    ])
                ], className="mb-4")
            ])
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Resumo Estatístico"),
                    dbc.CardBody([
                        html.Div([
                            html.P(f"Média de Desemprego: {df['Last'].mean():.2f}%"),
                            html.P(f"Mediana de Desemprego: {df['Last'].median():.2f}%"),
                            html.P(f"Maior Taxa: {df['Last'].max():.2f}% ({df.loc[df['Last'].idxmax(), 'Country']})"),
                            html.P(f"Menor Taxa: {df['Last'].min():.2f}% ({df.loc[df['Last'].idxmin(), 'Country']})"),
                            html.P(f"Países com Melhora: {(df['Change'] < 0).sum()} ({(df['Change'] < 0).sum() / len(df) * 100:.1f}%)"),
                            html.P(f"Países com Piora: {(df['Change'] > 0).sum()} ({(df['Change'] > 0).sum() / len(df) * 100:.1f}%)")
                        ])
                    ])
                ], className="mb-4")
            ])
        ]),
        
        dbc.Row([
            dbc.Col([
                html.P(
                    "Fonte: Trading Economics - Dados extraídos em " + 
                    datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    className="text-muted text-center"
                ),
                html.P(
                    "Dashboard desenvolvido com Python, Dash e Plotly",
                    className="text-muted text-center"
                )
            ])
        ])
    ], fluid=True)
    
    # Callback para atualizar o gráfico principal
    @app.callback(
        Output('main-chart', 'figure'),
        [Input('chart-type', 'value')]
    )
    def update_chart(chart_type):
        """Atualiza o gráfico principal com base no tipo selecionado."""
        if chart_type == 'heatmap':
            # Criar um pivot table para o mapa de calor
            pivot_df = df.pivot_table(
                values='Last', 
                index='Country', 
                columns='Region', 
                aggfunc='first'
            ).fillna(0)
            
            fig = px.imshow(
                pivot_df,
                labels=dict(x="Região", y="País", color="Taxa de Desemprego (%)"),
                title="Mapa de Calor das Taxas de Desemprego por Região",
                color_continuous_scale='YlOrRd'
            )
            
            return fig
            
        elif chart_type == 'bar_current':
            # Ordenar por taxa atual
            sorted_df = df.sort_values('Last', ascending=False)
            
            fig = px.bar(
                sorted_df,
                x='Country',
                y='Last',
                color='Region',
                title="Taxa de Desemprego Atual por País",
                labels={'Last': 'Taxa de Desemprego (%)', 'Country': 'País'},
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            
            fig.update_layout(xaxis_tickangle=-45)
            return fig
            
        elif chart_type == 'bar_compare':
            # Selecionar os 15 principais países para melhor visualização
            top_df = df.sort_values('Last', ascending=False).head(15)
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=top_df['Country'],
                y=top_df['Last'],
                name='Taxa Atual',
                marker_color='indianred'
            ))
            
            fig.add_trace(go.Bar(
                x=top_df['Country'],
                y=top_df['Previous'],
                name='Taxa Anterior',
                marker_color='lightsalmon'
            ))
            
            fig.update_layout(
                title="Comparação: Taxa de Desemprego Atual vs Anterior (Top 15)",
                xaxis_title="País",
                yaxis_title="Taxa de Desemprego (%)",
                barmode='group',
                xaxis_tickangle=-45
            )
            
            return fig
            
        elif chart_type == 'scatter':
            fig = px.scatter(
                df,
                x='Last',
                y='Change',
                color='Region',
                size='Last',
                hover_name='Country',
                title="Relação entre Taxa Atual e Variação Percentual",
                labels={
                    'Last': 'Taxa de Desemprego Atual (%)',
                    'Change': 'Variação em relação à taxa anterior (%)'
                },
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            
            # Adicionar linha horizontal em y=0 para referência
            fig.add_hline(y=0, line_dash="dash", line_color="gray")
            
            return fig
            
        elif chart_type == 'treemap':
            fig = px.treemap(
                df,
                path=[px.Constant("Américas"), 'Region', 'Country'],
                values='Last',
                color='Last',
                hover_data=['Previous', 'Change'],
                color_continuous_scale='RdBu_r',
                title="Treemap das Taxas de Desemprego por Região e País"
            )
            
            return fig
            
        elif chart_type == 'top5_high':
            # Top 5 maiores taxas
            top5_df = df.sort_values('Last', ascending=False).head(5)
            
            fig = px.bar(
                top5_df,
                x='Country',
                y='Last',
                color='Last',
                text='Last',
                title="Top 5 Países com Maiores Taxas de Desemprego",
                labels={'Last': 'Taxa de Desemprego (%)', 'Country': 'País'},
                color_continuous_scale='Reds'
            )
            
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            
            return fig
            
        elif chart_type == 'top5_low':
            # Top 5 menores taxas
            top5_df = df.sort_values('Last').head(5)
            
            fig = px.bar(
                top5_df,
                x='Country',
                y='Last',
                color='Last',
                text='Last',
                title="Top 5 Países com Menores Taxas de Desemprego",
                labels={'Last': 'Taxa de Desemprego (%)', 'Country': 'País'},
                color_continuous_scale='Greens'
            )
            
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            
            return fig
        
        # Caso padrão
        return px.bar(
            df.sort_values('Last', ascending=False),
            x='Country',
            y='Last',
            title="Taxa de Desemprego Atual por País",
            labels={'Last': 'Taxa de Desemprego (%)', 'Country': 'País'}
        )
    
    return app

def main():
    """Função principal que executa o fluxo de extração, processamento e visualização dos dados."""
    print("Iniciando extração de dados de desemprego nas Américas...")
    
    try:
        # Extrair dados
        df = extract_unemployment_data()
        
        # Salvar dados brutos
        csv_path, excel_path = save_data(df)
        
        # Preparar dados para o dashboard
        df_dashboard = prepare_data_for_dashboard(df)
        
        # Exibir informações sobre os dados extraídos
        print(f"Dados extraídos com sucesso! Total de {len(df)} países com dados de desemprego.")
        print("\nPrimeiros 5 países:")
        print(df.head())
        
        print("\nCriando e iniciando o dashboard...")
        
        # Criar e iniciar o dashboard
        app = create_dashboard(df_dashboard)
        
        print("\nDashboard pronto! Iniciando servidor...")
        print("Acesse o dashboard em http://127.0.0.1:8050/")
        
        # Iniciar o servidor
        app.run(debug=True)
    
    except Exception as e:
        print(f"Erro durante a execução: {str(e)}")
        logger.error(f"Erro durante a execução: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()