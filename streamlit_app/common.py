"""
common.py — Shared logic used across all pages of the dashboard:
data loading, translations (EN/AR), constants, and sidebar filters.
ملف مشترك: يحتوي كل الأكواد المستخدمة بأكثر من صفحة (بيانات، ترجمة، ثيم، فلاتر)
حتى ما نكرر نفس الكود بكل صفحة لحالها.
"""

import os
import json
import urllib.request

import numpy as np
import pandas as pd
import streamlit as st

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(APP_DIR, "clean_data.csv")

EQUIP_COLS = [
    "aircraft", "helicopter", "tank", "apc", "field_artillery", "mrl",
    "military_auto", "fuel_tank", "drone", "naval_ship",
    "anti_aircraft_warfare", "special_equipment", "mobile_srbm_system",
    "vehicles_and_fuel_tanks", "cruise_missiles", "submarines",
    "ground_robotic_systems",
]

# أيقونة مميزة لكل فئة معدات (لمسة بصرية بدل أيقونة عامة واحدة للكل)
EQUIP_ICONS = {
    "aircraft": "✈️", "helicopter": "🚁", "tank": "🛡️", "apc": "🚙",
    "field_artillery": "💣", "mrl": "🚀", "military_auto": "🚚", "fuel_tank": "⛽",
    "drone": "🛸", "naval_ship": "🚢", "anti_aircraft_warfare": "📡",
    "special_equipment": "🔧", "mobile_srbm_system": "🎯",
    "vehicles_and_fuel_tanks": "🚛", "cruise_missiles": "🛰️",
    "submarines": "⚓", "ground_robotic_systems": "🤖",
}

EQUIP_LABELS = {
    "en": {
        "aircraft": "Aircraft", "helicopter": "Helicopter", "tank": "Tank",
        "apc": "APC", "field_artillery": "Field Artillery", "mrl": "MRL",
        "military_auto": "Military Auto", "fuel_tank": "Fuel Tank", "drone": "Drone",
        "naval_ship": "Naval Ship", "anti_aircraft_warfare": "Anti-Aircraft Warfare",
        "special_equipment": "Special Equipment", "mobile_srbm_system": "Mobile SRBM System",
        "vehicles_and_fuel_tanks": "Vehicles & Fuel Tanks", "cruise_missiles": "Cruise Missiles",
        "submarines": "Submarines", "ground_robotic_systems": "Ground Robotic Systems",
    },
    "ar": {
        "aircraft": "طائرات", "helicopter": "مروحيات", "tank": "دبابات",
        "apc": "مدرعات", "field_artillery": "مدفعية", "mrl": "راجمات صواريخ",
        "military_auto": "مركبات عسكرية", "fuel_tank": "صهاريج وقود", "drone": "طائرات مسيّرة",
        "naval_ship": "سفن حربية", "anti_aircraft_warfare": "دفاع جوي",
        "special_equipment": "معدات خاصة", "mobile_srbm_system": "منظومات صواريخ متنقلة",
        "vehicles_and_fuel_tanks": "مركبات وصهاريج وقود", "cruise_missiles": "صواريخ كروز",
        "submarines": "غواصات", "ground_robotic_systems": "أنظمة روبوتية أرضية",
    },
}

# دالة ترجع تسمية الفئة مع أيقونتها معًا، جاهزة للعرض بالقوائم والرسومات
def equip_label_with_icon(key: str, lang: str) -> str:
    return f"{EQUIP_ICONS.get(key, '')} {EQUIP_LABELS[lang].get(key, key)}"


