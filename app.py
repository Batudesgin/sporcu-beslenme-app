import streamlit as st
import os
import io
from dotenv import load_dotenv
import markdown

# Import modules
from modules.calculator import get_athlete_nutrition
from modules.rag_engine import get_relevant_papers
from modules.ai_generator import generate_nutrition_plan

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Sporcu Beslenme Planlayıcı", layout="wide")

# Custom CSS for Background and Glassmorphism
st.markdown("""
<style>
/* Base Dark Theme (Ensures readability outside the form) */
.stApp {
    background-color: #0f172a !important;
}
/* Background Image ONLY for the top header part, keep rest solid dark */
div[data-testid="stForm"] {
    background-image: linear-gradient(rgba(15, 23, 42, 0.85), rgba(15, 23, 42, 0.85)), url("https://images.unsplash.com/photo-1517836357463-d25dfeac3438?q=80&w=1200&auto=format&fit=crop");
    background-size: cover;
    background-position: center;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 20px;
}
/* Glassmorphism focus only on metric containers */
div[data-testid="metric-container"] {
    background: rgba(30, 41, 59, 0.5) !important;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 20px;
}
/* Button Visibility Fix */
.stButton > button, div[data-testid="stForm"] button, .stDownloadButton button {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 10px 24px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
    opacity: 1 !important;
    visibility: visible !important;
}
.stButton > button:hover, div[data-testid="stForm"] button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}
/* Font Colors for dark theme */
h1, h2, h3, h4, p, label, li, span, td, th {
    color: #f8fafc !important;
}
/* Fix Dropdown options text color so they aren't invisible */
div[data-baseweb="popover"] ul li, 
div[role="listbox"] span, 
[data-baseweb="select"] ul li, 
div[data-testid="stVirtualDropdown"] li {
    color: #0f172a !important; 
}
div[data-baseweb="select"] {
    background-color: white !important;
}
div[data-baseweb="select"] span {
    color: #0f172a !important;
}
/* Fix Download Button Text Contrast */
.stDownloadButton button p {
    color: #f8fafc !important;
}
/* Ensure Table Borders are Visible */
table {
    border-collapse: collapse;
    width: 100%;
}
th, td {
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    padding: 12px !important;
}
th {
    background-color: rgba(255, 255, 255, 0.1) !important;
}
/* Print PDF Fixes - White background, black/dark-gray text */
@media print {
    * { background: transparent !important; color: black !important; filter: none !important; }
    body, .stApp { background-color: white !important; }
    h1, h2, h3, h4, p, label, div, span, td, th, li { color: black !important; }
    div[data-testid="stForm"] {
        background-image: none !important;
        background-color: white !important;
    }
    .stButton, .stDownloadButton { display: none !important; }
}
</style>
""", unsafe_allow_html=True)
st.title("🏃‍♂️ Kişiye Özel Sporcu Beslenme Planlayıcı")
st.markdown("""
Bu platform; yüzücü, koşucu, triatloncu, bisikletçi ve fitness sporcuları için kişiselleştirilmiş, 
bilimsel makalelere (ISSN, ACSM) dayalı 7 günlük beslenme planı oluşturur.
""")

st.header("1. Sporcu Profili & Gelişmiş Metrikler")

