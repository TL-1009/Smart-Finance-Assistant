from flask import Flask, request, jsonify, send_from_directory
import math
import random
import csv
import os
from datetime import datetime

try:
    from scipy.optimize import linprog
except ImportError:
    linprog = None


app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CSV_FILE = os.path.join(BASE_DIR, "finance_data.csv")
REPORT_FILE = os.path.join(BASE_DIR, "financial_report.txt")


# ============================================================
# HELPERS
# ============================================================

def safe_float(value, default=0.0):
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_int(value, default=0):
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return default


def ratio(value, total):
    if total <= 0:
        return 0
    return (value / total) * 100


def money(value):
    return round(float(value or 0), 2)


def emi_calc(principal, annual_rate, years):
    principal = safe_float(principal)
    annual_rate = safe_float(annual_rate)
    years = safe_float(years)

    if principal <= 0 or years <= 0:
        return 0

    if annual_rate <= 0:
        return principal / (years * 12)

    monthly_rate = annual_rate / 12 / 100
    months = years * 12

    emi = (
        principal
        * monthly_rate
        * (1 + monthly_rate) ** months
        / ((1 + monthly_rate) ** months - 1)
    )

    return emi


# ============================================================
# INVESTMENT EXPLANATIONS
# ============================================================

def investment_risk_explainer():
    return {
        "FD": {
            "risk": "Low",
            "description": "Fixed Deposits offer relatively stable returns and are suitable for conservative investors.",
            "pros": "Predictable returns and lower volatility.",
            "cons": "Growth may be limited and may not always beat inflation.",
            "examples": [
                "Bank fixed deposits",
                "Post Office Time Deposit",
                "AAA-rated corporate FDs"
            ]
        },
        "Debt": {
            "risk": "Low-Medium",
            "description": "Debt investments generally invest in bonds or fixed-income instruments.",
            "pros": "Generally more stable than equity investments.",
            "cons": "Returns can be affected by interest-rate movements and credit risk.",
            "examples": [
                "Debt mutual funds",
                "Liquid funds",
                "Government securities (G-Secs)",
                "Corporate bond funds"
            ]
        },
        "SIP": {
            "risk": "Medium",
            "description": "A SIP invests a fixed amount regularly into mutual funds.",
            "pros": "Disciplined investing and diversification.",
            "cons": "Market-linked returns fluctuate.",
            "examples": [
                "Multi-cap mutual fund SIP",
                "Flexi-cap mutual fund SIP",
                "ELSS (tax-saving) SIP"
            ]
        },
        "Index": {
            "risk": "Medium-High",
            "description": "Index funds track a market index and provide broad market exposure.",
            "pros": "Diversification and relatively low-cost long-term investing.",
            "cons": "Still exposed to market crashes and volatility.",
            "examples": [
                "Nifty 50 index fund",
                "Sensex index fund",
                "Nifty Next 50 index fund"
            ]
        },
        "Stocks": {
            "risk": "High",
            "description": "Individual stocks can provide high growth potential but also have significant volatility.",
            "pros": "High long-term growth potential.",
            "cons": "High risk and large short-term fluctuations.",
            "examples": [
                "Large-cap blue-chip stocks",
                "Diversified holdings across sectors",
                "Mid-cap growth stocks (higher risk)"
            ]
        }
    }


# ============================================================
# REFERENCE DATA (informational only — not personalized advice)
# ============================================================

# Representative FD rates for reference/comparison only. Real rates change
# often — this is a snapshot to give a sense of scale, not a live feed.
# Update this periodically; don't treat it as always-current.
FD_REFERENCE = {
    "updated": "June 2026 (indicative — verify current rates with the bank)",
    "rates": [
        {"bank": "State Bank of India (SBI)", "one_year": 6.25, "three_year": 6.30, "five_year": 6.30},
        {"bank": "HDFC Bank", "one_year": 6.25, "three_year": 6.50, "five_year": 6.40},
        {"bank": "ICICI Bank", "one_year": 6.25, "three_year": 6.50, "five_year": 6.50},
        {"bank": "Axis Bank", "one_year": 6.25, "three_year": 6.45, "five_year": 6.45},
        {"bank": "Punjab National Bank", "one_year": 6.25, "three_year": 6.35, "five_year": 6.35},
        {"bank": "Post Office Time Deposit", "one_year": 6.90, "three_year": 7.10, "five_year": 7.50}
    ]
}


