import subprocess
import time
import requests
import os

def start_backend():
    """Start the FastAPI backend inside the backend directory"""
    backend_dir = os.path.join(os.path.dirname(__file__), "backend")
    print("🚀 Starting backend server...")

    # Launch uvicorn inside backend folder
    return subprocess.Popen(
        ["uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=backend_dir,  # 👈 this ensures we run inside /backend
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

def wait_for_backend(timeout=20):
    """Wait for backend to respond"""
    url = "http://127.0.0.1:8000"
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(url)
            if r.status_code == 200:
                print("✅ Backend is up and running!")
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
    print("❌ Backend did not start in time.")
    return False

def start_game():
    """Start the pygame game"""
    print("🎮 Launching KrishiPatha Game...")
    subprocess.run(["python", "game.py"], check=True)

if __name__ == "__main__":
    backend_process = start_backend()
    if wait_for_backend(timeout=20):
        start_game()
    else:
        print("⚠️ Could not start backend. Exiting.")
        backend_process.terminate()
