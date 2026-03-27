from flask import Flask, render_template, request, jsonify
import threading
import time
from arama_sayfası import AramaSayfasi 
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import traceback

app = Flask(__name__)

bot_aktif = False
bot_loglari = []

def log_ekle(mesaj):
    global bot_loglari
    zaman = time.strftime("%H:%M:%S")
    bot_loglari.append(f"[{zaman}] {mesaj}")
    if len(bot_loglari) > 50: bot_loglari.pop(0)

def bot_calistir(kalkis, varis, t_gidis, t_donus, v_gidis, v_donus, email):
    global bot_aktif
    log_ekle("🚀 Sistem aktif edildi. Bot nöbete başlıyor...")
    
    while bot_aktif:
        try:
            log_ekle(f"🕵️ Tarama Başladı: {kalkis} -> {varis}")
            
            
            chrome_options = Options()
            
            driver = webdriver.Chrome(options=chrome_options)
            
            arama = AramaSayfasi(driver)
            driver.get("https://ebilet.tcddtasimacilik.gov.tr/")
            time.sleep(2)
            
            
            arama.bilet_sorgula(kalkis, varis, t_gidis, t_donus, 1, v_gidis, v_donus, email, log_ekle)
            
        except Exception as e:
            log_ekle(f"⚠️ Dongu Hatası: {str(e)}")
            print(traceback.format_exc())
            
            try: driver.quit() 
            except: pass
            
       
        if bot_aktif:
            log_ekle("😴 Fırsat kollanıyor... Sonraki tarama 2 dakika sonra.")
            for _ in range(120):
                if not bot_aktif: break
                time.sleep(1)
                
    log_ekle("🛑 Sistem tamamen durduruldu.")

@app.route('/')
def ana_sayfa(): 
    return render_template('index.html')

@app.route('/get_logs')
def get_logs(): 
    return jsonify(bot_loglari)

@app.route('/sorgula', methods=['POST'])
def sorgula():
    global bot_aktif, bot_loglari
    if bot_aktif: return jsonify({"mesaj": "Bot zaten aktif!"})
    
    v = request.json
    bot_loglari = [] 
    bot_aktif = True
    
    
    threading.Thread(target=bot_calistir, args=(
        v['kalkis'], v['varis'], v['t_gidis'], v['t_donus'], v['v_gidis'], v['v_donus'], v['email']
    )).start()
    
    return jsonify({"mesaj": "Bilet Avcısı Nöbete Başladı!"})

@app.route('/durdur', methods=['POST'])
def durdur():
    global bot_aktif
    bot_aktif = False
    return jsonify({"mesaj": "Durduruluyor..."})

if __name__ == '__main__':
    app.run(debug=True, port=5000)