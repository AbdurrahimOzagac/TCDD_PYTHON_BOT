from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from base_page import BasePage
from bildirim_sistemi import mail_gonder, ses_cal
import time
import traceback

class AramaSayfasi(BasePage):
    # TCDD ELEMENTLER
    GIDIS_DONUS_RADYO = (By.XPATH, "//label[contains(., 'Gidiş - Dönüş')] | //label[contains(., 'Gidiş-Dönüş')]")
    KALKIS_INPUT = (By.XPATH, "//input[contains(@placeholder, 'Nereden') or contains(@name, 'Tren kalkış') or @id='departure']")
    VARIS_INPUT = (By.XPATH, "//input[contains(@placeholder, 'Nereye') or contains(@name, 'Tren varış') or @id='arrival']")
    SORGULA_BUTONU = (By.ID, "searchSeferButton")
    GIDIS_TARIHI_KUTUSU = (By.CLASS_NAME, "datePickerInput.departureDate")
    GIDIS_TARIHI_INPUT = (By.XPATH, "//input[contains(@placeholder, 'Gidiş')]")
    TAKVIM_ILERI_BTN = (By.CSS_SELECTOR, "th.next.available")
    
    YOLCU_KUTUSU = (By.XPATH, "//input[@selenium-test='passenger']")
    YOLCU_UYGULA_BUTONU = (By.XPATH, "//button[@selenium-test='passenger-btn']")

    def bilet_sorgula(self, nereden, nereye, gidis_tarihi, donus_tarihi, yolcu, v_g, v_d, email, logger, saat_baslangic=None, saat_bitis=None):
        wait = WebDriverWait(self.driver, 15)
        actions = ActionChains(self.driver)
        
        # Bulunan biletler
        bulunan_biletler_raporu = {"GİDİŞ": [], "DÖNÜŞ": []}
        bulundu = False
        
        try:
            logger("⚙️ İşlem Başlatıldı: TCDD BOTU ÇALIŞIYOR")
            time.sleep(2)
            self._popuplari_temizle()

            if donus_tarihi:
                logger("🔄 Seçim Modu: Gidiş - Dönüş aktif ediliyor.")
                try:
                    btns = wait.until(EC.presence_of_all_elements_located(self.GIDIS_DONUS_RADYO))
                    if btns: self.driver.execute_script("arguments[0].click();", btns[0])
                    time.sleep(1)
                except: pass

            logger(f"📍 Rota Çiziliyor: {nereden} ➔ {nereye}")
            self._sehir_doldur(nereden, self.KALKIS_INPUT, "gidis", logger)
            self._sehir_doldur(nereye, self.VARIS_INPUT, "donus", logger)

            logger("📅 Takvim modülüne seçiliyor...")
            self.driver.execute_script("window.scrollBy(0, 200);")
            time.sleep(1.5) 
            
            try:
                wait.until(EC.element_to_be_clickable(self.GIDIS_TARIHI_KUTUSU)).click()
            except:
                kutular = self.driver.find_elements(*self.GIDIS_TARIHI_INPUT)
                if kutular: self.driver.execute_script("arguments[0].click();", kutular[0])
            time.sleep(1.5) 
            
            logger(f"⏳ Gidiş tarihi aranıyor: {gidis_tarihi}")
            gidis_elementi = self._tarih_elementini_bul(gidis_tarihi, logger)
            actions.move_to_element(gidis_elementi).click().perform() 
            time.sleep(1)
            
            if donus_tarihi: 
                logger(f"⏳ Dönüş aranıyor: {donus_tarihi}")
                donus_elementi = self._tarih_elementini_bul(donus_tarihi, logger)
                actions.move_to_element(donus_elementi).pause(0.5).click().perform() 
                time.sleep(1)

         
            self._yolcu_ayarla(logger, actions)

            logger("🚀 'Sefer Ara' butonuna tıklanım başlatılıyor...")
            try: 
                self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                time.sleep(0.8)
            except: pass

            s_btn = wait.until(EC.presence_of_element_located(self.SORGULA_BUTONU))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", s_btn)
            time.sleep(1.5)
            try: actions.move_to_element(s_btn).click().perform() 
            except: self.driver.execute_script("arguments[0].click();", s_btn)

            logger("⏳ TCDD Sefer Arama devrede (Maksimum 30 sn beklenecek)...")
            wait_long = WebDriverWait(self.driver, 30)
            
            try:
                wait_long.until(EC.visibility_of_element_located((By.ID, "gidis0")))
                time.sleep(2)
                # gidiş bileti listele
                bulunan_biletler_raporu["GİDİŞ"] = self.vagon_filtrele("GİDİŞ", v_g, logger, saat_baslangic, saat_bitis)

                if donus_tarihi:
                    ilk_kart = self.driver.find_element(By.ID, "gidis0")
                    self.driver.execute_script("arguments[0].click();", ilk_kart.find_element(By.CLASS_NAME, "priceArea"))
                    time.sleep(1)
                    wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@selenium-test='btn-gidis0']"))).click()
                    
                    wait_long.until(EC.visibility_of_element_located((By.ID, "donus0")))
                    time.sleep(2)
                    # dönüş bileti liste
                    bulunan_biletler_raporu["DÖNÜŞ"] = self.vagon_filtrele("DÖNÜŞ", v_d, logger, saat_baslangic, saat_bitis)

            except Exception as e:
                self._hata_okuyucu(e, logger)

            # rapor ve mail yazdırma
            bulundu = self._raporu_yazdir_ve_mail_at(bulunan_biletler_raporu, donus_tarihi, email, logger)

        except Exception as genel_hata:
            logger(f"❌ SİSTEM ÇÖKTÜ: {str(genel_hata).splitlines()[0]}")
            print(traceback.format_exc())
        
        #tarayıcı kapat
        finally:
            logger("🧹 Başarıyla Bilet Verileri Çekildi. Tarayıcı bellekten temizleniyor...")
            try:
                self.driver.quit()
            except:
                pass
        return bulundu

 
    
    def _yolcu_ayarla(self, logger, actions):
        logger("👥 Yolcu menüsü prosedür gereği açılıp uygulanıyor...")
        wait = WebDriverWait(self.driver, 5)
        try:
            try: self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
            except: pass
            time.sleep(0.5)

            y_kutu = wait.until(EC.element_to_be_clickable(self.YOLCU_KUTUSU))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", y_kutu)
            time.sleep(1.5) 
            
            try: actions.move_to_element(y_kutu).click().perform() 
            except: self.driver.execute_script("arguments[0].click();", y_kutu) 
            time.sleep(1.0) 
            
            uygula_btn = wait.until(EC.element_to_be_clickable(self.YOLCU_UYGULA_BUTONU))
            actions.move_to_element(uygula_btn).perform()
            time.sleep(0.5)
            
            try: actions.click(uygula_btn).perform() 
            except: self.driver.execute_script("arguments[0].click();", uygula_btn)
                
            logger("✅ Yolcu menüsü onaylandı.")
            time.sleep(1)
        except Exception as e:
            logger(f"⚠️ Yolcu menüsü takıldı, atlanıyor! Hata: {str(e).splitlines()[0]}")

    def vagon_filtrele(self, tip, hedef_vagon, logger, saat_baslangic=None, saat_bitis=None):
        bulunanlar = []
        def normalize(t): return t.upper().replace('İ', 'I').replace('Ü', 'U').replace('Ö', 'O').strip()
        target = normalize(hedef_vagon)
        prefix = "gidis" if tip == "GİDİŞ" else "donus"
        kartlar = self.driver.find_elements(By.CSS_SELECTOR, f"div[id^='{prefix}']")

        if len(kartlar) == 0:
            return bulunanlar

        for i in range(len(kartlar)):
            try:
                kart = self.driver.find_element(By.ID, f"{prefix}{i}")
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", kart)
                time.sleep(0.3)

                f_kutusu = kart.find_element(By.CLASS_NAME, "priceArea")
                vagonlar = kart.find_elements(By.CLASS_NAME, "btnTicketType")
                
                if not vagonlar or not vagonlar[0].is_displayed():
                    self.driver.execute_script("arguments[0].click();", f_kutusu)
                    time.sleep(0.8)
                    vagonlar = kart.find_elements(By.CLASS_NAME, "btnTicketType")

                for v in vagonlar:
                    if target in normalize(v.text):
                        self.driver.execute_script("arguments[0].click();", v)
                        time.sleep(0.4)
                        
                        y = v.find_element(By.CLASS_NAME, "emptySeat").text.strip()
                        s = kart.find_elements(By.TAG_NAME, "time")[0].text.strip()
                        
                        if y != "0" and y != "":
                            if saat_baslangic and saat_bitis:
                                if not self._saat_araliginda_mi(s, saat_baslangic, saat_bitis):
                                    break  # Saat aralığı dışında, bu seferi atla
                            bulunanlar.append(f"Saat: {s} | Vagon: {target} | Boş Koltuk: {y}")
                        break

                self.driver.execute_script("arguments[0].click();", f_kutusu)
                time.sleep(0.4)
            except: continue
        return bulunanlar

    def _raporu_yazdir_ve_mail_at(self, rapor, donus_var_mi, email, logger):
        logger("\n" + "="*45)
        logger("🎫 TCDD BİLET TARAMA SONUÇ RAPORU 🎫")
        logger("="*45)
        
        bilet_bulundu_mu = False

      
        html_govde = """
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 20px; border-radius: 10px; border-top: 5px solid #6366f1; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                <h1 style="color: #6366f1; text-align: center; font-size: 28px;">🚨 BİLET BULUNDU! 🚨</h1>
                <p style="font-size: 16px; color: #333; text-align: center;">Zırhlı Bot TCDD sisteminde aradığınız kriterlere uygun biletler yakaladı!</p>
                <hr style="border: 1px solid #eee;">
        """

        # Gidiş Raporu
        logger("➡️ GİDİŞ SEFERLERİ:")
        if rapor["GİDİŞ"]:
            bilet_bulundu_mu = True
            html_govde += "<h2 style='color: #2980b9;'>➡️ GİDİŞ SEFERLERİ:</h2><ul>"
            for bilet in rapor["GİDİŞ"]:
                logger(f"  ✅ {bilet}")
                html_govde += f"<li style='font-size: 18px; padding: 5px; color: #27ae60;'><b>{bilet}</b></li>"
            html_govde += "</ul>"
        else:
            logger("  ❌ Uygun bilet bulunamadı.")

        # Dönüş Raporu
        if donus_var_mi:
            logger("\n⬅️ DÖNÜŞ SEFERLERİ:")
            if rapor["DÖNÜŞ"]:
                bilet_bulundu_mu = True
                html_govde += "<h2 style='color: #2980b9;'>⬅️ DÖNÜŞ SEFERLERİ:</h2><ul>"
                for bilet in rapor["DÖNÜŞ"]:
                    logger(f"  ✅ {bilet}")
                    html_govde += f"<li style='font-size: 18px; padding: 5px; color: #27ae60;'><b>{bilet}</b></li>"
                html_govde += "</ul>"
            else:
                logger("  ❌ Uygun bilet bulunamadı.")
        
        logger("="*45)

        # Mail Altı Hızlı Erişim Linki
        html_govde += """
                <hr style="border: 1px solid #eee;">
                <div style="text-align: center; margin-top: 20px;">
                    <a href="https://ebilet.tcddtasimacilik.gov.tr/" style="background-color: #6366f1; color: white; padding: 15px 25px; text-decoration: none; font-size: 18px; border-radius: 5px; display: inline-block;"><b>HEMEN BİLETİ AL</b></a>
                </div>
            </div>
        </body>
        </html>
        """

        # Eğer en az 1 bilet varsa HTML maili gönder
        if bilet_bulundu_mu:
            logger("🔔 BİLET BULUNDU! Ses uyarısı çalınıyor...")
            ses_cal()
            if email:
                logger("📧 Bulunan biletler HTML formatında mail olarak iletiliyor...")
                mail_gonder("🔥 ACİL FIRSAT! TCDD BOTU RAPORU", html_govde, email)

        return bilet_bulundu_mu

    def _tarih_elementini_bul(self, hedef, logger):
        t_id = hedef.replace(".", " ") 
        for_count = 0
        while for_count < 12: 
            gunler = self.driver.find_elements(By.XPATH, f"//span[@id='{t_id}']")
            for gun in gunler:
                if gun.is_displayed():
                    return gun 
            
            ileri_btn = self.driver.find_elements(*self.TAKVIM_ILERI_BTN)
            if ileri_btn and ileri_btn[0].is_displayed():
                self.driver.execute_script("arguments[0].click();", ileri_btn[0])
                time.sleep(1) 
            else:
                break
            for_count += 1
        raise Exception(f"{hedef} tarihi takvimde bulunamadı!")

    def _sehir_doldur(self, sehir, loc, btn_prefix, logger):
        wait = WebDriverWait(self.driver, 10)
        try:
            inp = wait.until(EC.presence_of_element_located(loc))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", inp)
            time.sleep(1) 
            self.driver.execute_script("arguments[0].value = '';", inp)
            inp.click()
            time.sleep(0.5)
            
            inp.send_keys(sehir)
            time.sleep(2) 
            
            hedef_btn = (By.CSS_SELECTOR, f"button[id^='{btn_prefix}-']")
            btns = self.driver.find_elements(*hedef_btn)
            if btns: 
                self.driver.execute_script("arguments[0].click();", btns[0])
                logger(f"✅ İstasyon kilitlendi: {sehir}")
            else:
                inp.send_keys(Keys.ENTER)
            time.sleep(1)
        except Exception as e:
            raise Exception(f"İstasyon Kutusu ({sehir}) aşılamadı!")

    def _popuplari_temizle(self):
        try:
            btns = self.driver.find_elements(By.XPATH, "//button[contains(translate(text(), 'KAPAT', 'kapat'), 'kapat') or contains(translate(text(), 'TAMAM', 'tamam'), 'tamam') or contains(@class, 'close')]")
            for b in btns:
                if b.is_displayed():
                    self.driver.execute_script("arguments[0].click();", b)
                    time.sleep(0.5)
        except: pass

    def _hata_okuyucu(self, e, logger):
        logger("⚠️ Seferler listelenmedi. Sistem uyarıları taranıyor...")
        try:
            uyari = self.driver.find_element(By.XPATH, "//*[@role='alert' or contains(@class, 'toast-message') or contains(@class, 'alert') or contains(translate(text(), 'BULUNAMADI', 'bulunamadı'), 'bulunamadı')]").text
            if uyari:
                logger(f"🛑 TCDD UYARISI: {uyari}")
            else:
                logger("❌ O güne ait sefer bulunamadı veya biletler henüz satışa açılmamış.")
        except:
            pass

    def _saat_araliginda_mi(self, saat_str, baslangic, bitis):
        """Verilen saat stringinin (HH:MM) belirtilen aralıkta olup olmadığını kontrol eder."""
        try:
            from datetime import datetime
            saat = datetime.strptime(saat_str.strip(), "%H:%M").time()
            bas  = datetime.strptime(baslangic.strip(), "%H:%M").time()
            bit  = datetime.strptime(bitis.strip(), "%H:%M").time()
            return bas <= saat <= bit
        except:
            return True  # Parse edilemeyen saati filtreden geçir