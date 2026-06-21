import streamlit as st
import google.generativeai as genai
import pypdf
import json
import requests
from datetime import datetime

st.set_page_config(page_title="פורטל המאמרים המחלקתי", layout="wide")

# הזרקת עיצוב מודרני מותאם אישית (CSS) עם תמיכה מלאה ב-RTL וכפתורי ניהול
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Assistant', sans-serif;
        direction: RTL; text-align: right; background-color: #f8f9fa;
    }
    h1 { color: #1e3d59; font-weight: 700; text-align: center; margin-bottom: 5px; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: #ffffff; padding: 10px; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .stTabs [data-baseweb="tab"] { font-weight: 600; color: #437c90; border-radius: 8px; padding: 10px 20px; }
    .stTabs [aria-selected="true"] { background-color: #1e3d59 !important; color: white !important; }
    
    /* עיצוב כרטיסיית מאמר */
    .article-card {
        background-color: #ffffff; padding: 22px; border-radius: 14px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03); margin-bottom: 20px;
        border-right: 6px solid #1e3d59; position: relative;
    }
    .article-title { color: #1e3d59; font-size: 1.2rem; font-weight: 700; margin-bottom: 5px; line-height: 1.4; }
    .summary-box { background-color: #f5f7fa; padding: 15px; border-radius: 8px; border: 1px solid #e1e8ed; line-height: 1.6; margin-top: 10px; font-size: 0.95rem; }
    .takeaway-box { background-color: #e8f5e9; padding: 12px; border-radius: 8px; border-right: 4px solid #2e7d32; font-weight: bold; color: #1b5e20; margin-top: 10px; }
    
    /* עיצוב כפתורים */
    div.stButton > button:first-child {
        background-color: #1e3d59; color: white; font-weight: bold; font-size: 1rem;
        padding: 10px 25px; border-radius: 8px; border: none; width: 100%; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>🔬 פורטל המאמרים המחלקתי - שלב א'</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666; font-size: 1.05rem; margin-bottom: 30px;'>מערכת ענן מרכזית קבועה - המידע נשמר ומסונכרן אוטומטית ללא אפשרות מחיקה אקראית</p>", unsafe_allow_html=True)

# טעינת חיבורים קבועים מה-Secrets
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    sheets_url = st.secrets["SHEETS_WEBAPP_URL"]
except Exception:
    st.error("❌ שגיאה: נתוני החיבור הוסרו מה-Secrets. אנא הגדר אותם שוב בלוח הבקרה של Streamlit.")
    st.stop()

# בניית רשימת 36 החודשים
months_list = []
start_date = datetime(2025, 5, 1)
current = start_date
for _ in range(37):
    months_list.append(current.strftime("%m.%Y"))
    if current.month == 12: current = datetime(current.year + 1, 1, 1)
    else: current = datetime(current.year, current.month + 1, 1)

# משיכת המידע העדכני מגוגל שיטס
db_data = {"JCP": [], "JOP": [], "COIR": []}
try:
    response = requests.get(sheets_url, timeout=10)
    if response.status_code == 200:
        db_data = response.json()
except Exception:
    st.sidebar.warning("⚠️ לא ניתן להתחבר לטבלה ברגע זה. בדקו את חיבור האינטרנט או את תקינות הקישור בגוגל.")

tabs = st.tabs(["📰 Journal of Clinical Periodontology (JCP)", "📰 Journal of Periodontology (JOP)", "📰 Clinical Oral Implants Research (COIR)"])

def render_journal_tab(journal_name):
    col_list, col_upload = st.columns([3, 2], gap="large")
    
    with col_list:
        st.markdown("### 📅 ארכיון מאמרים מסוכמים")
        selected_month = st.selectbox("בחר חודש לצפייה:", months_list, key=f"m_{journal_name}")
        
        rows = db_data.get(journal_name, [])
        found_any = False
        
        if len(rows) > 1:
            for row_idx, row in enumerate(rows[1:]):
                # מבנה השורה החדש בטבלה: [0]=מזהה, [1]=חודש, [2]=כותרת וכותבים, [3]=סיכום, [4]=שורה תחתונה, [5]=נושא
                if len(row) >= 6 and str(row[1]).strip() == selected_month:
                    found_any = True
                    article_id = row[0]
                    
                    st.markdown(f"""
                        <div class="article-card">
                            <div class="article-title">📄 {row[2]}</div>
                            <div style="color: #666; font-size: 0.9rem;">🏷️ נושא: <b>{row[5]}</b></div>
                            <div class="summary-box"><b>📝 סיכום מורחב (10 שורות):</b><br>{row[3]}</div>
                            <div class="takeaway-box">🎯 שורה תחתונה: {row[4]}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # אזור ניהול, עריכה ומחיקה קשיח לכל מאמר
                    c_edit, c_del, _ = st.columns([1, 1, 3])
                    with c_edit:
                        if st.button("📝 ערוך מלל", key=f"edit_btn_{article_id}"):
                            st.session_state[f"editing_{article_id}"] = True
                    with c_del:
                        if st.button("🗑️ מחק מאמר", key=f"del_btn_{article_id}"):
                            # פנייה לגוגל שיטס למחיקת השורה לצמיתות
                            del_payload = {"journal": journal_name, "action": "delete", "id": article_id}
                            res = requests.post(sheets_url, json=del_payload)
                            if res.status_code == 200:
                                st.success("המאמר נמחק מהטבלה המחלקתית!")
                                st.rerun()
                    
                    # ממשק עריכה ייעודי במידה ונלחץ
                    if st.session_state.get(f"editing_{article_id}", False):
                        with st.form(key=f"form_{article_id}"):
                            st.markdown("#### ✏️ עריכת נתוני המאמר")
                            new_title = st.text_input("שם המאמר וכותבים:", value=row[2])
                            new_summary = st.text_area("סיכום מורחב:", value=row[3], height=150)
                            new_one_liner = st.text_input("שורה תחתונה:", value=row[4])
                            new_topic = st.text_input("נושא:", value=row[5])
                            
                            if st.form_submit_button("שמור שינויים קבועים 💾"):
                                edit_payload = {
                                    "journal": journal_name, "action": "edit", "id": article_id,
                                    "title_and_authors": new_title, "summary": new_summary,
                                    "one_liner": new_one_liner, "topic": new_topic
                                }
                                res = requests.post(sheets_url, json=edit_payload)
                                if res.status_code == 200:
                                    st.session_state[f"editing_{article_id}"] = False
                                    st.success("השינויים נשמרו בהצלחה!")
                                    st.rerun()
                                    
        if not found_any:
            st.info(f"לא נמצאו עדיין מאמרים מסוכמים לחודש {selected_month}.")
            
    with col_upload:
        st.markdown(f"### ➕ סריקת מאמר חדש ל-{journal_name}")
        uploaded_file = st.file_uploader("גררו קובץ PDF של מאמר מדעי", type=["pdf"], key=f"f_{journal_name}_{selected_month}")
        
        if uploaded_file:
            if st.button("הפעל ניתוח קבוע ב-Gemini 3.5 🚀", key=f"b_{journal_name}_{selected_month}"):
                with st.spinner("ה-AI קורא את 15 עמודי המאמר ומבצע שמירה מאובטחת..."):
                    try:
                        pdf_reader = pypdf.PdfReader(uploaded_file)
                        article_text = ""
                        for page in pdf_reader.pages[:15]:
                            text = page.extract_text()
                            if text: article_text += text + "\n"
                        
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel("gemini-3.5-flash")
                        
                        prompt = f"""
                        Analyze the following dental article text and extract these fields in Hebrew:
                        1. 'title_and_authors': Combined English Title and Main Authors (e.g., 'Title - By J. Doe et al.').
                        2. 'summary': A detailed summary of methods and findings, strictly spanning approximately 10 lines in coherent Hebrew.
                        3. 'one_liner': A sharp, single-sentence clinical takeaway ('שורה תחתונה') in Hebrew.
                        4. 'topic': Standard category like: פריודונטיטיס ומצבים סיסטמיים, מוקוג'ינג'יבלי, בקרת רובד ותחזוקה, רגנרציה- חומרים וטכניקות- שיניים, טיפולים בפרי אימפלנטיטיס, שרידות ופרוגנוזה- שיניים.
                        
                        Return ONLY a valid JSON object with keys: 'title_and_authors', 'summary', 'one_liner', 'topic'. Do not use markdown syntax.
                        Text: {article_text[:50000]}
                        """
                        
                        response = model.generate_content(prompt)
                        raw_res = response.text.strip().replace("```json", "").replace("```", "").strip()
                        parsed = json.loads(raw_res)
                        
                        # שליחת הנתונים לשרת גוגל לרישום קבוע בטבלה
                        payload = {
                            "journal": journal_name,
                            "action": "add",
                            "month": selected_month,
                            "title_and_authors": parsed.get("title_and_authors", ""),
                            "summary": parsed.get("summary", ""),
                            "one_liner": parsed.get("one_liner", ""),
                            "topic": parsed.get("topic", "")
                        }
                        
                        api_res = requests.post(sheets_url, json=payload, timeout=15)
                        
                        if api_res.status_code == 200 and "success" in api_res.text:
                            st.success(f"המאמר נשמר לצמיתות ב-Google Sheets תחת חודש {selected_month}!")
                            st.rerun()
                        else:
                            st.error(f"המאמר סוכם אך גוגל סירבה לרשום אותו בטבלה. ודאו שהגדרתם את ה-Web App ל-'Anyone'. תגובת השרת: {api_res.text}")
                            
                    except Exception as e:
                        st.error(f"תקלה בתהליך העיבוד: {str(e)}")

# רינדור הלשוניות
with tabs[0]: render_journal_tab("JCP")
with tabs[1]: render_journal_tab("JOP")
with tabs[2]: render_journal_tab("COIR")
