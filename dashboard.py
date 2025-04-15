import dash
from dash import dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import glob
import warnings
from datetime import datetime

# Suprimir o aviso de depreciação relacionado à análise de datas
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Encontrar o arquivo CSV mais recente na pasta data
list_of_files = glob.glob('data/*.csv')
latest_file = max(list_of_files, key=os.path.getctime) if list_of_files else None

if not latest_file:
    raise FileNotFoundError("Nenhum arquivo CSV encontrado na pasta 'data'. Execute main.py primeiro para extrair os dados.")

# Carregar os dados
df = pd.read_csv(latest_file)

# Converter colunas numéricas
for col in ['Last', 'Previous']:
    if col in df.columns:
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

















# Nova paleta de cores com quadros mais escuros e texto branco
dark_theme_colors = {
    'background': '#121212',          # Fundo muito escuro
    'card_bg': 'rgba(18, 18, 18, 0.95)', # Fundo dos cards mais escuro e quase opaco
    'card_bg_lighter': 'rgba(30, 30, 30, 0.95)', # Fundo dos cards um pouco mais claro
    'primary': '#BB86FC',             # Roxo/lilás
    'secondary': '#03DAC6',           # Verde-água
    'accent1': '#CF6679',             # Rosa
    'accent2': '#4dabf5',             # Azul
    'accent3': '#FFB74D',             # Laranja
    'text': '#FFFFFF',                # Texto branco
    'light_text': '#E0E0E0',          # Texto levemente acinzentado
    'gradient_start': '#121212',      # Gradiente início (escuro)
    'gradient_end': '#1F1F1F',        # Gradiente fim (um pouco menos escuro)
    'positive': '#4CAF50',            # Verde para valores positivos
    'negative': '#F44336',            # Vermelho para valores negativos
    'border': '#333333',              # Cor da borda dos cards
}

# Paleta para gráficos






dark_theme_palette = [
    dark_theme_colors['primary'], 
    dark_theme_colors['secondary'], 
    dark_theme_colors['accent1'], 
    dark_theme_colors['accent2'], 
    dark_theme_colors['accent3']
]


# Manter a mesma imagem de fundo (cityscape noturno com pôr do sol)
background_image = 'https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80'

# Inicializar o app Dash com tema Bootstrap e folha de estilo personalizada
app = dash.Dash(
    __name__, 
    external_stylesheets=[
        dbc.themes.DARKLY,  # Tema base escuro

        'https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;600;700&display=swap'  # Fonte Sans-serif
    ]
)

