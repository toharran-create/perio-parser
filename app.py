import streamlit as st
import google.generativeai as genai
import pypdf
import json
import requests
from datetime import datetime

# הגדרת עיצוב הממשק בעברית
st.set_page_config(page_title="מערכת מאמרים משותפת - שלב א'", layout="wide")
st.markdown("""
    <style>
    .reportview-container .main .block-container { text-align: right; direction: RTL; }
    div.stButton > button:first-child { background-color: #008080; color: white; font-weight: bold; }
    .stTextArea textarea { direction: RTL; text-align: right; }
    </style>
""", unsafe_allow_html=True)

st.title("🗂️ לוח בקרה משותף: סיכומי מאמרים לשלב א'")
st.write("מערכת ענן מרכזית עבור כל המתמחים. המידע מסתנכרן אוטומטית מול קובץ ה-Google Sheets המחלקתי.")

# הגדרות מפתח וקישור בסרגל הצד
with st.sidebar:
    st.header("🔑 הגדרות חיבור")
    api_key = st.text_input("הזינו מפתח Gemini API:", type="password")
    # כאן מדביקים את הכתובת שקיבלתם מחלק 1 בשלב 4
    sheets_url = st.text_input("הזינו את כתובת ה-Web App של ה-Sheets שלכם:", type="password")

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

# טעינת הנתונים הקיימים ישירות מ-Google Sheets בזמן אמת
db_data = {"JCP": [], "JOP": [], "COIR": []}
if sheets_url:
    try:
        response = requests.get(sheets_url)
        if response.status_code == 200:
            db_data = response.json()
    except:
        st.sidebar.error("לא הצלחנו למשוך נתונים מה-Sheets. ודאו שהקישור תקין.")

# יצירת 3 הלשוניות לעיתונים
tab_jcp, tab_jop, tab_coir = st.tabs(["📰 עיתון JCP", "📰 עיתון JOP", "📰 עיתון COIR"])

def render_journal_tab(journal_name):
    selected_month = st.selectbox(f"בחר חודש:", months_list, key=f"m_{journal_name}")
    
    st.subheader(f"📊 מאמרים קיימים בטבלה לחודש {selected_month}")
    
    # הצגת המאמרים הקיימים ב-Google Sheets לחודש הנבחר
    rows = db_data.get(journal_name, [])
    found_any = False
    
    if len(rows) > 1: # אם יש יותר משורת הכותרות
        for idx, row in enumerate(rows[1:]):
            if len(row) >= 5 and str(row[0]).strip() == selected_month:
                found_any = True
                with st.expander(f"📄 {row[1]}"):
                    st.markdown(f"**📝 סיכום מורחב (10 שורות):**\n{row[2]}")
                    st.markdown(f"**🎯 שורה תחתונה:** {row[3]}")
                    st.caption(f"🏷️ נושא: {row[4]}")
                    
    if not found_any:
        st.info("אין עדיין מאמרים מסוכמים לחודש זה ב-Google Sheets.")
        
    st.write("---")
    st.markdown(f"### ➕ העלאה וסיכום מאמר חדש ל-{journal_name} ({selected_month})")
    
    uploaded_file = st.file_uploader("גררו קובץ PDF של מאמר", type=["pdf"], key=f"up_{journal_name}_{selected_month}")
    
    if uploaded_file and api_key and sheets_url:
        if st.button("הפעל ניתוח אוטומטי 🚀", key=f"btn_{journal_name}_{selected_month}"):
            with st.spinner("ה-AI קורא את המאמר המלא ומעדכן את ה-Google Sheets..."):
                try:
                    pdf_reader = pypdf.PdfReader(uploaded_file)
                    article_text = ""
                    for page in pdf_reader.pages[:15]:
                        text = page.extract_text()
                        if text: article_text += text + "\n"
                    
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
                    
                    # שליחת הנתונים ל-Google Sheets
                    payload = {
                        "journal": journal_name,
                        "month": selected_month,
                        "title_and_authors": parsed.get("title_and_authors", ""),
                        "summary": parsed.get("summary", ""),
                        "one_liner": parsed.get("one_liner", ""),
                        "topic": parsed.get("topic", "")
                    }
                    
                    requests.post(sheets_url, json=payload)
                    st.success("המאמר נשמר בהצלחה ב-Google Sheets של המחלקה!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"תקלה בעיבוד: {str(e)}")

with tab_jcp: render_journal_tab("JCP")
with tab_jop: render_journal_tab("JOP")
with tab_coir: render_journal_tab("COIR")
