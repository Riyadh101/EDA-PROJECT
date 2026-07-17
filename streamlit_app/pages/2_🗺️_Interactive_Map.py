"""
pages/2_🗺️_Interactive_Map.py — combat directions map with search + time animation.
صفحة الخريطة التفاعلية: بحث عن المواقع + خريطة متحركة عبر الزمن + خريطة إجمالية ثابتة.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from common import (
    COLOR_SEQUENTIAL, LOCATION_COORDS, LOCATION_LABELS_AR, get_data,
    init_sidebar_controls, parse_directions, render_banner, t,
)

st.set_page_config(page_title="Interactive Map", page_icon="🗺️", layout="wide", initial_sidebar_state="expanded")

df, is_live = get_data()
ctrl = init_sidebar_controls(df, is_live)
lang = ctrl["lang"]
filtered_df = ctrl["filtered_df"]

render_banner(
    "🗺️ Interactive Map — Reported Combat Directions" if lang == "en" else "🗺️ خريطة تفاعلية — مناطق القتال المُبلغ عنها",
    "Built from the free-text location column, geocoded to real coordinates." if lang == "en"
    else "مبنية من عمود المواقع النصي، مربوطة بإحداثيات حقيقية.",
)

loc_label_map = LOCATION_LABELS_AR if lang == "ar" else {k: k for k in LOCATION_COORDS}

# --- Search box: filter map markers by location name ---
search_query = st.text_input(
    "🔎 Search for a location" if lang == "en" else "🔎 ابحث عن منطقة",
    value="", key="map_search",
    placeholder="e.g. Bakhmut" if lang == "en" else "مثال: باخموت",
)


def build_location_counts(data: pd.DataFrame) -> dict:
    counts = {}
    for direction_text in data["greatest_losses_direction"]:
        for loc in parse_directions(direction_text):
            if loc in LOCATION_COORDS:
                counts[loc] = counts.get(loc, 0) + 1
    return counts


# =========================================================
# Static aggregate map (whole selected date range at once)
# =========================================================
st.subheader("📍 Aggregate Map (Selected Date Range)" if lang == "en" else "📍 خريطة إجمالية (النطاق الزمني المختار)")

location_counts = build_location_counts(filtered_df)
if search_query.strip():
    q = search_query.strip().lower()
    location_counts = {
        loc: c for loc, c in location_counts.items()
        if q in loc_label_map.get(loc, loc).lower() or q in loc.lower()
    }

if not location_counts:
    st.info(
        "No matching combat directions found for the current filters/search."
        if lang == "en" else
        "لا توجد مناطق قتال مطابقة للفلاتر أو البحث الحالي."
    )
else:
    map_df = pd.DataFrame(
        [
            {"location": loc_label_map.get(loc, loc), "lat": LOCATION_COORDS[loc][0],
             "lon": LOCATION_COORDS[loc][1], "days_mentioned": count}
            for loc, count in location_counts.items()
        ]
    ).sort_values("days_mentioned", ascending=False)

    fig_map = px.scatter_mapbox(
        map_df, lat="lat", lon="lon", size="days_mentioned", color="days_mentioned",
        hover_name="location", hover_data={"lat": False, "lon": False, "days_mentioned": True},
        color_continuous_scale=COLOR_SEQUENTIAL, size_max=40, zoom=5.3,
        center={"lat": 48.5, "lon": 37.0}, mapbox_style="open-street-map",
    )
    fig_map.update_layout(height=520, margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig_map, use_container_width=True)

    top_loc = map_df.iloc[0]
    if lang == "en":
        st.info(f"📌 **{top_loc['location']}** was the most frequently reported direction, mentioned on **{int(top_loc['days_mentioned'])}** day(s).")
    else:
        st.info(f"📌 **{top_loc['location']}** كانت أكثر منطقة مذكورة، وردت في **{int(top_loc['days_mentioned'])}** يوم.")

st.markdown("---")

# =========================================================
# Animated map: how reported combat directions shift month by month
# خريطة متحركة: كيف تتغيّر مناطق القتال المذكورة شهرًا بعد شهر
# =========================================================
st.subheader("🎬 Animated Map — Month by Month" if lang == "en" else "🎬 خريطة متحركة — شهرًا بشهر")
st.caption(
    "Press ▶ play to watch how reported hotspots shift over time within your selected date range."
    if lang == "en" else
    "اضغط ▶ تشغيل عشان تشوف كيف تتغيّر بؤر القتال المذكورة عبر الزمن ضمن النطاق المختار."
)

anim_df = filtered_df.copy()
anim_df["month_label"] = anim_df["date"].dt.strftime("%Y-%m")

rows = []
for month_label, group in anim_df.groupby("month_label"):
    counts = build_location_counts(group)
    if search_query.strip():
        q = search_query.strip().lower()
        counts = {loc: c for loc, c in counts.items() if q in loc_label_map.get(loc, loc).lower() or q in loc.lower()}
    for loc, c in counts.items():
        rows.append({
            "month": month_label, "location": loc_label_map.get(loc, loc),
            "lat": LOCATION_COORDS[loc][0], "lon": LOCATION_COORDS[loc][1], "days_mentioned": c,
        })

if not rows:
    st.info(
        "No monthly combat-direction data available for the current filters/search."
        if lang == "en" else
        "لا توجد بيانات شهرية لمناطق القتال ضمن الفلاتر أو البحث الحالي."
    )
else:
    anim_plot_df = pd.DataFrame(rows).sort_values("month")
    fig_anim = px.scatter_mapbox(
        anim_plot_df, lat="lat", lon="lon", size="days_mentioned", color="days_mentioned",
        hover_name="location", animation_frame="month",
        color_continuous_scale=COLOR_SEQUENTIAL, size_max=35, zoom=5,
        center={"lat": 48.5, "lon": 37.0}, mapbox_style="open-street-map",
        range_color=[0, anim_plot_df["days_mentioned"].max()],
    )
    fig_anim.update_layout(height=550, margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig_anim, use_container_width=True)

st.caption(t("accessibility_note", lang))
st.caption(t("footer", lang))