LOCATION_COORDS = {
    "Donetsk": (48.0159, 37.8028), "Bakhmut": (48.5956, 38.0034),
    "Kramatorsk": (48.7389, 37.5848), "Kharkiv": (49.9935, 36.2304),
    "Izyum": (49.2039, 37.2554), "Avdiivka": (48.1394, 37.7461),
    "Lyman": (48.9836, 37.8028), "Sloviansk": (48.8578, 37.6053),
    "Sievierodonetsk": (48.9483, 38.4930), "Kurakhove": (47.9761, 37.2686),
    "Kryvyi Rih": (47.9105, 33.3918), "Zaporizhzhia": (47.8388, 35.1396),
    "Mykolaiv": (46.9750, 31.9946), "Popasna": (48.6483, 38.3564),
    "Slobozhanskyi": (50.05, 36.95), "Novopavlivsk": (47.75, 37.15),
    "Kupiansk": (49.7086, 37.6157),
}

LOCATION_LABELS_AR = {
    "Donetsk": "دونيتسك", "Bakhmut": "باخموت", "Kramatorsk": "كراماتورسك",
    "Kharkiv": "خاركيف", "Izyum": "إيزيوم", "Avdiivka": "أفدييفكا",
    "Lyman": "ليمان", "Sloviansk": "سلوفيانسك", "Sievierodonetsk": "سيفيرودونيتسك",
    "Kurakhove": "كوراخوفي", "Kryvyi Rih": "كريفي ريه", "Zaporizhzhia": "زابوريجيا",
    "Mykolaiv": "ميكولايف", "Popasna": "بوباسنا", "Slobozhanskyi": "سلوبوجانسكي",
    "Novopavlivsk": "نوفوبافليفسك", "Kupiansk": "كوبيانسك",
}

# أحداث/معارك كبرى موثقة تاريخيًا، تُستخدم كعلامات (annotations) على الرسم الزمني
# التواريخ تقريبية لتاريخ الحدث الرئيسي المُعلن إعلاميًا
BATTLE_EVENTS = [
    {"date": "2022-09-10", "en": "Kharkiv counteroffensive", "ar": "هجوم خاركيف المضاد"},
    {"date": "2022-11-11", "en": "Liberation of Kherson city", "ar": "تحرير مدينة خيرسون"},
    {"date": "2023-05-20", "en": "Fall of Bakhmut", "ar": "سقوط باخموت"},
    {"date": "2024-02-17", "en": "Fall of Avdiivka", "ar": "سقوط أفدييفكا"},
    {"date": "2024-08-06", "en": "Kursk incursion begins", "ar": "بدء توغل كورسك"},
]

# ألوان آمنة لعمى الألوان (colorblind-friendly): تدرجات Viridis/Cividis بدل أحمر-أخضر التقليدي
COLOR_SEQUENTIAL = "Viridis"
COLOR_DIVERGING = "RdBu_r"  # أحمر-أزرق (مو أحمر-أخضر) وهو آمن لأغلب أنواع عمى الألوان


@st.cache_data(ttl=3600, show_spinner=False)
def load_data_live() -> pd.DataFrame:
    """تحميل ونظافة البيانات مباشرة من GitHub (نفس منطق النوتبوك)، مخزّنة مؤقتًا ساعة واحدة."""
    personnel_url = "https://raw.githubusercontent.com/PetroIvaniuk/2022-Ukraine-Russia-War-Dataset/main/data/russia_losses_personnel.json"
    equipment_url = "https://raw.githubusercontent.com/PetroIvaniuk/2022-Ukraine-Russia-War-Dataset/main/data/russia_losses_equipment.json"

    def fetch_json(url):
        with urllib.request.urlopen(url, timeout=10) as response:
            return json.loads(response.read().decode())

    personnel_raw = fetch_json(personnel_url)
    equipment_raw = fetch_json(equipment_url)

    df_p = pd.DataFrame(personnel_raw).drop(columns=["personnel*"])
    df_e = pd.DataFrame(equipment_raw)

    df = pd.merge(df_p, df_e, on=["date", "day"], how="inner")
    df["date"] = pd.to_datetime(df["date"])
    df.columns = [c.strip().lower().replace(" ", "_").replace("-", "_") for c in df.columns]

    for c in EQUIP_COLS:
        df[c] = df[c].fillna(0).astype(int)

    df["pow"] = df["pow"].ffill().fillna(0).astype(int)
    df["greatest_losses_direction"] = df["greatest_losses_direction"].fillna("Unknown")

    df["total_equipment_losses"] = df[EQUIP_COLS].sum(axis=1)
    df["personnel_daily_new"] = df["personnel"].diff().fillna(df["personnel"]).clip(lower=0).astype(int)
    df["equipment_daily_new"] = df["total_equipment_losses"].diff().fillna(df["total_equipment_losses"]).clip(lower=0).astype(int)
    return df


