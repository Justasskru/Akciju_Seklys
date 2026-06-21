import yfinance as yf

def gauti_kaina_ir_pokyti(simbolis: str):
    akcija = yf.Ticker(simbolis)

    
    last_price = akcija.fast_info.get("last_price") if akcija.fast_info else None

  
    if last_price is None:
        hist = akcija.history(period="1d", interval="1m")
        if hist.empty:
            hist = akcija.history(period="5d", interval="1d")
        if hist.empty:
            raise ValueError(f"Nerasta kainos simboliui: {simbolis}")
        last_price = float(hist["Close"].dropna().iloc[-1])

    dabartine_kaina = round(float(last_price), 2)

    
    info = akcija.info or {}
    atidarymo_kaina = info.get("regularMarketOpen")

    if atidarymo_kaina is None:
        hist_day = akcija.history(period="1d", interval="1d")
        if not hist_day.empty and "Open" in hist_day.columns:
            atidarymo_kaina = float(hist_day["Open"].iloc[0])

    pokytis = None if atidarymo_kaina is None else round(dabartine_kaina - float(atidarymo_kaina), 2)

    return dabartine_kaina, pokytis