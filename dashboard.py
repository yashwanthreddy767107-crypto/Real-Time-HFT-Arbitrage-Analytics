import time
import html

import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components

from database import get_connection


# =========================================================
# 1. PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="HFT Arbitrage Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# 2. PROFESSIONAL DASHBOARD STYLE
# =========================================================

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(
                circle at 10% 5%,
                rgba(38, 105, 145, 0.25),
                transparent 35%
            ),
            linear-gradient(135deg, #101827, #182c40);
        color: #f5f7fa;
    }

    [data-testid="stMetric"] {
        background: rgba(255,255,255,0.055);
        padding: 17px;
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 15px;
    }

    [data-testid="stMetricLabel"] {
        color: #c6d2df;
    }

    h1, h2, h3 {
        color: #f7fafc;
    }

    .section-label {
        color: #b7c8d9;
        font-size: 13px;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }

    .status-card {
        border-radius: 16px;
        padding: 18px;
        text-align: center;
        margin: 10px 0;
        background: rgba(255,255,255,0.045);
    }

    .profit-card {
        border: 2px solid #2ecc71;
        box-shadow: 0 0 18px rgba(46,204,113,0.13);
    }

    .loss-card {
        border: 2px solid #ff6262;
        box-shadow: 0 0 18px rgba(255,98,98,0.13);
    }

    .neutral-card {
        border: 2px solid #e9c94b;
    }

    .status-value {
        font-size: 26px;
        font-weight: 800;
        overflow-wrap: anywhere;
    }

    .small-note {
        font-size: 12px;
        color: #b8c6d4;
    }

    div[data-testid="stPlotlyChart"] {
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 5px;
        background: rgba(255,255,255,0.025);
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 3. DATABASE FUNCTIONS
# =========================================================

@st.cache_data(ttl=5, show_spinner=False)
def get_database_metadata():
    """Discover the existing public PostgreSQL tables and columns."""

    connection = get_connection()

    try:
        query = """
            SELECT
                table_name,
                column_name,
                data_type
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position;
        """

        return pd.read_sql_query(query, connection)

    finally:
        connection.close()


@st.cache_data(ttl=5, show_spinner=False)
def read_database_table(table_name):
    """Read a table whose name was verified in PostgreSQL metadata."""

    metadata = get_database_metadata()

    if table_name not in metadata["table_name"].unique():
        raise ValueError("The selected table was not found.")

    # Quote the identifier safely.
    quoted_table = '"' + table_name.replace('"', '""') + '"'

    connection = get_connection()

    try:
        return pd.read_sql_query(
            f"SELECT * FROM {quoted_table}",
            connection,
        )

    finally:
        connection.close()


def find_column(dataframe, candidates):
    """Find a column without depending on capitalization."""

    lookup = {
        str(column).lower(): column
        for column in dataframe.columns
    }

    for candidate in candidates:
        if candidate.lower() in lookup:
            return lookup[candidate.lower()]

    return None


# =========================================================
# 4. ANIMATED TRADER
# =========================================================

def show_animated_trader(status, profit_value):
    """
    Display a CSS-drawn standing trader.

    Left hand: PROFIT panel.
    Right hand: LOSS panel.

    The panel values and active states use the latest
    available database result.
    """

    if status == "PROFIT":
        profit_state = "active"
        loss_state = ""
        message = "PROFIT OPPORTUNITY DETECTED"
        message_class = "profit-message"

    elif status == "LOSS":
        profit_state = ""
        loss_state = "active"
        message = "NEGATIVE RESULT DETECTED"
        message_class = "loss-message"

    elif status == "NEUTRAL":
        profit_state = ""
        loss_state = ""
        message = "NO PROFITABLE OPPORTUNITY"
        message_class = "neutral-message"

    else:
        profit_state = ""
        loss_state = ""
        message = "WAITING FOR MARKET DATA"
        message_class = "neutral-message"

    if status == "PROFIT":
        profit_text = f"+{profit_value:,.2f}"
        loss_text = "INACTIVE"
    elif status == "LOSS":
        profit_text = "INACTIVE"
        loss_text = f"{profit_value:,.2f}"
    else:
        profit_text = "WAITING"
        loss_text = "WAITING"

    # Escape dynamic text before embedding it in HTML.
    profit_text = html.escape(profit_text)
    loss_text = html.escape(loss_text)
    message = html.escape(message)

    trader_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        * {{
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            font-family: Arial, sans-serif;
            background: transparent;
            color: white;
        }}

        .stage {{
            position: relative;
            width: 100%;
            height: 355px;
            overflow: hidden;
            border-radius: 20px;
            background:
                radial-gradient(
                    circle at 50% 45%,
                    rgba(70, 130, 175, 0.25),
                    transparent 55%
                ),
                linear-gradient(
                    135deg,
                    rgba(17, 33, 53, 0.97),
                    rgba(28, 48, 68, 0.95)
                );
            border: 1px solid rgba(255,255,255,0.12);
        }}

        .stage-title {{
            position: absolute;
            top: 14px;
            width: 100%;
            text-align: center;
            color: #d8e6f2;
            font-size: 12px;
            letter-spacing: 2px;
        }}

        .ground {{
            position: absolute;
            width: 76%;
            height: 20px;
            left: 12%;
            bottom: 25px;
            border-radius: 50%;
            background: rgba(0,0,0,0.35);
            filter: blur(5px);
        }}

        /* LEFT PROFIT PANEL */

        .panel {{
            position: absolute;
            top: 105px;
            width: 31%;
            min-height: 112px;
            padding: 12px 5px;
            text-align: center;
            border-radius: 15px;
            background: rgba(12, 28, 42, 0.95);
            transition: all .4s ease;
            z-index: 5;
        }}

        .profit-panel {{
            left: 3%;
            border: 2px solid #318b63;
        }}

        .profit-panel.active {{
            border-color: #37f39b;
            box-shadow: 0 0 24px rgba(55,243,155,.65);
            animation: profitPulse 1.2s infinite alternate;
        }}

        .loss-panel {{
            right: 3%;
            border: 2px solid #a64b52;
        }}

        .loss-panel.active {{
            border-color: #ff5555;
            box-shadow: 0 0 24px rgba(255,85,85,.55);
            animation: lossPulse 1.2s infinite alternate;
        }}

        .panel-label {{
            font-size: 14px;
            font-weight: 800;
            letter-spacing: 1px;
        }}

        .profit-panel .panel-label {{
            color: #49f6a1;
        }}

        .loss-panel .panel-label {{
            color: #ff7070;
        }}

        .panel-value {{
            margin-top: 12px;
            font-size: 17px;
            font-weight: 800;
            overflow-wrap: anywhere;
        }}

        .panel-status {{
            margin-top: 8px;
            font-size: 10px;
            color: #cad7e3;
        }}

        /* STANDING CHARACTER */

        .person {{
            position: absolute;
            width: 100px;
            height: 250px;
            left: 50%;
            top: 64px;
            transform: translateX(-50%);
            z-index: 4;
            animation: bodyFloat 2.4s ease-in-out infinite;
        }}

        .head {{
            position: absolute;
            width: 42px;
            height: 47px;
            left: 29px;
            top: 0;
            border-radius: 46% 46% 43% 43%;
            background: linear-gradient(135deg, #e6b38c, #bc805c);
            border: 2px solid rgba(255,255,255,.2);
        }}

        .hair {{
            position: absolute;
            width: 43px;
            height: 18px;
            left: 28px;
            top: -2px;
            border-radius: 60% 60% 25% 25%;
            background: #26323c;
            z-index: 2;
        }}

        .eye {{
            position: absolute;
            width: 4px;
            height: 4px;
            top: 22px;
            background: #28333b;
            border-radius: 50%;
        }}

        .eye-left {{
            left: 10px;
        }}

        .eye-right {{
            right: 10px;
        }}

        .torso {{
            position: absolute;
            width: 54px;
            height: 78px;
            top: 45px;
            left: 23px;
            border-radius: 12px 12px 7px 7px;
            background: linear-gradient(135deg, #e1a74c, #a76b29);
            border: 1px solid rgba(255,255,255,.18);
        }}

        .shirt-line {{
            position: absolute;
            top: 4px;
            left: 25px;
            width: 2px;
            height: 63px;
            background: rgba(255,255,255,.25);
        }}

        .arm {{
            position: absolute;
            top: 53px;
            width: 66px;
            height: 13px;
            border-radius: 20px;
            background: linear-gradient(90deg, #d9a07a, #f0c39b);
            transform-origin: 10% 50%;
        }}

        .arm-left {{
            left: -31px;
            transform: rotate(-12deg);
        }}

        .arm-right {{
            right: -31px;
            transform-origin: 90% 50%;
            transform: rotate(12deg);
        }}

        .hand {{
            position: absolute;
            width: 15px;
            height: 15px;
            top: 49px;
            border-radius: 50%;
            background: #e9b58d;
        }}

        .hand-left {{
            left: -43px;
        }}

        .hand-right {{
            right: -43px;
        }}

        .leg {{
            position: absolute;
            top: 117px;
            width: 17px;
            height: 83px;
            border-radius: 5px;
            background: linear-gradient(90deg, #435d83, #263a5a);
        }}

        .leg-left {{
            left: 30px;
            transform: rotate(3deg);
        }}

        .leg-right {{
            right: 30px;
            transform: rotate(-3deg);
        }}

        .shoe {{
            position: absolute;
            top: 193px;
            width: 29px;
            height: 12px;
            border-radius: 8px 8px 4px 4px;
            background: #e3e8ed;
        }}

        .shoe-left {{
            left: 18px;
        }}

        .shoe-right {{
            right: 18px;
        }}

        .status-message {{
            position: absolute;
            bottom: 9px;
            width: 100%;
            text-align: center;
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 1px;
        }}

        .profit-message {{
            color: #54f6a2;
        }}

        .loss-message {{
            color: #ff7474;
        }}

        .neutral-message {{
            color: #f2d45e;
        }}

        @keyframes profitPulse {{
            from {{ transform: scale(1); }}
            to {{ transform: scale(1.045); }}
        }}

        @keyframes lossPulse {{
            from {{ transform: scale(1); }}
            to {{ transform: scale(1.035); }}
        }}

        @keyframes bodyFloat {{
            0%, 100% {{ margin-top: 0; }}
            50% {{ margin-top: -5px; }}
        }}

        @media (prefers-reduced-motion: reduce) {{
            *, *::before, *::after {{
                animation: none !important;
                transition: none !important;
            }}
        }}
    </style>
    </head>

    <body>
        <div class="stage">
            <div class="stage-title">
                REAL-TIME ARBITRAGE CONTROL CENTER
            </div>

            <div class="ground"></div>

            <div class="panel profit-panel {profit_state}">
                <div class="panel-label">PROFIT</div>
                <div class="panel-value">{profit_text}</div>
                <div class="panel-status">LEFT HAND</div>
            </div>

            <div class="panel loss-panel {loss_state}">
                <div class="panel-label">LOSS</div>
                <div class="panel-value">{loss_text}</div>
                <div class="panel-status">RIGHT HAND</div>
            </div>

            <div class="person">
                <div class="hair"></div>

                <div class="head">
                    <div class="eye eye-left"></div>
                    <div class="eye eye-right"></div>
                </div>

                <div class="torso">
                    <div class="shirt-line"></div>
                </div>

                <div class="arm arm-left"></div>
                <div class="arm arm-right"></div>

                <div class="hand hand-left"></div>
                <div class="hand hand-right"></div>

                <div class="leg leg-left"></div>
                <div class="leg leg-right"></div>

                <div class="shoe shoe-left"></div>
                <div class="shoe shoe-right"></div>
            </div>

            <div class="status-message {message_class}">
                {message}
            </div>
        </div>
    </body>
    </html>
    """

    components.html(
        trader_html,
        height=365,
        scrolling=False,
    )


# =========================================================
# 5. HEADER
# =========================================================

st.title("⚡ HFT Arbitrage Analytics")
st.caption(
    "Simulated cryptocurrency markets • Arbitrage detection "
    "• Profit and loss monitoring"
)


# =========================================================
# 6. LOAD TABLES
# =========================================================

try:
    metadata = get_database_metadata()

except Exception as error:
    st.error(f"PostgreSQL connection failed: {error}")
    st.stop()


if metadata.empty:
    st.warning("No tables were found in the public PostgreSQL schema.")
    st.stop()


# =========================================================
# 7. IDENTIFY THE ARBITRAGE TABLE
# =========================================================

profit_candidates = [
    "net_profit",
    "estimated_net_profit",
    "profit",
    "profit_loss",
    "pnl",
    "net_pnl",
]

table_summaries = []

for table_name, group in metadata.groupby("table_name"):
    columns_lower = {
        str(column).lower()
        for column in group["column_name"]
    }

    matched_profit = any(
        candidate in columns_lower
        for candidate in profit_candidates
    )

    if matched_profit:
        table_summaries.append(table_name)


if not table_summaries:
    st.error(
        "No table with a recognized profit column was found. "
        "Expected one of: " + ", ".join(profit_candidates)
    )

    st.write(
        "Tables and columns found:",
        metadata,
    )

    st.stop()


preferred_names = [
    "arbitrage_opportunities",
    "arbitrage_results",
    "arbitrage",
    "opportunities",
]

default_table = next(
    (
        name for name in preferred_names
        if name in table_summaries
    ),
    table_summaries[0],
)

selected_table = st.sidebar.selectbox(
    "Arbitrage results table",
    table_summaries,
    index=table_summaries.index(default_table),
)


try:
    data = read_database_table(selected_table)

except Exception as error:
    st.error(f"Could not read the selected table: {error}")
    st.stop()


if data.empty:
    st.info(
        "No arbitrage results are available yet. "
        "Start the simulator and arbitrage detector."
    )

    show_animated_trader("WAITING", 0)
    st.stop()


# =========================================================
# 8. MAP DATABASE COLUMNS
# =========================================================

profit_column = find_column(data, profit_candidates)

timestamp_column = find_column(
    data,
    [
        "timestamp",
        "created_at",
        "detected_at",
        "time",
        "event_time",
    ],
)

crypto_column = find_column(
    data,
    [
        "symbol",
        "crypto",
        "cryptocurrency",
        "trading_pair",
        "pair",
        "asset",
    ],
)

buy_exchange_column = find_column(
    data,
    [
        "buy_exchange",
        "source_exchange",
        "exchange_buy",
    ],
)

sell_exchange_column = find_column(
    data,
    [
        "sell_exchange",
        "target_exchange",
        "exchange_sell",
    ],
)

exchange_column = find_column(
    data,
    [
        "exchange",
        "exchange_name",
    ],
)

buy_price_column = find_column(
    data,
    [
        "buy_price",
        "buy_ask",
        "ask_price",
        "best_ask",
    ],
)

sell_price_column = find_column(
    data,
    [
        "sell_price",
        "sell_bid",
        "bid_price",
        "best_bid",
    ],
)


# =========================================================
# 9. NORMALIZE DATA
# =========================================================

data[profit_column] = pd.to_numeric(
    data[profit_column],
    errors="coerce",
)

data = data.dropna(
    subset=[profit_column]
).copy()

if data.empty:
    st.warning("The selected table contains no valid numeric profit results.")
    st.stop()


if timestamp_column:
    data[timestamp_column] = pd.to_datetime(
        data[timestamp_column],
        errors="coerce",
        utc=True,
    )

    data = data.sort_values(
        timestamp_column,
        na_position="first",
    )


# =========================================================
# 10. FILTERS
# =========================================================

st.sidebar.header("Analytics Filters")

filtered_data = data.copy()

if crypto_column:
    crypto_values = sorted(
        filtered_data[crypto_column]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    selected_crypto = st.sidebar.multiselect(
        "Cryptocurrency",
        crypto_values,
        default=crypto_values,
    )

    filtered_data = filtered_data[
        filtered_data[crypto_column]
        .astype(str)
        .isin(selected_crypto)
    ]


if filtered_data.empty:
    st.warning("No records match the selected filters.")
    st.stop()


# =========================================================
# 11. LATEST RESULT AND ANIMATION
# =========================================================

latest_row = filtered_data.iloc[-1]
latest_profit = float(latest_row[profit_column])

if latest_profit > 0:
    latest_status = "PROFIT"
elif latest_profit < 0:
    latest_status = "LOSS"
else:
    latest_status = "NEUTRAL"


st.markdown(
    '<div class="section-label">Live profit / loss animation</div>',
    unsafe_allow_html=True,
)

show_animated_trader(
    latest_status,
    latest_profit,
)


# =========================================================
# 12. PROFESSIONAL METRICS
# =========================================================

profits = filtered_data[profit_column]

total_opportunities = len(filtered_data)
profitable_count = int((profits > 0).sum())
loss_count = int((profits < 0).sum())
neutral_count = int((profits == 0).sum())

average_profit = float(profits.mean())
best_opportunity = float(profits.max())
worst_opportunity = float(profits.min())
combined_result = float(profits.sum())


st.subheader("📊 Performance Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Total Opportunities",
    f"{total_opportunities:,}",
)

c2.metric(
    "Profitable",
    f"{profitable_count:,}",
)

c3.metric(
    "Average Net Result",
    f"{average_profit:,.2f}",
)

c4.metric(
    "Best Opportunity",
    f"{best_opportunity:,.2f}",
)


c5, c6, c7, c8 = st.columns(4)

c5.metric(
    "Combined Net Result",
    f"{combined_result:,.2f}",
)

c6.metric(
    "Loss-Making Results",
    f"{loss_count:,}",
)

c7.metric(
    "Neutral Results",
    f"{neutral_count:,}",
)

c8.metric(
    "Worst Opportunity",
    f"{worst_opportunity:,.2f}",
)


# =========================================================
# 13. PROFIT / LOSS BAR CHART
# =========================================================

st.subheader("📊 Profit vs Loss Opportunities")

summary_data = pd.DataFrame(
    {
        "Result": [
            "Profitable",
            "Loss-making",
            "Neutral",
        ],
        "Opportunities": [
            profitable_count,
            loss_count,
            neutral_count,
        ],
    }
)

fig_status = px.bar(
    summary_data,
    x="Result",
    y="Opportunities",
    color="Result",
    text="Opportunities",
    title="Number of Opportunities by Result",
    color_discrete_map={
        "Profitable": "#2ecc71",
        "Loss-making": "#ff6262",
        "Neutral": "#e9c94b",
    },
)

fig_status.update_layout(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#f5f7fa"),
    showlegend=False,
    margin=dict(l=20, r=20, t=60, b=20),
)

fig_status.update_traces(
    textposition="outside",
)

st.plotly_chart(
    fig_status,
    use_container_width=True,
)


# =========================================================
# 14. PROFIT HISTORY CHART
# =========================================================

st.subheader("📈 Profit / Loss History")

if timestamp_column and filtered_data[timestamp_column].notna().any():

    history_data = filtered_data.dropna(
        subset=[timestamp_column]
    ).copy()

    fig_history = px.line(
        history_data,
        x=timestamp_column,
        y=profit_column,
        markers=True,
        title="Estimated Net Result Over Time",
        labels={
            timestamp_column: "Timestamp",
            profit_column: "Estimated Net Result",
        },
    )

    fig_history.add_hline(
        y=0,
        line_dash="dash",
        line_color="#f2d45e",
    )

    fig_history.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    st.plotly_chart(
        fig_history,
        use_container_width=True,
    )

else:
    chart_data = filtered_data.reset_index(drop=True).copy()
    chart_data["Opportunity Number"] = range(
        1,
        len(chart_data) + 1,
    )

    fig_history = px.line(
        chart_data,
        x="Opportunity Number",
        y=profit_column,
        markers=True,
        title="Estimated Net Result by Opportunity",
    )

    fig_history.add_hline(
        y=0,
        line_dash="dash",
        line_color="#f2d45e",
    )

    fig_history.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    st.plotly_chart(
        fig_history,
        use_container_width=True,
    )


# =========================================================
# 15. BEST AND WORST OPPORTUNITIES
# =========================================================

st.subheader("🏆 Best and Worst Opportunities")

best_index = filtered_data[profit_column].idxmax()
worst_index = filtered_data[profit_column].idxmin()

best_row = filtered_data.loc[[best_index]]
worst_row = filtered_data.loc[[worst_index]]

left, right = st.columns(2)

with left:
    st.markdown("### 🟢 Best opportunity")
    st.dataframe(
        best_row,
        use_container_width=True,
        hide_index=True,
    )

with right:
    st.markdown("### 🔴 Worst opportunity")
    st.dataframe(
        worst_row,
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# 16. EXCHANGE COMPARISON
# =========================================================

st.subheader("🏦 Exchange Comparison")

if buy_exchange_column and sell_exchange_column:

    exchange_data = filtered_data.copy()

    exchange_data["Route"] = (
        exchange_data[buy_exchange_column].astype(str)
        + " → "
        + exchange_data[sell_exchange_column].astype(str)
    )

    route_summary = (
        exchange_data.groupby("Route", dropna=False)
        .agg(
            Opportunities=(profit_column, "count"),
            Average_Net_Result=(profit_column, "mean"),
            Combined_Net_Result=(profit_column, "sum"),
            Best_Opportunity=(profit_column, "max"),
        )
        .reset_index()
    )

    route_summary = route_summary.sort_values(
        "Combined_Net_Result",
        ascending=False,
    )

    st.dataframe(
        route_summary,
        use_container_width=True,
        hide_index=True,
    )

    fig_exchange = px.bar(
        route_summary,
        x="Route",
        y="Combined_Net_Result",
        color="Combined_Net_Result",
        color_continuous_scale=[
            "#ff6262",
            "#e9c94b",
            "#2ecc71",
        ],
        title="Estimated Net Result by Exchange Route",
        labels={
            "Route": "Buy → Sell Route",
            "Combined_Net_Result": "Combined Net Result",
        },
    )

    fig_exchange.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_tickangle=-20,
    )

    st.plotly_chart(
        fig_exchange,
        use_container_width=True,
    )

elif exchange_column:

    exchange_summary = (
        filtered_data.groupby(exchange_column)[profit_column]
        .agg(["count", "mean", "sum", "max"])
        .reset_index()
    )

    exchange_summary.columns = [
        "Exchange",
        "Opportunities",
        "Average Net Result",
        "Combined Net Result",
        "Best Opportunity",
    ]

    st.dataframe(
        exchange_summary,
        use_container_width=True,
        hide_index=True,
    )

    fig_exchange = px.bar(
        exchange_summary,
        x="Exchange",
        y="Combined Net Result",
        color="Combined Net Result",
        title="Estimated Net Result by Exchange",
    )

    fig_exchange.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    st.plotly_chart(
        fig_exchange,
        use_container_width=True,
    )

else:
    st.info(
        "Exchange comparison needs exchange information in your results table. "
        "Available columns: "
        + ", ".join(str(column) for column in filtered_data.columns)
    )


# =========================================================
# 17. PRICE COMPARISON
# =========================================================

if buy_price_column and sell_price_column:

    st.subheader("💱 Buy Price vs Sell Price")

    price_data = filtered_data.copy()

    price_data[buy_price_column] = pd.to_numeric(
        price_data[buy_price_column],
        errors="coerce",
    )

    price_data[sell_price_column] = pd.to_numeric(
        price_data[sell_price_column],
        errors="coerce",
    )

    price_data = price_data.dropna(
        subset=[buy_price_column, sell_price_column]
    )

    if not price_data.empty:

        price_data["Opportunity"] = range(
            1,
            len(price_data) + 1,
        )

        long_prices = price_data.melt(
            id_vars=["Opportunity"],
            value_vars=[
                buy_price_column,
                sell_price_column,
            ],
            var_name="Price Type",
            value_name="Price",
        )

        fig_prices = px.bar(
            long_prices,
            x="Opportunity",
            y="Price",
            color="Price Type",
            barmode="group",
            title="Buy and Sell Price Comparison",
        )

        fig_prices.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )

        st.plotly_chart(
            fig_prices,
            use_container_width=True,
        )


# =========================================================
# 18. RECENT OPPORTUNITIES
# =========================================================

st.subheader("📋 Recent Arbitrage Results")

st.dataframe(
    filtered_data.tail(100).iloc[::-1],
    use_container_width=True,
    hide_index=True,
)


# =========================================================
# 19. CSV EXPORT
# =========================================================

csv_data = filtered_data.to_csv(
    index=False,
).encode("utf-8")

st.download_button(
    label="⬇️ Download Analytics CSV",
    data=csv_data,
    file_name="hft_arbitrage_analytics.csv",
    mime="text/csv",
)


# =========================================================
# 20. REFRESH
# =========================================================

st.caption(
    "Automatic refresh: every 5 seconds | "
    "Results are based on the latest records available in PostgreSQL."
)

# Stop the script briefly, then rerun the dashboard.
time.sleep(5)
st.rerun()