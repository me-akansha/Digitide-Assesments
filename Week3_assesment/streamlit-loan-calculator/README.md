# 💸 Interactive Loan Calculator (Streamlit)

A polished Streamlit application to explore EMI schedules and visualize loan repayments with multiple inputs and charts.

## Features
- Text, numbers, sliders, checkboxes, toggles, and date inputs
- Supports deposit, fees (with optional GST), insurance, and extra prepayments
- Multiple interactive charts (balance, interest, pie, yearly totals)
- Full amortization schedule with CSV download

## Quickstart (Local)

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Cloud

1. Create a **new GitHub repo** and upload this folder.
2. Go to **streamlit.io -> Deploy an app**.
3. Choose your repo, set:
   - **Main file path**: `app.py`
   - **Python version**: 3.10+
4. Click **Deploy**.

### What to submit
- **GitHub Repo URL**: e.g., `https://github.com/<your-username>/streamlit-loan-calculator`
- **Live App URL**: e.g., `https://<your-app-name>.streamlit.app`

## Project structure
```
streamlit-loan-calculator/
├─ app.py
├─ requirements.txt
└─ .streamlit/
   └─ config.toml
```

## Notes
- EMI formula used: standard amortization with exact extra prepayments per period.
- Frequencies supported: monthly, quarterly, yearly.