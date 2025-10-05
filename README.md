# 🌾 KrishiPatha — Smart Sustainable Farming Game

**KrishiPatha** is an interactive, simulation-based educational game built using **Python (Pygame)** and **FastAPI** to teach the principles of sustainable and smart farming practices.  
Developed as part of the **NASA Space Apps Challenge 2025**, it empowers users to explore, learn, and simulate farming decisions that affect crop yield, water management, and sustainability.

---

## 🚀 Features

- 🗺️ **Explore Mode:** Choose a plot and environment to begin your farming journey.  
- 🌱 **Crop & Livestock Selection:** Select from recommended crops and livestock based on soil and weather data.  
- 💧 **Water & Irrigation Setup:** Experiment with irrigation techniques and water management systems.  
- 🎬 **Simulation Process:** Watch a short video that visualizes crop growth and livestock activities.  
- 📊 **Sustainability Report:** Get yield predictions, sustainability scores, and performance insights powered by backend ML models.  
- 🧩 **Challenge Mode:** Play interactive quizzes and farming challenges (coming soon).  

---

## 🧠 Tech Stack

| Component | Technology Used |
|------------|----------------|
| **Frontend (Game)** | Python, Pygame, Pillow, MoviePy |
| **Backend (API)** | FastAPI |
| **Data & ML Models** | Scikit-learn (via mock simulation APIs) |
| **Visualization** | Pygame Video + Simulation |
| **Deployment** | Render (for API), Local Executable (PyInstaller) |

---

## 📁 Project Structure

KrishiPatha_Game/
│
├── backend/ # FastAPI backend
│ ├── api/ # Environment & Yield simulation APIs
│ ├── models/ # Placeholder ML models
│ ├── services/ # Business logic & utilities
│ └── main.py # FastAPI app entry point
│
├── screens/ # Pygame screen modules
│ ├── explore.py # Explore mode logic & simulation
│ ├── challenge.py # Challenge/quiz screens
│ └── levels/ # Mini farming challenges
│
├── assets/ # Game visuals, backgrounds, and video
│ ├── background/
│ ├── simulation.mp4
│ └── icons/
│
├── run_game.py # Launcher script (for packaged build)
├── game.py # Main Pygame engine file
├── requirements.txt # Dependencies
└── README.md # Documentation


---

## 🧩 Backend API Overview

### 🌍 Environment Analysis API
```http
POST /analyze/environment

Input:
{
  "latitude": 28.6,
  "longitude": 77.2
}

Output:
{
  "soil": "loamy",
  "avg_rainfall": 700,
  "avg_temp": 27,
  "water_source": "river",
  "recommended_crops": ["Wheat", "Maize", "Pulses"],
  "recommended_livestock": ["Goat", "Cow", "Chicken"]
}

🌾 Yield Simulation API
POST /analyze/simulate

Input:
{
  "crop": "Rice",
  "livestock": "Cow",
  "water_amount": "High",
  "irrigation": "Drip",
  "soil": "clay",
  "temp": 28,
  "rainfall": 750
}

Output:
{
  "yield_value": 4200.5,
  "score": 87.4
}

How to Run Locally

1️⃣ Clone the Repository
git clone https://github.com/<your-username>/KrishiPatha_Game.git
cd KrishiPatha_Game

2️⃣ Create Virtual Environment
python -m venv venv
venv\Scripts\activate

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Run Backend Server
cd backend
uvicorn main:app --reload

5️⃣ Run the Game
python run_game.py

🌱 Vision

KrishiPatha aims to educate and empower farmers and students by gamifying sustainable agriculture.
It demonstrates how real-world decisions — like water management, irrigation choice, and crop-livestock balance — impact long-term sustainability and yield.

“Learn farming the smart way — play, experiment, and grow sustainably.”

📜 License

This project is licensed under the MIT License — free for educational and non-commercial use.

🛰️ NASA Space Apps Challenge 2025 Submission

Project Title: KrishiPatha — Smart Sustainable Farming Game
Challenge Category: Agriculture & Sustainability through Technology
Submission Includes:

Working game demo (Pygame)

FastAPI backend (Render-hosted)

Presentation PDF + Gameplay Video

Source code repository on GitHub


---

Would you like me to make a **README version with visuals** (badges, emojis, and image placeholders) to make it look like a top GitHub project page? It’ll look like this:

> 🖼️ Project Banner  
> ⭐ Badges (Made with Python, FastAPI, Pygame)  
> 📸 Screenshot Gallery  

It’ll help your NASA submission *stand out visually*.
