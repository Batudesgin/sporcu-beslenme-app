def calculate_bmr(weight, height, age, gender, body_fat=0):
    """
    Calculates Basal Metabolic Rate using Cunningham (if body fat > 0)
    or Mifflin-St Jeor equation.
    """
    if body_fat and body_fat > 0:
        lbm = weight * (1 - (body_fat / 100))
        return 500 + (22 * lbm)
    
    if gender == "Erkek":
        return (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:
        return (10 * weight) + (6.25 * height) - (5 * age) - 161

def calculate_activity_factor(training_days, training_hours, intensity="Orta"):
    """
    Determines activity multiplier based on training frequency, duration, and intensity.
    """
    avg_daily_hours = (training_days * training_hours) / 7
    
    # Base factor on hours
    if avg_daily_hours < 0.5:
        factor = 1.375 # Light
    elif avg_daily_hours <= 1.0:
        factor = 1.55 # Moderate
    elif avg_daily_hours <= 2.0:
        factor = 1.725 # Heavy
    else:
        factor = 1.9 # Very Heavy
        
    # Adjust for intensity
    if intensity == "Yüksek (Interval / Yarış temposu)":
        factor += 0.1
    elif intensity == "Düşük":
        factor -= 0.1
        if factor < 1.2:
            factor = 1.2
            
    return factor

def calculate_macros(weight, sport_type, goal, avg_daily_hours, total_calories):
    """
    Calculates macro distribution (Protein, Carbs, Fat) based on ISSN/ACSM guidelines.
    """
    # Base multiplier for protein
    protein_per_kg = 1.6
    
    if goal == "Kilo Verme (Yağ Yakımı)":
        protein_per_kg = 2.0 # Preserve muscle while in deficit
    elif goal == "Kas Gelişimi":
        protein_per_kg = 1.8
        
    # Carbs
    if sport_type in ["Koşucu", "Bisikletçi", "Triatloncu"]:
        if avg_daily_hours < 1.0:
            carbs_per_kg = 5.5
        elif avg_daily_hours <= 2.0:
            carbs_per_kg = 7.0
        else:
            carbs_per_kg = 9.0
    elif sport_type == "Fitness":
        protein_per_kg = max(protein_per_kg, 1.8)  # Fitness needs higher protein
        if avg_daily_hours < 1.0:
            carbs_per_kg = 4.0
        elif avg_daily_hours <= 2.0:
            carbs_per_kg = 5.0
        else:
            carbs_per_kg = 6.0
    else: # Yüzücü
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
    
    # Safety check: fat shouldn't be too low (< 0.8g/kg)
    if fat_g < (weight * 0.8):
        fat_g = weight * 0.8
        fat_kcal = fat_g * 9
        # Adjust carbs down
        carbs_kcal = total_calories - protein_kcal - fat_kcal
        carbs_g = carbs_kcal / 4
        
    return {
        "protein_g": round(protein_g),
        "carbs_g": round(carbs_g),
        "fat_g": round(fat_g),
        "total_kcal": round(total_calories)
    }

def get_athlete_nutrition(profile):
    """
    Main function to calculate comprehensive athlete nutrition data.
    """
    bmr = calculate_bmr(profile['weight'], profile['height'], profile['age'], profile['gender'], profile.get('body_fat', 0))
    intensity = profile.get('intensity', "Orta")
    activity_factor = calculate_activity_factor(profile['training_days'], profile['training_hours'], intensity)
    
    tdee = bmr * activity_factor
    
    # Adjust for goal
    if profile['goal'] == "Kilo Verme (Yağ Yakımı)":
        target_calories = tdee - 500
    elif profile['goal'] == "Kas Gelişimi":
        target_calories = tdee + 300
    else:
        target_calories = tdee
        
    # Minimum safe calories
    if profile['gender'] == "Kadın" and target_calories < 1200:
        target_calories = 1200
    elif profile['gender'] == "Erkek" and target_calories < 1500:
        target_calories = 1500
        
    avg_daily_hours = (profile['training_days'] * profile['training_hours']) / 7
    macros = calculate_macros(profile['weight'], profile['sport_type'], profile['goal'], avg_daily_hours, target_calories)
    
    # Calculate hydration based on weight (typically 35ml per kg base + extra for training)
    hydration_L = (profile['weight'] * 0.035) + (avg_daily_hours * 0.5)
    
    return {
        "bmr": round(bmr),
        "tdee": round(tdee),
        "target_calories": round(target_calories),
        "activity_factor": round(activity_factor, 2),
        "hydration_L": hydration_L,
        "macros": macros
    }
