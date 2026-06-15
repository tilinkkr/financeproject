# Simple Personal Finance Tracker

I built this project because I wanted a lightweight way to track my budget without setting up a complex database. I intentionally save the transaction data to a CSV file, so the output stays universally compatible with Microsoft Excel and Google Drive.

## Features

- Log income and expense transactions with an amount, category, date, and optional note
- Filter transactions by category, type, or date range
- View total income, total expenses, net balance, and the top spending category
- Explore spending by category with an interactive Plotly pie chart
- Set a monthly budget and get a dynamic safe daily spending insight

## Tech Stack

- **Python** for the application
- **Streamlit** for the user interface
- **Pandas** for high-efficiency data loading, filtering, grouping, and calculations
- **Plotly Express** for interactive charting
- **CSV** for simple, portable transaction storage

## How to Run Locally

1. Clone the repository:

   ```bash
   git clone https://github.com/tilinkkr/financeproject.git
   cd financeproject
   ```

2. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Start the app:

   ```bash
   streamlit run app.py
   ```

4. Open the local URL shown by Streamlit, usually:

   ```text
   http://localhost:8501
   ```

The app creates `transactions.csv` automatically when it first runs.

## Deployment

### Vercel

I included a separate browser-based version in `index.html` for Vercel. It has the transaction form, filters, summary metrics, Plotly chart, budget insight, and CSV import/export. Transactions are stored in the browser's local storage because Vercel Functions do not provide a persistent writable filesystem.

[Deploy to Vercel](https://vercel.com/new/clone?repository-url=https://github.com/tilinmys/financeproject)

The Vercel version does not require a build command. `vercel.json` serves `index.html`, and `.vercelignore` prevents Vercel from treating the Streamlit entry point as a Python Function.

### Render

I also included a `render.yaml` Blueprint so the original Python and Streamlit app can run as a Render web service.

[Deploy to Render](https://dashboard.render.com/blueprint/new?repo=https://github.com/tilinmys/financeproject)

The Blueprint:

- Installs the packages from `requirements.txt`
- Starts Streamlit on Render's assigned port
- Uses the Singapore region
- Redeploys automatically when I push to `main`
- Stores `transactions.csv` on a persistent disk at `/var/data`

The persistent disk requires a paid Render service. I use the Starter plan in the Blueprint because Render's free filesystem is temporary and would lose saved transactions after a restart or redeploy.

## Next Steps

I might add automated keyword-based transaction categorization in the future, so notes like "Uber" or "Whole Foods" can suggest a category automatically.
