from selenium import webdriver
from selenium.webdriver.chrome.service import Service
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

print("-"*21)
yolcu_giris=input("👥 Yolcu Sayısı (Sadece sayı girin, Örn: 1, 2, 3) [Varsayılan 1]:")
yolcu_sayısı=int(yolcu_giris) if yolcu_giris.strip() else 1


print("-"*25)
print("💺 Vagon Tipleri: EKONOMİ, BUSİNESS, LOCA, TEKERLEKLİ SANDALYE")
gidis_vagon = input("💺Gidiş Vagon Tipi (Örn: EKONOMİ): ").upper() or "EKONOMİ"
donus_vagon=None
if yolculuk_tipi=="2":
    donus_vagon=input("💺Dönüş Vagon Tipi (Örn: EKONOMİ): ").upper() or "EKONOMİ"

print("*" * 40)
print("🚆 Tarayıcı açılıyor, lütfen bekle...")


driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.maximize_window()

try:
   
    driver.get("https://ebilet.tcddtasimacilik.gov.tr")
    
    
    arama = AramaSayfasi(driver)
    arama.bilet_sorgula(kalkis, varis, gidis_zamani, donus_zamani,yolcu_sayısı,gidis_vagon,donus_vagon)
    
    print("✅ Bot görevini yaptı! Ekrandaki biletleri inceleyebilirsin.")
    time.sleep(600)  # Tarayıcıyı 10 dakika açık tut
    
except Exception as e:
    print(f"❌ Hata oluştu: {e}")