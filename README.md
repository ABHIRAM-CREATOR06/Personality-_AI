# 🧠 Personality Profiler  

AI tool that analyzes your reflections on real‑world scenarios and creates a **personality profile PDF** with MBTI prediction + radar chart.  

---

## ⚙️ Setup   

### 1. Install Required Python Packages  
Open **Command Prompt** in your project folder and run:

```bash
pip install streamlit matplotlib fpdf numpy
```

### 2. Install Ollama
Download **Ollama** 👉 https://ollama.com/download

Check installation:
```bash
ollama --version
```

### 3. Download DeepSeek Model
Pull the required model:
```bash
ollama pull deepseek-r1:7b
```

### 4. Place the Project File
Create a folder (example):
```bash
C:\Users\YourName\Documents\personalityai
```

### 5. Run the Project
In the folder, run:
```bash
python -m streamlit run analyzer.py
```
The app will open in your browser 👉 http://localhost:8501

###📝 Usage
Read the scenario shown.
#### 1.Write your answer (minimum 50 words).
If shorter, the system auto‑expands it.
Click Analyze Me.
#### 2.See your results:
✅ MBTI Type
📊 Radar Chart
📝 Personality Summary
**Download** your PDF report.

#### 3.📂 Output Files
chart.png → radar chart
personality_report.pdf → personality report
