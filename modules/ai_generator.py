import streamlit as st
from google import genai

# Initialize API client from Streamlit secrets (no .env required)
gemini_api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=gemini_api_key)

def generate_nutrition_plan(profile, nutrition_data, academic_context):
    """
    Calls Google Gemini 2.0 Flash to generate a 7-day personalized meal plan 
    based on math modules and academic research context.
    """
    system_prompt = """Sen alanında uzman bir sporcu diyetisyeni ve beslenme danışmanısın. 
Görevin; kullanıcının profiline ve matematiksel olarak hesaplanmış makro değerlerine harfiyen uyarak 7 günlük bir plan oluşturmaktır.

ÇOK KRİTİK MATEMATİK KURALLARI (HAYATİ ÖNEM TAŞIR):
1. Asla açlık diyeti yazma! Eğer sistem sana "Hedef Kalori: 2300 kcal, Protein: 150g" verdiyse, yazdığın menülerin toplamı 800 kcal'de KALAMAZ! Öğün porsiyonlarını (örneğin 50g yulaf yerine 150g, 100g tavuk yerine 250g) hedef kaloriye VE hedef proteine TAM ULAŞACAK şekilde cesurca artır.
2. Öğün Bazlı Basit Hesaplama (ÇOK ÖNEMLİ): Tabloda "Muz: 100 kalori, Yulaf: 150 kalori" gibi her bir besini AYRI AYRI satırlarda HESAPLAMAKLA UĞRAŞMA! AI modelinin halüsinasyon yapmasını önlemek için, o öğünde yenilecek TÜM besinleri (Muz, Yulaf, Süt) "Besinler ve Porsiyonlar" sütununa alt alta yaz. Kalori ve Makroları ise SADECE O ÖĞÜNÜN GENEL TOPLAMI olarak tek bir rakam halinde yaz. Yani her öğün sistemde SADECE 1 SATIR yer kaplasın.
3. Kalori Sağlaması Kuralı (Kesin): 1g Protein = 4 kcal, 1g Karb = 4 kcal, 1g Yağ = 9 kcal. Tablodaki HER ÖĞÜN ve "Günlük Toplam" için `Kalori = (Protein * 4) + (Karbonhidrat * 4) + (Yağ * 9)` denklemi HARFİYEN tutmak zorundadır. Örneğin Kahvaltı satırına 25g Pro, 50g Karb, 15g Yağ yazdıysan -> (25*4)+(50*4)+(15*9)= 435 kcal.
4. Kalori Bölüştürme: Tabloyu çizmeden önce hedefini öğünlere böl. Hedef 2000 kcal ise: Kahvaltı=500, Öğle=600, Ara=300, Akşam=600.

DİĞER KURALLAR:
5. Format (ÖNEMLİ): Her gün için ayrı başlık aç (Örn: `### 1. Gün`). O günün altına `| Öğün | Besinler ve Porsiyonlar | Öğün Toplam Kalori (kcal) | Protein (g) | Karbonhidrat (g) | Yağ (g) |` formatında tablo çiz. Günü tek tabloda bitir, en alta da "Günlük Toplam" satırı ekle. Tablolar bu sayede çok daha temiz olur.
6. Akademik Uyum: "Akademik Bağlam" kısmında verilen bilimsel yönergeleri entegre et.
7. Mutfak Kültürü: Türk yemek kodeksine (Yoğurt, Ayran, Kefir, Lor peyniri, Yulaf, Bulgur, Kuruyemiş vs.) öncelik ver.
8. Hedef Uyum (Kritik): Diyet tercihi "Vejetaryen" veya "Vegan" ise plana KESİNLİKLE et, tavuk, hindi, balık, bulyon vs. EKLEME.
9. Kaynakça (ÇOK KRİTİK): Planın EN ALTINA mutlak suretle 'Kaynaklar ve Gerekçeler' adında bir bölüm ekle. "Şu öğünü verdim, çünkü..." şeklinde RAG veritabanından aldığın akademik dayanakları açık ve doyurucu bir şekilde listele. Uzun sürmesi önemli değil, yeter ki kaliteli ve bilimsel referanslı olsun.
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
- **Dehidrasyon / Ter Oranı**: {profile.get('sweat_rate', 'Belirtilmedi')} L/saat
- **Uyku Süresi**: {profile.get('sleep_duration', 'Belirtilmedi')} saat
- **Diyet Tercihi**: {profile['diet_preference']}
- **Alerjiler**: {profile['allergies']}
- **Kullanılan Supplementler**: {profile.get('supplements') or 'Yok'}
- **Kafein Toleransı**: {profile.get('caffeine_tolerance', 'Belirtilmedi')}
- **Bütçe**: {profile.get('budget', 'Belirtilmedi')}

### Hesaplanmış Günlük İhtiyaçlar (BU RAKAMLARA UYMAK ZORUNLUDUR):
- **Toplam Kalori**: {nutrition_data['target_calories']:.0f} kcal
- **Protein**: {nutrition_data['macros']['protein_g']:.0f} g
- **Karbonhidrat**: {nutrition_data['macros']['carbs_g']:.0f} g
- **Yağ**: {nutrition_data['macros']['fat_g']:.0f} g
- **Sıvı İhtiyacı**: {nutrition_data['hydration_L']:.1f} Litre

### Akademik Bağlam (RAG Sonuçları):
{academic_context if academic_context else "Akademik veri bulunamadı. Genel sporcu beslenmesi kurallarını uygula."}

Lütfen yukarıdaki kurallara, matematiksel hedeflere ve akademik bağlama sıkı sıkıya bağlı kalarak 7 günlük diyet planını markdown tablosu formatında oluştur.
"""
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=system_prompt + "\n\n" + user_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
            )
        )
        return response.text
    except Exception as e:
        print(f"OpenAI API Hatası: {e}")
        return f"Plan oluşturulurken teknik bir sorun oluştu: {str(e)}"
