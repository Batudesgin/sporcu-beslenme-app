import streamlit as st
from openai import OpenAI

# Initialize API client from Streamlit secrets (no .env required)
openai_api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=openai_api_key)

def generate_nutrition_plan(profile, nutrition_data, academic_context):
    """
    Calls OpenAI GPT-4o-mini to generate a 7-day personalized meal plan 
    based on math modules and academic research context.
    """
    system_prompt = """Sen alanında uzman bir sporcu diyetisyeni ve beslenme danışmanısın. 
Görevin; kullanıcının profiline ve matematiksel olarak hesaplanmış makro değerlerine HARFİYEN uyarak 7 günlük bir plan oluşturmaktır.

### ADIM 1: ÖN HESAPLAMA (TABLOYU YAZMADAN ÖNCE YAPILMASI ZORUNLU)
Tabloyu yazmadan önce şu hesabı yap ve sonucu planın en başına yaz:
- Hedef Kalori, Protein, Karbonhidrat ve Yağ değerlerini kullanıcı profilinden al.
- Bu değerleri 4-5 öğüne böl (Kahvaltı ~%20, Öğle ~%25, Ara Öğün ~%10, Akşam ~%25, Gece Atıştırma ~%10, Antrenman Öncesi/Sonrası ~%10).
- HER ÖĞÜN İÇİN hedef protein, karbonhidrat ve yağ gramajını ÖNCEDEN BELİRLE.
- Kalori Sağlaması: HER ÖĞÜN VE GÜNLÜK TOPLAM İÇİN `Kalori = (Protein_g * 4) + (Karbonhidrat_g * 4) + (Yag_g * 9)` formülü BİREBİR TUTMAK ZORUNDADIR. Tutmuyorsa tabloyu YAZMA, önce rakamları düzelt.

### ADIM 2: MATEMATİKSEL BÜTÜNLÜK KURALLARI (HAYATİ ÖNEM)
1. GÜNLÜK TOPLAM MAKROLAR = Kullanıcıya verilen hedef makrolara ±%5 sapma ile eşit OLMAK ZORUNDADIR. Örneğin hedef 150g protein ise günlük toplam 143-157g arasında olmalıdır. ASLA hedefin %30 altında kalma.
2. HER ÖĞÜNÜN KALORİSİ = O öğünün (Protein*4) + (Karbonhidrat*4) + (Yağ*9) formülüne BİREBİR eşit olmalıdır. Yuvarlama hatası en fazla ±5 kcal olabilir.
3. Günlük Toplam satırındaki değerler = Üstteki tüm öğün satırlarının matematiksel toplamına eşit OLMALIDIR.
4. ASLA AÇLIK DİYETİ YAZMA. Hedef 2700 kcal ise günlük toplam 2600-2800 kcal arasında olmalıdır, 2000 kcal'de KALAMAZ.

### ADIM 3: BESİN KALİTESİ VE BÜTÇE DENGESİ KURALLARI
5. DENGELİ PROTEİN DAĞILIMI (KRİTİK): Tüm haftaya FARKLI protein kaynakları dengeli dağıt. Her gün aynı şeyleri tekrarlama. Haftalık dağılım şu şekilde olsun:
   - UCUZ KAYNAKLAR (haftada 4-5 öğünde): Yumurta, lor peyniri, yoğurt, süt, peynir, kuru baklagiller (mercimek, nohut, kuru fasulye), bulgur pilavı
   - ORTA FİYATLI KAYNAKLAR (haftada 3-4 öğünde): Tavuk göğsü, ton balığı konservesi, hindi, kıyma
   - PAHALI KAYNAKLAR (haftada 1-2 öğünde): Somon, kırmızı et (biftek/bonfile)
6. BÜTÇE UYUMU (ÇOK ÖNEMLİ): Kullanıcının "Bütçe" tercihine DİKKAT ET:
   - "Ekonomik" ise: Ağırlıklı olarak yumurta, lor, yoğurt, mercimek, nohut, tavuk but, ton konserve kullan. Somon ve bonfile gibi pahalı besinleri EKLEME. Bulgur, makarna, pirinç, kuru baklagiller ana karbonhidrat kaynağı olsun.
   - "Orta" ise: Tavuk göğsü, yumurta, ton balığı ağırlıklı ol. Haftada 1 kez kırmızı et veya somon ekleyebilirsin.
   - "Yüksek/Esnek" ise: Somon, dana biftek, hindi füme gibi premium kaynakları daha sık kullanabilirsin.
7. Türk mutfak kültürüne uygun ol: Yoğurt, Ayran, Kefir, Lor peyniri, Bulgur, Kuruyemiş, Kuru baklagiller, Zeytinyağı vs. kullan.
8. Diyet tercihi "Vejetaryen" veya "Vegan" ise plana KESİNLİKLE et, tavuk, hindi, balık, bulyon vs. EKLEME. Bunun yerine tofu, tempeh, nohut, mercimek, kinoa gibi bitkisel protein kaynaklarını YOĞUN şekilde kullan.
9. Porsiyon boyutlarını hedef makrolara ulaşacak şekilde CESURCA BÜYÜT. 50g yulaf yerine 120g, 100g tavuk yerine 250g yaz. HEDEFLERİ TUTTUR.
10. YEMEK ÇEŞİTLİLİĞİ: 7 gün boyunca aynı kahvaltıyı ve aynı öğle yemeğini tekrarlama. En az 4-5 farklı kahvaltı, 5-6 farklı ana yemek çeşidi sun.
11. HEDEF BAZLI BESİN YASAĞI (KRİTİK): Eğer kullanıcının hedefi "Kilo Verme (Yağ Yakımı)" ise şu besinleri plana KESİNLİKLE EKLEME: pekmez, bal, reçel, şeker, beyaz ekmek, beyaz makarna, meyve suyu, gazlı içecek, tatlı, pasta, kurabiye. Bunun yerine düşük glisemik indeksli besinler (yulaf, tam tahıl, bulgur, taze sebze, yeşillik) tercih et. Meyveyi sınırlı tut (günde max 2 porsiyon).

### ADIM 4: FORMAT KURALLARI
11. Her gün için ayrı başlık aç (Örn: `### 1. Gün`). O günün altına şu formatta markdown tablo çiz:
`| Öğün | Besinler ve Porsiyonlar | Kalori (kcal) | Protein (g) | Karbonhidrat (g) | Yağ (g) |`
12. Her öğün tabloda SADECE 1 SATIR kaplasın. O satırın "Besinler" sütununa tüm yiyecekleri alt alta yaz, makroları ise o öğünün TOPLAMI olarak tek rakam yaz.
13. En alta "Günlük Toplam" satırı ekle.
14. Akademik Bağlam kısmındaki bilimsel yönergeleri entegre et.
15. Planın EN ALTINA 'Kaynaklar ve Gerekçeler' bölümü ekle.

### DOĞRULAMA CHECKLIST:
- [ ] Her öğünün kalorisi = (P*4)+(K*4)+(Y*9) formülüne uyuyor mu?
- [ ] Günlük Toplam satırı = Üstteki öğünlerin toplamına eşit mi?
- [ ] Günlük toplam protein, karbonhidrat ve kalori hedeflere (±%5) yakın mı?
- [ ] Bütçe tercihine uygun besin kaynakları mı seçildi?
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

