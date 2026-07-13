import streamlit as st
import logging
import os
import signal
import subprocess
import sys
from settings_manager import load_settings, save_settings

logging.basicConfig(
    level=logging.INFO,
    filename="programos_logai.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s"
)

PID_FILE = "bot.pid"

st.set_page_config(page_title="Akcijų Seklys", layout="centered")
st.title("📈 Akcijų Seklys - Valdymo panelė")

settings = load_settings()
stocks = settings.get("stocks", {})
check_interval = int(settings.get("check_interval", 300))

st.subheader("⏱ Tikrinimo intervalas")
new_interval = st.number_input("Intervalas sekundėmis", min_value=10, max_value=86400, value=check_interval, step=10)

st.subheader("📌 Stebimos akcijos")
if stocks:
    for symbol, limit_val in list(stocks.items()):
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            st.write(symbol)
        with c2:
            new_limit = st.number_input(f"Riba {symbol}", value=float(limit_val), key=f"limit_{symbol}")
            stocks[symbol] = float(new_limit)
        with c3:
            if st.button("❌", key=f"remove_{symbol}"):
                del stocks[symbol]
                st.rerun()
else:
    st.info("Akcijų sąrašas tuščias.")

st.subheader("➕ Pridėti akciją")
col1, col2 = st.columns(2)
with col1:
    new_symbol = st.text_input("Simbolis (pvz. AAPL)").upper().strip()
with col2:
    new_symbol_limit = st.number_input("Riba", value=100.0)

if st.button("Pridėti"):
    if not new_symbol:
        st.warning("Įvesk simbolį.")
    else:
        stocks[new_symbol] = float(new_symbol_limit)
        st.success(f"Pridėta/atnaujinta: {new_symbol}")

st.divider()

if st.button("💾 Išsaugoti nustatymus", type="primary"):
    save_settings({"stocks": stocks, "check_interval": int(new_interval)})
    st.success("Nustatymai išsaugoti")

def botas_veikia():
    if not os.path.exists(PID_FILE):
        return False
    try:
        with open(PID_FILE, "r") as f:
            pid = int(f.read().strip())
        os.kill(pid, 0)  # tikrinimas
        return True
    except Exception:
        return False

c1, c2 = st.columns(2)

with c1:
    if st.button("▶️ Paleisti botą"):
        if botas_veikia():
            st.info("Botas jau veikia.")
        else:
            p = subprocess.Popen([sys.executable, "main.py"])
            with open(PID_FILE, "w") as f:
                f.write(str(p.pid))
            st.success(f"Botas paleistas (PID: {p.pid})")
            logging.info("Botas paleistas iš panelės. PID=%s", p.pid)

with c2:
    if st.button("⏹ Stabdyti botą"):
        if not os.path.exists(PID_FILE):
            st.warning("Nerastas bot.pid (botas greičiausiai neveikia).")
        else:
            try:
                with open(PID_FILE, "r") as f:
                    pid = int(f.read().strip())
                os.kill(pid, signal.SIGTERM)
                os.remove(PID_FILE)
                st.success("Botas sustabdytas.")
                logging.info("Botas sustabdytas iš panelės. PID=%s", pid)
            except Exception as e:
                st.error(f"Nepavyko sustabdyti boto: {e}")

# Jei nori atskiro mygtuko uždaryti panelę – geriau nedaryti per killpg.