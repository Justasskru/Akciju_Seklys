from config import MANO_AKCIJOS
from price_fetcher import gauti_kaina_ir_pokyti
from telegram_sender import siusti_telegram

def formatuoti_pokyti(pokytis):
    if pokytis is None:
        return "N/A"
    return f"{pokytis} USD"

def main():
    print("Pradedamas akcijų tikrinimas...\n")

    for simbolis, norima_riba in MANO_AKCIJOS.items():
        try:
            dabartine_kaina, pokytis = gauti_kaina_ir_pokyti(simbolis)

            if dabartine_kaina <= norima_riba:
                zinute = (
                    f"🔥 DĖMESIO! {simbolis} kaina: {dabartine_kaina} USD\n"
                    f"Tavo riba: {norima_riba} USD\n"
                    f"Pokytis nuo atidarymo: {formatuoti_pokyti(pokytis)}"
                )
                print(zinute)
                siusti_telegram(zinute)
            else:
                print(
                    f"👀 {simbolis}: {dabartine_kaina} USD | "
                    f"riba: {norima_riba} USD | "
                    f"pokytis: {formatuoti_pokyti(pokytis)}"
                )

        except Exception as e:
            print(f"❌ Klaida tikrinant {simbolis}: {e}")

if __name__ == "__main__":
    main()