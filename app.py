import streamlit as st
import google.generativeai as genai
import pypdf
import json

# הגדרות עיצוב בסיסי בעברית
st.set_page_config(page_title="מנתח מאמרים - שלב א'", layout="centered")
st.markdown("""
    <style>
    .reportview-container .main .block-container { text-align: right; direction: RTL; }
    div.stButton > button:first-child { background-color: #008080; color: white; width: 100%; font-weight: bold; }
    label { font-weight: bold !important; }
    </style>
""", unsafe_allow_html=True)

st.title("🔬 מנתח המאמרים הרשמי - שלב א'")
st.write("העלו את קובץ ה-PDF של המאמר, וקבלו את הסיכומים מוכנים להעתקה ישירות לטבלת ה-Sheets שלכם.")

# הזנת מפתח API
api_key = st.text_input("שלב 1: הזינו את מפתח ה-Gemini API שלכם:", type="password")

# העלאת קובץ PDF
uploaded_file = st.file_uploader("שלב 2: בחרו קובץ PDF של מאמר מדעי", type=["pdf"])

if uploaded_file and api_key:
    if st.button("שלב 3: נתח מאמר והפק סיכומים 🚀"):
        with st.spinner("ה-AI קורא ומנתח את כל עמודי המאמר..."):
            try:
                # חילוץ טקסט מה-PDF
                pdf_reader = pypdf.PdfReader(uploaded_file)
                article_text = ""
                for page in pdf_reader.pages[:15]:
                    text = page.extract_text()
                    if text:
                        article_text += text + "\n"

                if len(article_text.strip()) < 100:
                    st.error("שגיאה: לא הצלחנו לקרוא את הטקסט מהקובץ. ודאו שה-PDF אינו סרוק כתמונה בלבד.")
                else:
                    # חיבור ל-Gemini
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel("gemini-2.0-flash")

                    # פרומפט להפקת 2 העמודות
                    prompt = f"""
                    You are an expert Periodontist and Implantologist summarizing literature for a board exam.
                    Analyze the following full-text article and generate two specific outputs strictly in Hebrew:
                    
                    1. 'summary': A professional, comprehensive, and scientifically accurate summary of the study (Objectives, Materials and Methods, Results, and Conclusions) in coherent Hebrew.
                    2. 'one_liner': A sharp, single-sentence clinical takeaway ('שורה תחתונה') in Hebrew that captures the practical significance of the study.

                    Return the output ONLY as a valid JSON object with the keys 'summary' and 'one_liner'. Do not include any markdown formatting or backticks.
                    
                    The article text:
                    {article_text[:40000]}
                    """

                    response = model.generate_content(prompt)
                    raw_response = response.text.strip()
                    
                    if raw_response.startswith("```json"):
                        raw_response = raw_response.replace("```json", "").replace("```", "").strip()
                    
                    result = json.loads(raw_response)

                    st.success("הניתוח הושלם בהצלחה! העתיקו את התוצאות לטבלה:")
                    
                    st.subheader("📋 עמודה ג': סיכום")
                    st.text_area(label="סחבו עם העכבר והעתיקו (Copy):", value=result.get("summary", ""), height=250)

                    st.subheader("🎯 עמודה ד': סיכום בשורה (שורה תחתונה)")
                    st.text_area(label="סחבו עם העכבר והעתיקו (Copy):", value=result.get("one_liner", ""), height=70)

            except Exception as e:
                st.error(f"אירעה תקלה בעיבוד: {str(e)}")
