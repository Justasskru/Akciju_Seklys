import yfinance as yf
import time 
import requests
import sys
import logging

logging.basicConfig(level=logging.INFO, filename="programos_logai.log", filemode="a", format="%(asctime)s - %(levelname)s - %(message)s")
logging.info("Programa pradėta")


TOKEN = "7887940869:AAHiGI6QYuRWy_QCr5ewCvkwa1lPCM-VrwI"
CHAT_ID = "6749079167"


mano_akcijos = {
    "AAPL": 245.0,
    "TSLA": 340.0,
    "MSFT": 350.0,
    "GOOGL": 300.0,
    "NVDA": 700.0,
    "AMZN": 240.0
}

laukimo_laikas = 3600

def pranesk_i_telegram(zinute):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={zinute}"
    try:
        requests.get(url)
    except Exception as e:
        print(f"Nepavyko išsiųsti žinutės į Telegram: {e}")
        logging.error("Klaida siunciant zinute i Telegram: %s", e)


 
while True:
    print(f"\n[{time.strftime('%H:%M:%S')}] Pradedamas naujas patikrinimas...")
    
   
    for simbolis, norima_riba in mano_akcijos.items():
        try:
            akcija = yf.Ticker(simbolis)
            atidarymo_kaina = akcija.info['regularMarketOpen']
            dabartine_kaina = round(akcija.fast_info['last_price'], 2)
            pokytis = round(dabartine_kaina - atidarymo_kaina, 2)
            if dabartine_kaina <= norima_riba:
                pranesimas = f"🔥 DĖMESIO! {simbolis} kaina gera: {dabartine_kaina} USD (tavo riba: {norima_riba}) Pokytis nuo atidarymo: {pokytis}"
                print(pranesimas)
                pranesk_i_telegram(pranesimas)
            
            else:
                print(f"👀 {simbolis}: {dabartine_kaina} USD (riba: {norima_riba} Pokytis nuo atidarymo: {pokytis})")
                pranesimas2 = f"👀 {simbolis}: {dabartine_kaina} USD (riba: {norima_riba}) Pokytis nuo atidarymo: {pokytis}"
                pranesk_i_telegram(pranesimas2)
                
        
        except Exception as e:
            print(f"❌ Klaida tikrinant {simbolis}: {e}")
            logging.error("Klaida tikrinant %s: %s", simbolis, e)
            #-----------------------------------------------------------------
    print("--------------------------------------")
    #Užklausa vartotojui, ar nori tęsti laukimą ar nutraukti programą
    print(f"Ka norite daryti ?")
    print("1. Laukti iki kito patikrinimo")
    print("2. Nutraukti programą")
    pasirinkimas = input("Įveskite 1 arba 2: ")
    if pasirinkimas == "2":
        print("Programa nutraukiama...")
        break
    elif pasirinkimas != "1":
        print("Neteisingas pasirinkimas, tęsiama laukimo režimu...")
        #-----------------------------------------------------------------
 
    for liko in range(laukimo_laikas, 0, -1):
        mins, seks = divmod(liko, 60)
        sys.stdout.write(f"\rLiko iki kito patikrinimo: {mins:02d}:{seks:02d} ")
        sys.stdout.flush()
        time.sleep(1)
    
   