with st.form("athlete_profile_form"):
    st.subheader("Temel Fiziksel Bilgiler")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        age = st.number_input("Yaş", min_value=15, max_value=80, value=25)
        gender = st.selectbox("Cinsiyet", ["Erkek", "Kadın"])
    with col2:
        weight = st.number_input("Kilo (kg)", min_value=40.0, max_value=150.0, value=70.0, step=0.1)
        height = st.number_input("Boy (cm)", min_value=140, max_value=220, value=175)
    with col3:
        body_fat = st.number_input("Yağ Oranı (%) - Opsiyonel", min_value=0.0, max_value=50.0, value=0.0, step=0.1)
        vo2max = st.number_input("VO2max (mL/kg/dk) - Opsiyonel", min_value=0.0, max_value=90.0, value=0.0, step=0.1)
    with col4:
        menstrual_phase = None
        if gender == "Kadın":
            menstrual_phase = st.selectbox("Menstrüel Döngü Fazı", ["Belirtmek İstemiyorum", "Foliküler Faz (1-14. Günler)", "Luteal Faz (15-28. Günler)"])
            
    st.subheader("Antrenman ve Hedef")
    col5, col6, col7, col8 = st.columns(4)
    with col5:
        sport_type = st.selectbox("Spor Dalı", ["Koşucu", "Yüzücü", "Bisikletçi", "Triatloncu", "Fitness", "Dans", "Jimnastik", "Dövüş Sporları", "Tenis", "Powerlifting"])
        goal = st.selectbox("Genel Hedef", ["Performans Artışı / Kilo Koruma", "Kilo Verme (Yağ Yakımı)", "Kas Gelişimi"])
    with col6:
        # Mesafeler spora göre değişir. Streamlit form içinde dinamik update zor olduğu için tüm seçenekleri gruplayabiliriz
        # veya selectbox'ı dışarı alabiliriz ama form içinde let's keep a generic list or a combined list.
        # But wait, inside st.form, dynamic updates of widgets based on other widgets don't work well immediately.
        # We can ask for the distance with a text input or generic selectbox.
        target_distance = st.selectbox("Yarış / Hedef Mesafe", [
            "Belirtilmedi",
            "Koşu: 5K / 10K", "Koşu: Yarı Maraton", "Koşu: Maraton / Ultra",
            "Yüzme: 400m-1500m", "Yüzme: Açık Su 5K+",
            "Bisiklet: Kriter / Kısa", "Bisiklet: Yol 100K+ / Gran Fondo",
            "Triatlon: Sprint / Olimpik", "Triatlon: 70.3 / Ironman",
            "Fitness: Genel / Vücut Geliştirme",
            "Dans: Performans / Yarışma", "Jimnastik: Artistik / Ritmik",
            "Dövüş: MMA / Boks / Güreş", "Tenis: Tekler / Çiftler",
            "Powerlifting: Squat / Bench / Deadlift"
        ])
    with col7:
        training_days = st.slider("Haftalık Antrenman Günü", 1, 7, 5)
        training_hours = st.number_input("Günlük Ortalama Antrenman (Saat)", min_value=0.5, max_value=8.0, value=1.5, step=0.5)
    with col8:
        training_time = st.selectbox("Antrenman Saati (Ortalama)", ["Sabah (05:00 - 09:00)", "Öğle (10:00 - 14:00)", "İkindi (15:00 - 18:00)", "Akşam (19:00 - 23:00)"])
        intensity = st.selectbox("Antrenman Yoğunluğu", ["Düşük", "Orta", "Yüksek (Interval / Yarış temposu)"])
        
    st.subheader("Beslenme ve Yaşam Tarzı")
    col9, col10, col11 = st.columns(3)
    with col9:
        diet_preference = st.selectbox("Diyet Tercihi", ["Standart (Her Şeyi Yer)", "Vejetaryen", "Vegan", "Glutensiz"])
        allergies = st.text_input("Alerji (Varsa)", placeholder="Örn: Fıstık, Süt ürünü")
        supplements = st.text_input("Kullanılan Supplementler", placeholder="Örn: Whey, Kreatin")
    with col10:
        sweat_rate = st.selectbox("Terleme Miktarı", ["Az (Kıyafet kuru kalır)", "Normal", "Çok (Kıyafet sırılsıklam)", "Aşırı (Tuz lekesi kalır)"])
        caffeine_tolerance = st.selectbox("Kafein Toleransı", ["Kullanmam", "1-2 fincan/gün", "3+ fincan/gün"])
    with col11:
        sleep_duration = st.selectbox("Uyku Süresi (Ortalama)", ["5-6 saat", "6-7 saat", "7-8 saat", "8+ saat"])
        budget = st.selectbox("Bütçe", ["Ekonomik", "Normal", "Fark etmez"])
        
    if 'generations_count' not in st.session_state:
        st.session_state.generations_count = 0
        
    if st.session_state.generations_count >= 3:
        st.warning("Bu oturum için plan oluşturma hakkınızı doldurdunuz (Limit: 3).")
        submitted = st.form_submit_button("Limit Aşıldı", disabled=True)
    else:
        submitted = st.form_submit_button("Detaylı Beslenme Planı Oluştur")

if 'meal_plan' not in st.session_state:
    st.session_state.meal_plan = None
if 'nutrition_data' not in st.session_state:
    st.session_state.nutrition_data = None
if 'sport_type' not in st.session_state:
    st.session_state.sport_type = "Sporcu"

