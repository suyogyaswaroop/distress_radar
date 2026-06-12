import yfinance as yf
import pandas as pd

def get_financials(ticker):
    """
    Fetch key financial data for a given NSE ticker
    ticker format for Indian stocks: "RELIANCE.NS" or "TATAMOTORS.NS"
    """
    
    stock = yf.Ticker(ticker)
    
    try:
        # Balance Sheet
        balance_sheet = stock.balance_sheet
        
        # Income Statement
        income_stmt = stock.income_stmt
        
        # Market Data
        info = stock.info
        
        print(f"\n--- {ticker} ---")
        print(f"Company: {info.get('longName', 'N/A')}")
        print(f"Market Cap: {info.get('marketCap', 'N/A')}")
        print(f"\nBalance Sheet Columns Available:")
        print(balance_sheet.index.tolist())
        print(f"\nIncome Statement Columns Available:")
        print(income_stmt.index.tolist())
        
        return balance_sheet, income_stmt, info
    
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return None, None, None

# Test with one company first
if __name__ == "__main__":
    bs, inc, info = get_financials("RELIANCE.NS")

