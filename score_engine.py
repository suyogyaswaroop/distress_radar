import yfinance as yf
import pandas as pd
import time

def get_latest(series, field):
    """Safely extract the most recent value of a financial field"""
    try:
        return float(series.loc[field].iloc[0])
    except:
        return None

def calculate_z_score(ticker):
    """
    Calculate Altman Z-Score for a given NSE ticker
    Z = 1.2(X1) + 1.4(X2) + 3.3(X3) + 0.6(X4) + 1.0(X5)
    """
    
    stock = yf.Ticker(ticker)
    time.sleep(1.5)

    
    try:
        bs = stock.balance_sheet
        inc = stock.income_stmt
        info = stock.info
        
        # --- Extract raw values ---
        working_capital     = get_latest(bs, 'Working Capital')
        total_assets        = get_latest(bs, 'Total Assets')
        retained_earnings   = get_latest(bs, 'Retained Earnings')
        total_liabilities   = get_latest(bs, 'Total Liabilities Net Minority Interest')
        ebit                = get_latest(inc, 'EBIT')
        total_revenue       = get_latest(inc, 'Total Revenue')
        market_cap          = info.get('marketCap', None)
        
        # --- Validate we have everything ---
        values = {
    'Working Capital': working_capital,
    'Total Assets': total_assets,
    'Retained Earnings': retained_earnings,
    'Total Liabilities': total_liabilities,
    'EBIT': ebit,
    'Total Revenue': total_revenue,
    'Market Cap': market_cap
     }
        
        missing = [k for k, v in values.items() if v is None]
        if missing:
            print(f"  Missing fields for {ticker}: {missing}")
            return None
        
        # Guard against division by zero
        if total_assets == 0 or total_liabilities == 0:
            print(f"  Skipping {ticker}: zero value in denominator")
            return None
        
        # --- Calculate Z-Score components ---
        X1 = working_capital / total_assets           # Liquidity
        X2 = retained_earnings / total_assets         # Cumulative profitability
        X3 = ebit / total_assets                      # Operating efficiency
        X4 = market_cap / total_liabilities           # Market vs debt
        X5 = total_revenue / total_assets             # Asset utilisation
        
        Z = (1.2 * X1) + (1.4 * X2) + (3.3 * X3) + (0.6 * X4) + (1.0 * X5)
        
        # --- Classify ---
        if Z > 2.99:
            zone = "Safe"
        elif Z > 1.81:
            zone = "Grey"
        else:
            zone = "Distress"
        
        return {
            'Ticker': ticker,
            'Company': info.get('longName', ticker),
            'Sector': info.get('sector', 'N/A'),
            'Z_Score': round(Z, 3),
            'Zone': zone,
            'X1_Liquidity': round(X1, 3),
            'X2_Profitability': round(X2, 3),
            'X3_Efficiency': round(X3, 3),
            'X4_Leverage': round(X4, 3),
            'X5_Asset_Use': round(X5, 3),
            'Market_Cap_Cr': round(market_cap / 1e7, 1)  # Convert to Crores
        }
        
    except Exception as e:
        print(f"  Error processing {ticker}: {e}")
        return None


def score_multiple(tickers):
    """Score a list of companies and return a clean DataFrame"""
    
    results = []
    
    for ticker in tickers:
        print(f"Processing {ticker}...")
        result = calculate_z_score(ticker)
        if result:
            results.append(result)
    
    if not results:
        return pd.DataFrame()
    
    df = pd.DataFrame(results)
    df = df.sort_values('Z_Score', ascending=True)  # Distressed companies first
    return df


# --- Test run ---
if __name__ == "__main__":
    
    # A mix of sectors and known distress cases
    test_tickers = [
    # Stable / Safe zone expected
    "RELIANCE.NS",
    "TCS.NS",
    "HINDUNILVR.NS",
    "INFY.NS",
    "WIPRO.NS",
    "NESTLEIND.NS",

    # Grey zone expected
    "TATASTEEL.NS",
    "ONGC.NS",
    "NTPC.NS",

    # Distress zone expected
    "JPASSOCIAT.NS",
    "IDEA.NS",
    "STERLINBIO.NS",
    "JETAIRWAYS.NS",
]
   
    df = score_multiple(test_tickers)
    
    if not df.empty:
        print("\n" + "="*60)
        print("DISTRESS RADAR — RESULTS")
        print("="*60)
        print(df[['Company', 'Z_Score', 'Zone', 'Sector']].to_string(index=False))
        print("\nFull results saved to output/distress_report.csv")
        
        import os
        os.makedirs('output', exist_ok=True)
        df.to_csv('output/distress_report.csv', index=False)
