import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'stocks.db')

def create_db():
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Drop table if it exists
        cursor.execute("DROP TABLE IF EXISTS stocks")

        # Create the stocks table
        cursor.execute("""
        CREATE TABLE stocks (
            symbol TEXT PRIMARY KEY,
            name TEXT,
            sector TEXT,
            "High Gap %" REAL,
            "1D Returns" REAL,
            "Rel Ret vs Nifty50 1D" REAL,
            "Low Gap %" REAL,
            "1W Returns" REAL,
            "Rel Ret vs Nifty50 1W" REAL,
            "Close Price 1W" REAL,
            "1M Returns" REAL,
            "Rel Ret vs Nifty50 1M" REAL,
            "Close Price 1M" REAL,
            "3M Returns" REAL,
            "Rel Ret vs Nifty50 3M" REAL,
            "Close Price 3M" REAL,
            "6M Returns" REAL,
            "Rel Ret vs Nifty50 6M" REAL,
            "Half Yr Close" REAL,
            "YTD Returns" REAL,
            "Rel Ret vs Nifty50 YTD" REAL,
            "1Y Close" REAL,
            "1Y Returns" REAL,
            "Rel Ret vs Nifty50 1Y" REAL,
            "Day Open Rs" REAL,
            "3Y Returns" REAL,
            "Rel Ret vs Nifty50 3Y" REAL,
            "Day Close Rs" REAL,
            "5Y Returns" REAL,
            "Rel Ret vs Nifty50 5Y" REAL,
            "Day Low Rs" REAL,
            "5Y CAGR Returns" REAL,
            "Rel Ret vs BSE Sensex 1D" REAL,
            "Day High Rs" REAL,
            "3Y CAGR Returns" REAL,
            "Rel Ret vs BSE Sensex 1W" REAL,
            "Previous Day Close" REAL,
            "Rel Ret vs BSE Sensex 1M" REAL,
            "Previous Day Low" REAL,
            "Rel Ret vs BSE Sensex 3M" REAL,
            "Previous Day High" REAL,
            "Rel Ret vs BSE Sensex 6M" REAL,
            "1M High" REAL,
            "Rel Ret vs BSE Sensex YTD" REAL,
            "1M Low" REAL,
            "Rel Ret vs BSE Sensex 1Y" REAL,
            "3M High" REAL,
            "Rel Ret vs BSE Sensex 3Y" REAL,
            "3M Low" REAL,
            "Rel Ret vs BSE Sensex 5Y" REAL,
            "6M High" REAL,
            "Rel Ret vs NiftyIT 1D" REAL,
            "6M Low" REAL,
            "Rel Ret vs NiftyIT 1W" REAL,
            "Current Price" REAL,
            "Rel Ret vs NiftyIT 1M" REAL,
            "Rel Ret vs NiftyIT 3M" REAL,
            "Rel Ret vs NiftyIT 6M" REAL,
            "Rel Ret vs NiftyIT YTD" REAL,
            "Rel Ret vs NiftyIT 1Y" REAL,
            "Rel Ret vs NiftyIT 3Y" REAL,
            "Rel Ret vs NiftyIT 5Y" REAL,
            "Rel Ret vs NiftyBank 1D" REAL,
            "Rel Ret vs NiftyBank 1W" REAL,
            "Rel Ret vs NiftyBank 1M" REAL,
            "Rel Ret vs NiftyBank 3M" REAL,
            "Rel Ret vs NiftyBank 6M" REAL,
            "Rel Ret vs NiftyBank YTD" REAL,
            "Rel Ret vs NiftyBank 1Y" REAL,
            "Rel Ret vs NiftyBank 3Y" REAL,
            "Rel Ret vs NiftyBank 5Y" REAL,
            "Rel Ret vs BSE 500 1D" REAL,
            "Rel Ret vs BSE 500 1W" REAL,
            "Rel Ret vs BSE 500 1M" REAL,
            "Rel Ret vs BSE 500 3M" REAL,
            "Rel Ret vs BSE 500 6M" REAL,
            "Rel Ret vs BSE 500 YTD" REAL,
            "Rel Ret vs BSE 500 1Y" REAL,
            "Rel Ret vs BSE 500 3Y" REAL,
            "Rel Ret vs BSE 500 5Y" REAL,
            "Rel Ret vs Nifty Smallcap250 1D" REAL,
            "Rel Ret vs Nifty Smallcap250 1W" REAL,
            "Rel Ret vs Nifty Smallcap250 1M" REAL,
            "Rel Ret vs Nifty Smallcap250 3M" REAL,
            "Rel Ret vs Nifty Smallcap250 6M" REAL,
            "Rel Ret vs Nifty Smallcap250 YTD" REAL,
            "Rel Ret vs Nifty Smallcap250 1Y" REAL,
            "Rel Ret vs Nifty Smallcap250 3Y" REAL,
            "Rel Ret vs Nifty Smallcap250 5Y" REAL,
            "Rel Ret vs Nifty Midcap100 1D" REAL,
            "Rel Ret vs Nifty Midcap100 1W" REAL,
            "Rel Ret vs Nifty Midcap100 1M" REAL,
            "Rel Ret vs Nifty Midcap100 3M" REAL,
            "Rel Ret vs Nifty Midcap100 6M" REAL,
            "Rel Ret vs Nifty Midcap100 YTD" REAL,
            "Rel Ret vs Nifty Midcap100 1Y" REAL,
            "Rel Ret vs Nifty Midcap100 3Y" REAL,
            "Rel Ret vs Nifty Midcap100 5Y" REAL
        )
        """)
        
        conn.commit()
        print(f"Database '{DATABASE_PATH}' created successfully with 'stocks' table.")
    except sqlite3.Error as e:
        print(f"Database Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    create_db()
