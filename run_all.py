import subprocess
import signal
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    filename="programos_logai.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.info("run_all.py pradėta")


def main():
    processes = []
    try:
        
        panel = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "app.py"])
        processes.append(panel)
        logging.info("UI panelė paleista")

        print("✅ Paleista:")
   
        print(f"   - UI  PID: {panel.pid}")
        print("UI dažniausiai bus: http://localhost:8501")

        # Laukiam kol vienas procesas baigsis
        while True:
            for p in processes:
                if p.poll() is not None:
                    raise KeyboardInterrupt

    except KeyboardInterrupt:
        logging.info("Vartotojas sustabdė procesus.")
        print("\n🛑 Stabdau procesus...")
        for p in processes:
            if p.poll() is None:
                p.terminate()
        for p in processes:
            try:
                p.wait(timeout=5)
            except Exception:
                if p.poll() is None:
                    p.kill()
        logging.info("Viskas sustabdyta.")
        print("✅ Viskas sustabdyta.")

if __name__ == "__main__":
    main()