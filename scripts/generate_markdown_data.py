import os
from pathlib import Path

# Hedef klasör (RAG verilerinin toplanacağı yer)
DATA_DIR = Path("D:/athlete_nutrition_app/data/raw_papers_md")

def create_knowledge_base():
    """
    Sporcu beslenmesi (ISSN / ACSM) alanındaki kritik makalelerin özetlenmiş,
    yapılandırılmış Markdown verilerini oluşturur.
    Bu veriler Pinecone vektör veritabanına beslendiğinde RAG sistemi
    çok daha yüksek bir isabetle çalışacaktır.
    """
    
    if not DATA_DIR.exists():
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        print(f"📁 {DATA_DIR} oluşturuldu.")

    papers = [
        {
            "filename": "ISSN_Position_Stand_Carbohydrates.md",
            "content": """# ISSN Position Stand: Carbohydrates for Training and Performance
            
## General Guidelines
- Athletes should consume 5-12 g/kg/body weight of carbohydrates per day depending on the sport, training volume, and goal.
- For light training (low intensity, skill-based): 3-5 g/kg/day.
- For moderate training (1 hour/day): 5-7 g/kg/day.
- For high training (endurance programs, 1-3 hours/day): 6-10 g/kg/day.
- For extreme commitment (moderate to high intensity, >4-5 hours/day): 8-12 g/kg/day.

## Pre-Exercise Carbohydrates
- Consume 1-4 g/kg of carbohydrates 1 to 4 hours prior to exercise to maximize muscle and liver glycogen stores.

## During Exercise Carbohydrates
- For exercise < 45 minutes: Not needed.
- For sustained high-intensity exercise (45-75 min): Small amounts including mouth rinse.
- For endurance and stop-and-go sports (1-2.5 hours): 30-60 g/hour.
- For ultra-endurance (>2.5 - 3 hours): Up to 90 g/hour of multiple transportable carbohydrates (e.g., glucose + fructose).

## Post-Exercise Recovery
- Rapid recovery requires 1.0-1.2 g/kg/hour of carbohydrates consumed every hour for the first 4-6 hours post-exercise.
- Adding protein (0.2-0.5 g/kg) to carbohydrates can improve glycogen synthesis and promote muscle repair.
"""
        },
        {
            "filename": "ISSN_Position_Stand_Protein.md",
            "content": """# ISSN Position Stand: Protein and Exercise
            
## General Guidelines
- For building and maintaining muscle mass, an overall daily protein intake in the range of 1.4-2.0 g/kg body weight/day (g/kg/d) is sufficient for most exercising individuals.
- Higher protein intakes (2.3-3.1 g/kg/d) may be needed to maximize the retention of lean body mass in resistance-trained subjects during hypocaloric periods (weight loss).

## Protein Timing
- Doses should ideally be evenly distributed, every 3-4 hours, across the day.
- A single dose should contain 20-40 g of protein (or 0.25-0.40 g/kg/dose).
- Pre-sleep protein ingestion (30-40 g of casein) provides an increase in overnight muscle protein synthesis and metabolic rate.

## Protein Quality
- Athletes should focus on whole food sources that contain all essential amino acids (EAAs), particularly leucine (700-3000 mg per dose).
- Examples include whey, casein, egg, meat, and soy. For vegetarians/vegans, a mix of plant proteins (pea, rice, hemp) is required to get a complete amino acid profile.
"""
        },
        {
            "filename": "ACSM_Hydration_and_Sweat.md",
            "content": """# ACSM Position Stand: Exercise and Fluid Replacement
            
## Pre-hydration
- The goal of prehydrating is to start the activity euhydrated. If normally hydrated, drinking fluids (e.g., 5-7 mL/kg) at least 4 hours prior to exercise is recommended.
- If urine is dark or highly concentrated, drink another 3-5 mL/kg 2 hours before the event.

## During Exercise Hydration
- The aim is to prevent excessive dehydration (>2% body weight loss from water deficit).
- Sweat rates can vary from 0.3 L/h to >2.4 L/h depending on the sport, intensity, and environment.
- Athletes with "High" or "Excessive" sweat rates (salty sweaters leaving white stains on clothes) must consume beverages containing sodium (20-30 mEq/L) to prevent hyponatremia.
- Carbohydrates (5-10% solution) should be included in fluids if exercise exceeds 1 hour.

## Post-Exercise Rehydration
- If rapid recovery is needed (< 24 h between sessions), consume ~1.5 L (1500 mL) of fluid for every 1 kg of body weight lost during the session.
- Sodium must be included in the recovery fluid or food to retain the ingested water.
"""
        },
        {
            "filename": "Nutritional_Strategies_for_Different_Sports.md",
            "content": """# Dietary Strategies Specific to Sport Types
            
## Runners (Marathon / Ultra / 10K)
- Focus is on extremely high carbohydrate availability.
- Carbohydrate loading (8-10 g/kg/day) 36-48 hours before the race is critical.
- Ultra runners must balance solid foods and liquids to avoid gastrointestinal distress while hitting 60-90 g carbs/hour during the race.

## Swimmers
- Frequent training (often 2-a-days) requires constant glycogen replenishment.
- Swimmers often struggle to eat right before morning sessions. Recommend liquid carbs (sports drinks, gels) or easily digestible carbs (banana, toast) 30 mins prior.
- High training volume necessitates 6-8 g/kg/day of carbohydrates.

## Cyclists (Gran Fondo / Road Racing)
- Cycling allows for easier consumption of solid foods and fluids compared to running.
- During long events, solid food (rice cakes, energy bars, bananas) is preferred early, switching to liquids and gels in the later, higher-intensity stages.

## Triathletes (Ironman / 70.3)
- Must train the gut to handle massive caloric intakes (up to 400 kcal/hour).
- Most nutrition is taken on the bike leg as the stomach is stable.
- The run leg relies heavily on Coke, gels, and water as the stomach cannot tolerate solid foods.
"""
        },
        {
            "filename": "Sleep_and_Menstrual_Cycle_Impact.md",
            "content": """# Impact of Sleep and Menstrual Cycle on Nutrition
            
## Sleep Deprivation Impact (5-6 hours or less)
- Increases cortisol, which catabolizes muscle. Protein intake should be skewed slightly higher (e.g. +0.2 g/kg).
- Decreases insulin sensitivity, so complex carbohydrates are favored over simple sugars when not immediately pre/post workout.
- Causes cravings for high-fat/high-sugar foods. Satiety-promoting meals (high fiber, high protein) are essential.

## Menstrual Cycle Nutrition (Female Athletes)
- Follicular Phase (Days 1-14): Higher estrogen, better insulin sensitivity. Body is primed to use carbohydrates for high-intensity work. Carbohydrate loading is more effective here.
- Luteal Phase (Days 15-28): Higher progesterone. Basal body temperature rises. Body relies more on fat oxidation and less on carbs. Sweat rate and core temp increase, requiring aggressive hydration protocols. Sodium and fluid needs increase. Iron needs may increase due to menstruation.
"""
        }
    ]

    for paper in papers:
        file_path = DATA_DIR / paper["filename"]
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(paper["content"])
        print(f"✅ Oluşturuldu: {paper['filename']}")

    print("\n🎉 Tüm kaliteli beslenme verileri Markdown (.md) formatında hazırlandı!")

if __name__ == "__main__":
    create_knowledge_base()
