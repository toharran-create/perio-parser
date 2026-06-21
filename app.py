import streamlit as st
import google.generativeai as genai
import pypdf
import json
import requests
from datetime import datetime

st.set_page_config(page_title="פורטל המאמרים האוטומטי", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Assistant', sans-serif;
        direction: RTL; text-align: right; background-color: #f8f9fa;
    }
    h1 { color: #1e3d59; font-weight: 700; text-align: center; margin-top: 20px; }
    .upload-container { background-color: #ffffff; padding: 30px; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 25px; border-top: 5px solid #1e3d59; }
    .article-card { background-color: #ffffff; padding: 22px; border-radius: 14px; box-shadow: 0 4px 12px rgba(0,0,0,0.03); margin-bottom: 20px; border-right: 6px solid #1e3d59; }
    .article-title { color: #1e3d59; font-size: 1.2rem; font-weight: 700; margin-bottom: 5px; }
    .summary-box { background-color: #f5f7fa; padding: 15px; border-radius: 8px; border: 1px solid #e1e8ed; line-height: 1.6; margin-top: 10px; }
    .takeaway-box { background-color: #e8f5e9; padding: 12px; border-radius: 8px; border-right: 4px solid #2e7d32; font-weight: bold; color: #1b5e20; margin-top: 10px; }
    div.stButton > button:first-child { background-color: #1e3d59; color: white; font-weight: bold; font-size: 1.1rem; padding: 12px; border-radius: 8px; border: none; width: 100%; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>🚀 פורטל מאמרים לפריודונטיה ושתלים - אוטומציה מלאה</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666; font-size: 1.1rem; margin-bottom: 30px;'>אין צורך לבחור עיתון או חודש. העלו את ה-PDF והמערכת תזהה, תסכם ותנתב אותו אוטומטית ל-Google Sheets.</p>", unsafe_allow_html=True)

# טעינת נתונים מה-Secrets
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    sheets_url = st.secrets["SHEETS_WEBAPP_URL"]
except Exception:
    st.error("❌ שגיאה: נתוני החיבור חסרים ב-Streamlit Secrets.")
    st.stop()

# משיכת המידע הקיים מהגיליון לצורך הצגת הארכיון למטה
db_data = {"JCP": [], "JOP": [], "COIR": []}
try:
    response = requests.get(sheets_url, timeout=10)
    if response.status_code == 200:
        db_data = response.json()
except Exception:
    pass

# אזור העלאת הקובץ (ממשק נקי ומרכזי)
st.markdown("<div class='upload-container'>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("גררו ושחררו לכאן את קובץ ה-PDF של המאמר המדעי", type=["pdf"])
st.markdown("</div>", unsafe_allow_html=True)

if uploaded_file:
    if st.button("סרוק, סכם ונתב אוטומטית לטבלה המחלקתית ⚡"):
        with st.spinner("ה-AI קורא את המאמר, מזהה את כתב העת, תאריך הפרסום ומפיק את הסיכומים..."):
            try:
                # קריאת 15 עמודים ראשונים מהקובץ
                pdf_reader = pypdf.PdfReader(uploaded_file)
                article_text = ""
                for page in pdf_reader.pages[:15]:
                    text = page.extract_text()
                    if text: article_text += text + "\n"
                
                if len(article_text.strip()) < 100:
                    st.error("שגיאה: לא הצלחנו לקרוא את הטקסט מה-PDF. ודא שהקובץ אינו סרוק כתמונה.")
                    st.stop()
                
                # הגדרת המודל החדש והמעודכן
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-3.5-flash")
                
                # פרומפט משודרג שמאלץ את ה-AI לקבוע לבד את העיתון והתאריך
                prompt = f"""
                Analyze the following scientific dental article text and extract the required information.
                You must automatically identify the journal (strictly map it to either 'JCP', 'JOP', or 'COIR') and the publication date.
                
                Provide the output strictly as a JSON object with the following keys:
                1. 'journal': Must be exactly 'JCP' (if Journal of Clinical Periodontology), 'JOP' (if Journal of Periodontology), or 'COIR' (if Clinical Oral Implants Research).
                2. 'month': The publication month and year formatted strictly as MM.YYYY (e.g., '05.2025' or '11.2026'). Look closely at the header/footer metadata.
                3. 'title_and_authors': Combined English Title and Main Authors (e.g., 'Study Title - By Smith J. et al.').
                4. 'summary': A comprehensive, detailed summary of methods and findings, spanning approximately 10 lines in coherent Hebrew.
                5. 'one_liner': A sharp, single-sentence clinical takeaway ('שורה תחתונה') in Hebrew.
                6. 'topic': Standard category in Hebrew like: פריודונטיטיס ומצבים סיסטמיים, מוקוג'ינג'יבלי, בקרת רובד ותחזוקה, רגנרציה- חומרים וטכניקות- שיניים, טיפולים בפרי אימפלנטיטיס, שרידות ופרוגנוזה- שיניים.
                
                Return ONLY the raw JSON object. Do not wrap in markdown syntax.
                Text:
                {article_text[:50000]}
                """
                
                response = model.generate_content(prompt)
                raw_res = response.text.strip().replace("```json", "").replace("```", "").strip()
                parsed = json.loads(raw_res)
                
                detected_journal = parsed.get("journal", "").upper()
                detected_month = parsed.get("month", "")
                
                if detected_journal not in ["JCP", "JOP", "COIR"]:
                    st.error(f"ה-AI זיהה את העיתון כ-{detected_journal}, אך המערכת תומכת רק ב-JCP, JOP, COIR.")
                    st.stop()
                
                # שיגור אוטומטי ל-Google Sheets ללא מגע יד אדם
                payload = {
                    "journal": detected_journal,
                    "action": "add",
                    "month": detected_month,
                    "title_and_authors": parsed.get("title_and_authors", ""),
                    "summary": parsed.get("summary", ""),
                    "one_liner": parsed.get("one_liner", ""),
                    "topic": parsed.get("topic", "")
                }
                
                api_res = requests.post(sheets_url, json=payload, timeout=15)
                
                if api_res.status_code == 200 and "success" in api_res.text:
                    st.balloons()
                    st.success(f"🎉 הצלחה! המאמר זוהה כעיתון {detected_journal} (חודש {detected_month}) ונשמר אוטומטית ב-Google Sheets החדש!")
                    
                    # הצגת מה שסוכם על המסך לביקורת מהירה
                    st.markdown(f"""
                        <div class="article-card">
                            <div class="article-title">📄 {parsed.get('title_and_authors')}</div>
                            <div style="color: #666; font-size: 0.9rem;">📅 עיתון: <b>{detected_journal}</b> | חודש: <b>{detected_month}</b> | נושא: <b>{parsed.get('topic')}</b></div>
                            <div class="summary-box"><b>📝 סיכום (10 שורות):</b><br>{parsed.get('summary')}</div>
                            <div class="takeaway-box">🎯 שורה תחתונה: {parsed.get('one_liner')}</div>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error(f"המאמר סוכם אך אירעה שגיאה בכתיבה לגיליון: {api_res.text}")
                    
            except Exception as e:
                st.error(f"תקלה בתהליך העיבוד האוטומטי: {str(e)}")

# חלק תחתון - הצגת ארכיון מהיר לעיון המתמחים
st.write("---")
st.markdown("### 🗂️ הצצה מהירה למאמרים הקיימים בגיליון")
arch_jcp, arch_jop, arch_coir = st.tabs(["JCP Archive", "JOP Archive", "COIR Archive"])

def show_archive(journal_name):
    rows = db_data.get(journal_name, [])
    if len(rows) > 1:
        for row in rows[1:]:
            if len(row) >= 6:
                st.markdown(f"- **[{row[1]}]** {row[2]} | *שורה תחתונה:* {row[4]}")
    else:
        st.info("אין עדיין מאמרים רשומים בלשונית זו ב-Sheets החדש.")

with arch_jcp: show_archive("JCP")
with arch_jop: show_archive("JOP")
with arch_coir: show_archive("COIR")
