# Smart Finance Assistant 💰

A web-based **Financial Health Analyzer** that helps users understand their financial position through income and expense analysis, savings evaluation, investment planning, emergency-fund estimation, financial goals, budget optimization, and long-term wealth simulation.

🌐 **Live Demo:** https://smart-finance-assistant-3goy.onrender.com/

---

## 📌 Overview

**Smart Finance Assistant** is a personal-finance analysis tool designed to turn basic financial information into actionable insights.

Users can enter their income, recurring expenses, housing costs, lifestyle spending, loan commitments, investments, and financial goals. The application analyzes this information and generates a personalized financial snapshot.

The project combines a **Flask backend** with an interactive **HTML/CSS/JavaScript frontend**, along with numerical optimization and simulation techniques for deeper financial analysis.

---

## ✨ Key Features

### 📊 Financial Health Analysis

* Calculates a financial health score
* Evaluates savings and spending patterns
* Categorizes financial status as:

  * **Good**
  * **Moderate**
  * **Risky**
* Provides personalized financial insights

### 💸 Expense Analysis

Users can account for expenses such as:

* Housing / rent
* Food & groceries
* Travel
* Medical expenses
* Miscellaneous spending
* Home-loan EMI

The application analyzes the relationship between income, expenses, and savings.

### 🏦 Emergency Fund Planning

Estimates the recommended emergency fund based on monthly expenses.

The current model uses a **6-month expense benchmark** for emergency-fund planning.

### 📈 Investment Planning

The application provides guidance around different investment categories, including:

* Fixed deposits
* Debt-oriented investments
* SIPs
* Index investments
* Stocks

### 🎯 Financial Goals

Users can define financial goals and evaluate their financial position in relation to those goals.

### 🔮 Monte Carlo Wealth Forecast

The application uses simulation-based forecasting to visualize possible long-term wealth outcomes.

A **10-year Monte Carlo simulation** is used to demonstrate how different investment outcomes can affect future wealth.

### ⚙️ Budget Optimization

The application uses **SciPy optimization** to analyze spending allocations and identify potential budget improvements.

### 📜 Financial Reports

Users can generate a financial report based on their inputs.

### 📂 Financial History

Financial data can be recorded and analyzed over time, allowing users to observe changes in their financial position.

---

## 🛠️ Tech Stack

### Frontend

* HTML5
* CSS3
* JavaScript

### Backend

* Python
* Flask

### Data & Analysis

* SciPy
* CSV
* Mathematical modelling
* Monte Carlo simulation
* Linear programming / optimization

### Deployment

* GitHub
* Render
* Gunicorn

---

## 🧠 How It Works

The application follows a simple pipeline:

```text
User Financial Inputs
        ↓
Income & Expense Analysis
        ↓
Savings & Financial Health Calculation
        ↓
Financial Risk Evaluation
        ↓
Investment & Emergency Fund Analysis
        ↓
Budget Optimization
        ↓
Long-Term Wealth Simulation
        ↓
Personalized Financial Insights
```

---

## 📁 Project Structure

```text
Smart-Finance-Assistant/
│
├── app.py
├── main.py
├── index.html
├── style.css
├── requirements.txt
├── .gitignore
│
├── assets/
│   ├── financial_report.png
│   └── home.png
│
├── Budget Optimization.png
├── Monte Carlo Wealth Forecast.png
├── Savings Trend.png
│
└── README.md
```

### File Overview

| File               | Purpose                                             |
| ------------------ | --------------------------------------------------- |
| `app.py`           | Flask backend and financial-analysis logic          |
| `main.py`          | Earlier command-line implementation                 |
| `index.html`       | Web application interface                           |
| `style.css`        | Website styling                                     |
| `requirements.txt` | Python dependencies                                 |
| `assets/`          | Project images and visual assets                    |
| `.gitignore`       | Prevents generated/local files from being committed |

---

## 🚀 Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/TL-1009/Smart-Finance-Assistant.git
cd Smart-Finance-Assistant
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the environment

**Windows:**

```bash
venv\Scripts\activate
```

**macOS / Linux:**

```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Start the application

```bash
python app.py
```

The application will run locally at:

```text
http://127.0.0.1:5000
```

---

## 🌐 Live Deployment

The current web application is deployed using **Render**.

### Production start command

```bash
gunicorn app:app
```

### Build command

```bash
pip install -r requirements.txt
```

### Live application

🌐 **https://smart-finance-assistant-3goy.onrender.com/**

> The application currently uses Render's free instance. The service may temporarily spin down after periods of inactivity, which can cause a delay when the application is opened for the first time.

---

## 🔐 Data & Privacy

The project is designed as a personal-finance analysis tool.

Generated files such as:

```text
finance_data.csv
financial_report.txt
```

are excluded from version control through `.gitignore`.

Users should avoid entering sensitive information such as:

* Bank account numbers
* Card numbers
* Passwords
* OTPs
* Banking credentials

---

## 🔮 Future Enhancements

Potential improvements include:

* [ ] User authentication
* [ ] Persistent database storage
* [ ] Interactive financial dashboards
* [ ] More advanced investment modelling
* [ ] Tax-aware financial planning
* [ ] Inflation-adjusted projections
* [ ] Portfolio risk analysis
* [ ] Additional financial goals
* [ ] Automated financial recommendations
* [ ] Mobile-responsive improvements
* [ ] Cloud database integration

---

## ⚠️ Disclaimer

This project is intended for **educational and informational purposes**.

The financial insights generated by the application should not be considered professional investment, tax, legal, or financial advice. Users should consult qualified professionals before making significant financial decisions.

---

## 👩‍💻 Author

**Tisya Lall**

GitHub: https://github.com/TL-1009

---

## ⭐ Project

**Smart Finance Assistant — turning financial data into understandable insights.**
