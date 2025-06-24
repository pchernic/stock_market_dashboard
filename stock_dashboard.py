from dash import Dash, dcc, html, dash_table, Input, Output
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go

# Initialize Dash
app = Dash(__name__)
server = app.server  # Optional if deploying later

# Bloomberg-style colors
BLOOM_BG = "#121212"
BLOOM_CARD = "#1e1e1e"
BLOOM_TEXT = "#f0f0f0"
BLOOM_ACCENT = "#fdae61"

# Period options
PERIOD_OPTIONS = [
    {'label': '5 Days', 'value': '5d'},
    {'label': '1 Month', 'value': '1mo'},
    {'label': '6 Months', 'value': '6mo'},
    {'label': '1 Year', 'value': '1y'},
    {'label': '5 Years', 'value': '5y'},
]

# Layout
app.layout = html.Div(style={'backgroundColor': BLOOM_BG, 'padding': '30px'}, children=[
    html.H1("📊 Bloomberg-Style Market Dashboard", style={
        'textAlign': 'center',
        'color': BLOOM_TEXT,
        'marginBottom': '30px'
    }),

    html.Div([
        dcc.Input(
            id='ticker-input',
            value='AAPL',
            type='text',
            style={'padding': '8px', 'width': '120px', 'backgroundColor': BLOOM_CARD, 'color': BLOOM_TEXT, 'border': '1px solid #555'}
        ),
        dcc.Dropdown(
            id='period-dropdown',
            options=PERIOD_OPTIONS,
            value='6mo',
            style={'width': '150px', 'backgroundColor': BLOOM_CARD, 'color': BLOOM_TEXT}
        )
    ], style={'display': 'flex', 'gap': '20px', 'justifyContent': 'center', 'marginBottom': '30px'}),

    html.Div(id='kpi-cards', style={
        'display': 'flex',
        'justifyContent': 'space-between',
        'gap': '20px',
        'marginBottom': '40px'
    }),

    dcc.Graph(id='candlestick-chart')
])

# Callback
@app.callback(
    Output('candlestick-chart', 'figure'),
    Output('kpi-cards', 'children'),
    Input('ticker-input', 'value'),
    Input('period-dropdown', 'value')
)
def update_dashboard(ticker, period):
    df = yf.download(ticker.upper(), period=period)

    if df.empty:
        return go.Figure(), [html.Div("No data found", style={'color': BLOOM_TEXT})]

    df.reset_index(inplace=True)
    df.columns = [str(c) for c in df.columns]

    latest = df.iloc[-1]

    # KPIs
    def kpi(title, value):
        return html.Div([
            html.Div(title, style={'fontSize': '14px', 'color': BLOOM_ACCENT}),
            html.Div(value, style={'fontSize': '22px', 'fontWeight': 'bold', 'color': BLOOM_TEXT})
        ], style={'padding': '15px', 'backgroundColor': BLOOM_CARD, 'borderRadius': '8px', 'flex': '1', 'textAlign': 'center'})

    kpis = [
        kpi("Last Close", f"${latest['Close']:.2f}"),
        kpi("High / Low", f"${latest['High']:.2f} / ${latest['Low']:.2f}"),
        kpi("Volume", f"{int(latest['Volume']):,}")
    ]

    # Candlestick chart
    fig = go.Figure(data=[go.Candlestick(
        x=df['Date'],
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name=ticker.upper()
    )])
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        plot_bgcolor=BLOOM_BG,
        paper_bgcolor=BLOOM_BG,
        font=dict(color=BLOOM_TEXT),
        margin=dict(l=30, r=30, t=40, b=20),
        template='plotly_dark',
        height=500
    )

    return fig, kpis

if __name__ == '__main__':
    app.run(debug=True)
