import streamlit as st
import google.generativeai as genai
import pypdf
import json
import requests
from datetime import datetime

# הגדרת תצורה ועיצוב מתקדם המדמה אפליקציית ווב מודרנית (דומה ל-TAU Parser)
st.set_page_config(page_title="מערכת מאמרים פריודונטיה ושתלים", layout="wide")

# הזרקת עיצוב מותאם אישית - צבעים, צללים, פינות מעוגלות וכיוון טקסט (RTL)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600;700&display=swap');
    
    /* הגדרות גופן וכיוון כללי */
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Assistant', sans-serif;
        direction: RTL;
        text-align: right;
        background-color: #f8f9fa;
    }
    
    /* עיצוב כותרות */
    h1 {
        color: #1e3d59;
        font-weight: 700;
        padding-bottom: 10px;
    }
    
    /* עיצוב אזור הלשוניות (Tabs) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: #ffffff;
        padding: 10px;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        color: #437c90;
        border-radius: 8px;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1e3d59 !important;
        color: white !important;
    }

    /* עיצוב כרטיסיות המאמרים (Cards) */
    .article-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02), 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 15px;
        border-right: 5px solid #1e3d59;
    }
    .article-title {
        color: #1e3d59;
        font-size: 1.15rem;
        font-weight: 600;
        margin-bottom: 8px;
    }
    
    /* עיצוב תיבות סיכום */
    .summary-box {
        background-color: #f5f7fa;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #e1e8ed;
        line-height: 1.6;
        margin-top: 10px;
    }
    .takeaway-box {
        background-color: #e8f5e9;
        padding: 12px;
        border-radius: 8px;
        border-right: 4px solid #2e7d32;
        font-weight: bold;
        color: #1b5e20;
        margin-top: 10px;
    }
    
    /* עיצוב כפתור ההפעלה */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #1e3d59 0%, #17b978 import, #437c90 100%);
        background-color: #1e3d59;
        color: white;
        font-weight: bold;
        font-size: 1.1rem;
        padding: 12px 30px;
        border-radius: 8px;
        border: none;
        width: 100%;
        box-shadow: 0 4px 10px rgba(30,61,89,0.2);
        transition: all 0.3s ease;
    }
    div.stButton > button:first-child:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(30,61,89,0.3);
    }
    
    /* התאמת אלמנטים נוספים ל-RTL */
    .stSelectbox label, .stFileUploader label {
        text-align: right;
        display: block;
        font-weight: 600;
        color: #1e3d59;
    }
    </style>
