import threading
import streamlit as st
from main import run_bot
from settings_manager import load_settings, save_settings

st.set_page_config(page_title="Akcijų Seklys Bot", page_icon="📈", layout="centered")
st.title("📈 Akcijų Seklys Bot valdymas")


def ensure_state():
    if "bot_thread" not in st.session_state:
        st.session_state.bot_thread = None
    if "stop_event" not in st.session_state:
        st.session_state.stop_event = None


def is_bot_running() -> bool:
    t = st.session_state.bot_thread
    return t is not None and t.is_alive()


def start_bot():
    if is_bot_running():
        return
    stop_event = threading.Event()
    t = threading.Thread(target=run_bot, kwargs={"stop_event": stop_event}, daemon=True)
    st.session_state.stop_event = stop_event
    st.session_state.bot_thread = t
    t.start()


def stop_bot():
    if st.session_state.stop_event is not None:
        st.session_state.stop_event.set()

    t = st.session_state.bot_thread
    if t is not None and t.is_alive():
        t.join(timeout=2.0)


ensure_state()

settings = load_settings()
stocks = settings.get("stocks", {})
interval = int(settings.get("check_interval", 60))

st.subheader("⚙️ Nustatymai")
new_interval = st.number_input("Tikrinimo intervalas (sek.)", min_value=10, value=interval, step=10)

if st.button("💾 Išsaugoti intervalą"):
    save_settings({"stocks": stocks, "check_interval": int(new_interval)})
    st.success(f"Išsaugota: intervalas = {int(new_interval)} s")

st.divider()

running = is_bot_running()
st.write(f"**Būsena:** {'🟢 Botas veikia' if running else '🔴 Botas sustabdytas'}")

col1, col2 = st.columns(2)

with col1:
    if st.button("▶️ Paleisti botą", disabled=running):
        start_bot()
        st.success("Botas paleistas.")

with col2:
    if st.button("⏹ Sustabdyti botą", disabled=not running):
        stop_bot()
        st.warning("Botas stabdomas...")

st.caption("Pastaba: nustatymai perkraunami automatiškai kiekvieno ciklo pradžioje.")

settings = load_settings()
stocks = settings.get("stocks", {})


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