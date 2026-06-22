import time
from config import MANO_AKCIJOS, CHECK_INTERVAL
from price_fetcher import gauti_kaina_ir_pokyti
from telegram_sender import siusti_telegram, gauti_paskutine_komanda
from state_manager import uzkrauti_busena, issaugoti_busena
import logging

logging.basicConfig(level=logging.INFO, filename="programos_logai.log", filemode="a", format="%(asctime)s - %(levelname)s - %(message)s")
logging.info("Programa pradėta")

def formatuoti_pokyti(pokytis):
    if pokytis is None:
        return "N/A"
    return f"{pokytis} USD"

def sugeneruoti_statuso_zinute():
    eilutes = ["📊 Dabartinis akcijų statusas:"]
    for simbolis, riba in MANO_AKCIJOS.items():
        try:
            kaina, pokytis = gauti_kaina_ir_pokyti(simbolis)
            eilutes.append(
                f"{simbolis}: {kaina} USD | riba: {riba} USD | pokytis: {formatuoti_pokyti(pokytis)}"
            )
        except Exception as e:
            eilutes.append(f"{simbolis}: klaida ({e})")
            logging.error("Klaida siunciant zinute i Telegram: %s", e)
    return "\n".join(eilutes)

def main():
    print("Programa pradėta. Pradedamas ciklas...\n")
    busena = uzkrauti_busena()
    paskutinis_update_id = None

    while True:
        print(f"[{time.strftime('%H:%M:%S')}] Pradedamas naujas patikrinimas...")

    
        komanda, update_id = gauti_paskutine_komanda(
            None if paskutinis_update_id is None else paskutinis_update_id + 1
        )
        if update_id is not None:
            paskutinis_update_id = update_id

        if komanda == "/status":
            statuso_zinute = sugeneruoti_statuso_zinute()
            siusti_telegram(statuso_zinute)

        # 2) Įprastas alert tikrinimas
        for simbolis, norima_riba in MANO_AKCIJOS.items():
            try:
                dabartine_kaina, pokytis = gauti_kaina_ir_pokyti(simbolis)
                buvo_zemiau = busena.get(simbolis, False)
                yra_zemiau = dabartine_kaina <= norima_riba

                if yra_zemiau and not buvo_zemiau:
                    zinute = (
                        f"🔥 DĖMESIO! {simbolis} kaina: {dabartine_kaina} USD\n"
                        f"Tavo riba: {norima_riba} USD\n"
                        f"Pokytis nuo atidarymo: {formatuoti_pokyti(pokytis)}"
                    )
                    print(zinute)
                    siusti_telegram(zinute)
                    busena[simbolis] = True
                elif not yra_zemiau and buvo_zemiau:
                    print(f"✅ {simbolis} pakilo virš ribos: {dabartine_kaina} USD")
                    busena[simbolis] = False
                else:
                    status = "🔴 ŽEMIAU ribos" if yra_zemiau else "🟢 Virš ribos"
                    print(
                        f"{status} {simbolis}: {dabartine_kaina} USD | "
                        f"riba: {norima_riba} USD | pokytis: {formatuoti_pokyti(pokytis)}"
                    )
            except Exception as e:
                print(f"❌ Klaida tikrinant {simbolis}: {e}")
                logging.error("Klaida tikrinant %s: %s", simbolis, e)

        issaugoti_busena(busena)
        time.sleep(CHECK_INTERVAL)
        if CHECK_INTERVAL < 10:
            print("⚠️ CHECK_INTERVAL yra mažas, įsitikinkite, kad tai neperkraus API!")
        print("--------------------------------------")

if __name__ == "__main__":
    main()