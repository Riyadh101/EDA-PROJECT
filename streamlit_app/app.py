"""
app.py — Entry point / router for the multi-page dashboard.
نقطة الدخول الرئيسية: تستدعي st.set_page_config مرة واحدة، وتعرّف صفحات
التطبيق الثلاث بأسماء ورموز واضحة، وتعرض التنقل بينها كشريط علوي (بدل قائمة
جانبية) عبر st.navigation.
Run with: streamlit run app.py
"""

import streamlit as st

st.set_page_config(
    page_title="War Losses Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

overview_page = st.Page("views/overview.py", title="Overview", icon="🏠", default=True)
deep_analysis_page = st.Page("views/deep_analysis.py", title="Deep Analysis", icon="📊")
map_page = st.Page("views/interactive_map.py", title="Interactive Map", icon="🗺️")

# شريط تنقل علوي (position="top") بدل القائمة الجانبية التقليدية
pg = st.navigation([overview_page, deep_analysis_page, map_page], position="top")
pg.run()
