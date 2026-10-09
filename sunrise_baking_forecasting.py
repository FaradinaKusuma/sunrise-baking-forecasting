import streamlit as st
import pandas as pd
import plotly.express as px

# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="Sunrise Baking Forecasting",
    page_icon="🥯",
    layout="wide"
)

# ============================================================
# TITLE
# ============================================================
st.title("🥯 Sunrise Baking Company")
st.subheader("Demand Forecasting Application")

st.markdown("""
Aplikasi ini menyelesaikan kasus forecasting Sunrise Baking Company
dengan empat pendekatan:

1. **Simple Four-Week Moving Average**
2. **Weighted Moving Average**
3. **Exponential Smoothing**
4. **Updated Exponential Smoothing**
""")

# ============================================================
# SIDEBAR - PARAMETERS
# ============================================================
st.sidebar.header("⚙️ Forecasting Parameters")

alpha = st.sidebar.slider(
    "Alpha (α)",
    min_value=0.01,
    max_value=1.00,
    value=0.10,
    step=0.01,
    help="Nilai alpha untuk exponential smoothing."
)

st.sidebar.markdown("---")
st.sidebar.subheader("Weighted Moving Average")

w_oldest = st.sidebar.number_input(
    "4 Weeks Ago",
    min_value=0.0,
    max_value=1.0,
    value=0.10,
    step=0.05
)

w_3weeks = st.sidebar.number_input(
    "3 Weeks Ago",
    min_value=0.0,
    max_value=1.0,
    value=0.20,
    step=0.05
)

w_2weeks = st.sidebar.number_input(
    "2 Weeks Ago",
    min_value=0.0,
    max_value=1.0,
    value=0.30,
    step=0.05
)

w_last = st.sidebar.number_input(
    "Last Week",
    min_value=0.0,
    max_value=1.0,
    value=0.40,
    step=0.05
)

weight_total = w_oldest + w_3weeks + w_2weeks + w_last

if abs(weight_total - 1.0) > 0.0001:
    st.sidebar.error(
        f"Total bobot = {weight_total:.2f}. "
        "Total bobot harus sama dengan 1.00."
    )
else:
    st.sidebar.success("Total bobot = 1.00 ✓")

# ============================================================
# HISTORICAL DATA
# ============================================================
days = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday + Sunday"
]

data = {
    "4 Weeks Ago": [2200, 2000, 2300, 1800, 1900, 2800],
    "3 Weeks Ago": [2400, 2100, 2400, 1900, 1800, 2700],
    "2 Weeks Ago": [2300, 2200, 2300, 1800, 2100, 3000],
    "Last Week":  [2400, 2200, 2500, 2000, 2000, 2900]
}

df = pd.DataFrame(data, index=days)

# ============================================================
# SECTION 1 - HISTORICAL DATA
# ============================================================
st.header("1. Historical Demand")

st.info(
    "Bakery tutup pada hari Sabtu. Oleh karena itu, "
    "forecast untuk periode Jumat produksi mencakup kebutuhan "
    "Saturday + Sunday, sesuai solution pada soal."
)

display_df = df.copy()
st.dataframe(
    display_df.style.format("{:,.0f}"),
    use_container_width=True
)

# ============================================================
# SECTION 2 - SIMPLE MOVING AVERAGE
# ============================================================
st.header("2. Part A — Simple Four-Week Moving Average")

st.markdown("""
### Rumus

$$
F_t = \\frac{D_{t-1}+D_{t-2}+D_{t-3}+D_{t-4}}{4}
$$

Setiap forecast menggunakan demand untuk **hari/periode yang sama**
selama empat minggu sebelumnya.
""")

df["SMA Forecast"] = df[
    ["4 Weeks Ago", "3 Weeks Ago", "2 Weeks Ago", "Last Week"]
].mean(axis=1)

sma_result = df[["SMA Forecast"]].copy()

st.dataframe(
    sma_result.style.format("{:,.0f}"),
    use_container_width=True
)

with st.expander("🔎 Lihat contoh perhitungan Monday"):
    monday_sma = (
        2400 + 2300 + 2400 + 2200
    ) / 4

    st.latex(
        r"F_{Monday} = "
        r"\frac{2400+2300+2400+2200}{4}"
        r"= 2,325"
    )

# ============================================================
# SECTION 3 - WEIGHTED MOVING AVERAGE
# ============================================================
st.header("3. Part B — Weighted Moving Average")

st.markdown("""
### Rumus

$$
F_t =
w_1D_{t-4}
+w_2D_{t-3}
+w_3D_{t-2}
+w_4D_{t-1}
$$

Bobot default sesuai soal:

- 4 Weeks Ago = **0.10**
- 3 Weeks Ago = **0.20**
- 2 Weeks Ago = **0.30**
- Last Week = **0.40**
""")

if abs(weight_total - 1.0) <= 0.0001:
    df["WMA Forecast"] = (
        w_oldest * df["4 Weeks Ago"]
        + w_3weeks * df["3 Weeks Ago"]
        + w_2weeks * df["2 Weeks Ago"]
        + w_last * df["Last Week"]
    )
else:
    df["WMA Forecast"] = float("nan")

wma_result = df[["WMA Forecast"]].copy()

st.dataframe(
    wma_result.style.format("{:,.0f}"),
    use_container_width=True
)

