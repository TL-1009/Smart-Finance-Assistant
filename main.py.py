import math
import random
import csv
import os

print("===================================================")
print("SMART FINANCE ASSISTANT")
print("===================================================")

print("\n🟢 Welcome to your Financial Health Analyzer.")
print("This tool will evaluate your income, expenses, savings,")
print("and investment risk profile to generate a full report.\n")


# ---------------- MODE ----------------
print("📘 INPUT MODE SELECTION")

print("\n1️⃣  Simple Mode  → LOW / MEDIUM / HIGH lifestyle inputs")
print("2️⃣    Advanced Mode → Exact ₹ values for all expenses")

mode_choice = input("\nEnter mode (1 or 2): ").strip()
mode = "simple" if mode_choice != "2" else "advanced"


# ---------------- EXPLANATION ----------------
print("\n📊 UNDERSTANDING INPUT LEVELS")

print("\n🟢 LOW LEVEL")
print("Represents controlled spending habits (0%–30% intensity).")
print("Typically contributes 5%–10% of income per category.")
print("Indicates strong savings discipline.\n")

print("🟡 MEDIUM LEVEL")
print("Represents balanced spending habits (30%–70% intensity).")
print("Typically contributes 10%–15% of income per category.")
print("Indicates stable but moderate savings.\n")

print("🔴 HIGH LEVEL")
print("Represents heavy spending habits (70%–100% intensity).")
print("Typically contributes 15%–25% of income per category.")
print("Indicates lifestyle-heavy expenses and lower savings.\n")


# ---------------- SAFE INPUT ----------------
def get_int(prompt):
    while True:
        try:
            return max(int(input(prompt)), 0)
        except ValueError:
            print("❌ Invalid input. Please enter a valid number.")

def get_float(prompt):
    while True:
        try:
            return max(float(input(prompt)), 0)
        except ValueError:
            print("❌ Invalid input. Please enter a valid number.")

def get_choice(prompt, options):
    while True:
        val = input(prompt).strip().lower()
        if val in options:
            return val
        print("❌ Invalid input. Choose from:", ", ".join(options))


# ---------------- USER ----------------
print("\n🧾 USER PROFILE")

name = input("Enter your name: ")
income = get_int("Enter your monthly income (₹): ")

if income == 0:
    print("⚠ Income cannot be zero. Setting it to 1 for safety.")
    income = 1

# ---------------- INVESTMENT RISK LIBRARY ----------------
def investment_risk_explainer(option):
    if option == "fd":
        return ("🟢 LOW RISK",
                "Fixed Deposits are safe because returns are guaranteed by banks, "
                "but they have low growth and may not beat inflation.")

    elif option == "debt":
        return ("🟢 LOW-MEDIUM RISK",
                "Debt mutual funds invest in government/corporate bonds. "
                "They are relatively stable but can be affected by interest rate changes.")

    elif option == "sip":
        return ("🟡 MEDIUM RISK",
                "SIPs invest in diversified mutual funds. "
                "Returns fluctuate with market but reduce risk through averaging.")

    elif option == "index":
        return ("🟡 MEDIUM-HIGH RISK",
                "Index funds follow the market. They are stable long-term "
                "but still exposed to market crashes.")

    elif option == "stocks":
        return ("🔴 HIGH RISK",
                "Stocks have high return potential but are volatile. "
                "Prices can rise or fall sharply in short periods.")

    else:
        return ("UNKNOWN RISK", "No risk data available.")
    

risk = get_choice("Investment risk you want to take (Low / Medium / High): ",
                  ["low", "medium", "high"])

print("\n🎯 FINANCIAL GOAL SECTION")

goal = get_choice(
    "Select goal (emergency/car/house/retirement): ",
    ["emergency","car","house","retirement"]
)

goal_values = {
    "emergency":100000,
    "car":500000,
    "house":5000000,
    "retirement":10000000
}

goal_amount = goal_values[goal]

expense = 0
emi = 0
warnings = []
reasons = []


# ---------------- EMI ----------------
def emi_calc(p, r, y):
    if y <= 0:
        y = 1

    if r == 0:
        return p / (y * 12)

    r = r / (12 * 100)
    n = y * 12

    return (p * r * math.pow(1 + r, n)) / (math.pow(1 + r, n) - 1)


# ---------------- HOUSING ----------------
print("\n🏠 HOUSING SECTION")

