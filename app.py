import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Stock Market Dashboard",
    layout="wide"
)

# ---------------- TITLE ----------------
st.title("📈 Stock Market Visualization Dashboard")

# ---------------- LOAD DATA ----------------
try:
    df = pd.read_csv("./stock_dataset_1000_rows.csv")
except FileNotFoundError:
    st.error("❌ stock_dataset_1000_rows.csv not found. Keep it in the same folder as app.py")
    st.stop()

df["Date"] = pd.to_datetime(df["Date"])

# Handle NaN safely (do NOT remove everything)
df = df.dropna().reset_index(drop=True)

# Debug info (safe to keep)
st.write("✅ Data Loaded Successfully")
st.write("Total Rows:", df.shape[0])

# ---------------- SIDEBAR ----------------
st.sidebar.header("📊 Chart Controls")

show_sma = st.sidebar.checkbox("Show SMA 20 & SMA 50", True)
show_ema = st.sidebar.checkbox("Show EMA 20", True)
show_vwap = st.sidebar.checkbox("Show VWAP", False)
show_signals = st.sidebar.checkbox("Show Buy/Sell Signals", True)
animate = st.sidebar.checkbox("Animate chart", False)
animation_speed = st.sidebar.slider("Animation speed (ms)", 50, 2000, 200)
frame_step = st.sidebar.slider("Frame step (points)", 1, 50, 5)
visualization_mode = st.sidebar.selectbox(
    "Visualization type",
    ["Candlestick", "OHLC", "Line (Close)", "Area (Close)", "Volume Histogram", "Returns Histogram", "Up/Down Pie"]
)