def calculate_sip(monthly_amount, years, annual_rate_percent):
    """
    Standard SIP future-value formula (ordinary annuity, monthly
    contributions, compounded monthly). Returns None if the inputs don't
    describe a real SIP (no amount or no duration) so the caller/frontend
    can skip the section instead of showing a zeroed-out result.
    """

    if monthly_amount <= 0 or years <= 0:
        return None

    months = int(round(years * 12))
    monthly_rate = annual_rate_percent / 12 / 100

    if monthly_rate == 0:
        maturity_value = monthly_amount * months
    else:
        maturity_value = (
            monthly_amount *
            (((1 + monthly_rate) ** months - 1) / monthly_rate) *
            (1 + monthly_rate)
        )

    invested = monthly_amount * months
    gains = maturity_value - invested

    return {
        "monthly_amount": round(monthly_amount),
        "years": years,
        "annual_rate": annual_rate_percent,
        "invested": round(invested),
        "maturity_value": round(maturity_value),
        "gains": round(gains)
    }


# ============================================================
# HISTORY
# ============================================================

def save_history(name, income, expenses, savings, savings_rate, score, risk):
    file_exists = os.path.isfile(CSV_FILE)

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "Date",
                "Name",
                "Income",
                "Expenses",
                "Savings",
                "SavingsRate",
                "Score",
                "Risk"
            ])

        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            name,
            round(income, 2),
            round(expenses, 2),
            round(savings, 2),
            round(savings_rate, 2),
            round(score, 2),
            risk
        ])


