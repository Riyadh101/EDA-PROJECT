"""
views/deep_analysis.py — detailed charts and the predictive model.
صفحة التحليل المتعمق: مقارنة الفئات، خريطة الارتباط، النموذج التنبؤي.
(لا يوجد هنا st.set_page_config — يُستدعى مرة واحدة فقط من app.py الموجّه الرئيسي)
"""

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from common import (
    COLOR_DIVERGING, COLOR_SEQUENTIAL, EQUIP_COLS, equip_label_with_icon,
    get_data, init_sidebar_controls, render_banner, t,
)

df, is_live = get_data()
ctrl = init_sidebar_controls(df, is_live)
lang = ctrl["lang"]
filtered_df = ctrl["filtered_df"]
selected_equipment = ctrl["selected_equipment"]
trend_category = ctrl["trend_category"]

render_banner(
    "📊 Deep Analysis" if lang == "en" else "📊 تحليل متعمق",
    "Multi-category comparisons, correlations, and a predictive model" if lang == "en"
    else "مقارنة عدة فئات، الارتباطات، ونموذج تنبؤي",
)

# 1) Multi-line comparison of selected equipment categories
st.subheader("Selected Equipment Categories Over Time" if lang == "en" else "مقارنة فئات المعدات المختارة عبر الزمن")
long_df = filtered_df.melt(id_vars="date", value_vars=selected_equipment, var_name="category", value_name="count")
long_df["category"] = long_df["category"].apply(lambda c: equip_label_with_icon(c, lang))
fig2 = px.line(long_df, x="date", y="count", color="category",
               labels={"count": "Cumulative Losses" if lang == "en" else "الخسائر التراكمية", "date": "Date", "category": ""},
               color_discrete_sequence=px.colors.sequential.Viridis_r)
fig2.update_layout(height=450, legend=dict(orientation="h", y=1.15))
st.plotly_chart(fig2, use_container_width=True)

# 2) Trend of a single selected category
st.subheader(
    ("Daily New Losses for: " if lang == "en" else "الخسائر اليومية الجديدة لفئة: ")
    + equip_label_with_icon(trend_category, lang)
)
trend_series = filtered_df[["date", trend_category]].copy()
trend_series["daily_new"] = trend_series[trend_category].diff().fillna(trend_series[trend_category]).clip(lower=0)
fig3 = px.bar(trend_series, x="date", y="daily_new",
              labels={"daily_new": "Daily New Losses" if lang == "en" else "الخسائر اليومية الجديدة", "date": "Date"},
              color_discrete_sequence=["#1d4ed8"])
fig3.update_layout(height=400)
st.plotly_chart(fig3, use_container_width=True)

# 3) Bar chart of totals by category (colorblind-safe Viridis)
st.subheader("Total Losses by Equipment Category (Latest Day in Range)" if lang == "en"
             else "إجمالي الخسائر حسب فئة المعدات (آخر يوم ضمن النطاق المختار)")
latest_row = filtered_df.iloc[-1]
totals = latest_row[EQUIP_COLS].sort_values(ascending=False)
totals_df = pd.DataFrame({"category": [equip_label_with_icon(c, lang) for c in totals.index], "total": totals.values})
fig4 = px.bar(totals_df, x="total", y="category", orientation="h", color="total",
              color_continuous_scale=COLOR_SEQUENTIAL,
              labels={"total": "Total Units Lost" if lang == "en" else "إجمالي الوحدات المفقودة", "category": ""})
fig4.update_layout(height=550, yaxis=dict(autorange="reversed"))
st.plotly_chart(fig4, use_container_width=True)

# 4) Correlation heatmap (colorblind-safe diverging scale)
st.subheader("Correlation Heatmap Between Loss Categories" if lang == "en" else "خريطة الارتباط الحرارية بين فئات الخسائر")
corr_cols = ["personnel_daily_new", "equipment_daily_new"] + selected_equipment
corr_matrix = filtered_df[corr_cols].corr()
corr_name_map = {
    "personnel_daily_new": t("kpi_personnel", lang),
    "equipment_daily_new": t("kpi_equipment", lang),
}
corr_matrix.index = [corr_name_map.get(c, equip_label_with_icon(c, lang)) for c in corr_matrix.index]
corr_matrix.columns = [corr_name_map.get(c, equip_label_with_icon(c, lang)) for c in corr_matrix.columns]
fig5 = px.imshow(corr_matrix, text_auto=".2f", color_continuous_scale=COLOR_DIVERGING, zmin=-1, zmax=1)
fig5.update_layout(height=500)
st.plotly_chart(fig5, use_container_width=True)
st.caption(t("accessibility_note", lang))

st.markdown("---")

# =========================================================
# Predictive model
# =========================================================
st.header("🔮 Simple Predictive Model" if lang == "en" else "🔮 نموذج تنبؤي بسيط")
st.caption(
    "A simple linear regression projecting the trend of cumulative personnel losses for upcoming days."
    if lang == "en" else
    "انحدار خطي بسيط لتوقّع اتجاه الخسائر البشرية التراكمية للأيام القادمة."
)

forecast_days = st.number_input(
    "Number of Future Days to Forecast" if lang == "en" else "عدد الأيام المستقبلية للتوقع",
    min_value=7, max_value=90, value=30, step=7, key="forecast_days",
)

if len(filtered_df) < 3:
    st.warning(
        "⚠️ Too few days in the current filter selection to build a reliable predictive model."
        if lang == "en" else
        "⚠️ عدد الأيام ضمن الفلاتر الحالية قليل جدًا لبناء نموذج تنبؤي موثوق."
    )
else:
    x = np.arange(len(filtered_df))
    y = filtered_df["personnel"].values
    coeffs = np.polyfit(x, y, deg=1)
    poly = np.poly1d(coeffs)

    future_x = np.arange(len(filtered_df), len(filtered_df) + forecast_days)
    future_dates = pd.date_range(filtered_df["date"].max() + pd.Timedelta(days=1), periods=forecast_days)
    future_y = poly(future_x)

    import plotly.graph_objects as go
    fig6 = go.Figure()
    fig6.add_trace(go.Scatter(x=filtered_df["date"], y=y, name="Actual" if lang == "en" else "فعلي", line=dict(color="#b91c1c")))
    fig6.add_trace(go.Scatter(x=future_dates, y=future_y, name="Projected" if lang == "en" else "متوقّع", line=dict(color="#d97706", dash="dash")))
    fig6.update_layout(height=450, xaxis_title="Date", yaxis_title=t("kpi_personnel", lang), legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig6, use_container_width=True)

    if lang == "en":
        st.info(f"📌 Based on the current linear trend, cumulative personnel losses are projected to reach approximately **{int(future_y[-1]):,}** over the next {forecast_days} days (~{coeffs[0]:.0f}/day).")
    else:
        st.info(f"📌 وفق الاتجاه الخطي الحالي، التوقع هو ازدياد الخسائر البشرية التراكمية إلى **{int(future_y[-1]):,}** تقريبًا خلال {forecast_days} يومًا (بمعدل ~{coeffs[0]:.0f} يوميًا).")

st.caption(t("footer", lang))