housing = get_choice("Enter housing type (rent / pg / own / own place): ",
                     ["rent", "pg", "own", "own place"])

if housing == "pg":
    expense += income * 0.20
    print("🟡 PG selected → moderate fixed cost assumed.")

elif housing == "rent":
    expense += income * 0.35
    print("🟡 Rent selected → higher fixed monthly expense assumed.")

elif housing in ["own", "own place"]:
    print("🟢 Home ownership detected.")

    loan = get_choice("Do you have a home loan? (yes/no): ", ["yes", "no"])

    if loan == "yes":
        p = get_int("Enter loan amount (₹): ")
        r = get_float("Enter interest rate (%): ")
        y = get_int("Enter tenure (years): ")

        emi = emi_calc(p, r, y)

        print(f"📌 Your monthly EMI is calculated as ₹{round(emi)}")

        if emi > income * 0.4:
            warnings.append("⚠ EMI exceeds 40 percent of income (high risk)")

    maintenance = get_choice("Do you pay maintenance? (yes/no): ",
                              ["yes", "no"])

if maintenance == "yes":

    print("\n🏠 MAINTENANCE DETAILS")

    maintenance_mode = get_choice(
        "Choose maintenance type (fixed/estimated): ",
        ["fixed", "estimated"]
    )

    if maintenance_mode == "fixed":

        maintenance_cost = get_int(
            "Enter monthly maintenance cost (₹): "
        )

        expense += maintenance_cost

    else:

        expense += income * 0.03

    print("🟡 Maintenance cost added to expenses.")


# ---------------- LIFESTYLE ----------------
print("\n🍽️ LIFESTYLE SECTION")

def ratio(x, a, b, c):
    if x == "low":
        return a
    if x == "medium":
        return b
    if x == "high":
        return c
    return 0


if mode == "simple":

    travel = get_choice(
        "Travel (low / medium / high): ",
        ["low", "medium", "high"]
    )

    grocery = get_choice(
        "Groceries (low / medium / high): ",
        ["low", "medium", "high"]
    )

    food = get_choice(
        "Food (low / medium / high): ",
        ["low", "medium", "high"]
    )

    print("\n🏥 MEDICAL EXPENSE DETAILS")
    print("This includes medicines, doctor visits, health checkups,")
    print("insurance gaps, emergency treatments, etc.")

    medical = get_choice(
        "Medical expenses (low / medium / high): ",
        ["low", "medium", "high"]
    )

    print("\n📦 MISCELLANEOUS EXPENSE DETAILS")
    print("This includes subscriptions, shopping, entertainment,")
    print("unexpected spending and other personal expenses.")

    misc = get_choice(
        "Miscellaneous expenses (low / medium / high): ",
        ["low", "medium", "high"]
    )

    expense += income * ratio(grocery, 0.08, 0.14, 0.20)
    expense += income * ratio(travel, 0.05, 0.10, 0.15)
    expense += income * ratio(food, 0.08, 0.12, 0.18)
    expense += income * ratio(medical, 0.03, 0.07, 0.12)
    expense += income * ratio(misc, 0.02, 0.05, 0.10)


else:

    print("\n🧾 Enter exact monthly expenses")

    expense += get_int("Enter Travel expense (₹): ")
    expense += get_int("Enter Grocery expense (₹): ")
    expense += get_int("Enter Food expense (₹): ")

    print("\n🏥 Medical expense details")
    print("Include medicines, doctor visits,")
    print("insurance gaps and emergencies.")

    expense += get_int(
        "Enter Medical expense (₹): "
    )

    print("\n📦 Miscellaneous expense details")
    print("Include shopping, subscriptions,")
    print("entertainment and other spending.")

    expense += get_int(
        "Enter Miscellaneous expense (₹): "
    )
# ---------------- CALCULATIONS ----------------
total_expense = expense + emi
savings = max(0, income - total_expense)
if savings > 0:
    goal_months = round(goal_amount/savings,1)
else:
    goal_months = "Not achievable currently"

savings_rate = (savings / income) * 100
expense_rate = (total_expense / income) * 100
emi_rate = (emi / income) * 100


# ---------------- SCORE ----------------
score = 100

if savings_rate < 10:
    score -= 40
elif savings_rate < 20:
    score -= 25
elif savings_rate < 35:
    score -= 10

if emi_rate > 40:
    score -= 30
