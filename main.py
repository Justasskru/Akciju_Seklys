import time
from config import MANO_AKCIJOS, CHECK_INTERVAL
from price_fetcher import gauti_kaina_ir_pokyti
from telegram_sender import siusti_telegram
from state_manager import uzkrauti_busena, issaugoti_busena

def formatuoti_pokyti(pokytis):
    if pokytis is None:
        return "N/A"
    return f"{pokytis} USD"

def main():
    print("Programa pradėta. Pradedamas ciklas...\n")
    

    busena = uzkrauti_busena()

    while True:
        print(f"[{time.strftime('%H:%M:%S')}] Pradedamas naujas patikrinimas...")

  
        for simbolis, norima_riba in MANO_AKCIJOS.items():
            try:
             
                dabartine_kaina, pokytis = gauti_kaina_ir_pokyti(simbolis)

             
                buvo_zemiau = busena.get(simbolis, False)
                yra_zemiau = dabartine_kaina <= norima_riba

                #
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
                    # Pakilo virš ribos — atrakini kitam alertui
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

       
        issaugoti_busena(busena)

       
        print("--------------------------------------")
        for liko in range(CHECK_INTERVAL, 0, -1):
            mins, seks = divmod(liko, 60)
            print(f"\rLiko iki kito patikrinimo: {mins:02d}:{seks:02d}", end="", flush=True)
            time.sleep(1)

        print()  

if __name__ == "__main__":
    main()