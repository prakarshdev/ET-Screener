const express = require('express');
const cors = require('cors');
const sqlite3 = require('sqlite3').verbose();
const { OpenAIClient, AzureKeyCredential } = require('@azure/openai');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 5001;
const DATABASE_PATH = `${__dirname}/stocks.db`;

app.use(cors({
  origin: [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://localhost:5500',
    'http://127.0.0.1:5500'
  ]
}));
app.use(express.json());

if (!process.env.AZURE_OPENAI_API_KEY || !process.env.AZURE_OPENAI_ENDPOINT || !process.env.AZURE_OPENAI_DEPLOYMENT_NAME) {
  console.error('Missing Azure OpenAI environment variables.');
  process.exit(1);
}

const client = new OpenAIClient(
  process.env.AZURE_OPENAI_ENDPOINT,
  new AzureKeyCredential(process.env.AZURE_OPENAI_API_KEY)
);
const deploymentName = process.env.AZURE_OPENAI_DEPLOYMENT_NAME;

const SYSTEM_PROMPT = `
You are a helpful assistant that converts natural language filters into SQL WHERE clause conditions ONLY.

- Only return the condition part. For example: 1D Returns > 34
- Do NOT include SELECT, FROM, WHERE, or any table names.
- Always match the column names exactly from this list:
"High Gap %","1D Returns","Rel Ret vs Nifty50 1D","Low Gap %","1W Returns","Rel Ret vs Nifty50 1W","Close Price 1W","1M Returns","Rel Ret vs Nifty50 1M","Close Price 1M","3M Returns","Rel Ret vs Nifty50 3M","Close Price 3M","6M Returns","Rel Ret vs Nifty50 6M","Half Yr Close","YTD Returns","Rel Ret vs Nifty50 YTD","1Y Close","1Y Returns","Rel Ret vs Nifty50 1Y","Day Open Rs","3Y Returns","Rel Ret vs Nifty50 3Y","Day Close Rs","5Y Returns","Rel Ret vs Nifty50 5Y","Day Low Rs","5Y CAGR Returns","Rel Ret vs BSE Sensex 1D","Day High Rs","3Y CAGR Returns","Rel Ret vs BSE Sensex 1W","Previous Day Close","Rel Ret vs BSE Sensex 1M","Previous Day Low","Rel Ret vs BSE Sensex 3M","Previous Day High","Rel Ret vs BSE Sensex 6M","1M High","Rel Ret vs BSE Sensex YTD","1M Low","Rel Ret vs BSE Sensex 1Y","3M High","Rel Ret vs BSE Sensex 3Y","3M Low","Rel Ret vs BSE Sensex 5Y","6M High","Rel Ret vs NiftyIT 1D","6M Low","Rel Ret vs NiftyIT 1W","Current Price","Rel Ret vs NiftyIT 1M","Rel Ret vs NiftyIT 3M","Rel Ret vs NiftyIT 6M","Rel Ret vs NiftyIT YTD","Rel Ret vs NiftyIT 1Y","Rel Ret vs NiftyIT 3Y","Rel Ret vs NiftyIT 5Y","Rel Ret vs NiftyBank 1D","Rel Ret vs NiftyBank 1W","Rel Ret vs NiftyBank 1M","Rel Ret vs NiftyBank 3M","Rel Ret vs NiftyBank 6M","Rel Ret vs NiftyBank YTD","Rel Ret vs NiftyBank 1Y","Rel Ret vs NiftyBank 3Y","Rel Ret vs NiftyBank 5Y","Rel Ret vs BSE 500 1D","Rel Ret vs BSE 500 1W","Rel Ret vs BSE 500 1M","Rel Ret vs BSE 500 3M","Rel Ret vs BSE 500 6M","Rel Ret vs BSE 500 YTD","Rel Ret vs BSE 500 1Y","Rel Ret vs BSE 500 3Y","Rel Ret vs BSE 500 5Y","Rel Ret vs Nifty Smallcap250 1D","Rel Ret vs NiftySmallcap250 1W","Rel Ret vs NiftySmallcap250 1M","Rel Ret vs NiftySmallcap250 3M","Rel Ret vs NiftySmallcap250 6M","Rel Ret vs NiftySmallcap250 YTD","Rel Ret vs NiftySmallcap250 1Y","Rel Ret vs NiftySmallcap250 3Y","Rel Ret vs NiftySmallcap250 5Y","Rel Ret vs NiftyMidcap100 1D","Rel Ret vs NiftyMidcap100 1W","Rel Ret vs NiftyMidcap100 1M","Rel Ret vs NiftyMidcap100 3M","Rel Ret vs NiftyMidcap100 6M","Rel Ret vs NiftyMidcap100 YTD","Rel Ret vs NiftyMidcap100 1Y","Rel Ret vs NiftyMidcap100 3Y","Rel Ret vs NiftyMidcap100 5Y"

Respond ONLY with the expression, e.g.: "1D Returns" > 34
`;

async function getWhereClause(nlQuery) {
  const result = await client.getChatCompletions(deploymentName,
    [
      { role: 'system', content: SYSTEM_PROMPT },
      { role: 'user', content: nlQuery }
    ],
    { temperature: 0.1, maxTokens: 150 }
  );
  let clause = result.choices[0].message.content.trim();
  clause = clause.replace(/^```(?:sql)?/, '').replace(/```$/, '').trim().replace(/;$/, '');
  return clause;
}

function executeSql(query) {
  return new Promise((resolve, reject) => {
    const db = new sqlite3.Database(DATABASE_PATH, sqlite3.OPEN_READONLY, err => {
      if (err) return reject(`Database error: ${err.message}`);
    });
    db.all(query, [], (err, rows) => {
      db.close();
      if (err) return reject(`Database error: ${err.message}`);
      resolve(rows);
    });
  });
}

app.post('/api/chat-to-sql', async (req, res) => {
  const { naturalLanguage } = req.body || {};
  if (!naturalLanguage) {
    return res.status(400).json({ detail: "'naturalLanguage' field is required." });
  }
  const nl = naturalLanguage.trim();
  if (!nl) {
    return res.status(400).json({ detail: 'Query cannot be empty.' });
  }
  try {
    const whereClause = await getWhereClause(nl);
    const sql = `SELECT * FROM stocks WHERE ${whereClause}`;
    console.log(`Executing SQL: ${sql}`);
    const results = await executeSql(sql);
    return res.json({ sql: whereClause.replace(/['"]/g, ''), results });
  } catch (err) {
    console.error(err);
    return res.status(500).json({ detail: err.toString() });
  }
});

app.listen(PORT, () => console.log(`Server running on http://127.0.0.1:${PORT}`));
