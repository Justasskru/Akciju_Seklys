import time
import logging

from config import MANO_AKCIJOS, CHECK_INTERVAL
from price_fetcher import gauti_kaina_ir_pokyti
from telegram_sender import siusti_telegram, gauti_paskutine_komanda
from state_manager import uzkrauti_busena, issaugoti_busena

logging.basicConfig(
    level=logging.INFO,
    filename="programos_logai.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.info("Programa pradėta")


def formatuoti_pokyti(pokytis):
    if pokytis is None:
        return "N/A"
    return f"{pokytis} USD"


def sugeneruoti_statuso_zinute(stocks):
    eilutes = ["📊 Dabartinis akcijų statusas:"]
    for simbolis, riba in stocks.items():
        try:
            kaina, pokytis = gauti_kaina_ir_pokyti(simbolis)
            eilutes.append(
                f"{simbolis}: {kaina} USD | riba: {riba} USD | pokytis: {formatuoti_pokyti(pokytis)}"
            )
        except Exception as e:
            eilutes.append(f"{simbolis}: klaida ({e})")
            logging.error("Klaida gaunant statusą %s: %s", simbolis, e)
    return "\n".join(eilutes)


def sugeneruoti_list_zinute(stocks):
    if not stocks:
        return "📭 Stebimų akcijų sąrašas tuščias."
    eilutes = ["📌 Stebimos akcijos ir ribos:"]
    for simbolis, riba in stocks.items():
        eilutes.append(f"- {simbolis}: {riba} USD")
    return "\n".join(eilutes)


def help_zinute():
    return (
        "🤖 Galimos komandos:\n"
        "/help - parodyti komandas\n"
        "/status - parodyti dabartines kainas\n"
        "/list - parodyti stebimų akcijų sąrašą\n"
        "/set SYMBOL RIBA - pakeisti ribą (pvz: /set AAPL 210)\n"
        "/add SYMBOL RIBA - pridėti akciją (pvz: /add TSLA 180)\n"
        "/remove SYMBOL - pašalinti akciją (pvz: /remove TSLA)\n"
        "/interval SEK - pakeisti intervalą sekundėmis (pvz: /interval 300)\n"
        "/show_interval - parodyti dabartinį intervalą"
    )


def apdoroti_komanda(komanda, stocks, check_interval, busena):
    if not komanda:
        return stocks, check_interval

    tekstas = komanda.strip()
    dalys = tekstas.split()
    cmd = dalys[0].lower()
    args = dalys[1:]

    if cmd == "/help":
        siusti_telegram(help_zinute())

    elif cmd == "/status":
        siusti_telegram(sugeneruoti_statuso_zinute(stocks))

    elif cmd == "/list":
        siusti_telegram(sugeneruoti_list_zinute(stocks))

    elif cmd == "/show_interval":
        siusti_telegram(f"⏱ Dabartinis tikrinimo intervalas: {check_interval} s")

    elif cmd == "/set":
        if len(args) != 2:
            siusti_telegram("Naudojimas: /set AAPL 210")
            return stocks, check_interval
        simbolis = args[0].upper()
        try:
            riba = float(args[1])
            if simbolis not in stocks:
                siusti_telegram(f"{simbolis} nėra sąraše. Naudok /add {simbolis} {riba}")
                return stocks, check_interval
            stocks[simbolis] = riba
            siusti_telegram(f"✅ Atnaujinta: {simbolis} riba -> {riba} USD")
            logging.info("Atnaujinta riba: %s -> %s", simbolis, riba)
        except ValueError:
            siusti_telegram("Riba turi būti skaičius. Pvz: /set AAPL 210")

    elif cmd == "/add":
        if len(args) != 2:
            siusti_telegram("Naudojimas: /add TSLA 180")
            return stocks, check_interval
        simbolis = args[0].upper()
        try:
            riba = float(args[1])
            stocks[simbolis] = riba
            if simbolis not in busena:
                busena[simbolis] = False
            siusti_telegram(f"✅ Pridėta: {simbolis} su riba {riba} USD")
            logging.info("Pridėta akcija: %s -> %s", simbolis, riba)
        except ValueError:
            siusti_telegram("Riba turi būti skaičius. Pvz: /add TSLA 180")

    elif cmd == "/remove":
        if len(args) != 1:
            siusti_telegram("Naudojimas: /remove TSLA")
            return stocks, check_interval
        simbolis = args[0].upper()
        if simbolis in stocks:
            del stocks[simbolis]
            if simbolis in busena:
                del busena[simbolis]
            siusti_telegram(f"🗑 Pašalinta: {simbolis}")
            logging.info("Pašalinta akcija: %s", simbolis)
        else:
            siusti_telegram(f"{simbolis} nerasta sąraše.")

    elif cmd == "/interval":
        if len(args) != 1:
            siusti_telegram("Naudojimas: /interval 300")
            return stocks, check_interval
        try:
            naujas = int(args[0])
            if naujas < 10:
                siusti_telegram("Intervalas turi būti bent 10 sekundžių.")
                return stocks, check_interval
            check_interval = naujas
            siusti_telegram(f"✅ Naujas intervalas: {check_interval} s")
            logging.info("Atnaujintas intervalas: %s", check_interval)
        except ValueError:
            siusti_telegram("Intervalas turi būti sveikas skaičius. Pvz: /interval 300")

    elif cmd == "/kill":
        siusti_telegram("🛑 Programa nutraukiama pagal komandą /kill")
        logging.info("Programa nutraukiama pagal komandą /kill")
        exit(0)
        
    return stocks, check_interval


def main():
    print("Programa pradėta. Pradedamas ciklas...\n")
    busena = uzkrauti_busena()
    paskutinis_update_id = None

    # Lokali (runtime) būsena - startuoja iš config
    stocks = dict(MANO_AKCIJOS)
    check_interval = int(CHECK_INTERVAL)

    while True:
        print(f"[{time.strftime('%H:%M:%S')}] Pradedamas naujas patikrinimas...")

        komanda, update_id = gauti_paskutine_komanda(
            None if paskutinis_update_id is None else paskutinis_update_id + 1
        )
        if update_id is not None:
            paskutinis_update_id = update_id

        stocks, check_interval = apdoroti_komanda(komanda, stocks, check_interval, busena)

        # Įprastas alert tikrinimas
        for simbolis, norima_riba in stocks.items():
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

        if check_interval < 10:
            print("⚠️ CHECK_INTERVAL yra mažas, įsitikinkite, kad tai neperkraus API!")
            logging.warning("Labai mažas intervalas: %s", check_interval)

        time.sleep(check_interval)


if __name__ == "__main__":
    main()