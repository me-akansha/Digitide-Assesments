import math
from datetime import date, timedelta
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Interactive Loan Calculator", page_icon="💸", layout="wide")

# ---- Sidebar / Header ----
st.title("💸 Interactive Loan Calculator")
st.caption("Built with Streamlit — supports multiple inputs, charts, and dataframes")

with st.sidebar:
    st.header("Borrower details")
    name = st.text_input("Full name", placeholder="Akansha Chaudhary")
    age = st.number_input("Age", min_value=0, max_value=120, value=26, step=1)
    start_date = st.date_input("Loan start date", value=date.today())
    st.markdown("---")
    st.subheader("Loan basics")
    purchase_price = st.number_input("Purchase price / Asset value", min_value=0.0, value=1_500_000.0, step=10_000.0, format="%.2f")
    deposit = st.number_input("Deposit / Down payment", min_value=0.0, value=300_000.0, step=10_000.0, format="%.2f")
    loan_amount = st.number_input("Loan amount (principal before fees)", min_value=0.0, value=max(0.0, purchase_price - deposit), step=10_000.0, format="%.2f")
    extra_fees = st.number_input("Processing + other upfront fees (added to principal)", min_value=0.0, value=5_000.0, step=1_000.0, format="%.2f")

    st.subheader("Rate & term")
    rate_pct = st.slider("Annual interest rate (%)", min_value=0.0, max_value=25.0, value=9.5, step=0.1)
    years = st.slider("Duration (years)", min_value=1, max_value=40, value=15, step=1)
    compounding = st.selectbox("Compounding & payment frequency", ["Monthly", "Quarterly", "Yearly"], index=0)

    st.subheader("Extras")
    include_insurance = st.toggle("Add monthly insurance/PMI", value=False, help="Adds a fixed monthly fee to EMI")
    insurance_amt = st.number_input("Monthly insurance amount", min_value=0.0, value=1000.0, step=100.0, format="%.2f", disabled=not include_insurance)
    consider_part_prepay = st.toggle("Consider fixed extra prepayment (EMI + extra)", value=False)
    extra_payment = st.number_input("Extra payment per period", min_value=0.0, value=0.0, step=100.0, format="%.2f", disabled=not consider_part_prepay)
    gst_toggle = st.checkbox("Include 18% GST on fees", value=False)

    st.markdown("---")
    st.caption("Tip: Use the checkboxes below to toggle charts and tables.")
    
# helpers
def periods_per_year(mode: str) -> int:
    return {"Monthly": 12, "Quarterly": 4, "Yearly": 1}[mode]

def pmt(rate_per_period: float, n_periods: int, principal: float) -> float:
    # Standard amortizing loan payment (negative sign removed for clarity)
    if n_periods == 0:
        return 0.0
    if abs(rate_per_period) < 1e-9:
        return principal / n_periods
    factor = (1 + rate_per_period) ** n_periods
    return principal * rate_per_period * factor / (factor - 1)

def amortization_schedule(principal: float, apr: float, years: int, freq: str, start_date: date, monthly_fee: float = 0.0, extra_per_period: float = 0.0):
    """Return schedule DataFrame with period, date, payment, interest, principal, balance."""
    m = periods_per_year(freq)
    n = years * m
    r = (apr / 100.0) / m

    base_payment = pmt(r, n, principal)
    total_payment = base_payment + monthly_fee

    # Build schedule iteratively to handle extra payments
    records = []
    bal = principal
    current_date = start_date
    period_delta = {
        "Monthly": 30,
        "Quarterly": 91,
        "Yearly": 365
    }[freq]

    period = 0
    while bal > 1e-6 and period < 1000 * n:  # safety cap
        period += 1
        interest = bal * r
        principal_pay = base_payment - interest

        # Apply extra payment (towards principal)
        total_paid_this_period = base_payment + extra_per_period
        principal_component = principal_pay + extra_per_period

        if principal_component > bal:
            principal_component = bal
            total_paid_this_period = interest + principal_component  # final period

        bal -= principal_component
        row_date = current_date
        current_date = row_date + timedelta(days=period_delta)

        records.append({
            "Period": period,
            "Date": row_date,
            "Payment (base)": round(base_payment, 2),
            "Extra Payment": round(extra_per_period, 2),
            "Payment (total excl. fees)": round(total_paid_this_period, 2),
            "Monthly Fee": round(monthly_fee, 2),
            "Payment (grand total)": round(total_paid_this_period + monthly_fee, 2),
            "Interest": round(interest, 2),
            "Principal": round(principal_component, 2),
            "Balance": round(bal, 2),
        })

    df = pd.DataFrame(records)
    return df, round(base_payment, 2), period

