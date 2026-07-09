import streamlit as st
import pypdf
import requests

st.set_page_config(page_title="פורטל המאמרים המחלקתי", layout="wide")

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

st.markdown("<h1>🚀 פורטל מאמרים לפריודונטיה ושתלים - סביבה מאובטחת</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666; font-size: 1.1rem; margin-bottom: 30px;'>ארכיטקטורה מאובטחת (Zero-Secret Frontend) - כל התקשורת מוצפנת ומנוהלת דרך שרת פרוקסי מחלקתי.</p>", unsafe_allow_html=True)

# 🌐 הכתובת של ה-Cloud Run Proxy שלכם (אין בעיה שזה גלוי בגיט, זה רק נתיב ללא הרשאות)
PROXY_URL = "https://pdf-proxy-741291032537.europe-west1.run.app/process-article"
st.markdown("<div class='upload-container'>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("גררו ושחררו לכאן את קובץ ה-PDF של המאמר המדעי", type=["pdf"])
st.markdown("</div>", unsafe_allow_html=True)

if uploaded_file:
    if st.button("סרוק, סכם ונתב אוטומטית באמצעות הפרוקסי ⚡"):
        with st.spinner("שרת הפרוקסי מעבד את המאמר ומאבטח את הנתונים..."):
            try:
                # חילוץ טקסט מ-4 עמודים ראשונים
                pdf_reader = pypdf.PdfReader(uploaded_file)
                article_text = ""
                for page in pdf_reader.pages[:4]:
                    text = page.extract_text()
                    if text: article_text += text + "\n"
                
                # שליחת הבקשה לפרוקסי המאובטח שלנו
                response = requests.post(PROXY_URL, json={"text": article_text}, timeout=30)
                
                if response.status_code == 200:
                    result_data = response.json().get("data", {})
                    st.balloons()
                    st.success(f"🎉 הצלחה! המאמר נותב אוטומטית לעיתון {result_data.get('journal')} (חודש {result_data.get('month')}) בגיליון המרכזי!")
                    
                    st.markdown(f"""
                        <div class="article-card">
                            <div class="article-title">📄 {result_data.get('title_and_authors')}</div>
                            <div style="color: #666; font-size: 0.9rem;">📅 עיתון: <b>{result_data.get('journal')}</b> | חודש: <b>{result_data.get('month')}</b> | נושא: <b>{result_data.get('topic')}</b></div>
                            <div class="summary-box"><b>📝 סיכום (10 שורות):</b><br>{result_data.get('summary')}</div>
                            <div class="takeaway-box">🎯 שורה תחתונה: {result_data.get('one_liner')}</div>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error(f"❌ שרת הפרוקסי החזיר שגיאה: {response.text}")
                    
            except Exception as e:
                st.error(f"תקלה בתקשורת מול שרת הפרוקסי: {str(e)}")
