import time
import logging
import requests
import sys
import threading
from typing import Optional

from config import TELEGRAM_TOKEN
from price_fetcher import gauti_kaina_ir_pokyti
from telegram_sender import siusti_telegram, gauti_update
from state_manager import uzkrauti_busena, issaugoti_busena
from settings_manager import load_settings, save_settings

logging.basicConfig(
    level=logging.INFO,
    filename="programos_logai.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.info("Programa pradėta")


def rodyti_countdown(sekundes, stop_event: Optional[threading.Event] = None):
    try:
        sekundes = int(sekundes)
    except (TypeError, ValueError):
        print("\n⚠️ Neteisingas intervalas countdown funkcijai.")
        return

    if sekundes <= 0:
        print("\n⚠️ Intervalas turi būti > 0.")
        return

    for liko in range(sekundes, 0, -1):
        if stop_event and stop_event.is_set():
            print("\n🛑 Gauta stop komanda. Countdown stabdomas.")
            return
        mins, seks = divmod(liko, 60)
        sys.stdout.write(f"\rLiko iki kito patikrinimo: {mins:02d}:{seks:02d}")
        sys.stdout.flush()
        time.sleep(1)

    sys.stdout.write("\rLiko iki kito patikrinimo: 00:00\n")
    sys.stdout.flush()


def gauti_paskutini_update_id():
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    try:
        r = requests.get(url, params={"timeout": 1}, timeout=5)
        r.raise_for_status()
        data = r.json()
        results = data.get("result", [])
        if not results:
            return None
        return results[-1]["update_id"]
    except Exception as e:
        logging.error("Nepavyko gauti paskutinio update_id: %s", e)
        return None


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
        "/show_interval - parodyti dabartinį intervalą\n"
        "/kill - nutraukti programą"
    )


def apdoroti_komanda(komanda, stocks, check_interval, busena, stop_event: Optional[threading.Event] = None):
    if not komanda:
        return stocks, check_interval

    tekstas = komanda.strip()
    dalys = tekstas.split()
    cmd = dalys[0].lower()
    args = dalys[1:]

    if cmd == "/help":
        siusti_telegram(help_zinute())
        logging.info("Išsiųsta pagalbos žinutė į Telegram")

    elif cmd == "/status":
        siusti_telegram(sugeneruoti_statuso_zinute(stocks))
        logging.info("Išsiųstas dabartinis statusas į Telegram")

    elif cmd == "/list":
        siusti_telegram(sugeneruoti_list_zinute(stocks))
        logging.info("Išsiųstas akcijų sąrašas į Telegram")

    elif cmd == "/show_interval":
        siusti_telegram(f"⏱ Dabartinis tikrinimo intervalas: {check_interval} s")
        logging.info("Išsiųstas dabartinis intervalas į Telegram")

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
            save_settings({"stocks": stocks, "check_interval": check_interval})
            siusti_telegram(f"✅ Atnaujinta: {simbolis} riba -> {riba} USD")
            logging.info("Atnaujinta riba: %s -> %s", simbolis, riba)
        except ValueError:
            logging.warning("Neteisinga riba keičiant akciją: %s", args[1])
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
            save_settings({"stocks": stocks, "check_interval": check_interval})
            issaugoti_busena(busena)
            siusti_telegram(f"✅ Pridėta: {simbolis} su riba {riba} USD")
            logging.info("Pridėta akcija: %s -> %s", simbolis, riba)
        except ValueError:
            logging.warning("Neteisinga riba pridedant akciją: %s", args[1])
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
            save_settings({"stocks": stocks, "check_interval": check_interval})
            issaugoti_busena(busena)
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
            save_settings({"stocks": stocks, "check_interval": check_interval})
            siusti_telegram(f"✅ Naujas intervalas: {check_interval} s")
            logging.info("Atnaujintas intervalas: %s", check_interval)
        except ValueError:
            logging.warning("Neteisingas intervalas: %s", args[0])
            siusti_telegram("Intervalas turi būti sveikas skaičius. Pvz: /interval 300")

    elif cmd == "/kill":
        siusti_telegram("🛑 Programa stabdoma pagal komandą /kill")
        logging.info("Programa stabdoma pagal komandą /kill")
        if stop_event:
            stop_event.set()
        else:
            raise SystemExit

    return stocks, check_interval


def run_bot(stop_event: Optional[threading.Event] = None):
    print("Programa pradėta. Pradedamas ciklas...\n")
    busena = uzkrauti_busena()

    settings = load_settings()
    stocks = settings["stocks"]
    check_interval = int(settings["check_interval"])

    paskutinis_update_id = gauti_paskutini_update_id()
    print(f"Start offset: {paskutinis_update_id}")
    logging.info("Start offset: %s", paskutinis_update_id)

    while True:
        if stop_event and stop_event.is_set():
            print("🛑 Botas sustabdytas per stop_event.")
            logging.info("Botas sustabdytas per stop_event.")
            break

        print(f"[{time.strftime('%H:%M:%S')}] Pradedamas naujas patikrinimas...")

        komanda, update_id = gauti_update(
            None if paskutinis_update_id is None else paskutinis_update_id + 1
        )
        if update_id is not None:
            paskutinis_update_id = update_id

        stocks, check_interval = apdoroti_komanda(
            komanda, stocks, check_interval, busena, stop_event=stop_event
        )

        if stop_event and stop_event.is_set():
            print("🛑 Gauta stop komanda po Telegram komandų apdorojimo.")
            logging.info("Stop po komandų apdorojimo.")
            break

        for simbolis, norima_riba in stocks.items():
            if stop_event and stop_event.is_set():
                print("🛑 Stop ciklo metu.")
                break
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
                    logging.info("Išsiųstas įspėjimas apie %s", simbolis)

                elif not yra_zemiau and buvo_zemiau:
                    print(f"✅ {simbolis} pakilo virš ribos: {dabartine_kaina} USD")
                    busena[simbolis] = False
                    logging.info("Atnaujinta būsena (virš ribos) %s", simbolis)

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

        rodyti_countdown(check_interval, stop_event=stop_event)

    print("✅ Botas sustabdytas.")
    logging.info("Botas sustabdytas.")


def main():
    try:
        run_bot(stop_event=None)
    except KeyboardInterrupt:
        print("\nPrograma nutraukiama vartotojo.")
        logging.info("Programa nutraukiama vartotojo.")


if __name__ == "__main__":
    main()