""", unsafe_allow_html=True)

# כותרת ראשית מעוצבת
st.markdown("<h1 style='text-align: center; margin-bottom: 5px;'>🔬 פורטל המאמרים המחלקתי - שלב א'</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666; font-size: 1.1rem; margin-bottom: 30px;'>מערכת אוטומטית לסיכום וניהול ספרות חובה ועדכנית לפריודונטיטיס ושתלים</p>", unsafe_allow_html=True)

# 🔒 משיכת מפתחות וחיבורים קבועים מתוך ה-Secrets של הענן (ללא צורך בהזנת מתמחים)
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    sheets_url = st.secrets["SHEETS_WEBAPP_URL"]
except Exception:
    st.error("⚠️ הגדרות חיבור חסרות במערכת. אנא הגדר את GEMINI_API_KEY ו-SHEETS_WEBAPP_URL ב-Streamlit Secrets.")
    st.stop()

# יצירת רשימת 36 החודשים (מאי 2025 עד מאי 2028)
months_list = []
start_date = datetime(2025, 5, 1)
current = start_date
for _ in range(37):
    months_list.append(current.strftime("%m.%Y"))
    if current.month == 12:
        current = datetime(current.year + 1, 1, 1)
    else:
        current = datetime(current.year, current.month + 1, 1)

# משיכת הנתונים בזמן אמת מ-Google Sheets
db_data = {"JCP": [], "JOP": [], "COIR": []}
try:
    response = requests.get(sheets_url)
    if response.status_code == 200:
        db_data = response.json()
except Exception:
    st.warning("שים לב: המערכת לא הצליחה להתחבר לטבלה ברגע זה. ייתכן שהטבלה ריקה או שאין הרשאת גישה.")

# יצירת 3 הלשוניות העליונות לעיתונים
tab_jcp, tab_jop, tab_coir = st.tabs(["📰 Journal of Clinical Periodontology (JCP)", "📰 Journal of Periodontology (JOP)", "📰 Clinical Oral Implants Research (COIR)"])

def render_journal_tab(journal_name):
    # סידור הממשק בשני טורים נקיים: ימין (המאמרים הקיימים), שמאל (העלאת מאמר חדש)
    col_list, col_upload = st.columns([3, 2], gap="large")
    
    with col_list:
        st.markdown("### 📅 ארכיון מאמרים לפי חודש")
        selected_month = st.selectbox("בחר חודש לצפייה:", months_list, key=f"month_{journal_name}")
        
        rows = db_data.get(journal_name, [])
        found_any = False
        
        if len(rows) > 1:
            for row in rows[1:]:
                if len(row) >= 5 and str(row[0]).strip() == selected_month:
                    found_any = True
                    # הצגת כרטיסיית מאמר מעוצבת ומעוגלת
                    st.markdown(f"""
                        <div class="article-card">
                            <div class="article-title">📄 {row[1]}</div>
                            <div style="color: #555; font-size: 0.9rem; margin-bottom: 10px;">🏷️ נושא: <b>{row[4]}</b></div>
                            <div class="summary-box"><b>📝 סיכום מורחב (10 שורות):</b><br>{row[2]}</div>
                            <div class="takeaway-box">🎯 שורה תחתונה: {row[3]}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
        if not found_any:
            st.info(f"לא נמצאו עדיין מאמרים מסוכמים בטבלה לחודש {selected_month}.")
            
    with col_upload:
        st.markdown(f"### ➕ הוספת מאמר חדש ל-{journal_name}")
        st.write(f"העלה קובץ PDF, והמערכת תנתח אותו ותזין אותו ישירות לחודש **{selected_month}** בטבלת ה-Sheets.")
        
        uploaded_file = st.file_uploader("גרור ושחרר קובץ PDF לכאן", type=["pdf"], key=f"file_{journal_name}_{selected_month}")
        
        if uploaded_file:
            if st.button("הפעל ניתוח וסכם אוטומטית ✨", key=f"btn_{journal_name}_{selected_month}"):
                with st.spinner("ה-AI קורא את ה-PDF ומחלץ נתונים..."):
                    try:
                        pdf_reader = pypdf.PdfReader(uploaded_file)
                        article_text = ""
                        for page in pdf_reader.pages[:6]:
                            text = page.extract_text()
                            if text: article_text += text + "\n"
                        
                        if len(article_text.strip()) < 100:
                            st.error("שגיאה: לא הצלחנו לקרוא את קובץ ה-PDF. ודא שהוא אינו סרוק כתמונה.")
                            return
                        
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel("gemini-2.0-flash")
                        
                        prompt = f"""
                        Analyze the following text and extract these fields in Hebrew:
                        1. 'title_and_authors': Combined English Title and Main Authors (e.g., 'Title of Study - By John Doe et al.').
                        2. 'summary': A comprehensive 10-line summary of methods and findings in fluent Hebrew.
                        3. 'one_liner': A single-sentence clinical takeaway in Hebrew.
                        4. 'topic': Standard category like: פריודונטיטיס ומצבים סיסטמיים, מוקוג'ינג'יבלי, בקרת רובד ותחזוקה, רגנרציה- חומרים וטכניקות- שיניים, טיפולים בפרי אימפלנטיטיס, שרידות ופרוגנוזה- שיניים.
                        
                        Return ONLY a valid JSON object with keys: 'title_and_authors', 'summary', 'one_liner', 'topic'. Do not use markdown blocks.
                        Text: {article_text[:40000]}
                        """
                        
                        response = model.generate_content(prompt)
                        raw_res = response.text.strip().replace("```json", "").replace("```", "").strip()
                        parsed = json.loads(raw_res)
                        
                        # שליחה ל-Google Sheets
                        payload = {
                            "journal": journal_name,
                            "month": selected_month,
                            "title_and_authors": parsed.get("title_and_authors", ""),
                            "summary": parsed.get("summary", ""),
                            "one_liner": parsed.get("one_liner", ""),
                            "topic": parsed.get("topic", "")
                        }
                        
                        requests.post(sheets_url, json=payload)
                        st.success("המאמר נותח בהצלחה ונשמר ב-Google Sheets של המחלקה!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"תקלה בעיבוד המאמר: {str(e)}")

# הפעלת הלשוניות בפועל
with tab_jcp: render_journal_tab("JCP")
with tab_jop: render_journal_tab("JOP")
with tab_coir: render_journal_tab("COIR")
