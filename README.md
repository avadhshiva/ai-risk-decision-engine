# 🚀 AI Risk Decision Engine

An AI-powered system that analyzes real-world scenarios, classifies risk, and provides actionable mitigation strategies — with an interactive dashboard for insights.

---

## 🔥 Features

* AI-based risk classification (Financial, Operational, Technical, Compliance)
* Risk scoring (Low / Medium / High)
* Scenario-based impact analysis
* Actionable mitigation suggestions
* CSV-based data pipeline
* Interactive Streamlit dashboard with filtering & visualization

---

## 🧠 Problem Statement

Traditional risk classification relies on rigid rules and keyword matching, which fails to capture real-world context.

This project solves that by leveraging LLMs to:

* Understand context
* Classify risk intelligently
* Provide structured decision outputs

---

## ⚙️ Architecture

```
User Input → LLM (OpenAI) → JSON Output → CSV Storage → Streamlit Dashboard
```

---

## 🛠️ Tech Stack

* Python
* OpenAI API (GPT-4o-mini)
* Pandas
* Streamlit

---

## ▶️ How to Run

### 1. Clone repo

```
git clone https://github.com/<your-username>/ai-risk-decision-engine.git
cd ai-risk-decision-engine
```

### 2. Setup environment

```
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

### 3. Add API key

Create `.env` file:

```
OPENAI_API_KEY=your_key_here
```

---

### 4. Run data generator

```
python app.py
```

---

### 5. Launch dashboard

```
streamlit run dashboard.py
```

---

## 📊 Dashboard Preview

![Dashboard](screenshots/dashboard.png)

---

## 🧪 Example Use Cases

* Market downturn risk analysis
* Hiring pipeline delays
* System reliability issues
* Operational bottlenecks

---

## 🚀 Key Highlights

* Replaced rule-based classification with LLM-driven intelligence
* Built end-to-end pipeline (input → analysis → visualization)
* Designed for extensibility (can plug into enterprise workflows)

---

## 💡 Future Enhancements

* Add confidence score for classification
* Integrate vector DB for historical insights
* Build API layer (FastAPI)
* Real-time streaming dashboard

---

## 👤 Author

Sivakumar Avadhanam
Senior Technical Program Manager | AI Delivery Lead

---