if submitted:
    st.session_state.sport_type = sport_type
    profile = {
        "age": age,
        "weight": weight,
        "height": height,
        "gender": gender,
        "body_fat": body_fat,
        "vo2max": vo2max,
        "menstrual_phase": menstrual_phase if gender == "Kadın" else None,
        "sport_type": sport_type,
        "goal": goal,
        "target_distance": target_distance,
        "training_days": training_days,
        "training_hours": training_hours,
        "training_time": training_time,
        "intensity": intensity,
        "diet_preference": diet_preference,
        "allergies": allergies,
        "supplements": supplements,
        "sweat_rate": sweat_rate,
        "caffeine_tolerance": caffeine_tolerance,
        "sleep_duration": sleep_duration,
        "budget": budget
    }
    
    with st.spinner("Matematiksel hesaplamalar yapılıyor... (Spor dalınıza göre makrolar belirleniyor)"):
        nutrition_data = get_athlete_nutrition(profile)
        
    with st.spinner("Akademik veritabanı (RAG) taranıyor... Pinecone'dan ilgili makaleler getiriliyor."):
        rag_result = get_relevant_papers(profile)
        academic_context = rag_result["text"]
        rag_sources = rag_result["sources"]
        
    with st.spinner("Biyometrik verileriniz ve antrenman parametreleriniz analiz ediliyor. Kişiye özel 7 günlük metabolik beslenme protokolü sentezleniyor. Lütfen bekleyin (30-50 sn)..."):
        meal_plan = generate_nutrition_plan(profile, nutrition_data, academic_context, rag_sources)
        
    st.session_state.nutrition_data = nutrition_data
    st.session_state.meal_plan = meal_plan
    st.session_state.generations_count += 1
    st.success("Plan başarıyla oluşturuldu!")
    
