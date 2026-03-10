def calculate_bmr(weight, height, age, gender, body_fat=0):
    """
    Calculates Basal Metabolic Rate.
    - If body fat % is provided: Katch-McArdle formula (370 + 21.6 * LBM)
    - Otherwise: Mifflin-St Jeor equation
    """
    if body_fat and body_fat > 0:
        lbm = weight * (1 - (body_fat / 100))
        return 370 + (21.6 * lbm)  # Katch-McArdle
    
    if gender == "Erkek":
        return (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:
        return (10 * weight) + (6.25 * height) - (5 * age) - 161

def calculate_activity_factor(training_days, training_hours, intensity="Orta"):
    """
    Determines activity multiplier (PAL) based on training frequency, duration, and intensity.
    """
    avg_daily_hours = (training_days * training_hours) / 7
    
    if avg_daily_hours < 0.5:
        factor = 1.375
    elif avg_daily_hours <= 1.0:
        factor = 1.55
    elif avg_daily_hours <= 2.0:
        factor = 1.725
    else:
        factor = 1.9
        
    if intensity == "Yüksek (Interval / Yarış temposu)":
        factor += 0.1
    elif intensity == "Düşük":
        factor -= 0.1
        if factor < 1.2:
            factor = 1.2
            
    return factor

def calculate_macros(weight, sport_type, goal, avg_daily_hours, total_calories, target_distance="Belirtilmedi"):
    """
    Calculates macro distribution (Protein, Carbs, Fat) based on ISSN/ACSM guidelines.
    Adapts to sport type, goal, training volume, AND target race distance.
    """
    # --- PROTEIN per KG (goal-driven) ---
    if goal == "Kilo Verme (Yağ Yakımı)":
        protein_per_kg = 2.0  # High protein to prevent catabolism in deficit
    elif goal == "Kas Gelişimi":
        protein_per_kg = 1.8
    else:
        protein_per_kg = 1.6  # Performance / maintenance
        
    # --- CARBS per KG (sport + distance + goal driven) ---
    is_endurance_long = any(d in str(target_distance) for d in ["Maraton", "Ultra", "Gran Fondo", "70.3", "Ironman", "Açık Su 5K+"])
    is_short_intensity = any(d in str(target_distance) for d in ["5K", "10K", "Sprint", "Kriter", "400m"])
    
    if goal == "Kilo Verme (Yağ Yakımı)":
        # Fat loss: keep carbs just enough for training energy
        carbs_per_kg = 3.5
        if avg_daily_hours > 1.5:
            carbs_per_kg = 4.0
    elif sport_type == "Fitness":
        protein_per_kg = max(protein_per_kg, 1.8)
        if goal == "Kas Gelişimi":
            protein_per_kg = 2.2
        carbs_per_kg = 4.0 if avg_daily_hours < 1.0 else 5.0
    elif sport_type == "Powerlifting":
        protein_per_kg = max(protein_per_kg, 2.0)
        if goal == "Kas Gelişimi":
            protein_per_kg = 2.2
        carbs_per_kg = 3.5 if avg_daily_hours < 1.0 else 4.5
    elif sport_type == "Dövüş Sporları":
        protein_per_kg = max(protein_per_kg, 1.8)
        if avg_daily_hours < 1.0:
            carbs_per_kg = 5.0
        elif avg_daily_hours <= 2.0:
            carbs_per_kg = 6.0
        else:
            carbs_per_kg = 7.0
    elif sport_type == "Tenis":
        protein_per_kg = max(protein_per_kg, 1.6)
        if avg_daily_hours < 1.0:
            carbs_per_kg = 5.0
        elif avg_daily_hours <= 2.0:
            carbs_per_kg = 6.0
        else:
            carbs_per_kg = 7.0
    elif sport_type in ["Dans", "Jimnastik"]:
        protein_per_kg = max(protein_per_kg, 1.6)
        if avg_daily_hours < 1.0:
            carbs_per_kg = 4.5
        elif avg_daily_hours <= 2.0:
            carbs_per_kg = 5.5
        else:
            carbs_per_kg = 6.5
    elif sport_type in ["Koşucu", "Bisikletçi", "Triatloncu"]:
        if is_endurance_long:
            # Long endurance: carb loading essential (5-8 g/kg)
            protein_per_kg = max(protein_per_kg, 1.4)
            if avg_daily_hours < 1.5:
                carbs_per_kg = 6.0
            elif avg_daily_hours <= 2.5:
                carbs_per_kg = 7.0
            else:
                carbs_per_kg = 8.0
        elif is_short_intensity:
            # Short high-intensity: moderate carbs (4-6 g/kg)
            carbs_per_kg = 4.5 if avg_daily_hours < 1.0 else 5.5
        else:
            # General endurance
            if avg_daily_hours < 1.0:
                carbs_per_kg = 5.0
            elif avg_daily_hours <= 2.0:
                carbs_per_kg = 6.5
            else:
                carbs_per_kg = 8.0
    else:  # Yüzücü
        if avg_daily_hours < 1.0:
            carbs_per_kg = 5.0
        elif avg_daily_hours <= 2.0:
            carbs_per_kg = 6.0
        else:
            carbs_per_kg = 7.0
            
    # Calculate grams
    protein_g = weight * protein_per_kg
    carbs_g = weight * carbs_per_kg
    
    # Calculate calories from protein and carbs (4 kcal/g)
    protein_kcal = protein_g * 4
    carbs_kcal = carbs_g * 4
    
    # Remaining for fat (9 kcal/g)
    fat_kcal = total_calories - (protein_kcal + carbs_kcal)
    fat_g = fat_kcal / 9
    
    # Safety: fat shouldn't be too low (< 0.8g/kg) or negative
    if fat_g < (weight * 0.8):
        fat_g = weight * 0.8
        fat_kcal = fat_g * 9
        carbs_kcal = total_calories - protein_kcal - fat_kcal
        carbs_g = max(carbs_kcal / 4, weight * 2.0)  # Min 2g/kg carbs
        
    return {
        "protein_g": round(protein_g),
        "protein_per_kg": round(protein_per_kg, 1),
        "carbs_g": round(carbs_g),
        "carbs_per_kg": round(carbs_per_kg, 1),
        "fat_g": round(fat_g),
        "total_kcal": round(total_calories)
    }

def calculate_hydration(profile):
    """
    Calculates detailed hydration plan based on ACSM & NSCA standards.
    Returns a dict with all hydration metrics in ml.
    """
    weight = profile['weight']
    training_hours = profile['training_hours']
    sweat_rate = profile.get('sweat_rate', 'Normal')
    training_time = profile.get('training_time', '')
    caffeine = profile.get('caffeine_tolerance', 'Kullanmam')
    target_distance = profile.get('target_distance', 'Belirtilmedi')
    
    # ── 1. Bazal Su İhtiyacı (Antrenman Dışı) ──
    # ACSM: Vücut ağırlığı × 35 ml
    basal_ml = weight * 35
    
    # ── 2. Egzersiz Sırasında Terleme Bazlı Ek Sıvı ──
    # Terleme şiddetine göre saatlik kayıp (ml/saat)
    if sweat_rate in ["Az (Kıyafet kuru kalır)", "Normal"]:
        sweat_per_hour_low = 500
        sweat_per_hour_high = 700
    elif sweat_rate == "Çok (Kıyafet sırılsıklam)":
        sweat_per_hour_low = 1000
        sweat_per_hour_high = 1500
    else:  # Aşırı (Tuz lekesi kalır)
        sweat_per_hour_low = 1200
        sweat_per_hour_high = 1800
    
    # Ortalama terleme kaybı
    sweat_per_hour_avg = (sweat_per_hour_low + sweat_per_hour_high) / 2
    exercise_loss_ml = sweat_per_hour_avg * training_hours
    
    # ── 3. Sıcaklık Faktörü (Öğle Antrenmanı) ──
    # Öğle saati (10:00-14:00) → +%15
    heat_bonus_ml = 0
    if "Öğle" in str(training_time):
        heat_bonus_ml = exercise_loss_ml * 0.15
        exercise_loss_ml += heat_bonus_ml
    
    # ── 4. Kafein Düzeltmesi ──
    # 3+ fincan → +300 ml (diüretik etki kompanzasyonu)
    caffeine_extra_ml = 0
    if caffeine == "3+ fincan/gün":
        caffeine_extra_ml = 300
    
    # ── 5. Toplam Günlük Su İhtiyacı ──
    total_ml = basal_ml + exercise_loss_ml + caffeine_extra_ml
    
    # ── 6. Antrenman Öncesi Hidrasyon (ACSM) ──
    # Antrenmandan 2-3 saat önce: 5-7 ml/kg
    pre_training_ml_low = weight * 5
    pre_training_ml_high = weight * 7
    
    # ── 7. Antrenman Sonrası Replasman ──
    # Kayıp × 1.5, 4 saat içine yayarak (NSCA)
    post_training_total_ml = exercise_loss_ml * 1.5
    post_training_per_hour_ml = post_training_total_ml / 4 if post_training_total_ml > 0 else 0
    
    # ── 8. Elektrolit / Hiponatremi Uyarısı ──
    # Uzun mesafe veya günlük antrenman > 90 dk → sodyum uyarısı
    endurance_keywords = ["Maraton", "Ultra", "Gran Fondo", "100K", "70.3", "Ironman"]
    is_long_endurance = any(k in str(target_distance) for k in endurance_keywords)
    needs_electrolyte = is_long_endurance or (training_hours > 1.5)
    
    # Kayıp litre başına 500-700 mg sodyum
    electrolyte_sodium_mg = 0
    if needs_electrolyte:
        lost_liters = exercise_loss_ml / 1000
        electrolyte_sodium_mg = round(lost_liters * 600)  # orta değer 600 mg/L
    
    return {
        "basal_ml": round(basal_ml),
        "exercise_loss_ml": round(exercise_loss_ml),
        "heat_bonus_ml": round(heat_bonus_ml),
        "caffeine_extra_ml": round(caffeine_extra_ml),
        "total_ml": round(total_ml),
        "total_L": round(total_ml / 1000, 1),
        "pre_training_ml": f"{round(pre_training_ml_low)}-{round(pre_training_ml_high)}",
        "post_training_total_ml": round(post_training_total_ml),
        "post_training_per_hour_ml": round(post_training_per_hour_ml),
        "needs_electrolyte": needs_electrolyte,
        "electrolyte_sodium_mg": electrolyte_sodium_mg,
        "sweat_per_hour_avg": round(sweat_per_hour_avg),
    }


def get_athlete_nutrition(profile):
    """
    Main function to calculate comprehensive athlete nutrition data.
    """
    bmr = calculate_bmr(
        profile['weight'], profile['height'], profile['age'],
        profile['gender'], profile.get('body_fat', 0)
    )
    
    # Determine which BMR formula was used
    bmr_formula = "Katch-McArdle" if profile.get('body_fat', 0) and profile.get('body_fat', 0) > 0 else "Mifflin-St Jeor"
    
    intensity = profile.get('intensity', "Orta")
    activity_factor = calculate_activity_factor(profile['training_days'], profile['training_hours'], intensity)
    
    tdee = bmr * activity_factor
    
    # Goal-based caloric adjustment (physiologically safe ranges)
    goal = profile['goal']
    if goal == "Kilo Verme (Yağ Yakımı)":
        deficit = 400  # 300-500 range, use moderate 400
        target_calories = tdee - deficit
    elif goal == "Kas Gelişimi":
        surplus = 350  # 300-500 range, use moderate 350
        target_calories = tdee + surplus
    else:
        target_calories = tdee  # Isocaloric
        
    # Minimum safe calories
    if profile['gender'] == "Kadın" and target_calories < 1200:
        target_calories = 1200
    elif profile['gender'] == "Erkek" and target_calories < 1500:
        target_calories = 1500
        
    avg_daily_hours = (profile['training_days'] * profile['training_hours']) / 7
    target_distance = profile.get('target_distance', 'Belirtilmedi')
    
    macros = calculate_macros(
        profile['weight'], profile['sport_type'], goal,
        avg_daily_hours, target_calories, target_distance
    )
    
    # Full hydration calculation (ACSM/NSCA)
    hydration = calculate_hydration(profile)
    
    return {
        "bmr": round(bmr),
        "bmr_formula": bmr_formula,
        "tdee": round(tdee),
        "target_calories": round(target_calories),
        "activity_factor": round(activity_factor, 2),
        "hydration_L": hydration["total_L"],
        "hydration": hydration,
        "macros": macros
    }