with st.expander("🔎 Lihat contoh perhitungan Monday"):
    st.latex(
        r"F_{Monday}="
        r"0.10(2200)+0.20(2400)+0.30(2300)+0.40(2400)"
        r"=2,350"
    )

# ============================================================
# SECTION 4 - COMPARISON
# ============================================================
st.header("4. Comparison: SMA vs Weighted MA")

comparison = df[
    ["SMA Forecast", "WMA Forecast"]
].reset_index()

comparison = comparison.rename(columns={"index": "Period"})

st.dataframe(
    comparison.style.format({
        "SMA Forecast": "{:,.0f}",
        "WMA Forecast": "{:,.0f}"
    }),
    use_container_width=True,
    hide_index=True
)

chart_df = comparison.melt(
    id_vars="Period",
    value_vars=["SMA Forecast", "WMA Forecast"],
    var_name="Method",
    value_name="Forecast"
)

fig = px.bar(
    chart_df,
    x="Period",
    y="Forecast",
    color="Method",
    barmode="group",
    title="Forecast This Week: SMA vs Weighted MA",
    labels={
        "Period": "Production Period",
        "Forecast": "Forecast Demand (dozen)"
    }
)

st.plotly_chart(fig, use_container_width=True)

# ============================================================
# SECTION 5 - EXPONENTIAL SMOOTHING
# ============================================================
st.header("5. Part C — Exponential Smoothing")

st.markdown("""
Diketahui:

- Forecast minggu lalu = **22,000 loaves**
- Actual demand minggu lalu = **21,000 loaves**
- α = **0.10**

Rumus:

$$
F_t = F_{t-1}+\\alpha(A_{t-1}-F_{t-1})
$$
""")

col1, col2, col3 = st.columns(3)

with col1:
    previous_forecast = st.number_input(
        "Forecast minggu lalu",
        min_value=0.0,
        value=22000.0,
        step=100.0
    )

with col2:
    actual_last_week = st.number_input(
        "Actual demand minggu lalu",
        min_value=0.0,
        value=21000.0,
        step=100.0
    )

with col3:
    st.metric(
        "Alpha",
        f"{alpha:.2f}"
    )

forecast_this_week = (
    previous_forecast
    + alpha * (
        actual_last_week - previous_forecast
    )
)

st.success(
    f"Forecast minggu ini = "
    f"{forecast_this_week:,.0f} loaves"
)

with st.expander("🔎 Lihat perhitungan Part C"):
    st.latex(
        rf"""
        F_t = 22,000 + 0.10(21,000-22,000)
        = 21,900
        """
    )

# ============================================================
# SECTION 6 - UPDATED EXPONENTIAL SMOOTHING
# ============================================================
st.header("6. Part D — Forecast Minggu Berikutnya")

st.markdown("""
Diketahui actual demand minggu ini adalah **22,500 loaves**.

Forecast minggu depan dihitung menggunakan:

$$
F_{t+1}=F_t+\\alpha(A_t-F_t)
$$
""")

actual_this_week = st.number_input(
    "Actual demand minggu ini",
    min_value=0.0,
    value=22500.0,
    step=100.0
)

forecast_next_week = (
    forecast_this_week
    + alpha * (
        actual_this_week - forecast_this_week
    )
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Forecast minggu ini",
        f"{forecast_this_week:,.0f}"
    )

with col2:
    st.metric(
        "Actual minggu ini",
        f"{actual_this_week:,.0f}"
    )

with col3:
    st.metric(
        "Forecast minggu depan",
        f"{forecast_next_week:,.0f}"
    )

with st.expander("🔎 Lihat perhitungan Part D"):
    st.latex(
        rf"""
        F_{{t+1}}
        = 21,900 + 0.10(22,500-21,900)
        = 21,960
        """
    )

# ============================================================
# SECTION 7 - SUMMARY
# ============================================================
st.header("7. Summary")

summary = pd.DataFrame({
    "Part": ["A", "B", "C", "D"],
    "Method": [
        "Simple 4-Week Moving Average",
        "Weighted Moving Average",
        "Exponential Smoothing",
        "Updated Exponential Smoothing"
    ],
    "Result": [
        "Forecast per production period",
        "Forecast per production period",
        f"{forecast_this_week:,.0f} loaves",
        f"{forecast_next_week:,.0f} loaves"
    ]
})

st.dataframe(
    summary,
    use_container_width=True,
    hide_index=True
)

# ============================================================
# KEY LEARNING POINTS
# ============================================================
st.header("8. Key Learning Points")

st.markdown("""
### 📌 Interpretasi

**Simple Moving Average**
- Semua periode historis memiliki bobot yang sama.
- Lebih sederhana dan stabil.

**Weighted Moving Average**
- Data terbaru diberi bobot lebih besar.
- Lebih responsif terhadap perubahan demand.

**Exponential Smoothing**
- Forecast diperbarui berdasarkan forecast sebelumnya
  dan actual demand.
- Nilai α menentukan seberapa responsif forecast terhadap perubahan aktual.

**Production Planning**
- Karena bakery tutup hari Sabtu, kebutuhan **Saturday + Sunday**
  diperlakukan sebagai satu periode produksi.
""")

st.caption(
    "Sunrise Baking Company — Forecasting Application | "
    "Streamlit + Pandas + Plotly"
)
