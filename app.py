from dash import Dash, dcc, html, Input, Output
import yfinance as yf
from plotly.graph_objs import Figure, Scatter, Candlestick

# --- Cores ---
BG_COLOR = "#0d1117"
CARD_COLOR = "#161b22"
TEXT_COLOR = "#c9d1d9"
ACCENT_COLOR = "#58a6ff"
ERROR_COLOR = "#f85149"

app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server

# --- Navbar ---
def navbar():
    return html.Div([
        dcc.Link("📈 Dashboard", href="/", style={'marginRight': '30px', 'color': ACCENT_COLOR}),
        dcc.Link("📑 Fundamentals", href="/fundamentals", style={'color': ACCENT_COLOR})
    ], style={'textAlign': 'center', 'marginBottom': '30px'})

# --- Página Dashboard ---
def dashboard_layout():
    return html.Div(style={'backgroundColor': BG_COLOR, 'padding': '30px', 'fontFamily': 'Arial'}, children=[
        navbar(),
        html.H1("📈 Interactive Stock Dashboard", style={
            'textAlign': 'center', 'color': TEXT_COLOR, 'marginBottom': '30px'}),

        html.Div([
            dcc.Input(id='ticker-input', value='AAPL', type='text',
                      style={'padding': '8px', 'width': '150px', 'backgroundColor': CARD_COLOR, 'color': TEXT_COLOR,
                             'border': f'1px solid {ACCENT_COLOR}'}),
            dcc.RadioItems(id='mode-selector', options=[
                {'label': 'Historical', 'value': 'historical'},
                {'label': 'Intraday', 'value': 'intraday'}], value='historical',
                labelStyle={'display': 'inline-block', 'marginRight': '15px', 'color': TEXT_COLOR},
                style={'marginLeft': '20px'}),
            dcc.Dropdown(id='period-dropdown', options=[
                {'label': '5 Days', 'value': '5d'},
                {'label': '1 Month', 'value': '1mo'},
                {'label': '6 Months', 'value': '6mo'},
                {'label': '1 Year', 'value': '1y'},
                {'label': '5 Years', 'value': '5y'}], value='6mo',
                style={'width': '150px', 'backgroundColor': CARD_COLOR, 'color': TEXT_COLOR, 'marginLeft': '20px'})
        ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '30px'}),

        html.Div(id='kpi-cards', style={'display': 'flex', 'gap': '20px', 'marginBottom': '40px'}),
        dcc.Graph(id='price-chart')
    ])

# --- Página Fundamentals ---
def fundamentals_layout(ticker='AAPL'):
    ticker = ticker.upper()
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        def row(label, value):
            return html.Div([
                html.Div(label, style={'color': ACCENT_COLOR, 'fontSize': '14px'}),
                html.Div(value, style={'color': TEXT_COLOR, 'fontSize': '18px', 'fontWeight': 'bold'})
            ], style={'padding': '10px', 'backgroundColor': CARD_COLOR, 'marginBottom': '10px', 'borderRadius': '6px'})

        data = [
            row("Company Name", info.get('longName', 'N/A')),
            row("Sector", info.get('sector', 'N/A')),
            row("Industry", info.get('industry', 'N/A')),
            row("Market Cap", f"${info.get('marketCap', 0)/1e9:.2f} B" if info.get('marketCap') else 'N/A'),
            row("Employees", info.get('fullTimeEmployees', 'N/A')),
            row("Website", info.get('website', 'N/A')),
        ]

        return html.Div(style={'backgroundColor': BG_COLOR, 'padding': '30px', 'fontFamily': 'Arial'}, children=[
            navbar(),
            html.H1(f"📑 Fundamentals: {ticker}", style={'color': TEXT_COLOR}),
            html.Div(data)
        ])

    except Exception as e:
        return html.Div(f"Error loading data for {ticker}: {str(e)}", style={'color': ERROR_COLOR})

# --- Callback para atualizar gráfico e KPIs ---
@app.callback(
    Output('price-chart', 'figure'),
    Output('kpi-cards', 'children'),
    Input('ticker-input', 'value'),
    Input('period-dropdown', 'value'),
    Input('mode-selector', 'value')
)
def update_dashboard(ticker, period, mode):
    try:
        stock = yf.Ticker(ticker.upper())
        df = stock.history(period='1d', interval='5m') if mode == 'intraday' else stock.history(period=period)

        if df.empty:
            return {}, [html.Div("No data found.", style={'color': ERROR_COLOR})]

        df.reset_index(inplace=True)
        last_close = df['Close'].iloc[-1]
        change = last_close - df['Close'].iloc[-2] if len(df) > 1 else 0
        pct_change = (change / df['Close'].iloc[-2]) * 100 if len(df) > 1 else 0

        def kpi(title, value, color=TEXT_COLOR):
            return html.Div([
                html.Div(title, style={'color': ACCENT_COLOR}),
                html.Div(value, style={'fontSize': '20px', 'fontWeight': 'bold', 'color': color})
            ], style={'padding': '10px', 'backgroundColor': CARD_COLOR, 'borderRadius': '6px',
                      'flex': '1', 'textAlign': 'center'})

        kpis = [
            kpi("Last Price", f"${last_close:,.2f}"),
            kpi("Change", f"{change:+.2f} ({pct_change:+.2f}%)", "#16c784" if change > 0 else ERROR_COLOR),
        ]

        fig_data = {'x': df['Datetime'] if mode == 'intraday' else df['Date'], 'y': df['Close']}
        fig = Figure()

        if mode == 'intraday':
            fig.add_trace(Scatter(x=fig_data['x'], y=fig_data['y'], mode='lines', line=dict(color=ACCENT_COLOR)))
        else:
            fig.add_trace(Candlestick(x=fig_data['x'], open=df['Open'], high=df['High'],
                                      low=df['Low'], close=df['Close'],
                                      increasing_line_color='#16c784', decreasing_line_color=ERROR_COLOR))

        fig.update_layout(plot_bgcolor=BG_COLOR, paper_bgcolor=BG_COLOR, font=dict(color=TEXT_COLOR), height=600)
        return fig, kpis
    except Exception as e:
        return {}, [html.Div(f"Error: {str(e)}", style={'color': ERROR_COLOR})]

# --- Routing ---
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'), Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/fundamentals':
        return fundamentals_layout()
    return dashboard_layout()

# --- Run ---
if __name__ == '__main__':
    app.run(debug=True)

