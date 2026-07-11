import streamlit as st
import pypdf
import requests

st.set_page_config(page_title="פורטל המאמרים המחלקתי", layout="wide")

# הזרקת שפת העיצוב הרשמית של Google Workspace (Material Design)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;500;600;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Assistant', sans-serif;
        direction: RTL; text-align: right; 
        background-color: #f8f9fa; /* הרקע הבהיר של גוגל */
        color: #202124; /* צבע הטקסט הרשמי של גוגל */
    }
    
    h1 { 
        color: #1a73e8; /* כחול גוגל */
        font-weight: 500; text-align: center; 
        margin-top: 30px; margin-bottom: 5px;
        font-size: 2.1rem;
    }
    
    /* תיבת העלאת קבצים נקייה - בסגנון Google Drive */
    .upload-container { 
        background-color: #ffffff; padding: 30px; 
        border-radius: 8px; border: 1px solid #dadce0; 
        margin-bottom: 30px; margin-top: 15px;
    }
    
    /* מלבני המדדים החדשים - נקיים, מקצועיים ללא רקע צעקני */
    .metric-card {
        background-color: #ffffff; padding: 20px; 
        border-radius: 8px; border: 1px solid #dadce0;
        text-align: right; position: relative;
    }
    .metric-title { 
        font-size: 0.88rem; font-weight: 500; 
        color: #5f6368; /* אפור משני של גוגל */
        margin: 0; 
    }
    .metric-value { 
        font-size: 2.2rem; font-weight: 600; 
        color: #202124; margin: 8px 0 0 0; 
        line-height: 1;
    }
    
    /* כרטיסיית מאמר מעוצבת כדף מידע נקי */
    .article-card { 
        background-color: #ffffff; padding: 24px; 
        border-radius: 8px; border: 1px solid #dadce0;
        margin-bottom: 20px; 
    }
    .article-title { 
        color: #1a73e8; font-size: 1.2rem; 
        font-weight: 600; margin-bottom: 6px; 
    }
    .summary-box { 
        background-color: #f1f3f4; color: #3c4043;
        padding: 16px; border-radius: 6px; 
        line-height: 1.6; margin-top: 12px; font-size: 0.95rem;
    }
    .takeaway-box { 
        background-color: #e6f4ea; padding: 14px; 
        border-radius: 6px; font-weight: 500; 
        color: #137333; /* ירוק מעודן של גוגל */
        margin-top: 12px; font-size: 0.95rem;
        border-right: 4px solid #137333;
    }
    
    /* כפתור גוגל רשמי (Google Flat Button) */
    div.stButton > button:first-child { 
        background-color: #1a73e8; color: white; 
        font-weight: 500; font-size: 0.95rem; 
        padding: 10px 24px; border-radius: 4px; 
        border: none; width: 100%; transition: background-color 0.2s;
    }
    div.stButton > button:first-child:hover {
        background-color: #1557b0; box-shadow: 0 1px 2px 0 rgba(60,64,67,0.3);
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1> פורטל מאמרים לשלב א' פריודונטיה </h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #5f6368; font-size: 1.05rem; margin-bottom: 35px;'>מערכת ענן מאובטחת לניהול וקטלוג ספרות הבחינה המחלקתית</p>", unsafe_allow_html=True)

# 🌐 נתוני שרת הפרוקסי שלכם ב-Cloud Run
PROXY_PROCESS_URL = "https://pdf-proxy-741291032537.europe-west1.run.app/process-article"
PROXY_DATA_URL = "https://pdf-proxy-741291032537.europe-west1.run.app/get-data"

# משיכת המידע העדכני
db_data = {"JCP": [], "JOP": [], "COIR": []}
try:
    response = requests.get(PROXY_DATA_URL, timeout=10)
    if response.status_code == 200:
        db_data = response.json()
except Exception:
    pass

# חישוב כמויות המאמרים
count_jcp = max(0, len(db_data.get("JCP", [])) - 1)
count_jop = max(0, len(db_data.get("JOP", [])) - 1)
count_coir = max(0, len(db_data.get("COIR", [])) - 1)
total_articles = count_jcp + count_jop + count_coir

# 📊 תצוגת המדדים החדשה בסגנון Google Workspace Dashboard
col1, col2, col3, col4 = st.columns(4, gap="medium")

with col1:
    st.markdown(f"""
        <div class="metric-card" style="border-right: 5px solid #1a73e8;">
            <p class="metric-title">עיתון JCP</p>
            <p class="metric-value">{count_jcp}</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="metric-card" style="border-right: 5px solid #137333;">
            <p class="metric-title">עיתון JOP</p>
            <p class="metric-value">{count_jop}</p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="metric-card" style="border-right: 5px solid #e37400;">
            <p class="metric-title">עיתון COIR</p>
            <p class="metric-value">{count_coir}</p>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class="metric-card" style="border-right: 5px solid #3c4043; background-color: #f1f3f4;">
            <p class="metric-title" style="color: #202124;">סה"כ מאמרים</p>
            <p class="metric-value" style="color: #202124;">{total_articles}</p>
        </div>
    """, unsafe_allow_html=True)

# אזור העלאת הקובץ
st.markdown("<div class='upload-container'>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("בחרו או גררו קובץ PDF של מאמר מדעי לסריקה:", type=["pdf"])
st.markdown("</div>", unsafe_allow_html=True)

if uploaded_file:
    if st.button("הפעל עיבוד וקטלוג אוטומטי"):
        with st.spinner("שרת הפרוקסי מאבטח ומעבד את הנתונים..."):
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
                    st.success(f"המאמר קוטלג בהצלחה והוזרק לעיתון {result_data.get('journal')} תחת חודש {result_data.get('month')}.")
                    
                    st.markdown(f"""
                        <div class="article-card">
                            <div class="article-title">📄 {result_data.get('title_and_authors')}</div>
                            <div style="color: #5f6368; font-size: 0.88rem; margin-bottom: 12px;">
                                📅 עיתון: <b>{result_data.get('journal')}</b> | חודש: <b>{result_data.get('month')}</b> | נושא: <b>{result_data.get('topic')}</b>
                            </div>
                            <div class="summary-box"><b>📝 סיכום מאמר מחלקתי:</b><br>{result_data.get('summary')}</div>
                            <div class="takeaway-box">🎯 שורה תחתונה קלינית: {result_data.get('one_liner')}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    st.rerun()
                else:
                    st.error(f"שגיאה בעיבוד המאמר: {response.text}")
            except Exception as e:
                st.error(f"תקלה בתקשורת מול שרת הענן: {str(e)}")

# חלק תחתון - ארכיון המאמרים
st.write("---")
st.markdown("<h3 style='color: #202124; font-size: 1.3rem; font-weight: 500; margin-bottom: 15px;'>🗂️ ארכיון המאמרים המוקלטים</h3>", unsafe_allow_html=True)
arch_jcp, arch_jop, arch_coir = st.tabs(["JCP Archive", "JOP Archive", "COIR Archive"])

def show_archive(journal_name):
    rows = db_data.get(journal_name, [])
    if len(rows) > 1:
        for row in rows[1:]:
            if len(row) >= 6:
                st.markdown(f"""
                    <div style="padding: 10px 0; border-bottom: 1px solid #f1f3f4;">
                        <span style="color: #1a73e8; font-weight: 600; margin-left: 10px;">[{row[1]}]</span> 
                        <span style="color: #202124; font-weight: 500;">{row[2]}</span>
                        <br><small style="color: #5f6368;"><b>נושא:</b> {row[5]} | <b>שורה תחתונה:</b> {row[4]}</small>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("אין עדיין מאמרים רשומים בלשונית זו ב-Google Sheets.")

with arch_jcp: show_archive("JCP")
with arch_jop: show_archive("JOP")
with arch_coir: show_archive("COIR")
