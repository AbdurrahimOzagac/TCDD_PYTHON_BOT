from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
from arama_sayfası import AramaSayfasi

print("*" * 40)
print("🚆 TCDD BİLET ARAMA BOTUNA HOŞ GELDİNİZ 🚆")
print("*" * 40)

print("\n--- Yolculuk Tipi ---")
print("1 - Sadece Gidiş")
print("2 - Gidiş & Dönüş")
yolculuk_tipi = input("Seçiminiz (1 veya 2): ")
print("-" * 21)

kalkis = input("Kalkış istasyonunu yazın (Örn: ANKARA GAR): ")
varis = input("Varış istasyonunu yazın (Örn: İSTANBUL(SÖĞÜTLÜÇEŞME)): ")
gidis_zamani = input("Gidiş tarihini yazın (Örn: 30.03.2026): ")

donus_zamani = None
if yolculuk_tipi == "2":
    donus_zamani = input("Dönüş Tarihini Yazınız (Örn: 05.04.2026): ")

print("-" * 21)
yolcu_giris = input("👥 Yolcu Sayısı (Sadece sayı girin, Örn: 1, 2, 3) [Varsayılan 1]: ")
yolcu_sayısı = int(yolcu_giris) if yolcu_giris.strip().isdigit() else 1

print("-" * 25)
print("💺 Vagon Tipleri: EKONOMİ, BUSİNESS, LOCA, TEKERLEKLİ SANDALYE")
gidis_vagon = input("💺 Gidiş Vagon Tipi (Örn: EKONOMİ): ").upper() or "EKONOMİ"
donus_vagon = None
if yolculuk_tipi == "2":
    donus_vagon = input("💺 Dönüş Vagon Tipi (Örn: EKONOMİ): ").upper() or "EKONOMİ"

print("-" * 35)
print("⏰ Saat Aralığı Filtresi (boş bırakılırsa tüm saatler taranır)")
saat_baslangic = input("   Başlangıç saati (Örn: 08:00): ").strip() or None
saat_bitis    = input("   Bitiş saati    (Örn: 14:00): ").strip() or None

print("-" * 35)
bekleme_giris = input("🔁 Bilet bulunamazsa kaç dakikada bir tekrar denensin? [Varsayılan: 3]: ").strip()
bekleme_dk = int(bekleme_giris) if bekleme_giris.isdigit() else 3

print("-" * 35)
email = input("📧 Bildirim e-postası (boş bırakılırsa mail gönderilmez): ").strip() or None

print("\n" + "*" * 40)
print("🤖 Bot başlatıldı! Bilet bulunana kadar tarayacak...")
print("*" * 40)

deneme = 1
while True:
    print(f"\n{'=' * 40}")
    print(f"🔁 Deneme #{deneme} — Tarayıcı açılıyor...")
    print(f"{'=' * 40}")

    driver = webdriver.Chrome(executable_path=ChromeDriverManager().install())
    driver.maximize_window()

    try:
        driver.get("https://ebilet.tcddtasimacilik.gov.tr")
        arama = AramaSayfasi(driver)
        bulundu = arama.bilet_sorgula(
            kalkis, varis, gidis_zamani, donus_zamani,
            yolcu_sayısı, gidis_vagon, donus_vagon,
            email, print, saat_baslangic, saat_bitis
        )

        if bulundu:
            print("\n✅ Bilet bulundu! Bot başarıyla tamamlandı.")
            break
        else:
            print(f"\n⏳ Uygun bilet bulunamadı. {bekleme_dk} dakika sonra tekrar denenecek...")
            time.sleep(bekleme_dk * 60)
            deneme += 1

    except Exception as e:
        print(f"❌ Hata oluştu: {e}")
        print(f"⏳ {bekleme_dk} dakika sonra tekrar denenecek...")
        time.sleep(bekleme_dk * 60)
        deneme += 1