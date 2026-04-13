🐍 CODEARENA - Python Coding Platform

A sleek, LeetCode-style web application designed for practicing Python coding 
with real-time execution and instant feedback.

🚀 QUICK START

1. Install dependencies:
   pip install -r requirements.txt

2. Start backend:
   python api/index.py

3. Start frontend (in a new terminal):
   cd public && python -m http.server 8000

4. Open browser:
   http://localhost:8000

✨ FEATURES

• 40+ Coding Problems with varying difficulty levels
• Code editor with auto-indentation & bracket closing
• Run code & test against multiple test cases in real-time
• Dark/Light theme toggle
• Collapsible sidebar & resizable panels for better UX
• Keyboard Shortcut: Ctrl+Enter to run code

📂 PROJECT STRUCTURE

api/index.py       - Backend Flask API
public/            - Frontend assets (HTML/CSS/JS)
data/problems.json  - Problems database
requirements.txt   - Python dependencies

🛠 TECH STACK

Frontend: HTML5, CSS3, JavaScript
Backend:  Python, Flask
Hosting:  Vercel

🌐 API ENDPOINTS

POST /api/run      - Execute Python code
POST /api/submit   - Test against specific test cases
GET  /api/problems - Fetch all problem data

☁️ DEPLOY TO VERCEL

1. Install Vercel CLI: npm install -g vercel
2. Deploy:             vercel --prod

📝 LICENSE & DEMO

LICENSE:   MIT License - Free to use and modify
LIVE DEMO: https://py-compiler-ten.vercel.app/

Created with 🐍 Python