# Build and render chart(s) based on selected visualization mode
if not animate:
    fig = go.Figure()
    if visualization_mode == "Candlestick":
        fig.add_candlestick(x=df["Date"], open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"], name="Price")
    elif visualization_mode == "OHLC":
        fig.add_trace(go.Ohlc(x=df["Date"], open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"], name="Price"))
    elif visualization_mode == "Line (Close)":
        fig.add_scatter(x=df["Date"], y=df["Close"], mode="lines", name="Close")
    elif visualization_mode == "Area (Close)":
        fig.add_scatter(x=df["Date"], y=df["Close"], mode="lines", fill="tozeroy", name="Close (Area)")
    elif visualization_mode == "Volume Histogram":
        fig = go.Figure(data=[go.Histogram(x=df["Volume"], nbinsx=50)])
        fig.update_layout(title="Volume Distribution", xaxis_title="Volume", yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)
        # skip indicator overlays
        pass
    elif visualization_mode == "Returns Histogram":
        returns = df["Close"].pct_change().dropna()
        fig = go.Figure(data=[go.Histogram(x=returns, nbinsx=50)])
        fig.update_layout(title="Returns Distribution", xaxis_title="Return", yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)
        pass
    elif visualization_mode == "Up/Down Pie":
        up = int((df["Close"] > df["Open"]).sum())
        down = int((df["Close"] <= df["Open"]).sum())
        fig = go.Figure(data=[go.Pie(labels=["Up", "Down"], values=[up, down], hole=0.25)])
        fig.update_layout(title="Up vs Down Days")
        st.plotly_chart(fig, use_container_width=True)
        pass

    # indicators overlay
    if show_sma:
        fig.add_scatter(x=df["Date"], y=df["SMA_20"], name="SMA 20", line=dict(width=1))
        fig.add_scatter(x=df["Date"], y=df["SMA_50"], name="SMA 50", line=dict(width=1))
    if show_ema:
        fig.add_scatter(x=df["Date"], y=df["EMA_20"], name="EMA 20", line=dict(width=1))
    if show_vwap:
        fig.add_scatter(x=df["Date"], y=df["VWAP"], name="VWAP", line=dict(width=1))

    # Buy/Sell markers (works for all modes)
    if show_signals:
        fig.add_scatter(x=df[df["Buy_Signal"]]["Date"], y=df[df["Buy_Signal"]]["Close"], mode="markers", marker=dict(symbol="triangle-up", size=10), name="Buy Signal")
        fig.add_scatter(x=df[df["Sell_Signal"]]["Date"], y=df[df["Sell_Signal"]]["Close"], mode="markers", marker=dict(symbol="triangle-down", size=10), name="Sell Signal")

    # For histogram/pie we already rendered above and can skip overlays
    if visualization_mode not in ["Volume Histogram", "Returns Histogram", "Up/Down Pie"]:
        # indicators overlay
        if show_sma:
            fig.add_scatter(x=df["Date"], y=df["SMA_20"], name="SMA 20", line=dict(width=1))
            fig.add_scatter(x=df["Date"], y=df["SMA_50"], name="SMA 50", line=dict(width=1))
        if show_ema:
            fig.add_scatter(x=df["Date"], y=df["EMA_20"], name="EMA 20", line=dict(width=1))
        if show_vwap:
            fig.add_scatter(x=df["Date"], y=df["VWAP"], name="VWAP", line=dict(width=1))

        # Buy/Sell markers (works for all modes except pure hist/pie)
        if show_signals:
            fig.add_scatter(x=df[df["Buy_Signal"]]["Date"], y=df[df["Buy_Signal"]]["Close"], mode="markers", marker=dict(symbol="triangle-up", size=10), name="Buy Signal")
            fig.add_scatter(x=df[df["Sell_Signal"]]["Date"], y=df[df["Sell_Signal"]]["Close"], mode="markers", marker=dict(symbol="triangle-down", size=10), name="Sell Signal")

        fig.update_layout(height=600, xaxis_rangeslider_visible=False, title=f"📈 {visualization_mode} with Indicators")
        st.plotly_chart(fig, use_container_width=True)
else:
    # Animated frames for selected visualization_mode
    # If user selected a non-time-series viz, render static instead
    if visualization_mode in ["Volume Histogram", "Returns Histogram", "Up/Down Pie"]:
        if visualization_mode == "Volume Histogram":
            fig = go.Figure(data=[go.Histogram(x=df["Volume"], nbinsx=50)])
            fig.update_layout(title="Volume Distribution", xaxis_title="Volume", yaxis_title="Count")
        elif visualization_mode == "Returns Histogram":
            returns = df["Close"].pct_change().dropna()
            fig = go.Figure(data=[go.Histogram(x=returns, nbinsx=50)])
            fig.update_layout(title="Returns Distribution", xaxis_title="Return", yaxis_title="Count")
        else:
            up = int((df["Close"] > df["Open"]).sum())
            down = int((df["Close"] <= df["Open"]).sum())
            fig = go.Figure(data=[go.Pie(labels=["Up", "Down"], values=[up, down], hole=0.25)])
            fig.update_layout(title="Up vs Down Days")

        st.plotly_chart(fig, use_container_width=True)
        # don't run the time-series animation
        pass
    else:
        frames = []
        n = len(df)
        step = max(1, int(frame_step))

        init_slice = df.iloc[:step]
        init_traces = []

        if visualization_mode == "Candlestick":
            init_traces.append(go.Candlestick(x=init_slice["Date"], open=init_slice["Open"], high=init_slice["High"], low=init_slice["Low"], close=init_slice["Close"], name="Price"))
        elif visualization_mode == "OHLC":
            init_traces.append(go.Ohlc(x=init_slice["Date"], open=init_slice["Open"], high=init_slice["High"], low=init_slice["Low"], close=init_slice["Close"], name="Price"))
        elif visualization_mode == "Line (Close)":
            init_traces.append(go.Scatter(x=init_slice["Date"], y=init_slice["Close"], mode="lines", name="Close"))
        elif visualization_mode == "Area (Close)":
            init_traces.append(go.Scatter(x=init_slice["Date"], y=init_slice["Close"], mode="lines", fill="tozeroy", name="Close (Area)"))

        if show_sma:
            init_traces.append(go.Scatter(x=init_slice["Date"], y=init_slice["SMA_20"], name="SMA 20"))
            init_traces.append(go.Scatter(x=init_slice["Date"], y=init_slice["SMA_50"], name="SMA 50"))
        if show_ema:
            init_traces.append(go.Scatter(x=init_slice["Date"], y=init_slice["EMA_20"], name="EMA 20"))
        if show_vwap:
            init_traces.append(go.Scatter(x=init_slice["Date"], y=init_slice["VWAP"], name="VWAP"))

        if show_signals:
            init_traces.append(go.Scatter(x=init_slice[init_slice["Buy_Signal"]]["Date"], y=init_slice[init_slice["Buy_Signal"]]["Close"], mode="markers", marker=dict(symbol="triangle-up", size=10), name="Buy Signal"))
            init_traces.append(go.Scatter(x=init_slice[init_slice["Sell_Signal"]]["Date"], y=init_slice[init_slice["Sell_Signal"]]["Close"], mode="markers", marker=dict(symbol="triangle-down", size=10), name="Sell Signal"))

        for i in range(step, n + 1, step):
            s = df.iloc[:i]
            if visualization_mode == "Candlestick":
                frame_main = go.Candlestick(x=s["Date"], open=s["Open"], high=s["High"], low=s["Low"], close=s["Close"])
            elif visualization_mode == "OHLC":
                frame_main = go.Ohlc(x=s["Date"], open=s["Open"], high=s["High"], low=s["Low"], close=s["Close"])
            elif visualization_mode == "Line (Close)":
                frame_main = go.Scatter(x=s["Date"], y=s["Close"], mode="lines")
            else:
                frame_main = go.Scatter(x=s["Date"], y=s["Close"], mode="lines", fill="tozeroy")

            frame_data = [frame_main]

            if show_sma:
                frame_data.append(go.Scatter(x=s["Date"], y=s["SMA_20"]))
                frame_data.append(go.Scatter(x=s["Date"], y=s["SMA_50"]))
            if show_ema:
                frame_data.append(go.Scatter(x=s["Date"], y=s["EMA_20"]))
            if show_vwap:
                frame_data.append(go.Scatter(x=s["Date"], y=s["VWAP"]))

            if show_signals:
                frame_data.append(go.Scatter(x=s[s["Buy_Signal"]]["Date"], y=s[s["Buy_Signal"]]["Close"], mode="markers", marker=dict(symbol="triangle-up", size=10)))
                frame_data.append(go.Scatter(x=s[s["Sell_Signal"]]["Date"], y=s[s["Sell_Signal"]]["Close"], mode="markers", marker=dict(symbol="triangle-down", size=10)))

            frames.append(go.Frame(data=frame_data, name=str(i)))

        fig = go.Figure(data=init_traces, frames=frames)
        fig.update_layout(height=600, xaxis_rangeslider_visible=False, title=f"📈 {visualization_mode} (animated)")
        fig.update_layout(updatemenus=[dict(type="buttons", showactive=False, y=1.05, x=1.15, xanchor="right", yanchor="top", buttons=[dict(label="Play", method="animate", args=[None, {"frame": {"duration": animation_speed, "redraw": True}, "fromcurrent": True}]), dict(label="Pause", method="animate", args=[[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}])])])
        st.plotly_chart(fig, use_container_width=True)

fig.update_layout(
    height=600,
    xaxis_rangeslider_visible=False,
    title="📈 Price Action with Indicators"
)

st.plotly_chart(fig, use_container_width=True)

# ---------------- VOLUME ----------------
st.subheader("📊 Trading Volume")
st.bar_chart(df.set_index("Date")["Volume"])

# ---------------- RSI ----------------
st.subheader("⚡ RSI Indicator")
st.line_chart(df.set_index("Date")["RSI"])

# ---------------- MACD ----------------
st.subheader("🔁 MACD Indicator")
macd_df = df.set_index("Date")[["MACD", "Signal_Line", "Histogram"]]
st.line_chart(macd_df)

# ---------------- FOOTER ----------------
st.markdown("---")

