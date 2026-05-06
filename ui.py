import streamlit as st

def guvenli_html(metin: str) -> str:
    return (str(metin).replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#x27;"))

def tema_degistir() -> None:
    st.session_state.tema = st.session_state.get("tema_secimi", "Koyu")

def enerjik_css(tema: str) -> None:
    if tema == "Koyu":
        bg = "#0B1121"; card = "#141B2D"; text = "#E2E8F0"; header_bg = "#141B2D"
        metric_bg = "linear-gradient(145deg, #1a1f35, #0f1424)"; input_bg = "#141B2D"
    else:
        bg = "#F8FAFC"; card = "#FFFFFF"; text = "#1E293B"; header_bg = "#F1F5F9"
        metric_bg = "linear-gradient(145deg, #E2E8F0, #CBD5E1)"; input_bg = "#FFFFFF"
    st.markdown(f"""
    <style>
        .stApp {{ background-color: {bg} !important; }}
        .main {{ color: {text}; }}
        header[data-testid="stHeader"] {{ background-color: {header_bg}; }}
        section[data-testid="stSidebar"] {{ background-color: {header_bg}; }}
        section[data-testid="stSidebar"] .stRadio label {{ color: {text} !important; font-weight: 600; }}
        div[data-testid="stMetric"] {{
            background: {metric_bg}; border: 1px solid #94A3B8; border-radius: 20px; padding: 24px;
            color: {text}; box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }}
        div[data-testid="stMetric"] label {{ color: #64748B !important; font-weight: 600; }}
        div[data-testid="stMetric"] div[data-testid="stMetricValue"] {{ color: {text} !important; font-size: 2.2rem; }}
        h1, h2, h3, h4, h5, h6 {{ color: {text}; font-weight: 700; }}
        p, span, label {{ color: {text}; }}
        .stButton > button {{
            border-radius: 14px; font-weight: 700;
            background: linear-gradient(135deg, #F97316, #8B5CF6);
            color: white; border: none; padding: 0.7rem 2rem;
            box-shadow: 0 5px 15px rgba(249,115,22,0.5);
        }}
        .stButton > button:hover {{
            background: linear-gradient(135deg, #ea580c, #7c3aed); box-shadow: 0 8px 25px rgba(249,115,22,0.7);
        }}
        input, select, textarea {{
            background-color: {input_bg} !important; color: {text} !important;
            border: 1px solid #94A3B8 !important; border-radius: 10px !important;
        }}
        .stDataFrame {{
            border-radius: 18px; overflow: hidden; border: 1px solid #94A3B8; background-color: {card};
        }}
        .stDataFrame th {{ background-color: #E2E8F0; color: #1E293B; }}
        .stDataFrame td {{ background-color: {card}; color: {text}; }}
        .custom-container {{
            background-color: {card}; border-radius: 24px; padding: 30px;
            border: 1px solid #94A3B8; box-shadow: 0 15px 30px rgba(0,0,0,0.1); margin-bottom: 25px;
        }}
        .main-header {{
            font-size: 2.3rem; font-weight: 800;
            background: linear-gradient(135deg, #F97316, #8B5CF6);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            margin-bottom: 1.5rem; padding-bottom: 0.5rem; border-bottom: 2px solid #F97316;
        }}
        div[data-testid="stToast"] {{
            background-color: {card} !important; color: {text} !important; border-left: 4px solid #F97316;
        }}
        .sticky-alert {{
            position: fixed; top: 0; left: 0; width: 100%;
            background: #EF4444; color: white; text-align: center;
            padding: 10px; font-weight: bold; z-index: 9999;
        }}
        @media (max-width: 768px) {{
            .custom-container {{ padding: 12px !important; margin: 8px 0 !important; }}
            .main-header {{ font-size: 1.4rem !important; }}
            .stButton > button {{ width: 100% !important; padding: 12px !important; font-size: 16px !important; }}
            input, select, textarea {{ font-size: 16px !important; }}
        }}
    </style>
    """, unsafe_allow_html=True)