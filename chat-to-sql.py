import os
import sqlite3
import traceback
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import sqlparse
import re
from dotenv import load_dotenv

# --- Load environment variables ---
load_dotenv()

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

# --- Flask app setup ---
app = Flask(__name__)
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'stocks.db')

CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:8000",
            "http://127.0.0.1:8000",
            "http://localhost:5500",
            "http://127.0.0.1:5500"
        ]
    }
})

# --- System prompt for the AI ---
SYSTEM_PROMPT = """
You are a helpful assistant that converts natural language filters into SQL WHERE clause conditions ONLY.

- Only return the condition part. For example: 1D Returns > 34
- Do NOT include SELECT, FROM, WHERE, or any table names.
- Always match the column names exactly from this list:

"High Gap %","1D Returns","Rel Ret vs Nifty50 1D","Low Gap %","1W Returns","Rel Ret vs Nifty50 1W","Close Price 1W","1M Returns","Rel Ret vs Nifty50 1M","Close Price 1M","3M Returns","Rel Ret vs Nifty50 3M","Close Price 3M","6M Returns","Rel Ret vs Nifty50 6M","Half Yr Close","YTD Returns","Rel Ret vs Nifty50 YTD","1Y Close","1Y Returns","Rel Ret vs Nifty50 1Y","Day Open Rs","3Y Returns","Rel Ret vs Nifty50 3Y","Day Close Rs","5Y Returns","Rel Ret vs Nifty50 5Y","Day Low Rs","5Y CAGR Returns","Rel Ret vs BSE Sensex 1D","Day High Rs","3Y CAGR Returns","Rel Ret vs BSE Sensex 1W","Previous Day Close","Rel Ret vs BSE Sensex 1M","Previous Day Low","Rel Ret vs BSE Sensex 3M","Previous Day High","Rel Ret vs BSE Sensex 6M","1M High","Rel Ret vs BSE Sensex YTD","1M Low","Rel Ret vs BSE Sensex 1Y","3M High","Rel Ret vs BSE Sensex 3Y","3M Low","Rel Ret vs BSE Sensex 5Y","6M High","Rel Ret vs NiftyIT 1D","6M Low","Rel Ret vs NiftyIT 1W","Current Price","Rel Ret vs NiftyIT 1M","Rel Ret vs NiftyIT 3M","Rel Ret vs NiftyIT 6M","Rel Ret vs NiftyIT YTD","Rel Ret vs NiftyIT 1Y","Rel Ret vs NiftyIT 3Y","Rel Ret vs NiftyIT 5Y","Rel Ret vs NiftyBank 1D","Rel Ret vs NiftyBank 1W","Rel Ret vs NiftyBank 1M","Rel Ret vs NiftyBank 3M","Rel Ret vs NiftyBank 6M","Rel Ret vs NiftyBank YTD","Rel Ret vs NiftyBank 1Y","Rel Ret vs NiftyBank 3Y","Rel Ret vs NiftyBank 5Y","Rel Ret vs BSE 500 1D","Rel Ret vs BSE 500 1W","Rel Ret vs BSE 500 1M","Rel Ret vs BSE 500 3M","Rel Ret vs BSE 500 6M","Rel Ret vs BSE 500 YTD","Rel Ret vs BSE 500 1Y","Rel Ret vs BSE 500 3Y","Rel Ret vs BSE 500 5Y","Rel Ret vs Nifty Smallcap250 1D","Rel Ret vs Nifty Smallcap250 1W","Rel Ret vs Nifty Smallcap250 1M","Rel Ret vs Nifty Smallcap250 3M","Rel Ret vs Nifty Smallcap250 6M","Rel Ret vs Nifty Smallcap250 YTD","Rel Ret vs Nifty Smallcap250 1Y","Rel Ret vs Nifty Smallcap250 3Y","Rel Ret vs Nifty Smallcap250 5Y","Rel Ret vs Nifty Midcap100 1D","Rel Ret vs Nifty Midcap100 1W","Rel Ret vs Nifty Midcap100 1M","Rel Ret vs Nifty Midcap100 3M","Rel Ret vs Nifty Midcap100 6M","Rel Ret vs Nifty Midcap100 YTD","Rel Ret vs Nifty Midcap100 1Y","Rel Ret vs Nifty Midcap100 3Y","Rel Ret vs Nifty Midcap100 5Y"

- Respond ONLY with the expression, e.g.:
"1D Returns" > 34
"""

