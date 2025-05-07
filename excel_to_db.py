import pandas as pd
import sqlite3
import os

# Path to Excel file and DB
EXCEL_PATH = r"C:\Users\Prakarsh\Desktop\ET Screener\sample_data.xlsx"
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'stocks.db')

def import_excel_to_db():
    try:
        # Read Excel
        df = pd.read_excel(EXCEL_PATH)

        # Strip column names and standardize
        df.columns = df.columns.str.strip()

        # Connect to DB
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Clear existing data
        cursor.execute("DELETE FROM stocks")

        # Insert data
        df.to_sql("stocks", conn, if_exists='append', index=False)

        conn.commit()
        print("Data successfully imported from Excel to database.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    import_excel_to_db()
