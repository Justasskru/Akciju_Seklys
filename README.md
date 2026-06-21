#Akcijų Seklys (Telegram Alert Bot)

Idėja

Šios programos idėja – automatiškai stebėti tavo pasirinktų akcijų kainas ir pranešti į Telegram, kai kaina pasiekia tavo nustatytą ribą (arba nukrenta žemiau jos).

Vietoj to, kad pats rankiniu būdu tikrintum kainas visą dieną, programa tai daro už tave kas tam tikrą intervalą (pvz. kas 1 valandą).

Ką daro programa

Programa:

Nuskaito tavo nustatymus (.env ir config.py).
Pasiima akcijų kainas iš yfinance.
Palygina dabartinę kainą su tavo norima riba.
Jei sąlyga tenkinama – siunčia pranešimą į Telegram.
Išsaugo būseną (state.json), kad nesiųstų to paties perspėjimo kas ciklą.
Palaukia nustatytą laiką ir kartoja procesą.
Kaip veikia logika (paprastai)

Tarkim, turi:

AAPL: 245
Dabartinė kaina: 244
Programa mato, kad 244 <= 245, todėl siunčia alertą.

Anti-spam principas

Be papildomos logikos, bot’as siųstų tą patį pranešimą kiekvieną ciklą, kol kaina liks žemiau ribos.
Kad taip nebūtų, naudojamas state.json:

Jei akcija pirmą kartą nukrenta žemiau ribos → siunčiam.
Jei kitame cikle ji vis dar žemiau → nebesiunčiam.
Kai akcija pakyla virš ribos → būsena „atrakinama“.
Jei vėl nukrenta žemiau → vėl siunčiam vieną naują alertą.
Projekto struktūra

Automacija/
├── main.py              # Pagrindinis ciklas ir visa orchestration logika
├── config.py            # Konfigūracija: .env + stebimų akcijų ribos
├── price_fetcher.py     # Akcijų kainos paėmimas iš yfinance
├── telegram_sender.py   # Telegram žinučių siuntimas
├── state_manager.py     # state.json skaitymas/rašymas (anti-spam būsena)
├── requirements.txt     # Reikalingos bibliotekos
├── .env                 # Slapti duomenys (token, chat_id, intervalas)
├── .gitignore           # Ignoruojami failai (pvz. .env, logai, state)
└── README.md            # Projekto aprašymas
Failų paskirtis detaliau

main.py

Programos entry-point.
Užkrauna būseną.
Sukasi per visas akcijas.
Priima sprendimą ar siųsti pranešimą.
Išsaugo būseną.
Palaukia iki kito ciklo.
config.py

Užkrauna .env reikšmes:
TELEGRAM_TOKEN
TELEGRAM_CHAT_ID
CHECK_INTERVAL
Laiko stebimų akcijų sąrašą, pvz:
MANO_AKCIJOS = {"AAPL": 245.0, "TSLA": 340.0}
price_fetcher.py

Pagrindinė funkcija paima:
dabartinę kainą,
pokytį nuo atidarymo (jei pavyksta gauti).
Turi fallback logiką, jei vienas kainos šaltinis negrąžina reikšmės.
telegram_sender.py

Siunčia žinutę į Telegram per Bot API (sendMessage).
Turi klaidų apdorojimą (try/except) ir timeout.
state_manager.py

Nuskaito state.json failą.
Išsaugo atnaujintą būseną po kiekvieno ciklo.
Konfigūracija

Sukurk .env failą:

TELEGRAM_TOKEN=cia_tavo_token
TELEGRAM_CHAT_ID=cia_tavo_chat_id
CHECK_INTERVAL=3600
Paaiškinimai

TELEGRAM_TOKEN – tavo Telegram boto tokenas.
TELEGRAM_CHAT_ID – į kurį chat siųsti žinutes.
CHECK_INTERVAL – kas kiek sekundžių kartoti tikrinimą.
3600 = 1 val.
300 = 5 min.
Įdiegimas ir paleidimas (Mac)

Sukurk virtualią aplinką:

python3 -m venv .venv
source .venv/bin/activate
Įdiek bibliotekas:

pip install -r requirements.txt
Paleisk programą:

python main.py
requirements.txt pavyzdys

yfinance
requests
python-dotenv
pandas
Pavyzdinė Telegram žinutė

🔥 DĖMESIO! AAPL kaina: 244.12 USD
Tavo riba: 245.0 USD
Pokytis nuo atidarymo: -1.34 USD
Klaidų valdymas

Programa apdoroja dažniausias klaidas:

Nepavyksta paimti kainos (yfinance laikinas sutrikimas).
Nepavyksta išsiųsti Telegram žinutės (ryšio/API klaida).
Nėra .env reikšmių.
Nėra state.json (sukuriama nauja būsena automatiškai).
Saugumas

Niekada nekelk .env į GitHub.
.gitignore turi turėti bent:
.env
*.log
state.json
.venv/
Galimi patobulinimai ateityje

Skirtingi alert tipai (kai kaina kyla virš ribos, ne tik krenta žemiau).
Procentinis pokytis per dieną.
Daugiau informacijos žinutėje (volume, market cap ir pan.).
Grafiko siuntimas į Telegram.
Paleidimas serveryje (VPS / Docker), kad veiktų 24/7.
Unit testai (pytest).
Kam ši programa naudinga

Pradedančiajam investuotojui, kuris nori paprasto automatizuoto stebėjimo.
Žmogui, kuris nenori nuolat ranka tikrinti kainų.
Mokymuisi: realus Python projektas su API, failais, ciklais ir klaidų valdymu.
Santrauka

Tai paprastas, bet praktiškas botas, kuris:

✅ stebi akcijų kainas
✅ lygina su tavo nustatytomis ribomis
✅ siunčia pranešimus į Telegram
✅ vengia spamo naudodamas būsenos failą
✅ dirba cikliškai automatiškai
