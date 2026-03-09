import os
import sys
import PyPDF2
from pathlib import Path

# Add project root to sys.path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.rag_engine import add_knowledge_to_index

DATA_DIR = Path("D:/athlete_nutrition_app/data/raw_papers_md")

def chunk_text(text, chunk_size=1000, overlap=200):
    """
    Kapsamlı metinleri (makaleleri) OpenAI embedding modelinin sınırlarına 
    ve anlam bütünlüğüne uygun şekilde parçalara (chunk) böler.
    """
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = min(start + chunk_size, text_length)
        
        # Anlam bütünlüğünü korumak için cümlenin ortasında kesmemeye çalış
        if end < text_length:
            # Geriye doğru ilk noktayı bul (en fazla 100 karakter geriye git)
            last_period = text.rfind('.', start, end)
            if last_period != -1 and (end - last_period) < 100:
                end = last_period + 1
                
        chunk = text[start:end].strip()
        if len(chunk) > 50: # Çok kısa (boş) parçaları alma
            chunks.append(chunk)
            
        start = end - overlap
        
    return chunks

def extract_text_from_file(file_path):
    """
    Verilen Markdown veya TXT dosyasındaki metni okur ve döndürür.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Hata! {file_path.name} okunamadı: {e}")
        return ""

def main():
    if not DATA_DIR.exists():
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        print(f"📁 {DATA_DIR} klasörü oluşturuldu. Lütfen .md veya .txt makalelerinizi bu klasöre kopyalayın ve betiği tekrar çalıştırın.")
        return

    # PDF yerine .md ve .txt dosyalarını ara
    md_files = list(DATA_DIR.glob("*.md"))
    txt_files = list(DATA_DIR.glob("*.txt"))
    all_files = md_files + txt_files
    
    if not all_files:
        print(f"⚠️ {DATA_DIR} klasöründe hiç metin dosyası bulunamadı.")
        return
        
    print(f"Toplam {len(all_files)} adet Markdown/Text makale bulundu. Pinecone veritabanına yükleme başlıyor...\n")
    
    success_count = 0
    
    for file_path in all_files:
        print(f"⏳ İşleniyor: {file_path.name}...")
        
        # 1. Metni çıkart
        text = extract_text_from_file(file_path)
        if not text:
            print(f"❌ {file_path.name} boş veya okunamadı, atlanıyor.")
            continue
            
        # 2. Chunk'lara böl
        chunks = chunk_text(text)
        print(f"   -> Toplam {len(chunks)} anlamlı parçaya bölündü.")
        
        # 3. Embedding (OpenAI) ve Vectordb'ye yükle (Pinecone)
        source_name = file_path.stem.replace(" ", "_")
        success = add_knowledge_to_index(chunks, source_name)
        
        if success:
            print(f"✅ {file_path.name} başarıyla veritabanına eklendi!")
            success_count += 1
        else:
            print(f"❌ {file_path.name} veritabanına yüklenirken hata oluştu.")
            
    print(f"\n🎉 İşlem Tamamlandı! {success_count}/{len(all_files)} makale Pinecone (Yapay Zeka Hafızası) üzerine kaydedildi.")

if __name__ == "__main__":
    main()