@st.cache_data
def load_data_local(path: str) -> pd.DataFrame:
    return pd.read_csv(path, parse_dates=["date"])


def get_data():
    """يرجّع (df, is_live): يحاول أولًا البيانات الحيّة من GitHub، ولو فشل يرجع للنسخة المحلية."""
    try:
        return load_data_live(), True
    except Exception:
        if not os.path.exists(DATA_PATH):
            st.error("Could not fetch live data and no local backup was found.")
            st.stop()
        return load_data_local(DATA_PATH), False


def parse_directions(direction_text: str):
    """تقسيم نص المناطق المركّب إلى قائمة أسماء مواقع منفردة."""
    if direction_text == "Unknown":
        return []
    cleaned = direction_text.replace(" and ", ",")
    return [p.strip() for p in cleaned.split(",") if p.strip()]


# =========================================================
# Translations / قاموس الترجمة الكامل (مشترك بين كل الصفحات)
# =========================================================
T = {
    "en": {
        "nav_hint": "Use the sidebar to switch pages: Overview, Deep Analysis, Interactive Map.",
        "lang_label": "🌐 Language",
        "about_title": "ℹ️ About the Data",
        "about_body": (
            "This dashboard shows real daily data documenting officially reported "
            "Russian losses (personnel and equipment) during the Russia-Ukraine war, "
            "starting from **2022-02-25** through the latest available update.\n\n"
            "**Source:** [GitHub – PetroIvaniuk](https://github.com/PetroIvaniuk/2022-Ukraine-Russia-War-Dataset)\n"
            "(Official data from the General Staff of the Armed Forces of Ukraine)\n\n"
            "**Number of days recorded:** {n_days}"
        ),
        "data_live": "🟢 Live data (refreshed hourly from GitHub)",
        "data_fallback": "🟡 Offline mode: showing a locally saved snapshot",
        "filters_header": "🔎 Filters",
        "start_date": "Start Date",
        "end_date": "End Date",
        "date_order_error": "Start Date must be before End Date.",
        "equip_multiselect": "Equipment Categories to Compare",
        "trend_dropdown": "Equipment Category for Trend Chart",
        "min_threshold": "Minimum Daily Personnel Losses (to isolate critical days)",
        "min_threshold_help": "Filters the whole dashboard down to days where at least this many personnel losses were reported *on that single day* (not the running total). Raise it to isolate unusually severe days — e.g. major battles — and see how the charts and map narrow down to just those days.",
        "sidebar_footer": "Individual Data Analysis Project — EDA & Streamlit Dashboard",
        "sidebar_sticky_note": "📌 Filters above stay visible while you scroll the page.",
        "no_data_warning": "No data matches the selected filters. Try widening the date range or lowering the minimum threshold.",
        "kpi_personnel": "Total Personnel Losses",
        "kpi_personnel_delta": "+{delta:,} over selected period",
        "kpi_equipment": "Total Equipment Losses",
        "kpi_equipment_delta": "+{delta:,} over selected period",
        "kpi_days": "Days in View",
        "kpi_avg": "Avg. Daily Personnel Losses",
        "footer": "Data Insights Dashboard · Built with Streamlit & Plotly · Data source: PetroIvaniuk/2022-Ukraine-Russia-War-Dataset (GitHub)",
        "accessibility_note": "🎨 Charts on this dashboard use colorblind-friendly palettes (Viridis / red-blue diverging) instead of red-green.",
    },
    "ar": {
        "nav_hint": "استخدم الشريط الجانبي للتنقل بين الصفحات: نظرة عامة، تحليل متعمق، خريطة تفاعلية.",
        "lang_label": "🌐 اللغة",
        "about_title": "ℹ️ عن البيانات",
        "about_body": (
            "تعرض هذه اللوحة بيانات يومية حقيقية توثّق الخسائر الروسية المُعلنة رسميًا "
            "(بشرية ومعدات) خلال الحرب الروسية الأوكرانية، بدءًا من **2022-02-25** "
            "وحتى آخر تحديث متوفر.\n\n"
            "**المصدر:** [GitHub – PetroIvaniuk](https://github.com/PetroIvaniuk/2022-Ukraine-Russia-War-Dataset)\n"
            "(بيانات رسمية من هيئة أركان الجيش الأوكراني)\n\n"
            "**عدد الأيام المسجّلة:** {n_days}"
        ),
        "data_live": "🟢 بيانات حيّة (تتحدث تلقائيًا كل ساعة من GitHub)",
        "data_fallback": "🟡 وضع غير متصل: تُعرض نسخة محفوظة محليًا",
        "filters_header": "🔎 الفلاتر",
        "start_date": "تاريخ البداية",
        "end_date": "تاريخ النهاية",
        "date_order_error": "لازم يكون تاريخ البداية قبل تاريخ النهاية.",
        "equip_multiselect": "فئات المعدات للمقارنة",
        "trend_dropdown": "فئة معدات لعرض اتجاهها الزمني",
        "min_threshold": "حد أدنى للخسائر البشرية اليومية (لتحديد الأيام الحرجة)",
        "min_threshold_help": "يفلتر كل لوحة المعلومات لتعرض بس الأيام اللي سُجّل فيها هذا الحد أو أكثر من الخسائر البشرية *في ذاك اليوم بالتحديد* (مو المجموع التراكمي). زوّد الرقم عشان تعزل الأيام الاستثنائية (زي المعارك الكبرى) وتشوف كيف تتغيّر الرسومات والخريطة لتعرض بس هذي الأيام.",
        "sidebar_footer": "مشروع تحليل بيانات فردي — EDA ولوحة معلومات Streamlit",
        "sidebar_sticky_note": "📌 الفلاتر أعلاه تفضل ظاهرة وأنت تنزل بالصفحة.",
        "no_data_warning": "لا توجد بيانات مطابقة للفلاتر المختارة. حاول توسيع نطاق التاريخ أو تقليل الحد الأدنى.",
        "kpi_personnel": "إجمالي الخسائر البشرية",
        "kpi_personnel_delta": "+{delta:,} خلال الفترة المختارة",
        "kpi_equipment": "إجمالي خسائر المعدات",
        "kpi_equipment_delta": "+{delta:,} خلال الفترة المختارة",
        "kpi_days": "عدد الأيام المعروضة",
        "kpi_avg": "متوسط الخسائر البشرية اليومية",
        "footer": "لوحة معلومات تحليل البيانات · مبنية بـ Streamlit و Plotly · مصدر البيانات: PetroIvaniuk/2022-Ukraine-Russia-War-Dataset (GitHub)",
        "accessibility_note": "🎨 رسومات هذه اللوحة تستخدم ألوانًا آمنة لعمى الألوان (Viridis / أحمر-أزرق) بدل أحمر-أخضر.",
    },
}


