import streamlit as st
import pypdf
import requests

st.set_page_config(page_title="פורטל המאמרים המחלקתי", layout="wide")

# הזרקת עיצוב מודרני מותאם אישית (CSS) כולל עיצוב למלבני המדדים
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Assistant', sans-serif;
        direction: RTL; text-align: right; background-color: #f8f9fa;
    }
    h1 { color: #1e3d59; font-weight: 700; text-align: center; margin-top: 15px; margin-bottom: 5px; }
    .upload-container { background-color: #ffffff; padding: 25px; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 25px; border-top: 5px solid #1e3d59; margin-top: 20px; }
    .article-card { background-color: #ffffff; padding: 22px; border-radius: 14px; box-shadow: 0 4px 12px rgba(0,0,0,0.03); margin-bottom: 20px; border-right: 6px solid #1e3d59; }
    .summary-box { background-color: #f5f7fa; padding: 15px; border-radius: 8px; border: 1px solid #e1e8ed; line-height: 1.6; margin-top: 10px; }
    .takeaway-box { background-color: #e8f5e9; padding: 12px; border-radius: 8px; border-right: 4px solid #2e7d32; font-weight: bold; color: #1b5e20; margin-top: 10px; }
    div.stButton > button:first-child { background-color: #1e3d59; color: white; font-weight: bold; font-size: 1.1rem; padding: 12px; border-radius: 8px; border: none; width: 100%; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    
    /* עיצוב כרטיסי המדדים (4 המלבנים) */
    .metric-card {
        padding: 20px; border-radius: 12px; text-align: center; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.04); transition: transform 0.2s;
    }
    .metric-card:hover { transform: translateY(-2px); }
    .metric-title { font-size: 1.05rem; font-weight: 600; margin: 0; }
    .metric-value { font-size: 2.3rem; font-weight: 700; margin: 5px 0 0 0; line-height: 1; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>🔬 פורטל מאמרים לפריודונטיה ושתלים</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666; font-size: 1.05rem; margin-bottom: 25px;'>מערכת ענן מאובטחת לניהול, ניתוח וקטלוג ספרות הבחינה המחלקתית</p>", unsafe_allow_html=True)

# 🌐 נתיבי השרת המאובטח ב-Cloud Run (ללא סודות גלויים)
PROXY_PROCESS_URL = "https://pdf-proxy-741291032537.europe-west1.run.app/process-article"
PROXY_DATA_URL = "https://pdf-proxy-741291032537.europe-west1.run.app/get-data"

# משיכת המידע העדכני מחשבון ה-Sheets דרך השרת המאובטח
db_data = {"JCP": [], "JOP": [], "COIR": []}
try:
    response = requests.get(PROXY_DATA_URL, timeout=10)
    if response.status_code == 200:
        db_data = response.json()
except Exception:
    pass

# חישוב כמויות המאמרים בזמן אמת (פחות שורת הכותרת הראשונה של הגיליון)
count_jcp = max(0, len(db_data.get("JCP", [])) - 1)
count_jop = max(0, len(db_data.get("JOP", [])) - 1)
count_coir = max(0, len(db_data.get("COIR", [])) - 1)
total_articles = count_jcp + count_jop + count_coir

# 📊 יצירת אזור 4 המלבנים הצבעוניים בראש העמוד
col1, col2, col3, col4 = st.columns(4, gap="medium")

with col1:
    st.markdown(f"""
        <div class="metric-card" style="background-color: #e3f2fd; border-bottom: 5px solid #1e88e5;">
            <p class="metric-title" style="color: #0d47a1;">עיתון JCP</p>
            <p class="metric-value" style="color: #0d47a1;">{count_jcp}</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="metric-card" style="background-color: #e0f2f1; border-bottom: 5px solid #00897b;">
            <p class="metric-title" style="color: #004d40;">עיתון JOP</p>
            <p class="metric-value" style="color: #004d40;">{count_jop}</p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="metric-card" style="background-color: #fff3e0; border-bottom: 5px solid #fb8c00;">
            <p class="metric-title" style="color: #e65100;">עיתון COIR</p>
            <p class="metric-value" style="color: #e65100;">{count_coir}</p>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class="metric-card" style="background-color: #1e3d59; border-bottom: 5px solid #17b978;">
            <p class="metric-title" style="color: #ffffff;">סה"כ מאמרים בפורטל</p>
            <p class="metric-value" style="color: #17b978;">{total_articles}</p>
        </div>
    """, unsafe_allow_html=True)

# אזור העלאת הקובץ
st.markdown("<div class='upload-container'>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("גררו ושחררו לכאן את קובץ ה-PDF של המאמר המדעי", type=["pdf"])
st.markdown("</div>", unsafe_allow_html=True)

if uploaded_file:
    if st.button("סרוק, סכם ונתב אוטומטית באמצעות הפרוקסי ⚡"):
        with st.spinner("שרת הפרוקסי המאובטח מעבד ומקטלג את המאמר..."):
            try:
                pdf_reader = pypdf.PdfReader(uploaded_file)
                article_text = ""
                for page in pdf_reader.pages[:4]:
                    text = page.extract_text()
                    if text: article_text += text + "\n"
                
                response = requests.post(PROXY_PROCESS_URL, json={"text": article_text}, timeout=35)
                
                if response.status_code == 200:
                    result_data = response.json().get("data", {})
                    st.balloons()
                    st.success(f"🎉 הצלחה! המאמר נשמר אוטומטית בעיתון {result_data.get('journal')} (חודש {result_data.get('month')})!")
                    
                    st.markdown(f"""
                        <div class="article-card">
                            <div class="article-title">📄 {result_data.get('title_and_authors')}</div>
                            <div style="color: #666; font-size: 0.9rem;">📅 עיתון: <b>{result_data.get('journal')}</b> | חודש: <b>{result_data.get('month')}</b> | נושא: <b>{result_data.get('topic')}</b></div>
                            <div class="summary-box"><b>📝 סיכום (10 שורות):</b><br>{result_data.get('summary')}</div>
                            <div class="takeaway-box">🎯 שורה תחתונה: {result_data.get('one_liner')}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    st.rerun()
                else:
                    st.error(f"❌ שרת הפרוקסי החזיר שגיאה: {response.text}")
            except Exception as e:
                st.error(f"תקלה בתקשורת מול שרת הפרוקסי: {str(e)}")

# חלק תחתון - הצצה מהירה לארכיון הקיים
st.write("---")
st.markdown("### 🗂️ הצצה מהירה למאמרים הקיימים בגיליון")
arch_jcp, arch_jop, arch_coir = st.tabs(["JCP Archive", "JOP Archive", "COIR Archive"])

def show_archive(journal_name):
    rows = db_data.get(journal_name, [])
    if len(rows) > 1:
        for row in rows[1:]:
            if len(row) >= 6:
                st.markdown(f"- **[{row[1]}]** {row[2]} | *נושא:* {row[5]} | *שורה תחתונה:* {row[4]}")
    else:
        st.info("אין עדיין מאמרים רשומים בלשונית זו ב-Sheets.")

with arch_jcp: show_archive("JCP")
with arch_jop: show_archive("JOP")
with arch_coir: show_archive("COIR")
