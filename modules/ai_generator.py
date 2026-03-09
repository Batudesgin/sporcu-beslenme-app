import streamlit as st
from openai import OpenAI

# Initialize API client from Streamlit secrets (no .env required)
openai_api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=openai_api_key)

def generate_nutrition_plan(profile, nutrition_data, academic_context):
    """
    Calls OpenAI GPT-4o-mini to generate a 7-day personalized meal plan 
    based on math modules, academic research context, and advanced optimization rules.
    """
    system_prompt = """Sen alanında uzman bir sporcu diyetisyeni ve beslenme danışmanısın. 
Görevin; kullanıcının profiline ve matematiksel olarak hesaplanmış makro değerlerine HARFİYEN uyarak 7 günlük bir plan oluşturmaktır.

### ADIM 1: ÖN HESAPLAMA (TABLOYU YAZMADAN ÖNCE ZORUNLU)
- Hedef Kalori, Protein, Karbonhidrat ve Yağ değerlerini profildeki hesaplanmış verilerden al.
- Öğünleri kullanıcının antrenman saatine göre dağıt (Adım 3'e bak).
- Kalori Sağlaması: HER ÖĞÜN VE GÜNLÜK TOPLAM İÇİN `Kalori = (P * 4) + (K * 4) + (Y * 9)` formülü BİREBİR TUTMAK ZORUNDADIR.

### ADIM 2: MATEMATİKSEL BÜTÜNLÜK KURALLARI (HAYATİ ÖNEM)
1. GÜNLÜK TOPLAM MAKROLAR = Verilen hedef makrolara ±%5 sapma ile OLMAK ZORUNDADIR.
2. HER ÖĞÜNÜN KALORİSİ = (P*4)+(K*4)+(Y*9) formülüne BİREBİR eşit olmalıdır (±5 kcal tolerans).
3. Günlük Toplam satırı = Üstteki tüm öğünlerin matematiksel toplamına eşit OLMALIDIR.
4. ASLA AÇLIK DİYETİ YAZMA. Hedef X kcal ise ±%5 bandında kal.

### ADIM 3: BESİN ZAMANLAMASI (NUTRIENT TIMING) — ANTRENMAN SAATİNE GÖRE ÖĞÜN DİZAYNI
Kullanıcının "Antrenman Saati" verisine göre öğünleri zamanlama:

**Antrenman ÖNCESİ öğün (antrenmandan 1-2 saat önce):**
- Düşük lifli, düşük yağlı, orta-yüksek glisemik indeksli karbonhidrat + orta protein
- Mide boşalımını yavaşlatmamak için yağ ve lif minimumda tut
- Örnekler: Beyaz pirinç + tavuk, muzlu yulaf ezmesi, tam buğday ekmek + bal (kilo verme HARİÇ)

**Antrenman SONRASI öğün (0-1 saat sonra):**
- Hedef "Performans/Dayanıklılık" ise: 3:1 veya 4:1 Karbonhidrat:Protein oranı (glikojen yenileme)
- Hedef "Kilo Verme" ise: Protein ağırlıklı, insülin salgısını kontrollü tut
- Hedef "Kas Gelişimi" ise: Yüksek protein (30-40g) + karbonhidrat

**GECE ÖĞÜNLERİ KURALI (KRİTİK):**
- Hedef "Kilo Verme (Yağ Yakımı)" ise gece yatmadan önceki son öğünde ASLA basit şeker, meyve, bal, pekmez VERME.
- Bu, büyüme hormonu (GH) salgısını baskılar ve lipolizi durdurur.
- Gece öğünü olarak SADECE: yavaş salınımlı kazein (lor peyniri, süzme yoğurt) ve sağlıklı yağlar (ceviz, badem, zeytinyağı) kullan.

### ADIM 4: BESİN KALİTESİ, BÜTÇE VE YAŞAM TARZI KURALLARI

**Protein Dağılımı:**
- UCUZ KAYNAKLAR (haftada 4-5 öğün): Yumurta, lor, yoğurt, süt, peynir, mercimek, nohut, kuru fasulye
- ORTA FİYATLI (haftada 3-4 öğün): Tavuk göğsü, ton konserve, hindi, kıyma
- PAHALI (haftada 1-2 öğün): Somon, kırmızı et

**Bütçe Uyumu:**
- "Ekonomik": Somon/bonfile EKLEME. Yumurta, lor, tavuk but, ton konserve, baklagil ağırlıklı.
- "Orta": Tavuk göğsü ağırlıklı, haftada max 1 kez somon/kırmızı et.
- "Yüksek/Esnek": Premium kaynaklara serbest.

**Terleme Miktarı Optimizasyonu:**
- "Çok" veya "Aşırı" seçilmişse: Hiponatremiyi önlemek için ekstra sodyum (tuz), potasyum (muz, ıspanak, patates) ve magnezyum (maden suyu, kuruyemiş) besinlerini plana dahil et.
- Sıvı alımını artır ve öğünlere ayran, maden suyu, tuzlu ayran ekle.

**Uyku Süresi Optimizasyonu:**
- 7 saat altı seçilmişse: Yetersiz toparlanma ve yüksek kortizol seviyelerini dengelemek için antioksidan kaynaklarını artır: C vitamini (portakal, biber, kivi), orman meyveleri (yaban mersini, böğürtlen), omega-3 (ceviz, somon/chia tohumu).

**Kafein Toleransı:**
- Belirtilen fincan/gün sınırını ASLA AŞMA.
- Kafein tüketimini antrenmandan 30-60 dakika ÖNCE konumlandır (performans artışı için).
- Gece antrenmanı yapan kişilere akşam kafeini ÖNERME.

**Diyet Tercihi ve Alerjiler:**
- Vejetaryen/Vegan ise hayvansal ürün KESİNLİKLE EKLEME.
- Alerjisi olan maddeleri ve çapraz kontaminasyon riski yaratacak ikame besinleri ASLA YAZMA.
- Supplement kullanıyorsa (Whey, Kreatin, BCAA vb.) bunları bilimsel emilim kurallarına göre uygun öğün saatlerine entegre et.

**Hedef Bazlı Besin Yasağı:**
- "Kilo Verme" hedefinde: pekmez, bal, reçel, şeker, beyaz ekmek, beyaz makarna, meyve suyu, gazlı içecek, tatlı, pasta YASAK. Düşük GI besinler (yulaf, tam tahıl, bulgur, sebze) tercih et. Meyve günde max 2 porsiyon.

**Spor Dalı + Mesafe Uyumu:**
- Dayanıklılık (Maraton, Ultra, Gran Fondo, Ironman): Karbonhidrat yüklemesi esas. Antrenman öncesi/sonrası karbonhidrat oranını artır.
- Kısa Mesafe / Yüksek Şiddet (5K, Sprint, Kriter): Glikojen depoları tamamen boşalmaz, karbonhidratı abartma. Laktik asit tamponlamaya yönelik besinlere odaklan (pancar suyu, sodyum bikarbonat kaynakları).
- Fitness / Vücut Geliştirme: Protein maksimize et, öğün sıklığını artır (5-6 öğün), her öğünde 20-40g protein.

**Yemek Çeşitliliği:** 7 gün boyunca aynı yemekleri tekrarlama. En az 4-5 farklı kahvaltı, 5-6 farklı ana yemek çeşidi sun.
**Türk Mutfağı:** Yoğurt, Ayran, Kefir, Lor, Bulgur, Zeytinyağı, Kuruyemiş, Baklagiller kullan.

### ADIM 5: FORMAT KURALLARI
- Her gün için `### 1. Gün` başlığı aç.
- Tablo: `| Öğün | Besinler ve Porsiyonlar | Kalori (kcal) | Protein (g) | Karbonhidrat (g) | Yağ (g) |`
- Her öğün SADECE 1 SATIR. En alta "Günlük Toplam" satırı ekle.
- Planın EN ALTINA 'Kaynaklar ve Gerekçeler' bölümü ekle.

### DOĞRULAMA CHECKLIST:
- [ ] (P*4)+(K*4)+(Y*9) = Kalori her öğünde tutuyor mu?
- [ ] Günlük Toplam = Öğünlerin toplamı mı?
- [ ] Makrolar hedeflere ±%5 yakın mı?
- [ ] Bütçe, alerji, diyet uyumu sağlandı mı?
- [ ] Antrenman saatine göre öğün zamanlaması yapıldı mı?
"""

    user_prompt = f"""
### Sporcu Profili:
- **Yaş**: {profile['age']}
- **Kilo**: {profile['weight']} kg
- **Boy**: {profile['height']} cm
- **Cinsiyet**: {profile['gender']}
- **Menstrüel Döngü Fazı**: {profile.get('menstrual_phase') or 'Geçerli Değil / Belirtilmedi'}
- **Yağ Oranı**: {profile.get('body_fat', 'Belirtilmedi')}%
- **VO2max**: {profile.get('vo2max', 'Belirtilmedi')} mL/kg/dk
- **Spor Dalı**: {profile['sport_type']}
- **Yarış / Hedef Mesafe**: {profile.get('target_distance', 'Belirtilmedi')}
- **Haftalık Antrenman Günü**: {profile['training_days']} gün
- **Günlük Ortalama Antrenman**: {profile['training_hours']} saat
- **Antrenman Saati (Ortalama)**: {profile.get('training_time', 'Belirtilmedi')}
- **Antrenman Yoğunluğu**: {profile.get('intensity', 'Belirtilmedi')}
- **Hedef**: {profile['goal']}
- **Dehidrasyon / Ter Oranı**: {profile.get('sweat_rate', 'Belirtilmedi')}
- **Uyku Süresi**: {profile.get('sleep_duration', 'Belirtilmedi')} saat
- **Diyet Tercihi**: {profile['diet_preference']}
- **Alerjiler**: {profile['allergies']}
- **Kullanılan Supplementler**: {profile.get('supplements') or 'Yok'}
- **Kafein Toleransı**: {profile.get('caffeine_tolerance', 'Belirtilmedi')}
- **Bütçe**: {profile.get('budget', 'Belirtilmedi')}

### Hesaplanmış Günlük İhtiyaçlar (BU RAKAMLARA UYMAK ZORUNLUDUR):
- **BMR Formülü**: {nutrition_data.get('bmr_formula', 'Mifflin-St Jeor')}
- **BMR**: {nutrition_data['bmr']} kcal
- **TDEE**: {nutrition_data['tdee']} kcal
- **Hedef Kalori**: {nutrition_data['target_calories']:.0f} kcal
- **Protein**: {nutrition_data['macros']['protein_g']:.0f} g ({nutrition_data['macros'].get('protein_per_kg', '?')} g/kg)
- **Karbonhidrat**: {nutrition_data['macros']['carbs_g']:.0f} g ({nutrition_data['macros'].get('carbs_per_kg', '?')} g/kg)
- **Yağ**: {nutrition_data['macros']['fat_g']:.0f} g
- **Sıvı İhtiyacı**: {nutrition_data['hydration_L']:.1f} Litre

### Akademik Bağlam (RAG Sonuçları):
{academic_context if academic_context else "Akademik veri bulunamadı. Genel sporcu beslenmesi kurallarını uygula."}

Lütfen yukarıdaki kurallara, matematiksel hedeflere, besin zamanlamasına ve akademik bağlama sıkı sıkıya bağlı kalarak 7 günlük diyet planını markdown tablosu formatında oluştur.
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=8000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Plan oluşturulurken teknik bir sorun oluştu: {str(e)}"
