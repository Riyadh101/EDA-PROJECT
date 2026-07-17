"""
views/overview.py — Home / Overview page content.
محتوى الصفحة الرئيسية: بانر، بطاقات KPI مخصصة، مقارنة أسبوعية، رسم زمني بعلامات أهم المعارك.
(لا يوجد هنا st.set_page_config — يُستدعى مرة واحدة فقط من app.py الموجّه الرئيسي)
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from common import (
    BATTLE_EVENTS, get_data, init_sidebar_controls, render_banner, render_kpi_card, t,
)

df, is_live = get_data()
ctrl = init_sidebar_controls(df, is_live)
lang = ctrl["lang"]
filtered_df = ctrl["filtered_df"]

# --- Banner / بانر علوي ---
render_banner(
    "📊 Russia-Ukraine War Losses — Overview" if lang == "en" else "📊 خسائر حرب روسيا وأوكرانيا — نظرة عامة",
    t("nav_hint", lang),
)

st.markdown(t("about_body", lang, n_days=len(df)).split("\n\n")[0])

# --- Custom KPI cards (colored borders instead of default st.metric) ---
# بطاقات KPI مخصصة بحدود ملونة بدل st.metric الافتراضية
latest_row = filtered_df.iloc[-1]
first_row = filtered_df.iloc[0]

col1, col2, col3, col4 = st.columns(4)
with col1:
    render_kpi_card(
        f"👤 {t('kpi_personnel', lang)}", f"{int(latest_row['personnel']):,}",
        t("kpi_personnel_delta", lang, delta=int(latest_row["personnel"] - first_row["personnel"])),
        color="#b91c1c",
    )
with col2:
    render_kpi_card(
        f"🛡️ {t('kpi_equipment', lang)}", f"{int(latest_row['total_equipment_losses']):,}",
        t("kpi_equipment_delta", lang, delta=int(latest_row["total_equipment_losses"] - first_row["total_equipment_losses"])),
        color="#1d4ed8",
    )
with col3:
    render_kpi_card(f"📅 {t('kpi_days', lang)}", f"{len(filtered_df):,}", "", color="#6b7280")
with col4:
    render_kpi_card(
        f"📈 {t('kpi_avg', lang)}", f"{filtered_df['personnel_daily_new'].mean():.0f}", "", color="#d97706",
    )

st.markdown("---")

# =========================================================
# This Week vs Last Week comparison (based on the full, unfiltered
# dataset's most recent 14 days, independent of sidebar date filter,
# since "this week" should reflect real calendar time, not a custom range)
# مقارنة هذا الأسبوع بالأسبوع اللي قبله (من كامل البيانات، مو من الفلتر المختار،
# لأن "هذا الأسبوع" لازم يعكس الوقت الفعلي الحالي مو نطاق تاريخ مخصص)
# =========================================================
st.subheader("📆 This Week vs. Last Week" if lang == "en" else "📆 هذا الأسبوع مقابل الأسبوع اللي قبله")

last_14 = df.tail(14)
if len(last_14) >= 14:
    this_week = last_14.tail(7)
    last_week = last_14.head(7)

    def compare_block(col_key, label_key, icon):
        this_sum = int(this_week[col_key].sum())
        last_sum = int(last_week[col_key].sum())
        delta = this_sum - last_sum
        pct = (delta / last_sum * 100) if last_sum > 0 else 0
        arrow = "🔺" if delta > 0 else ("🔻" if delta < 0 else "▪️")
        st.markdown(
            f"**{icon} {t(label_key, lang)}** — "
            f"{'This week' if lang == 'en' else 'هذا الأسبوع'}: **{this_sum:,}** · "
            f"{'Last week' if lang == 'en' else 'الأسبوع الماضي'}: **{last_sum:,}** · "
            f"{arrow} {delta:+,} ({pct:+.0f}%)"
        )

    c1, c2 = st.columns(2)
    with c1:
        compare_block("personnel_daily_new", "kpi_personnel", "👤")
    with c2:
        compare_block("equipment_daily_new", "kpi_equipment", "🛡️")
else:
    st.info("Not enough recent data yet for a week-over-week comparison." if lang == "en"
            else "لا توجد بيانات كافية حاليًا لعمل مقارنة أسبوعية.")

st.markdown("---")

# =========================================================
# Annotated cumulative timeline — key battles marked on the chart
# رسم زمني تراكمي مع علامات لأهم المعارك الموثقة
# =========================================================
st.subheader("📈 Cumulative Losses Timeline (with major reported battles marked)" if lang == "en"
             else "📈 الخط الزمني للخسائر التراكمية (مع علامات لأهم المعارك المُبلغ عنها)")

fig = go.Figure()
fig.add_trace(go.Scatter(x=filtered_df["date"], y=filtered_df["personnel"],
                          name=t("kpi_personnel", lang), line=dict(color="#b91c1c")))
fig.add_trace(go.Scatter(x=filtered_df["date"], y=filtered_df["total_equipment_losses"],
                          name=t("kpi_equipment", lang), line=dict(color="#1d4ed8"), yaxis="y2"))

date_min, date_max = filtered_df["date"].min(), filtered_df["date"].max()
for event in BATTLE_EVENTS:
    event_date = pd.Timestamp(event["date"])
    if date_min <= event_date <= date_max:
        fig.add_vline(x=event_date.timestamp() * 1000, line_dash="dot", line_color="gray", opacity=0.6)
        fig.add_annotation(
            x=event_date, y=1.02, yref="paper", showarrow=False,
            text=event[lang], textangle=-35, font=dict(size=10, color="gray"), xanchor="left",
        )

fig.update_layout(
    xaxis_title="Date",
    yaxis=dict(title=dict(text=t("kpi_personnel", lang), font=dict(color="#b91c1c"))),
    yaxis2=dict(title=dict(text=t("kpi_equipment", lang), font=dict(color="#1d4ed8")), overlaying="y", side="right"),
    legend=dict(orientation="h", y=1.12),
    height=480,
    margin=dict(t=60),
)
st.plotly_chart(fig, use_container_width=True)
st.caption(t("accessibility_note", lang))

st.caption(t("footer", lang))
