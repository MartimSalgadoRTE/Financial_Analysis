# crypto_analysis.py

import requests
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime
#import openai
from openai import OpenAI
import os

# Fetch market data
def fetch_data():
    ids = "bitcoin,ethereum,solana,ripple,polkadot,cardano,avalanche-2"
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        'vs_currency': 'usd',
        'ids': ids,
        'price_change_percentage': '30d'
    }
    response = requests.get(url, params=params)
    return pd.DataFrame(response.json())

# Simulated 90D and 180D return data
def simulate_long_returns():
    return {
        "bitcoin": {"90d": 18.5, "180d": 31.7},
        "ethereum": {"90d": 23.4, "180d": 27.2},
        "solana": {"90d": 7.9, "180d": 15.3},
        "ripple": {"90d": 21.3, "180d": 8.5},
        "cardano": {"90d": 10.1, "180d": 12.4},
        "avalanche-2": {"90d": 19.8, "180d": 26.1},
        "polkadot": {"90d": 6.2, "180d": 11.7}
    }

# Generate executive summary using OpenAI GPT-4o
def generate_summary(crypto_data):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    prompt = f\"\"\"
You are a strategic analyst writing an executive summary for a quarterly crypto capital flow report.

Use the following crypto data to highlight short-term winners, long-term potential, capital efficiency, and quantum disruption risk. Write 1 page (around 150-200 words) in a sharp, insightful tone.

Data format: [symbol, 30D return, 90D return, 180D return, overflow score, momentum score, MA slope, quantum risk]

Data:
{crypto_data}

Your audience is Martim Salgado, an advanced investor and strategist. Write clearly, analytically, and with conviction.
\"\"\"

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    return response.choices[0].message.content

# Generate report
def generate_report(df, long_returns):
    df = df[['id', 'name', 'symbol', 'current_price', 'price_change_percentage_30d_in_currency']]
    df.rename(columns={'price_change_percentage_30d_in_currency': '30D'}, inplace=True)

    records = []
    summary_input = []
    for _, row in df.iterrows():
        rid = row['id']
        r90 = long_returns.get(rid, {}).get("90d", float("nan"))
        r180 = long_returns.get(rid, {}).get("180d", float("nan"))
        price = row['current_price']
        r30 = row['30D']
        overflow = round(1.0 + (2.0 - (r30 / (r90 if r90 else 1))), 2)
        momentum = round(1.05 + (r30 / 100), 2)
        slope = round((r180 - r90) / 90 if r90 else 0, 2)
        quantum = "High" if row['symbol'] in ['btc', 'eth'] else ("Low" if row['symbol'] == 'avax' else "Moderate")

        summary_input.append([row['symbol'], r30, r90, r180, overflow, momentum, slope, quantum])

        records.append({
            "name": row['name'], "symbol": row['symbol'], "price": price,
            "30D": r30, "90D": r90, "180D": r180,
            "overflow": overflow, "momentum": momentum,
            "slope": slope, "quantum_risk": quantum
        })

    result_df = pd.DataFrame(records)

    # Chart
    result_df.set_index("symbol")[["30D", "90D", "180D"]].plot(kind="bar", figsize=(12, 6))
    plt.title("Crypto Returns Over Time")
    plt.ylabel("Return (%)")
    plt.tight_layout()
    plt.savefig("returns_chart.png")
    plt.close()

    # Generate GPT-4o executive summary
    summary_text = generate_summary(summary_input)

    # Build PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Quarterly Crypto Capital Flow Report", ln=True, align="C")

    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.multi_cell(0, 8, summary_text)

    pdf.ln(5)
    pdf.set_font("Arial", size=10)
    for _, row in result_df.iterrows():
        line = f"{row['name']} ({row['symbol']}): Price ${row['price']}, 30D: {row['30D']}%, 90D: {row['90D']}%, 180D: {row['180D']}%, Overflow: {row['overflow']}, Momentum: {row['momentum']}, Slope: {row['slope']}, Quantum Risk: {row['quantum_risk']}"
        pdf.multi_cell(0, 8, line)

    pdf.image("returns_chart.png", x=10, y=None, w=190)
    pdf.output("crypto_report.pdf")

if __name__ == "__main__":
    data = fetch_data()
    long_returns = simulate_long_returns()
    generate_report(data, long_returns)
