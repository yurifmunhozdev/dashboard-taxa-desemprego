Dashboard de Desemprego nas Américas
Descrição
Este projeto consiste em um dashboard interativo para visualização e análise das taxas de desemprego nos países das Américas. Os dados são extraídos automaticamente do site Trading Economics e apresentados em um dashboard elegante e informativo, com múltiplas visualizações e filtros.

Funcionalidades
Extração Automática de Dados: Web scraping do site Trading Economics usando Selenium
Dashboard Interativo: Construído com Dash e Plotly
Múltiplas Visualizações:
Mapa de calor por região
Gráficos de barras comparativos
Gráfico de dispersão
Treemap por região
Top 5 maiores e menores taxas
Tabela de Dados Interativa: Com filtragem e ordenação
Indicadores Principais: Média, maior taxa, menor taxa e tendências
Design Responsivo: Interface adaptável a diferentes tamanhos de tela
Tecnologias Utilizadas
Python 3.x
Selenium: Para web scraping
Pandas: Para manipulação e análise de dados
Dash & Plotly: Para criação do dashboard interativo
Dash Bootstrap Components: Para layout responsivo
WebDriver Manager: Para gerenciamento automático do ChromeDriver

1. Clone o repositório:

git clone https://github.com/seu-usuario/dashboard-desemprego-americas.git
cd dashboard-desemprego-americas

2. Instale as dependências:

pip install -r requirements.txt

3. Certifique-se de ter o Google Chrome instalado (necessário para o Selenium) OBS: Se atente a LGPD!

Uso:

1. Execute o script de extração de dados:

Este script irá extrair os dados mais recentes do Trading Economics e salvá-los em arquivos CSV e Excel na pasta data/.

2. Execute o dashboard:

python dashboard.py


Personalização
O dashboard utiliza um tema escuro com uma imagem de fundo de cityscape. Você pode personalizar a aparência modificando as variáveis de cores e estilos no início do arquivo dashboard.py.

Possíveis Problemas
Falha na Extração de Dados: O site Trading Economics pode mudar sua estrutura ou bloquear requisições automatizadas. Nesse caso, o script main.py possui uma função create_static_data() que pode ser usada como fallback.
Incompatibilidade de Versões: Certifique-se de que as versões das bibliotecas instaladas são compatíveis. Em versões mais recentes do Dash, use app.run() em vez de app.run_server().

Contribuições
Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests com melhorias.

Créditos
Dados: Trading Economics
Imagem de fundo: Unsplash

Desenvolvido com ❤️ usando Python, Dash e Plotly.