def t(key: str, lang: str, **kwargs) -> str:
    text = T[lang][key]
    return text.format(**kwargs) if kwargs else text



def render_banner(title: str, subtitle: str):
    """بانر/شريط علوي بسيط بتدرج لوني بدل عنوان نصي عادي فقط."""
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(90deg, #7f1d1d 0%, #1e3a5f 100%);
            padding: 22px 26px; border-radius: 10px; margin-bottom: 18px;">
            <div style="color: white; font-size: 26px; font-weight: 700;">{title}</div>
            <div style="color: #e2e8f0; font-size: 14px; margin-top: 4px;">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_card(label: str, value: str, delta: str, color: str):
    """بطاقة KPI مخصصة بحدود ملونة حسب نوع الرقم (بديل عن st.metric العادي)."""
    st.markdown(
        f"""
        <div style="
            border-left: 5px solid {color};
            background: rgba(127,29,29,0.04);
            border-radius: 8px; padding: 14px 16px; margin-bottom: 8px;">
            <div style="font-size: 13px; opacity: 0.75;">{label}</div>
            <div style="font-size: 26px; font-weight: 700;">{value}</div>
            <div style="font-size: 12px; opacity: 0.6;">{delta}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def init_sidebar_controls(df: pd.DataFrame, is_live: bool):
    """يُستدعى بأول كل صفحة: يعرض قائمة اللغة + معلومات البيانات + الفلاتر
    (dropdown + slider + multiselect + تواريخ)، ويرجّع كل القيم المختارة.
    استخدام key= صريح لكل عنصر يضمن بقاء نفس الاختيار وأنت تتنقل بين الصفحات."""
    lang_choice = st.sidebar.selectbox(
        "🌐 Language / اللغة", options=["English", "العربية"], index=0, key="lang_choice"
    )
    lang = "en" if lang_choice == "English" else "ar"

    st.sidebar.title(t("about_title", lang))
    st.sidebar.markdown(t("about_body", lang, n_days=len(df)))
    st.sidebar.caption(t("data_live", lang) if is_live else t("data_fallback", lang))

    st.sidebar.header(t("filters_header", lang))

    min_date, max_date = df["date"].min().date(), df["date"].max().date()
    col_start, col_end = st.sidebar.columns(2)
    start_date = col_start.date_input(t("start_date", lang), value=min_date, min_value=min_date, max_value=max_date, key="start_date")
    end_date = col_end.date_input(t("end_date", lang), value=max_date, min_value=min_date, max_value=max_date, key="end_date")
    if start_date > end_date:
        st.sidebar.error(t("date_order_error", lang))
        start_date, end_date = min_date, max_date

    default_equip = ["tank", "apc", "aircraft", "drone"]
    selected_equipment = st.sidebar.multiselect(
        t("equip_multiselect", lang), options=EQUIP_COLS, default=default_equip,
        format_func=lambda x: equip_label_with_icon(x, lang), key="selected_equipment",
    )
    if not selected_equipment:
        selected_equipment = default_equip

    trend_category = st.sidebar.selectbox(
        t("trend_dropdown", lang), options=EQUIP_COLS, index=EQUIP_COLS.index("tank"),
        format_func=lambda x: equip_label_with_icon(x, lang), key="trend_category",
    )

    max_daily = int(df["personnel_daily_new"].max())
    min_daily_threshold = st.sidebar.slider(
        t("min_threshold", lang), min_value=0, max_value=max_daily, value=0, step=10, key="min_daily_threshold",
    )
    st.sidebar.caption(t("min_threshold_help", lang))

    st.sidebar.caption(t("sidebar_sticky_note", lang))
    st.sidebar.markdown("---")
    st.sidebar.caption(t("sidebar_footer", lang))

    mask = (
        (df["date"].dt.date >= start_date)
        & (df["date"].dt.date <= end_date)
        & (df["personnel_daily_new"] >= min_daily_threshold)
    )
    filtered_df = df.loc[mask].copy()
    if filtered_df.empty:
        st.warning(t("no_data_warning", lang))
        st.stop()

    return {
        "lang": lang,
        "filtered_df": filtered_df,
        "selected_equipment": selected_equipment,
        "trend_category": trend_category,
        "min_daily_threshold": min_daily_threshold,
        "date_range": (start_date, end_date),
    }
