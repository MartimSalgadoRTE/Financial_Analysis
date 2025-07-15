# crypto_analysis.py
import requests
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime

def fetch_data():
    ids = "bitcoin,ethereum,solana,ripple,polkadot,cardano,avalanche-2"
    url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={ids}&price_change_percentage=30d,90d,180d"
    response = requests.get(url)
    return pd.DataFrame(response.json())

def generate_report(df):
    df = df[['name', 'symbol', 'current_price', 'price_change_percentage_30d_in_currency',
             'price_change_percentage_90d_in_currency', 'price_change_percentage_180d_in_currency']]

    df.set_index('symbol')[['price_change_percentage_30d_in_currency',
                            'price_change_percentage_90d_in_currency',
                            'price_change_percentage_180d_in_currency']].plot(kind='bar', figsize=(12, 6))
    plt.title("Crypto Returns (30D, 90D, 180D)")
    plt.ylabel("% Return")
    plt.tight_layout()
    plt.savefig("crypto_chart.png")
    plt.close()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Quarterly Crypto Capital Flow Report", ln=1, align="C")
    pdf.ln(10)
    for _, row in df.iterrows():
        line = f"{row['name']} ({row['symbol']}): Price ${row['current_price']}, 30D: {row['price_change_percentage_30d_in_currency']:.2f}%, 90D: {row['price_change_percentage_90d_in_currency']:.2f}%, 180D: {row['price_change_percentage_180d_in_currency']:.2f}%"
        pdf.cell(200, 10, txt=line, ln=1)
    pdf.image("crypto_chart.png", x=10, y=None, w=190)
    pdf.output("crypto_report.pdf")

if __name__ == "__main__":
    data = fetch_data()
    generate_report(data)