if st.session_state.meal_plan and st.session_state.nutrition_data:
    nutrition_data = st.session_state.nutrition_data
    meal_plan = st.session_state.meal_plan
    sport_type = st.session_state.sport_type
    
    st.header("📊 Matematiksel Analiz Sonuçları")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Bazal Metabolizma (BMR)", f"{nutrition_data['bmr']} kcal")
    with col2:
        st.metric("Günlük Harcanan (TDEE)", f"{nutrition_data['tdee']} kcal")
    with col3:
        st.metric("Hedef Kalori", f"{nutrition_data['target_calories']} kcal")
    with col4:
        st.metric("Aktivite Çarpanı", f"x{nutrition_data['activity_factor']}")
        
    st.subheader("Makro Besin Dağılımı (Günlük Hedef)")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Protein", f"{nutrition_data['macros']['protein_g']} g")
    with col2:
        st.metric("Karbonhidrat", f"{nutrition_data['macros']['carbs_g']} g")
    with col3:
        st.metric("Yağ", f"{nutrition_data['macros']['fat_g']} g")

    # ── Hydration Section ──
    hydration = nutrition_data.get("hydration", {})
    if hydration:
        st.subheader("💧 Günlük Hidrasyon Planı (ACSM/NSCA)")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Bazal Su (Antrenman Dışı)", f"{hydration['basal_ml']} ml")
        with col2:
            st.metric("Egzersiz Sıvı Kaybı", f"{hydration['exercise_loss_ml']} ml")
        with col3:
            st.metric("Toplam Günlük İhtiyaç", f"{hydration['total_L']} L")
        with col4:
            st.metric("Terleme Hızı (ort.)", f"{hydration['sweat_per_hour_avg']} ml/saat")
        
        col5, col6, col7 = st.columns(3)
        with col5:
            st.metric("Antrenman Öncesi (2-3 saat önce)", f"{hydration['pre_training_ml']} ml")
        with col6:
            st.metric("Antrenman Sonrası (4 saat içinde)", f"{hydration['post_training_total_ml']} ml")
        with col7:
            if hydration.get("caffeine_extra_ml", 0) > 0:
                st.metric("Kafein Kompanzasyonu", f"+{hydration['caffeine_extra_ml']} ml")
            if hydration.get("heat_bonus_ml", 0) > 0:
                st.metric("Sıcaklık Ek Sıvı (+%15)", f"+{round(hydration['heat_bonus_ml'])} ml")
        
        if hydration.get("needs_electrolyte"):
            st.warning(f"⚠️ **Hiponatremi Uyarısı:** Uzun süreli/uzun mesafe antrenmanınız için SADECE su yeterli değildir. "
                       f"Egzersiz sırasında tahmini **{hydration['electrolyte_sodium_mg']} mg sodyum** alımı gereklidir "
                       f"(izotonik sporcu içeceği veya elektrolit tableti ile).")

    st.header("📝 7 Günlük Kişiye Özel Beslenme Planı")
    st.markdown(meal_plan)
    
    # Generate PDF in memory using fpdf2
    def create_pdf(text_content):
        from fpdf import FPDF
        import re
        
        class PDF(FPDF):
            def header(self):
                self.set_font("Helvetica", "B", 16)
                self.set_text_color(30, 58, 138)
                self.cell(0, 12, "Sporcu Beslenme Plani", border=False, align="C", new_x="LMARGIN", new_y="NEXT")
                self.set_draw_color(30, 58, 138)
                self.set_line_width(0.5)
                self.line(10, self.get_y(), self.w - 10, self.get_y())
                self.ln(4)

            def footer(self):
                self.set_y(-15)
                self.set_font("Helvetica", "I", 8)
                self.set_text_color(128, 128, 128)
                self.cell(0, 10, f"Sayfa {self.page_no()}/{{nb}}", align="C")

        pdf = PDF(orientation="landscape", format="A4")
        pdf.set_auto_page_break(auto=True, margin=20)
        pdf.add_page()
        
        # Transliterate Turkish chars for latin-1 compatibility
        tr_map = str.maketrans({
            'ğ': 'g', 'Ğ': 'G', 'ı': 'i', 'İ': 'I',
            'ş': 's', 'Ş': 'S', 'ö': 'o', 'Ö': 'O',
            'ç': 'c', 'Ç': 'C', 'ü': 'u', 'Ü': 'U'
        })
        safe_text = text_content.translate(tr_map)
        # Remove emojis and other non-latin-1 characters (💧📚🏃 etc.)
        safe_text = re.sub(r'[^\x00-\xff]', '', safe_text)
        
        # Convert markdown to styled HTML for fpdf2's write_html
        lines = safe_text.split('\n')
        html_parts = []
        in_table = False
        is_header_row = True
        
        for line in lines:
            stripped = line.strip()
            
            # Headings
            if stripped.startswith('### '):
                if in_table:
                    html_parts.append('</table><br>')
                    in_table = False
                html_parts.append(f'<br><font size="14" color="#1e3a8a"><b>{stripped[4:]}</b></font><br>')
                is_header_row = True
                continue
            elif stripped.startswith('## '):
                if in_table:
                    html_parts.append('</table><br>')
                    in_table = False
                html_parts.append(f'<br><font size="16" color="#1e3a8a"><b>{stripped[3:]}</b></font><br>')
                continue
            elif stripped.startswith('# '):
                if in_table:
                    html_parts.append('</table><br>')
                    in_table = False
                html_parts.append(f'<br><font size="18" color="#1e3a8a"><b>{stripped[2:]}</b></font><br>')
                continue
            
            # Table separator row (|---|---|)
            if stripped.startswith('|') and set(stripped.replace('|', '').replace('-', '').replace(':', '').strip()) == set() :
                continue
                
            # Table rows
            if stripped.startswith('|') and stripped.endswith('|'):
                cells = [c.strip() for c in stripped.split('|')[1:-1]]
                
                if not in_table:
                    col_count = len(cells)
                    col_width = int(96 / col_count) if col_count > 0 else 16
                    html_parts.append(f'<table border="1" width="100%">')
                    in_table = True
                    is_header_row = True
                
                if is_header_row:
                    row_html = '<tr>'
                    for cell in cells:
                        row_html += f'<td width="{col_width}%" bgcolor="#1e3a8a" align="center"><font color="#ffffff" size="9"><b>{cell}</b></font></td>'
                    row_html += '</tr>'
                    html_parts.append(row_html)
                    is_header_row = False
                else:
                    # Check if this is a "Toplam" row
                    is_total = any('toplam' in c.lower() for c in cells)
                    bg = ' bgcolor="#e2e8f0"' if is_total else ''
                    row_html = '<tr>'
                    for i, cell in enumerate(cells):
                        align = 'left' if i < 2 else 'center'
                        bold_s = '<b>' if is_total else ''
                        bold_e = '</b>' if is_total else ''
                        row_html += f'<td width="{col_width}%"{bg} align="{align}"><font size="8">{bold_s}{cell}{bold_e}</font></td>'
                    row_html += '</tr>'
                    html_parts.append(row_html)
                continue
            
            # Close table if we were in one
            if in_table and not stripped.startswith('|'):
                html_parts.append('</table><br>')
                in_table = False
                is_header_row = True
            
            # Bold text
            if stripped.startswith('**') or stripped.startswith('- **'):
                clean = stripped.replace('**', '').replace('- ', '')
                html_parts.append(f'<font size="10"><b>{clean}</b></font><br>')
                continue
            
            # Regular text
            if stripped:
                clean = stripped.replace('**', '')
                html_parts.append(f'<font size="9">{clean}</font><br>')
        
        if in_table:
            html_parts.append('</table>')
        
        full_html = '\n'.join(html_parts)
        
        pdf.set_font("Helvetica", size=9)
        pdf.write_html(full_html)
            
        result = io.BytesIO()
        pdf.output(result)
        return result.getvalue()
    
    pdf_bytes = create_pdf(meal_plan)
    
    tr_map_file = str.maketrans("ğğıışşööççüüşş", "ggiissooccouss")
    safe_filename = f"{sport_type.lower().translate(tr_map_file)}_beslenme_plani.pdf"
    
    st.download_button(
        label="📥 Planı Doğrudan PDF Olarak İndir",
        data=pdf_bytes,
        file_name=safe_filename,
        mime="application/pdf"
    )
