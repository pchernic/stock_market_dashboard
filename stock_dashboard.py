from dash import Dash, dcc, html, Input, Output
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime

app = Dash(__name__)
server = app.server

# Colors
BG_COLOR = "#0d1117"
CARD_COLOR = "#161b22"
TEXT_COLOR = "#c9d1d9"
ACCENT_COLOR = "#58a6ff"
ERROR_COLOR = "#f85149"

# Layout
app.layout = html.Div(style={'backgroundColor': BG_COLOR, 'padding': '30px', 'fontFamily': 'Arial'}, children=[
    html.H1("📈 Professional Stock Dashboard", style={
        'textAlign': 'center',
        'color': TEXT_COLOR,
        'marginBottom': '30px'
    }),

    html.Div([
        dcc.Input(
            id='ticker-input',
            value='AAPL',
            type='text',
            placeholder='Enter Stock Symbol',
            style={'padding': '8px', 'width': '150px', 'backgroundColor': CARD_COLOR, 'color': TEXT_COLOR, 'border': f'1px solid {ACCENT_COLOR}'}
        ),
        dcc.RadioItems(
            id='mode-selector',
            options=[
                {'label': 'Historical', 'value': 'historical'},
                {'label': 'Intraday', 'value': 'intraday'}
            ],
            value='historical',
            labelStyle={'display': 'inline-block', 'marginRight': '15px', 'color': TEXT_COLOR},
            style={'marginLeft': '20px'}
        ),
        dcc.Dropdown(
            id='period-dropdown',
            options=[
                {'label': '5 Days', 'value': '5d'},
                {'label': '1 Month', 'value': '1mo'},
                {'label': '6 Months', 'value': '6mo'},
                {'label': '1 Year', 'value': '1y'},
                {'label': '5 Years', 'value': '5y'},
            ],
            value='6mo',
            style={'width': '150px', 'backgroundColor': CARD_COLOR, 'color': TEXT_COLOR, 'marginLeft': '20px'}
        ),
    ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '30px'}),

    html.Div(id='kpi-cards', style={
        'display': 'flex',
        'gap': '20px',
        'marginBottom': '40px'
    }),

    dcc.Graph(id='price-chart')
])

@app.callback(
    Output('price-chart', 'figure'),
    Output('kpi-cards', 'children'),
    Input('ticker-input', 'value'),
    Input('period-dropdown', 'value'),
    Input('mode-selector', 'value')
)
def update_dashboard(ticker, period, mode):
    ticker = ticker.upper()
    try:
        stock = yf.Ticker(ticker)

        # Intraday Mode
        if mode == 'intraday':
            df = stock.history(period='1d', interval='5m')
        else:
            df = stock.history(period=period)

        if df.empty:
            return go.Figure(), [html.Div(f"No data found for {ticker}.", style={'color': ERROR_COLOR, 'fontWeight': 'bold'})]

        df.reset_index(inplace=True)

        # KPIs
        info = stock.info

        last_close = df['Close'].iloc[-1]
        change = last_close - df['Close'].iloc[-2] if len(df) >= 2 else 0
        pct_change = (change / df['Close'].iloc[-2] * 100) if len(df) >= 2 else 0

        kpis = []

        def kpi(title, value, color=TEXT_COLOR):
            return html.Div([
                html.Div(title, style={'fontSize': '14px', 'color': ACCENT_COLOR}),
                html.Div(value, style={'fontSize': '22px', 'fontWeight': 'bold', 'color': color})
            ], style={'padding': '15px', 'backgroundColor': CARD_COLOR, 'borderRadius': '8px', 'flex': '1', 'textAlign': 'center'})

        kpis.append(kpi("Last Price", f"${last_close:,.2f}"))
        kpis.append(kpi("Change", f"{change:+.2f} ({pct_change:+.2f}%)", color=("#16c784" if change > 0 else "#f85149")))
        if 'marketCap' in info and info['marketCap']:
            kpis.append(kpi("Market Cap", f"${info['marketCap'] / 1e9:.2f} B"))
        if 'trailingPE' in info and info['trailingPE']:
            kpis.append(kpi("P/E Ratio", f"{info['trailingPE']:.2f}"))
        if 'dividendYield' in info and info['dividendYield']:
            kpis.append(kpi("Dividend Yield", f"{info['dividendYield'] * 100:.2f}%"))
        if 'ytdReturn' in info and info['ytdReturn']:
            kpis.append(kpi("YTD Return", f"{info['ytdReturn'] * 100:.2f}%"))

        # Chart
        fig = go.Figure()

        if mode == 'intraday':
            fig.add_trace(go.Scatter(
                x=df['Datetime'],
                y=df['Close'],
                mode='lines',
                line=dict(color=ACCENT_COLOR, width=2),
                name=f"{ticker} Intraday"
            ))
        else:
            fig.add_trace(go.Candlestick(
                x=df['Date'],
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name=f"{ticker} Historical",
                increasing_line_color='#16c784',
                decreasing_line_color='#f85149'
            ))

        fig.update_layout(
            title=f"{ticker} {'Intraday' if mode=='intraday' else 'Historical'} Price Chart",
            plot_bgcolor=BG_COLOR,
            paper_bgcolor=BG_COLOR,
            font=dict(color=TEXT_COLOR),
            xaxis_title="Date/Time",
            yaxis_title="Price (USD)",
            margin=dict(l=40, r=40, t=40, b=20),
            height=600
        )

        return fig, kpis

    except Exception as e:
        return go.Figure(), [html.Div(f"Error: {str(e)}", style={'color': ERROR_COLOR, 'fontWeight': 'bold'})]

if __name__ == '__main__':
    app.run(debug=True)