# --- SQL execution helper ---
def execute_sql(sql_query):
    print(f"DEBUG: execute_sql connecting to DB at {os.path.abspath(DATABASE_PATH)}")
    conn = None
    try:
        if not os.path.exists(DATABASE_PATH):
            print(f"DEBUG: Database file not found at {os.path.abspath(DATABASE_PATH)}")
            return None, "Database file 'stocks.db' not found."

        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        print(f"DEBUG: execute_sql fetched {len(rows)} rows")
        return [dict(row) for row in rows], None
    except sqlite3.Error as e:
        if "no such table: stocks" in str(e):
            return None, "Database error: The 'stocks' table does not exist."
        return None, f"Database error: {str(e)}"
    except Exception as e:
        traceback.print_exc()
        return None, f"Unexpected error: {str(e)}"
    finally:
        if conn:
            conn.close()

# --- Main API route ---
@app.route('/api/chat-to-sql', methods=['POST'])
def chat_to_sql():
    # Validate env vars
    if not AZURE_OPENAI_API_KEY or not AZURE_OPENAI_ENDPOINT or not AZURE_OPENAI_DEPLOYMENT_NAME:
        return jsonify({"detail": "Server is misconfigured. Missing OpenAI environment variables."}), 500

    # Load request
    data = request.get_json()
    if not data or 'naturalLanguage' not in data:
        return jsonify({"detail": "'naturalLanguage' field is required."}), 400

    natural_language_query = data['naturalLanguage'].strip()
    if not natural_language_query:
        return jsonify({"detail": "Query cannot be empty."}), 400

    # --- Call Azure OpenAI ---
    try:
        from openai import AzureOpenAI
        client = AzureOpenAI(
            api_key=AZURE_OPENAI_API_KEY,
            api_version=AZURE_OPENAI_API_VERSION,
            azure_endpoint=AZURE_OPENAI_ENDPOINT
        )

        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": natural_language_query}
            ],
            temperature=0.1,
            max_tokens=150
        )

        raw_sql = response.choices[0].message.content.strip()
        if raw_sql.lower().startswith("```sql"):
            raw_sql = raw_sql[len("```sql"):].strip()
        if raw_sql.endswith("```"):
            raw_sql = raw_sql[:-len("```")].strip()

        where_clause = raw_sql.strip().strip(";")
        execution_sql = f"SELECT * FROM stocks WHERE {where_clause}"
        response_sql = where_clause
        print(f"Generated SQL Query: {execution_sql}")
        # Strip single-quoted and double-quoted string literals for response
        clean_sql = re.sub(r"['\"]([^'\"]*)['\"]", r"\1", response_sql)

    except Exception as e:
        traceback.print_exc()
        return jsonify({"detail": f"OpenAI API error: {str(e)}"}), 502

    # --- Execute SQL ---
    results, error = execute_sql(execution_sql)
    if error:
        return jsonify({"detail": error, "sql_generated": clean_sql}), 400

    return jsonify({
        "sql": clean_sql,
        "results": results
    })

# --- Run the server ---
if __name__ == '__main__':
    print(f"Starting Flask server on http://127.0.0.1:5001")
    print(f"Database path: {DATABASE_PATH}")
    if not os.path.exists(DATABASE_PATH):
        print(f"Warning: Database not found at {DATABASE_PATH}")
    app.run(debug=True, port=5001, host='127.0.0.1')