elif emi_rate > 25:
    score -= 15

if expense_rate > 90:
    score -= 30
elif expense_rate > 75:
    score -= 15

score = max(0, min(100, score))


# ---------------- STATUS ----------------
if score >= 70:
    status = "🟢 GOOD"
elif score >= 40:
    status = "🟡 MODERATE"
else:
    status = "🔴 RISKY"


# ---------------- VISUAL BAR ----------------
def bar(p):
    p = min(100, p)
    return "█" * int(p // 5) + "-" * (20 - int(p // 5))


# ---------------- REPORT ----------------
print("\n===================================================")
print("📊 FINANCIAL REPORT")
print("===================================================")

print(f"👤 Name: {name}")
print(f"💰 Income: ₹{income}")
print(f"📉 Total Expenses: ₹{round(total_expense)}")
print(f"🏦 EMI: ₹{round(emi)}")
print(f"💵 Savings: ₹{round(savings)}")
print(f"📊 Savings Rate: {round(savings_rate,2)}%")


print("\n📊 VISUAL BREAKDOWN")
print("Expenses:", bar(expense_rate), f"{round(expense_rate,2)}%")
print("Savings :", bar(savings_rate), f"{round(savings_rate,2)}%")

# ---------------- HEALTH ----------------
print("\n🧠 FINANCIAL HEALTH REPORT")

print(f"Score  : {score}/100")
print(f"Status : {status}")

print("\n🧠 AI FINANCIAL EXPLANATION")

explanation=[]

if expense_rate > 80:
    explanation.append(
        f"Expenses consume {round(expense_rate,1)}% of income."
    )

if emi_rate > 30:
    explanation.append(
        "EMI exceeds recommended financial limits."
    )

if savings_rate < 20:
    explanation.append(
        "Savings rate is below the ideal range."
    )

if savings <= 0:
    explanation.append(
        "No monthly surplus exists for future investments."
    )

if not explanation:
    explanation.append(
        "Financial indicators appear healthy."
    )

for x in explanation:
    print("•", x)

print(
    "\nRecommendation: Reducing discretionary "
    "expenses and improving savings can "
    "strengthen financial flexibility."
)

# ---------------- GOAL ANALYSIS ----------------

print("\n🎯 GOAL ANALYSIS")

print(
    f"Goal Selected: {goal.capitalize()}"
)

print(
    f"Target Amount: ₹{goal_amount}"
)

print(
    f"Estimated Completion Time: {goal_months}"
)

# ---------------- INVESTMENT ----------------
print("\n📈 INVESTMENT ADVISORY")

if savings <= 0:

    print("No investment recommended due to zero surplus income.")

elif savings_rate < 10:

    print("Priority: Build emergency fund (6–12 months expenses).")

elif savings_rate < 20:

    option="debt"

    print("Suggested: Fixed Deposits + Debt Mutual Funds.")

else:

    if risk=="low":

        option="fd"
        print("Suggested: Safe investments (FDs / Debt Funds).")

    elif risk=="medium":

        option="sip"
        print("Suggested: SIPs + Index Funds.")

    else:

        option="stocks"
        print("Suggested: Stocks + Growth Mutual Funds.")

level, explanation = investment_risk_explainer(option)

print("\n🧠 RISK EXPLANATION")
print(level)
print(explanation)


# ---------------- REASONS ----------------
print("\n🧠 WHY THIS RESULT")

if savings_rate < 20:
    reasons.append("Low savings reduces financial flexibility.")

if emi_rate > 30:
    reasons.append("High EMI reduces monthly liquidity.")

if expense_rate > 80:
    reasons.append("High expenses reduce financial buffer.")

if not reasons:
    reasons.append("Your financial structure is stable.")

for r in reasons:
    print("-", r)


# ---------------- WARNINGS ----------------
if total_expense >= income:
    warnings.append("Expenses exceed or match income.")

if warnings:
    print("\n⚠ WARNINGS")
    for w in warnings:
        print("-", w)


print("\n===================================================")
print("✅ REPORT COMPLETE")
print("===================================================")

# ============================================================
# 📈 1. 10-YEAR SAVINGS GROWTH SIMULATION (MONTE CARLO)
# ============================================================

print("\n===================================================")
print("📈 LONG-TERM WEALTH SIMULATION (10 YEARS)")
print("===================================================")

years = 10
runs = 500

base_savings = savings

if base_savings <= 0:

    print("⚠ Simulation unavailable.")
    print("Reason: Current savings are ₹0.")
    print("Build positive monthly savings before projecting future growth.")

else:

    results = []

    for _ in range(runs):

        value = 0

        for _ in range(years * 12):

            inflation = random.uniform(0.03,0.07)/12
            market_return = random.uniform(0.04,0.12)/12

            value += base_savings

            value = value * (
                1 + market_return - inflation
            )

        results.append(value)

    avg = sum(results)/len(results)
    best = max(results)
    worst = min(results)

    print(f"📊 Expected Savings (10 yrs): ₹{round(avg,2)}")
    print(f"📈 Best Case Scenario: ₹{round(best,2)}")
    print(f"📉 Worst Case Scenario: ₹{round(worst,2)}")

    growth = avg/base_savings

    if growth < 5:
        print("🔴 Low long-term wealth growth potential")

    elif growth < 10:
        print("🟡 Moderate wealth growth potential")

    else:
        print("🟢 Strong compounding potential")

# ============================================================
# 🧠 2. LINEAR PROGRAMMING OPTIMAL BUDGET
# ============================================================

print("\n===================================================")
print("🧠 OPTIMAL BUDGET ALLOCATION (LINEAR PROGRAMMING)")
print("===================================================")

try:

    from scipy.optimize import linprog

    available_income = income - emi

    if available_income <= 0:

        print("⚠ Optimization unavailable.")
        print("Reason: EMI alone exceeds or consumes income.")
        print("Budget restructuring is needed first.")

    else:

        c = [1,1,1,1,1]

        min_grocery = available_income*0.08
        min_travel = available_income*0.05
        min_food = available_income*0.08
        min_medical = available_income*0.03
        min_misc = available_income*0.02

        A = [
            [-1,0,0,0,0],
            [0,-1,0,0,0],
            [0,0,-1,0,0],
            [0,0,0,-1,0],
            [0,0,0,0,-1]
        ]

        b = [
            -min_grocery,
            -min_travel,
            -min_food,
            -min_medical,
            -min_misc
        ]

        bounds=[(0,available_income)]*5

        result = linprog(
            c,
            A_ub=A,
            b_ub=b,
            bounds=bounds,
            method="highs"
        )

        if result.success:

            g,t,f,m,x=result.x

            optimal_expense=sum(result.x)

            optimal_savings=available_income-optimal_expense

            print("📊 Optimal Budget Split Found:")

            print(f"🥦 Groceries: ₹{round(g)}")
            print(f"🚗 Travel: ₹{round(t)}")
            print(f"🍔 Food: ₹{round(f)}")
            print(f"🏥 Medical: ₹{round(m)}")
            print(f"📦 Misc: ₹{round(x)}")

            print(f"\n💰 Max Possible Savings: ₹{round(optimal_savings)}")

        else:

            print("⚠ Optimization failed.")

except Exception as e:

    print("⚠ Optimization module skipped:",e)
    print("Install scipy using:")
    print("python -m pip install scipy")


#------- SAVING USER HISTORY-------

print("\n💾 SAVING USER HISTORY")

filename="finance_history.csv"

file_exists=os.path.isfile(filename)

with open(
    filename,
    "a",
    newline=""
) as file:

    writer=csv.writer(file)

    if not file_exists:

        writer.writerow([
            "Name",
            "Income",
            "Expenses",
            "Savings",
            "SavingsRate",
            "Score",
            "Risk"
        ])

    writer.writerow([
        name,
        income,
        round(total_expense),
        round(savings),
        round(savings_rate,2),
        score,
        risk
    ])

print("🟢 Financial history saved.")

#---------- TREND ANALYSIS ----------

print("\n📈 TREND ANALYSIS")

rows=[]

with open(
    filename,
    "r"
) as file:

    reader=csv.DictReader(file)

    for row in reader:

        if row["Name"]==name:
            rows.append(row)

if len(rows)>=2:

    previous=float(rows[-2]["Savings"])
    current=float(rows[-1]["Savings"])

    diff=current-previous

    if diff>0:

        print(
            f"⬆ Savings increased by ₹{round(diff)}"
        )

    elif diff<0:

        print(
            f"⬇ Savings decreased by ₹{abs(round(diff))}"
        )

    else:

        print(
            "Savings unchanged."
        )

else:

    print(
        "Not enough history available."
    )