# compute principal including fees/GST
principal_base = loan_amount + extra_fees
if gst_toggle:
    principal_base += 0.18 * extra_fees

# schedule
schedule_df, base_emi, periods = amortization_schedule(
    principal=principal_base,
    apr=rate_pct,
    years=years,
    freq=compounding,
    start_date=start_date,
    monthly_fee=(insurance_amt if include_insurance else 0.0),
    extra_per_period=(extra_payment if consider_part_prepay else 0.0)
)

# KPIs
total_interest = float(schedule_df["Interest"].sum()) if not schedule_df.empty else 0.0
total_principal = float(schedule_df["Principal"].sum()) if not schedule_df.empty else 0.0
total_fees = float(schedule_df["Monthly Fee"].sum()) if not schedule_df.empty else 0.0
grand_total_paid = float(schedule_df["Payment (grand total)"].sum()) if not schedule_df.empty else 0.0

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Base EMI / Periodic Payment", f"₹ {base_emi:,.2f}")
kpi2.metric("Total Interest", f"₹ {total_interest:,.2f}")
kpi3.metric("Total Principal", f"₹ {total_principal:,.2f}")
kpi4.metric("Total Paid (incl. fees)", f"₹ {grand_total_paid:,.2f}")

st.markdown("---")

left, right = st.columns([3,2], vertical_alignment="top")

with left:
    st.subheader("Amortization schedule")
    st.dataframe(schedule_df, use_container_width=True, height=420)
    csv = schedule_df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download schedule (CSV)", csv, file_name="amortization_schedule.csv", mime="text/csv")

with right:
    st.subheader("Visualization controls")
    show_balance = st.checkbox("Show Balance over time", value=True)
    show_interest = st.checkbox("Show Interest per period", value=True)
    show_pie = st.checkbox("Show Principal vs Interest pie", value=True)
    show_yearly = st.checkbox("Show Yearly totals", value=False)

# Charts
if not schedule_df.empty:
    if show_balance:
        fig_bal = px.line(schedule_df, x="Date", y="Balance", title="Outstanding Balance Over Time")
        st.plotly_chart(fig_bal, use_container_width=True)

    if show_interest:
        fig_int = px.bar(schedule_df, x="Date", y="Interest", title="Interest Per Period")
        st.plotly_chart(fig_int, use_container_width=True)

    if show_pie:
        fig_pie = px.pie(
            names=["Principal", "Interest", "Fees"],
            values=[total_principal, total_interest, total_fees],
            title="Breakdown of Payments"
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    if show_yearly:
        sdf = schedule_df.copy()
        sdf["Year"] = pd.to_datetime(sdf["Date"]).dt.year
        yearly = sdf.groupby("Year")[["Interest", "Principal"]].sum().reset_index()
        fig_year = px.bar(yearly, x="Year", y=["Principal", "Interest"], barmode="group", title="Yearly Principal vs Interest")
        st.plotly_chart(fig_year, use_container_width=True)

# Footer
st.markdown("---")
st.caption(f"Prepared for: **{name or '—'}**, Age: **{age}**")
st.caption("This tool is for educational purposes and estimates only. Please consult your lender for exact terms.")