def get_history(name):
    history = []

    if not os.path.isfile(CSV_FILE):
        return {
            "count": 0,
            "values": [],
            "average": 0,
            "highest": 0,
            "lowest": 0,
            "trend": "No history available yet."
        }

    try:
        with open(CSV_FILE, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                if str(row.get("Name", "")).strip().lower() == str(name).strip().lower():
                    history.append({
                        "date": row.get("Date", ""),
                        "savings": safe_float(row.get("Savings")),
                        "score": safe_float(row.get("Score"))
                    })

    except Exception:
        history = []

    values = [item["savings"] for item in history]

    if not values:
        return {
            "count": 0,
            "values": [],
            "average": 0,
            "highest": 0,
            "lowest": 0,
            "trend": "No previous records for this user."
        }

    if len(values) >= 2:
        if values[-1] > values[-2]:
            trend = "Savings are increasing."
        elif values[-1] < values[-2]:
            trend = "Savings are decreasing."
        else:
            trend = "Savings are stable."
    else:
        trend = "This is your first recorded analysis."

    return {
        "count": len(values),
        "values": values,
        "average": round(sum(values) / len(values), 2),
        "highest": round(max(values), 2),
        "lowest": round(min(values), 2),
        "trend": trend
    }


# ============================================================
# SIMULATION
# ============================================================

def monte_carlo_simulation(base_savings):
    if base_savings <= 0:
        return {
            "available": False,
            "average": 0,
            "best": 0,
            "worst": 0,
            "median": 0,
            "percentile_10": 0,
            "percentile_90": 0,
            "explanation": "Simulation is unavailable because there is no positive monthly savings surplus."
        }

    results = []

    for _ in range(1000):
        value = 0
        current_savings = base_savings

        for _ in range(120):
            market_return = random.gauss(
                0.10 / 12,
                0.15 / math.sqrt(12)
            )

            inflation = random.gauss(
                0.05 / 12,
                0.02 / math.sqrt(12)
            )

            salary_growth = random.gauss(0.08, 0.02)

            current_savings *= 1 + salary_growth / 12
            value += current_savings

            value *= 1 + market_return - inflation

            if value < 0:
                value = 0

        results.append(value)

    results.sort()

    average = sum(results) / len(results)
    median = results[len(results) // 2]
    p10 = results[int(len(results) * 0.10)]
    p90 = results[int(len(results) * 0.90)]

    growth = average / max(base_savings, 1)

    if growth < 5:
        explanation = "The simulation suggests relatively modest long-term growth."
    elif growth < 10:
        explanation = "The simulation suggests moderate long-term compounding."
    else:
        explanation = "The simulation suggests strong long-term compounding potential."

    return {
        "available": True,
        "average": round(average, 2),
        "best": round(max(results), 2),
        "worst": round(min(results), 2),
        "median": round(median, 2),
        "percentile_10": round(p10, 2),
        "percentile_90": round(p90, 2),
        "explanation": explanation
    }


# ============================================================
# OPTIMIZATION
# ============================================================

def optimize_budget(income, emi):
    available_income = income - emi

    if available_income <= 0:
        return {
            "available": False,
            "allocation": {},
            "optimal_savings": 0,
            "explanation": "Budget optimization is unavailable because EMI consumes the available income."
        }

    categories = [
        "Grocery",
        "Travel",
        "Food",
        "Medical",
        "Miscellaneous"
    ]

    coefficients = [0.8, 0.4, 0.7, 1.0, 0.2]

    minimum_ratios = [
        0.08,
        0.05,
        0.08,
        0.03,
        0.02
    ]

    minimums = [
        available_income * x
        for x in minimum_ratios
    ]

    if linprog is None:
        allocation = {
            categories[i]: round(minimums[i], 2)
            for i in range(len(categories))
        }

        optimal_savings = available_income - sum(minimums)

        return {
            "available": True,
            "allocation": allocation,
            "optimal_savings": round(max(0, optimal_savings), 2),
            "explanation": "Optimization used minimum recommended spending levels because SciPy is unavailable."
        }

    try:
        result = linprog(
            coefficients,
            A_ub=None,
            b_ub=None,
            bounds=[
                (minimums[i], available_income)
                for i in range(len(categories))
            ],
            method="highs"
        )

        if result.success:
            allocation = {
                categories[i]: round(float(result.x[i]), 2)
                for i in range(len(categories))
            }

            optimal_savings = available_income - sum(result.x)

            return {
                "available": True,
                "allocation": allocation,
                "optimal_savings": round(max(0, optimal_savings), 2),
                "explanation": "The optimizer estimates a spending allocation while preserving minimum lifestyle requirements."
            }

    except Exception:
        pass

    return {
        "available": False,
        "allocation": {},
        "optimal_savings": 0,
        "explanation": "Budget optimization could not be completed."
    }


# ============================================================
# MAIN ANALYSIS
# ============================================================

def analyze_finances(data):

    name = str(data.get("name") or "User").strip()

    income = safe_float(data.get("income"))

    if income <= 0:
        raise ValueError("Monthly income must be greater than ₹0.")

    mode = str(data.get("mode") or "simple").lower()
    risk = str(data.get("risk") or "medium").lower()

    if risk not in ["low", "medium", "high"]:
        risk = "medium"

    # --------------------------------------------------------
    # HOUSING
    # --------------------------------------------------------

    housing_type = str(data.get("housing") or "pg").lower()

    housing_cost = 0
    emi = 0
    maintenance = 0
    home_loan_choice = "no"

    if housing_type == "pg":
        housing_cost = income * 0.20

    elif housing_type == "rent":
        housing_cost = income * 0.35

    elif housing_type == "own":

        loan_choice = str(data.get("home_loan") or "no").lower()
        home_loan_choice = loan_choice

        if loan_choice == "yes":
            loan_amount = safe_float(data.get("loan_amount"))
            interest_rate = safe_float(data.get("interest_rate"))
            tenure = safe_float(data.get("loan_tenure"))

            emi = emi_calc(
                loan_amount,
                interest_rate,
                tenure
            )

        maintenance_choice = str(
            data.get("maintenance") or "no"
        ).lower()

        if maintenance_choice == "yes":

            maintenance_type = str(
                data.get("maintenance_mode") or "estimated"
            ).lower()

            if maintenance_type == "fixed":
                maintenance = safe_float(
                    data.get("maintenance_cost")
                )
            else:
                maintenance = income * 0.03

        housing_cost = maintenance

    # A real but modest set of benefits: several states discount stamp
    # duty for property registered in a woman's name, and several banks
    # offer a small home loan rate concession to women borrowers. This is
    # informational only — it does not change the EMI/expense math above,
    # since exact figures vary by bank and state and shouldn't be guessed.
    gender = str(data.get("gender") or "").lower()
    home_loan_gender_note = None

    if housing_type == "own" and gender == "female":

        note_parts = [
            "Many Indian states charge lower stamp duty when a property "
            "is registered in a woman's name (commonly 1-2% less, though "
            "some states charge the same regardless of gender) — worth "
            "checking your specific state's current rate."
        ]

        if home_loan_choice == "yes":
            note_parts.append(
                "Several banks (SBI, HDFC, ICICI, PNB, Bank of Baroda "
                "and others) also offer women borrowers a small home "
                "loan interest concession, typically 0.05%-0.25% below "
                "the standard rate — confirm the exact figure with your "
                "lender, as it varies and changes over time."
            )

        home_loan_gender_note = " ".join(note_parts)

    # --------------------------------------------------------
    # LIFESTYLE
    # --------------------------------------------------------

    lifestyle_categories = [
        "travel",
        "grocery",
        "food",
        "medical",
        "misc"
    ]

    simple_ratios = {
        "low": {
            "grocery": 0.08,
            "travel": 0.05,
            "food": 0.08,
            "medical": 0.03,
            "misc": 0.02
        },
        "medium": {
            "grocery": 0.14,
            "travel": 0.10,
            "food": 0.12,
            "medical": 0.07,
            "misc": 0.05
        },
        "high": {
            "grocery": 0.20,
            "travel": 0.15,
            "food": 0.18,
            "medical": 0.12,
            "misc": 0.10
        }
    }

    # The site sends one level (simple mode) or amount (advanced mode) per
    # category, nested under "lifestyle" — matching main.py, where travel,
    # grocery, food, medical and misc are each asked separately rather than
    # sharing a single overall level.
    lifestyle_input = data.get("lifestyle") or {}

    lifestyle = {}

    if mode == "advanced":

        for category in lifestyle_categories:
            lifestyle[category] = max(
                0,
                safe_float(lifestyle_input.get(category))
            )

    else:

        for category in lifestyle_categories:
            level = str(
                lifestyle_input.get(category) or "medium"
            ).lower()

            if level not in simple_ratios:
                level = "medium"

            lifestyle[category] = (
                income * simple_ratios[level][category]
            )

    lifestyle_total = sum(lifestyle.values())

    # --------------------------------------------------------
    # TOTAL EXPENSES
    # --------------------------------------------------------

    total_expense = round(
        housing_cost +
        lifestyle_total +
        emi,
        2
    )

    savings = round(
        max(0, income - total_expense),
        2
    )

    savings_rate = ratio(savings, income)
    expense_rate = ratio(total_expense, income)
    emi_rate = ratio(emi, income)

    # --------------------------------------------------------
    # SCORE
    # --------------------------------------------------------

    savings_score = min(savings_rate * 2, 100)

    expense_score = max(
        0,
        100 - expense_rate
    )

    emi_score = max(
        0,
        100 - (emi_rate * 2)
    )

    score = round(
        0.5 * savings_score +
        0.3 * expense_score +
        0.2 * emi_score
    )

    if score >= 70:
        status = "Good"
    elif score >= 40:
        status = "Moderate"
    else:
        status = "Risky"

    # --------------------------------------------------------
    # EXPLANATIONS
    # --------------------------------------------------------

    reasons = []

    if savings_rate < 20:
        reasons.append(
            "Your savings rate is below the commonly preferred 20%+ range."
        )

    if emi_rate > 30:
        reasons.append(
            "Your EMI is taking a significant portion of your income."
        )

    if expense_rate > 80:
        reasons.append(
            "Your expenses consume a very large share of your income."
        )

    if savings <= 0:
        reasons.append(
            "You currently have no monthly surplus."
        )

    if not reasons:
        reasons.append(
            "Your major financial indicators are currently healthy."
        )

    financial_explanation = (
        f"You earn approximately ₹{income:,.0f} per month. "
        f"Your estimated monthly expenses are ₹{total_expense:,.0f}, "
        f"leaving approximately ₹{savings:,.0f} in monthly savings. "
        f"Your savings rate is {savings_rate:.1f}%."
    )

    housing_explanation = {
        "pg": "PG costs are estimated at approximately 20% of monthly income.",
        "rent": "Rent is estimated at approximately 35% of monthly income.",
        "own": "Your own-home calculation includes the selected loan EMI and maintenance assumptions."
    }.get(
        housing_type,
        "Housing expenses were calculated from your selected inputs."
    )

    if mode == "simple":
        lifestyle_explanation = (
            "Lifestyle expenses were estimated using the Low, Medium or High spending profile you selected."
        )
    else:
        lifestyle_explanation = (
            "Lifestyle expenses were calculated directly from the monthly amounts you entered."
        )

    # --------------------------------------------------------
    # EMERGENCY FUND
    # --------------------------------------------------------

    emergency_fund = round(
        total_expense * 6,
        2
    )

    # --------------------------------------------------------
    # GOAL
    # --------------------------------------------------------

    goal_type = str(
        data.get("goal_type") or "preset"
    ).lower()

    preset_goals = {
        "emergency": ("Emergency Fund", 100000),
        "car": ("Car", 500000),
        "house": ("House", 5000000),
        "retirement": ("Retirement", 10000000)
    }

    if goal_type == "custom":

        goal_name = str(
            data.get("custom_goal_name") or "Custom Goal"
        )

        goal_amount = safe_float(
            data.get("custom_goal_amount")
        )

    else:

        # goal_type is just "preset" here — the actual choice (emergency /
        # car / house / retirement) comes from the goal_preset dropdown.
        goal_preset = str(
            data.get("goal_preset") or "emergency"
        ).lower()

        goal_name, goal_amount = preset_goals.get(
            goal_preset,
            preset_goals["emergency"]
        )

    if goal_amount > 0 and savings > 0:

        goal_months = goal_amount / savings
        goal_years = round(goal_months / 12, 1)

        yearly_savings = savings * 12

        goal_progress = round(
            min(
                100,
                (yearly_savings / goal_amount) * 100
            ),
            2
        )

        goal_message = (
            f"At your current savings rate, this goal could take approximately "
            f"{goal_years} years."
        )

        goal_explanation = (
            f"If you consistently save ₹{savings:,.0f} per month, "
            f"you could accumulate ₹{goal_amount:,.0f} in approximately "
            f"{goal_years} years, ignoring investment returns."
        )

    else:

        goal_months = None
        goal_years = None
        goal_progress = 0

        goal_message = (
            "A positive monthly savings surplus is required to estimate goal completion time."
        )

        goal_explanation = (
            "Increasing your monthly surplus will make the goal timeline shorter."
        )

    # --------------------------------------------------------
    # INVESTMENT ADVISORY
    # --------------------------------------------------------

    investment_option = None

    if savings <= 0:

        investment_recommendation = (
            "Focus on creating a positive monthly surplus before investing."
        )

    elif savings_rate < 10:

        investment_option = "FD"

        investment_recommendation = (
            "Prioritize your emergency fund and consider low-risk options such as FDs."
        )

    elif savings_rate < 20:

        investment_option = "Debt"

        investment_recommendation = (
            "Consider building your emergency fund while gradually using FDs and debt-oriented investments."
        )

    else:

        if risk == "low":
            investment_option = "FD"
            investment_recommendation = (
                "FDs and debt-oriented investments may suit your conservative risk profile."
            )

        elif risk == "medium":
            investment_option = "SIP"
            investment_recommendation = (
                "SIPs and index funds may suit your balanced risk profile for long-term growth."
            )

        else:
            investment_option = "Stocks"
            investment_recommendation = (
                "Stocks and growth-oriented mutual funds may suit your higher-risk profile."
            )

    explainers = investment_risk_explainer()

    # investment_explanation must be a single string — the template renders
    # it directly as text. Look up just the recommended option instead of
    # handing back the whole explainer dictionary. Examples are fund/
    # instrument categories (e.g. "Nifty 50 index fund"), never a specific
    # single stock or a named product — those go stale and aren't
    # personalized enough to responsibly bake into an app.
    if investment_option and investment_option in explainers:
        chosen = explainers[investment_option]
        investment_explanation = (
            f"{chosen['description']} "
            f"Pros: {chosen['pros']} "
            f"Cons: {chosen['cons']}"
        )
    else:
        investment_explanation = (
            "No specific investment is recommended until you have a positive monthly surplus."
        )

    # --------------------------------------------------------
    # PORTFOLIO
    # --------------------------------------------------------
    # A risk-based split only makes sense if there's actually a surplus to
    # invest. Without this check, someone with zero or negative savings
    # (Risky status) would still get a confident "60% Stocks..." plan,
    # which is misleading — there's no money behind it.

    if savings <= 0:

        portfolio = None

    elif risk == "low":

        portfolio = {
            "FD": 70,
            "Debt": 30
        }

    elif risk == "medium":

        portfolio = {
            "SIP": 50,
            "Index": 30,
            "FD": 20
        }

    else:

        portfolio = {
            "Stocks": 60,
            "SIP": 30,
            "Emergency Fund": 10
        }

    # --------------------------------------------------------
    # SIMULATION
    # --------------------------------------------------------

    simulation = monte_carlo_simulation(savings)

    # --------------------------------------------------------
    # SIP CALCULATOR
    # --------------------------------------------------------
    # Expected return is an assumption tied to the person's stated risk
    # profile (same idea as the portfolio split above) — not a promise or
    # a market prediction, just a reasonable planning estimate.

    sip_expected_returns = {
        "low": 7,
        "medium": 10,
        "high": 13
    }

    sip_amount = safe_float(data.get("sip_amount"))
    sip_years = safe_float(data.get("sip_years"))
    sip_rate = sip_expected_returns.get(risk, 10)

    sip = calculate_sip(sip_amount, sip_years, sip_rate)

    # --------------------------------------------------------
    # OPTIMIZATION
    # --------------------------------------------------------

    optimization = optimize_budget(
        income,
        emi
    )

    # --------------------------------------------------------
    # WARNINGS
    # --------------------------------------------------------

    warnings = []

    if emi_rate > 40:
        warnings.append(
            "Your EMI exceeds 40% of your monthly income."
        )

    if total_expense >= income:
        warnings.append(
            "Your total expenses are equal to or greater than your income."
        )

    # --------------------------------------------------------
    # SAVE HISTORY
    # --------------------------------------------------------

    save_history(
        name,
        income,
        total_expense,
        savings,
        savings_rate,
        score,
        risk
    )

    history = get_history(name)

    # --------------------------------------------------------
    # REPORT
    # --------------------------------------------------------

    report = f"""
SMART FINANCE ASSISTANT
=======================

Name: {name}
Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

MONTHLY FINANCIAL SNAPSHOT
--------------------------
Income: ₹{income:,.2f}
Expenses: ₹{total_expense:,.2f}
Savings: ₹{savings:,.2f}
Savings Rate: {savings_rate:.2f}%
Expense Rate: {expense_rate:.2f}%
EMI Rate: {emi_rate:.2f}%

FINANCIAL HEALTH
----------------
Score: {score}/100
Status: {status}

Emergency Fund Target:
₹{emergency_fund:,.2f}

GOAL
----
Goal: {goal_name}
Target: ₹{goal_amount:,.2f}
Estimated Time: {goal_years if goal_years is not None else "Unavailable"} years

INVESTMENT
----------
Risk Profile: {risk.title()}
Recommendation:
{investment_recommendation}

WARNINGS
--------
{chr(10).join(warnings) if warnings else "No major warnings."}
"""

    with open(
        REPORT_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        file.write(report)

    return {
        "name": name,
        "income": money(income),
        "total_expense": money(total_expense),
        "emi": money(emi),
        "savings": money(savings),

        "savings_rate": round(savings_rate, 2),
        "expense_rate": round(expense_rate, 2),
        "emi_rate": round(emi_rate, 2),

        "emergency_fund": money(emergency_fund),

        "score": score,
        "status": status,

        "reasons": reasons,
        "financial_explanation": financial_explanation,

        "housing": housing_type,
        "housing_cost": money(housing_cost),
        "maintenance": money(maintenance),

        "housing_explanation": housing_explanation,
        "lifestyle_explanation": lifestyle_explanation,

        "lifestyle": {
            key: money(value)
            for key, value in lifestyle.items()
        },

        "goal_name": goal_name,
        "goal_amount": money(goal_amount),
        "goal_years": goal_years,
        "goal_progress": goal_progress,
        "goal_message": goal_message,
        "goal_explanation": goal_explanation,

        "risk": risk,

        "investment_recommendation": investment_recommendation,
        "investment_explanation": investment_explanation,
        "investment_examples": (
            explainers[investment_option]["examples"]
            if investment_option and investment_option in explainers
            else []
        ),

        "portfolio": portfolio,

        "sip": sip,

        "fd_reference": FD_REFERENCE,

        "home_loan_gender_note": home_loan_gender_note,

        "simulation": simulation,

        "optimization": optimization,

        "history": history,

        "warnings": warnings
    }


# ============================================================
# ROUTES
# ============================================================

@app.route("/")
def home():
    return send_from_directory(
        BASE_DIR,
        "index.html"
    )


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(
        BASE_DIR,
        path
    )


@app.route("/api/analyze", methods=["POST"])
def analyze():

    try:

        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({
                "error": "Invalid request data."
            }), 400

        result = analyze_finances(data)

        return jsonify(result)

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 400

    except Exception as e:

        print("SERVER ERROR:", repr(e))

        return jsonify({
            "error": "Something went wrong while analysing the financial data.",
            "details": str(e)
        }), 500


@app.route("/api/report")
def report():

    if not os.path.isfile(REPORT_FILE):
        return jsonify({
            "error": "No report has been generated yet."
        }), 404

    return send_from_directory(
        BASE_DIR,
        "financial_report.txt",
        as_attachment=True
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )