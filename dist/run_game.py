# run_game.py — simplified version for hosted backend
import os
import subprocess

print("🚀 Launching KrishiPatha Game...")

# Directly run the main game file
try:
    subprocess.run(["python", "game.py"], check=True)
except KeyboardInterrupt:
    print("\n🛑 Game closed manually.")
except Exception as e:
    print(f"⚠️ Error launching game: {e}")
