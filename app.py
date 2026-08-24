import streamlit as st
from langchain_core.tools import tool
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

st.set_page_config(page_title="Personal Finance AI Agent", page_icon="💰", layout="centered")

@tool
def calculator(expression: str) -> str:
    """Perform basic mathematical calculations."""
    try:
        expression = expression.strip().lower()
        if "% of" in expression:
            percentage, amount = expression.split("% of")
            percentage = float(percentage.strip())
            amount = float(amount.strip())
            return str((percentage / 100) * amount)
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception:
        return "Invalid mathematical expression."

@tool
def emi_calculator(principal: float, annual_interest_rate: float, years: int) -> str:
    """Calculate monthly EMI for a loan."""
    try:
        monthly_rate = (annual_interest_rate / 100) / 12
        months = years * 12
        if monthly_rate == 0:
            emi = principal / months
        else:
            emi = principal * monthly_rate * (1 + monthly_rate) ** months / ((1 + monthly_rate) ** months - 1)
        return f"Monthly EMI: ₹{emi:,.2f}"
    except Exception:
        return "Unable to calculate EMI."

@tool
def sip_calculator(monthly_investment: float, annual_return_rate: float, years: int) -> str:
    """Calculate future value of monthly SIP investments."""
    try:
        monthly_rate = (annual_return_rate / 100) / 12
        months = years * 12
        if monthly_rate == 0:
            future_value = monthly_investment * months
        else:
            future_value = monthly_investment * ((1 + monthly_rate) ** months - 1) / monthly_rate
        return f"Future Value: ₹{future_value:,.2f}"
    except Exception:
        return "Unable to calculate SIP future value."

@tool
def budget_planner(monthly_income: float) -> str:
    """Create a monthly budget using the 50-30-20 rule."""
    try:
        needs = monthly_income * 0.50
        wants = monthly_income * 0.30
        savings = monthly_income * 0.20
        return (
            f"Monthly Income: ₹{monthly_income:,.2f}\n"
            f"Needs (50%): ₹{needs:,.2f}\n"
            f"Wants (30%): ₹{wants:,.2f}\n"
            f"Savings (20%): ₹{savings:,.2f}"
        )
    except Exception:
        return "Unable to create budget plan."

# Cloud-ready replacement for the local Ollama model.
llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash", temperature=0)

finance_agent = create_agent(
    model=llm,
    tools=[calculator, emi_calculator, sip_calculator, budget_planner],
    system_prompt="""
You are a helpful Personal Finance AI Assistant.
You help users with mathematical calculations, loan EMI calculations,
SIP investment calculations, and monthly budget planning.
Use the appropriate tool whenever a calculation is required.
Do not perform financial calculations yourself when a tool is available.
Explain the result clearly. Use Indian Rupees (₹) for financial amounts.
Do not invent missing financial information.
"""
)

st.title("💰 Personal Finance AI Agent")
st.write("Ask me about calculations, EMI, SIP investments, or monthly budgeting.")
st.divider()

user_query = st.text_input(
    "Enter your financial question:",
    placeholder="Example: Calculate EMI for a ₹10 lakh loan at 8% for 20 years"
)
if st.button("Calculate"):
    if not user_query.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Thinking..."):
            try:
                response = finance_agent.invoke({"messages": [{"role": "user", "content": user_query}]})
                raw_answer = response["messages"][-1].content

                if isinstance(raw_answer, list):
                    answer = "".join(
                        item.get("text", "") if isinstance(item, dict) else str(item)
                        for item in raw_answer
                    )
                else:
                    answer = str(raw_answer)

                st.success("Result")
                st.write(answer)

            except Exception as e:
                st.error(f"Something went wrong: {e}")

st.divider()
st.caption("Project 7 - Personal Finance AI Agent | Built with LangChain, Gemini and Streamlit")