# Estilo CSS personalizado para o dropdown escuro
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            /* Estilo para o dropdown escuro */
            .Select-control, .Select-menu-outer, .Select-menu, .Select-option, .Select-value {

                background-color: #121212 !important;
                color: white !important;
            }
            .Select-value-label, .Select-option {
                color: white !important;
            }
            .Select-control, .Select-menu-outer {

                border: 1px solid #333333 !important;
            }
            .Select-option.is-focused, .Select-option:hover {

                background-color: #1F1F1F !important;
            }
            .Select-arrow {

                border-color: #BB86FC transparent transparent !important;
            }
            .Select.is-open > .Select-control .Select-arrow {

                border-color: transparent transparent #BB86FC !important;
            }
            .dash-dropdown-dark .Select-value-label {
                color: white !important;
            }
            
            /* Estilo global para texto */
            body {
                font-family: 'Open Sans', sans-serif !important;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

server = app.server

# Título do dashboard

app.title = "Dashboard de Desemprego nas Américas"

# Estilo personalizado para o container principal
app_style = {

    'background': f'linear-gradient(rgba(18, 18, 18, 0.92), rgba(31, 31, 31, 0.92)), url({background_image})',
    'backgroundSize': 'cover',
    'backgroundAttachment': 'fixed',
    'backgroundPosition': 'center',
    'minHeight': '100vh',


    'fontFamily': '"Open Sans", sans-serif',
    'color': dark_theme_colors['text'],
    'padding': '20px',
}


# Estilo para os cards (mais escuros)
card_style = {




    'backgroundColor': dark_theme_colors['card_bg'],
    'borderRadius': '8px',
    'boxShadow': '0 4px 20px rgba(0, 0, 0, 0.5)',
    'border': f'1px solid {dark_theme_colors["border"]}',
    'marginBottom': '20px',
    'backdropFilter': 'blur(10px)',

    'padding': '15px'
}

card_header_style = {
    'backgroundColor': 'transparent',


    'borderBottom': f'1px solid {dark_theme_colors["border"]}',
    'color': dark_theme_colors['primary'],
    'fontWeight': '600',
    'fontSize': '1.2rem',
    'padding': '15px 20px',
    'fontFamily': '"Open Sans", sans-serif',
}

# Estilo para os contêineres de gráficos
graph_container_style = {


    'backgroundColor': 'rgba(18, 18, 18, 0.8)',
    'borderRadius': '8px',
    'boxShadow': '0 4px 20px rgba(0, 0, 0, 0.3)',
    'padding': '15px'
}

# Layout do dashboard
app.layout = dbc.Container([
    # Div de background
    html.Div(style={
        'position': 'fixed',
        'top': 0,
        'left': 0,
        'right': 0,
        'bottom': 0,
        'backgroundImage': f'url({background_image})',
        'backgroundSize': 'cover',
        'backgroundPosition': 'center',
        'zIndex': -1,
        'opacity': 0.5,
    }),
    
    # Cabeçalho
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H1("Taxa de Desemprego nas Américas", 
                        style={

                            'fontFamily': '"Open Sans", sans-serif',
                            'fontWeight': '700',

                            'color': dark_theme_colors['text'],
                            'textAlign': 'center',
                            'marginTop': '20px',
                            'marginBottom': '10px',
                            'fontSize': '2.5rem',


                            'textShadow': '0 0 20px rgba(0, 0, 0, 0.7)',
                            'letterSpacing': '1px',
                        }),
                html.P([
                    "Análise comparativa das taxas de desemprego nos países das Américas - ",
                    html.A(
                        "Trading Economics", 
                        href="https://tradingeconomics.com/country-list/unemployment-rate?continent=america",
                        target="_blank",
                        style={

                            'color': dark_theme_colors['primary'],
                            'textDecoration': 'underline'
                        }
                    )

                ], className="text-center", style={'color': dark_theme_colors['light_text']}),
                html.Div(style={

                    'borderBottom': f'2px solid {dark_theme_colors["primary"]}',
                    'width': '60%',
                    'margin': '0 auto 30px auto',

                    'boxShadow': f'0 0 10px {dark_theme_colors["primary"]}',
                })
            ], style={

                'backgroundColor': 'rgba(18, 18, 18, 0.9)',
                'backdropFilter': 'blur(5px)',
                'padding': '20px',


                'borderRadius': '8px',
                'boxShadow': '0 4px 30px rgba(0, 0, 0, 0.3)',
                'marginBottom': '30px',

                'border': f'1px solid {dark_theme_colors["border"]}',
            })
        ], width=12, style={'marginBottom': '20px'})
    ], className='mb-4'),
    
    # Cards de indicadores principais
    dbc.Row([
        # Card de Média de Desemprego
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Média de Desemprego", className="card-title", style={
                        'textAlign': 'center',

                        'color': dark_theme_colors['primary'],
                        'fontWeight': '600',
                        'marginBottom': '10px',

                        'fontFamily': '"Open Sans", sans-serif',
                    }),
                    html.H3(
                        f"{df['Last'].mean():.2f}%", 
                        style={
                            'textAlign': 'center',

                            'color': dark_theme_colors['text'],
                            'fontSize': '2.5rem',
                            'fontWeight': '700',
                            'margin': '15px 0',

                            'fontFamily': '"Open Sans", sans-serif',
                        }
                    ),
                    html.Div([

                        html.Span("vs anterior: ", style={'fontSize': '0.9rem', 'color': dark_theme_colors['light_text']}),
                        html.Span(
                            f"{df['Last'].mean() - df['Previous'].mean():+.2f}%",
                            style={

                                'color': dark_theme_colors['negative'] if df['Last'].mean() > df['Previous'].mean() else dark_theme_colors['positive'],
                                'fontWeight': '600',
                                'fontSize': '0.9rem',

                            }
                        )
                    ], style={'textAlign': 'center'})
                ])


            ], style={**card_style, 'height': '100%', 'border': f'1px solid {dark_theme_colors["border"]}'}),
        ], width=12, md=6, lg=3, className='mb-4'),
        
        # Card de Maior Taxa
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Maior Taxa", className="card-title", style={
                        'textAlign': 'center',

                        'color': dark_theme_colors['secondary'],
                        'fontWeight': '600',
                        'marginBottom': '10px',

                        'fontFamily': '"Open Sans", sans-serif',
                    }),
                    html.H3(
                        f"{df['Last'].max():.2f}%", 
                        style={
                            'textAlign': 'center',

                            'color': dark_theme_colors['text'],
                            'fontSize': '2.5rem',
                            'fontWeight': '700',
                            'margin': '15px 0',

                            'fontFamily': '"Open Sans", sans-serif',
                        }
                    ),
                    html.Div([

                        html.Span("País: ", style={'fontSize': '0.9rem', 'color': dark_theme_colors['light_text']}),
                        html.Span(
                            f"{df.loc[df['Last'].idxmax(), 'Country']}",
                            style={

                                'color': dark_theme_colors['text'],
                                'fontWeight': '600',
                                'fontSize': '0.9rem',

                            }
                        )
                    ], style={'textAlign': 'center'})
                ])


            ], style={**card_style, 'height': '100%', 'border': f'1px solid {dark_theme_colors["border"]}'}),
        ], width=12, md=6, lg=3, className='mb-4'),
        
        # Card de Menor Taxa
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Menor Taxa", className="card-title", style={
                        'textAlign': 'center',

                        'color': dark_theme_colors['accent1'],
                        'fontWeight': '600',
                        'marginBottom': '10px',

                        'fontFamily': '"Open Sans", sans-serif',
                    }),
                    html.H3(
                        f"{df['Last'].min():.2f}%", 
                        style={
                            'textAlign': 'center',

                            'color': dark_theme_colors['text'],
                            'fontSize': '2.5rem',
                            'fontWeight': '700',
                            'margin': '15px 0',

                            'fontFamily': '"Open Sans", sans-serif',
                        }
                    ),
                    html.Div([

                        html.Span("País: ", style={'fontSize': '0.9rem', 'color': dark_theme_colors['light_text']}),
                        html.Span(
                            f"{df.loc[df['Last'].idxmin(), 'Country']}",
                            style={

                                'color': dark_theme_colors['text'],
                                'fontWeight': '600',
                                'fontSize': '0.9rem',

                            }
                        )
                    ], style={'textAlign': 'center'})
                ])


            ], style={**card_style, 'height': '100%', 'border': f'1px solid {dark_theme_colors["border"]}'}),
        ], width=12, md=6, lg=3, className='mb-4'),
        
        # Card de Melhora/Piora
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Tendência", className="card-title", style={
                        'textAlign': 'center',

                        'color': dark_theme_colors['accent3'],
                        'fontWeight': '600',
                        'marginBottom': '10px',

                        'fontFamily': '"Open Sans", sans-serif',
                    }),
                    html.H3([
                        html.Span(f"{(df['Change'] < 0).sum()}", 


                                 style={'color': dark_theme_colors['positive']}),
                        html.Span(" / ", style={'color': dark_theme_colors['text']}),
                        html.Span(f"{(df['Change'] > 0).sum()}", 

                                 style={'color': dark_theme_colors['negative']})
                    ], style={
                        'textAlign': 'center',
                        'fontSize': '2.5rem',
                        'fontWeight': '700',
                        'margin': '15px 0',

                        'fontFamily': '"Open Sans", sans-serif',
                    }),
                    html.Div([
                        html.Span("Melhora / Piora", style={

                            'color': dark_theme_colors['light_text'],
                            'fontWeight': '600',
                            'fontSize': '0.9rem',

                        })
                    ], style={'textAlign': 'center'})
                ])


            ], style={**card_style, 'height': '100%', 'border': f'1px solid {dark_theme_colors["border"]}'}),
        ], width=12, md=6, lg=3, className='mb-4')
    ], className='g-3'),
    
    # Seleção de Visualização
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Selecione o Tipo de Visualização", style=card_header_style),
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
                        clearable=False,
                        className='dash-dropdown-dark',
                        style={


                            'backgroundColor': dark_theme_colors['background'],
                            'color': dark_theme_colors['text'],
                            'borderRadius': '8px',

                            'border': f'1px solid {dark_theme_colors["border"]}',
                        }
                    )

                ], style={'backgroundColor': 'rgba(18, 18, 18, 0.8)'})
            ], style=card_style)
        ], width=12, className='mb-4')
    ]),
    
    # Visualização Principal
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Visualização", style=card_header_style),
                dbc.CardBody([
                    dcc.Graph(
                        id='main-chart', 
                        style={'height': '600px'},
                        config={'displayModeBar': False}
                    )
                ], style=graph_container_style)
            ], style=card_style)
        ], width=12, className='mb-4')
    ]),
    
    # Tabela de Dados
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Tabela de Dados - Taxas de Desemprego por País", style=card_header_style),
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
                            'minWidth': '100px',



                            'backgroundColor': 'rgba(18, 18, 18, 0.9)',
                            'color': dark_theme_colors['text'],
                            'border': f'1px solid {dark_theme_colors["border"]}',
                            'fontFamily': '"Open Sans", sans-serif',
                        },
                        style_header={

                            'backgroundColor': 'rgba(18, 18, 18, 0.95)',
                            'fontWeight': 'bold',


                            'color': dark_theme_colors['primary'],
                            'border': f'1px solid {dark_theme_colors["border"]}',
                            'fontFamily': '"Open Sans", sans-serif',
                        },
                        style_data_conditional=[
                            {
                                'if': {'row_index': 'odd'},

                                'backgroundColor': 'rgba(30, 30, 30, 0.9)',
                            },
                            {
                                'if': {'column_id': 'Health', 'filter_query': '{Health} = "Bom"'},


                                'backgroundColor': 'rgba(76, 175, 80, 0.2)',
                                'color': dark_theme_colors['positive']
                            },
                            {
                                'if': {'column_id': 'Health', 'filter_query': '{Health} = "Médio"'},


                                'backgroundColor': 'rgba(255, 193, 7, 0.2)',
                                'color': '#FFB74D'
                            },
                            {
                                'if': {'column_id': 'Health', 'filter_query': '{Health} = "Ruim"'},


                                'backgroundColor': 'rgba(244, 67, 54, 0.2)',
                                'color': dark_theme_colors['negative']
                            },
                            {
                                'if': {'column_id': 'Change', 'filter_query': '{Change} < 0'},

                                'color': dark_theme_colors['positive']
                            },
                            {
                                'if': {'column_id': 'Change', 'filter_query': '{Change} > 0'},

                                'color': dark_theme_colors['negative']
                            }
                        ]
                    )
                ], style=graph_container_style)
            ], style=card_style)
        ], width=12, className='mb-4')
    ]),
    
    # Resumo Estatístico
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Resumo Estatístico", style=card_header_style),
                dbc.CardBody([
                    html.Div([
                        html.P(f"Média de Desemprego: {df['Last'].mean():.2f}%", 

                               style={'color': dark_theme_colors['text'], 'fontWeight': '500', 'fontFamily': '"Open Sans", sans-serif'}),
                        html.P(f"Mediana de Desemprego: {df['Last'].median():.2f}%", 

                               style={'color': dark_theme_colors['text'], 'fontWeight': '500', 'fontFamily': '"Open Sans", sans-serif'}),
                        html.P(f"Maior Taxa: {df['Last'].max():.2f}% ({df.loc[df['Last'].idxmax(), 'Country']})", 

                               style={'color': dark_theme_colors['text'], 'fontWeight': '500', 'fontFamily': '"Open Sans", sans-serif'}),
                        html.P(f"Menor Taxa: {df['Last'].min():.2f}% ({df.loc[df['Last'].idxmin(), 'Country']})", 

                               style={'color': dark_theme_colors['text'], 'fontWeight': '500', 'fontFamily': '"Open Sans", sans-serif'}),
                        html.P([
                            "Países com Melhora: ",
                            html.Span(f"{(df['Change'] < 0).sum()} ({(df['Change'] < 0).sum() / len(df) * 100:.1f}%)", 


                                     style={'color': dark_theme_colors['positive'], 'fontWeight': '600'})
                        ], style={'color': dark_theme_colors['text'], 'fontWeight': '500', 'fontFamily': '"Open Sans", sans-serif'}),
                        html.P([
                            "Países com Piora: ",
                            html.Span(f"{(df['Change'] > 0).sum()} ({(df['Change'] > 0).sum() / len(df) * 100:.1f}%)", 


                                     style={'color': dark_theme_colors['negative'], 'fontWeight': '600'})
                        ], style={'color': dark_theme_colors['text'], 'fontWeight': '500', 'fontFamily': '"Open Sans", sans-serif'})
                    ], style={'padding': '10px'})
                ], style=graph_container_style)
            ], style=card_style)
        ], width=12, className='mb-4')
    ]),
    
    # Rodapé
    dbc.Row([
        dbc.Col([
            html.Footer([
                html.P([
                    "Fonte: Trading Economics - Dados extraídos em ",
                    html.Span(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), 
                             style={'fontWeight': '500'})

                ], className="text-center", style={'color': dark_theme_colors['light_text'], 'fontFamily': '"Open Sans", sans-serif'}),
                html.P("Dashboard desenvolvido com Python, Dash e Plotly", 

                       className="text-center", style={'color': dark_theme_colors['light_text'], 'fontFamily': '"Open Sans", sans-serif'})
            ], style={
                'padding': '20px 0',

                'borderTop': f'1px solid {dark_theme_colors["border"]}',
                'marginTop': '20px',

            })
        ], width=12)
    ])
], fluid=True, style=app_style)

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
        
        fig.update_layout(

            plot_bgcolor='rgba(18, 18, 18, 0.3)',
            paper_bgcolor='rgba(0,0,0,0)',


            font=dict(color=dark_theme_colors['text'], family='"Open Sans", sans-serif'),
            title_font=dict(size=20, color=dark_theme_colors['text'], family='"Open Sans", sans-serif'),
            margin=dict(l=40, r=40, t=50, b=40),
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

            color_discrete_sequence=dark_theme_palette
        )
        
        fig.update_layout(

            plot_bgcolor='rgba(18, 18, 18, 0.3)',
            paper_bgcolor='rgba(0,0,0,0)',


            font=dict(color=dark_theme_colors['text'], family='"Open Sans", sans-serif'),
            title_font=dict(size=20, color=dark_theme_colors['text'], family='"Open Sans", sans-serif'),
            xaxis_tickangle=-45,
            margin=dict(l=40, r=40, t=50, b=80),
            xaxis={'gridcolor': 'rgba(255, 255, 255, 0.1)'},
            yaxis={'gridcolor': 'rgba(255, 255, 255, 0.1)'}
        )
        
        return fig
        
    elif chart_type == 'bar_compare':
        # Selecionar os 15 principais países para melhor visualização
        top_df = df.sort_values('Last', ascending=False).head(15)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=top_df['Country'],
            y=top_df['Last'],
            name='Taxa Atual',
            marker_color=dark_theme_colors['primary']
        ))
        
        fig.add_trace(go.Bar(
            x=top_df['Country'],
            y=top_df['Previous'],
            name='Taxa Anterior',
            marker_color=dark_theme_colors['secondary']
        ))
        
        fig.update_layout(
            title="Comparação: Taxa de Desemprego Atual vs Anterior (Top 15)",
            xaxis_title="País",
            yaxis_title="Taxa de Desemprego (%)",
            barmode='group',
            xaxis_tickangle=-45,
            plot_bgcolor='rgba(18, 18, 18, 0.3)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color=dark_theme_colors['text'], family='"Open Sans", sans-serif'),
            title_font=dict(size=20, color=dark_theme_colors['text'], family='"Open Sans", sans-serif'),
            margin=dict(l=40, r=40, t=50, b=80),
            xaxis={'gridcolor': 'rgba(255, 255, 255, 0.1)'},
            yaxis={'gridcolor': 'rgba(255, 255, 255, 0.1)'},
            legend=dict(
                font=dict(color=dark_theme_colors['text'], family='"Open Sans", sans-serif'),
                bgcolor='rgba(18, 18, 18, 0.7)',
                bordercolor=dark_theme_colors['border']
            )
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
            color_discrete_sequence=dark_theme_palette
        )
        
        # Adicionar linha horizontal em y=0 para referência
        fig.add_hline(y=0, line_dash="dash", line_color="rgba(255, 255, 255, 0.5)")
        
        fig.update_layout(
            plot_bgcolor='rgba(18, 18, 18, 0.3)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color=dark_theme_colors['text'], family='"Open Sans", sans-serif'),
            title_font=dict(size=20, color=dark_theme_colors['text'], family='"Open Sans", sans-serif'),
            margin=dict(l=40, r=40, t=50, b=40),
            xaxis={'gridcolor': 'rgba(255, 255, 255, 0.1)'},
            yaxis={'gridcolor': 'rgba(255, 255, 255, 0.1)'},
            legend=dict(
                font=dict(color=dark_theme_colors['text'], family='"Open Sans", sans-serif'),
                bgcolor='rgba(18, 18, 18, 0.7)',
                bordercolor=dark_theme_colors['border']
            )
        )
        
        return fig
        
    elif chart_type == 'treemap':
        fig = px.treemap(
            df,
            path=[px.Constant("Américas"), 'Region', 'Country'],
            values='Last',
            color='Last',
            hover_data=['Previous', 'Change'],
            color_continuous_scale=[dark_theme_colors['secondary'], dark_theme_colors['primary']],
            title="Treemap das Taxas de Desemprego por Região e País"
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(18, 18, 18, 0.3)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color=dark_theme_colors['text'], family='"Open Sans", sans-serif'),
            title_font=dict(size=20, color=dark_theme_colors['text'], family='"Open Sans", sans-serif'),
            margin=dict(l=20, r=20, t=50, b=20),
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
            color_continuous_scale=[dark_theme_colors['secondary'], dark_theme_colors['primary']]
        )
        
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        
        fig.update_layout(
            plot_bgcolor='rgba(18, 18, 18, 0.3)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color=dark_theme_colors['text'], family='"Open Sans", sans-serif'),
            title_font=dict(size=20, color=dark_theme_colors['text'], family='"Open Sans", sans-serif'),
            margin=dict(l=40, r=40, t=50, b=40),
            xaxis={'gridcolor': 'rgba(255, 255, 255, 0.1)'},
            yaxis={'gridcolor': 'rgba(255, 255, 255, 0.1)'},
            coloraxis_showscale=False
        )
        
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
            color_continuous_scale=[dark_theme_colors['accent3'], dark_theme_colors['secondary']]
        )
        
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        
        fig.update_layout(
            plot_bgcolor='rgba(18, 18, 18, 0.3)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color=dark_theme_colors['text'], family='"Open Sans", sans-serif'),
            title_font=dict(size=20, color=dark_theme_colors['text'], family='"Open Sans", sans-serif'),
            margin=dict(l=40, r=40, t=50, b=40),
            xaxis={'gridcolor': 'rgba(255, 255, 255, 0.1)'},
            yaxis={'gridcolor': 'rgba(255, 255, 255, 0.1)'},
            coloraxis_showscale=False
        )
        
        return fig
    
    # Caso padrão
    return px.bar(
        df.sort_values('Last', ascending=False),
        x='Country',
        y='Last',
        title="Taxa de Desemprego Atual por País",
        labels={'Last': 'Taxa de Desemprego (%)', 'Country': 'País'},
        color_discrete_sequence=[dark_theme_colors['primary']]
    )

if __name__ == '__main__':
    app.run(debug=True)
    