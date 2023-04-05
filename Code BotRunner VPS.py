import subprocess
import time
import os

def run_bot(bot_name):
    print(f"Exécution du bot {bot_name}...")
    cmd_command = f"start cmd /k python {bot_name}"
    process = subprocess.Popen(cmd_command, shell=True)
    return process

def kill_bot(process):
    process.terminate()

def main():
    bot_names = ["arbitr.py", "funding.py", "gpt.py", "himpact.py", "limpact.py", "mimpact.py", "pourcent.py", "prixBTC.py"]
    interval = 8 * 60 * 60  # 8 heures en secondes

    while True:
        processes = []
        for bot_name in bot_names:
            process = run_bot(bot_name)
            processes.append(process)

        time.sleep(interval)

        for process in processes:
            kill_bot(process)

if __name__ == "__main__":
    main()

