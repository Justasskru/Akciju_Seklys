import streamlit as st
from settings_manager import load_settings, save_settings
from bot_control import start_bot, stop_bot, refresh_bot_status

st.set_page_config(page_title="Akcijų Seklys", layout="centered")
st.title("📈 Akcijų Seklys - Valdymo panelė")

# ===== BOT STATUS =====
status = refresh_bot_status()
running = status.get("running", False)
pid = status.get("pid")

st.subheader("🤖 Boto valdymas")
st.write(f"Būsena: {'🟢 Veikia' if running else '🔴 Sustabdytas'}")
if running:
    st.caption(f"PID: {pid}")

c1, c2 = st.columns(2)
with c1:
    if st.button("▶️ Paleisti botą", use_container_width=True):
        ok, msg = start_bot()
        if ok:
            st.success(msg)
        else:
            st.info(msg)
        st.rerun()

with c2:
    if st.button("⏹ Stabdyti botą", use_container_width=True):
        ok, msg = stop_bot()
        if ok:
            st.success(msg)
        else:
            st.info(msg)
        st.rerun()

st.divider()

# ===== SETTINGS =====
settings = load_settings()
stocks = settings.get("stocks", {})
check_interval = int(settings.get("check_interval", 300))

st.subheader("⏱ Tikrinimo intervalas")
new_interval = st.number_input(
    "Intervalas sekundėmis",
    min_value=10,
    max_value=86400,
    value=check_interval,
    step=10
)

st.subheader("📌 Stebimos akcijos")
if stocks:
    for symbol, limit_val in list(stocks.items()):
        a, b, c = st.columns([2, 2, 1])
        with a:
            st.write(symbol)
        with b:
            new_limit = st.number_input(
                f"Riba {symbol}",
                value=float(limit_val),
                key=f"limit_{symbol}"
            )
            stocks[symbol] = float(new_limit)
        with c:
            if st.button("❌", key=f"remove_{symbol}"):
                del stocks[symbol]
                save_settings({"stocks": stocks, "check_interval": int(new_interval)})
                st.rerun()
else:
    st.info("Akcijų sąrašas tuščias.")

st.subheader("➕ Pridėti akciją")
x, y = st.columns(2)
with x:
    new_symbol = st.text_input("Simbolis (pvz. AAPL)").upper().strip()
with y:
    new_symbol_limit = st.number_input("Riba", value=100.0)

if st.button("Pridėti / atnaujinti"):
    if not new_symbol:
        st.warning("Įvesk simbolį.")
    else:
        stocks[new_symbol] = float(new_symbol_limit)
        save_settings({"stocks": stocks, "check_interval": int(new_interval)})
        st.success(f"Išsaugota: {new_symbol}")
        st.rerun()

if st.button("💾 Išsaugoti nustatymus", type="primary"):
    save_settings({
        "stocks": stocks,
        "check_interval": int(new_interval)
    })
    st.success("Nustatymai išsaugoti")