
import requests

response = requests.post("http://127.0.0.1:5001/api/chat-to-sql", json={"naturalLanguage": "IT stocks with ROCE over 25 and Mining stocks with high PE"})
print(response.json())
# ('http://127.0.0.1:5001/api/chat-to-sql', { 
#                     method: 'POST',
#                     headers: {
#                         'Content-Type': 'application/json',

#                     },
#                     body: JSON.stringify({ naturalLanguage: query }), // Use correct key 'naturalLanguage'
#                 })