# text-analyzer Python Server

This project is a backend server for a React client. It receives text from the client, sends it for analysis to a personal proxy (which forwards to OpenAI), and returns a one-word answer ('כן' or 'לא') indicating if the text is appropriate.

## Features
- Receives text from React client via HTTP POST
- Sends text to proxy at https://chat-api.malkabruk.co.il/openai
- Uses a system prompt to instruct the LLM to return only 'כן' or 'לא'
- Validates the response and returns it to the client

## How to Run
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the server:
   ```bash
   python server.py
   ```

## API
- **POST /analyze**
  - Request JSON: `{ "text": "..." }`
  - Response JSON: `{ "result": "כן" }` or `{ "result": "לא" }`

## Notes
- Make sure your proxy is accessible and configured to forward requests to OpenAI.
- The system prompt is sent with every request to ensure consistent output.
