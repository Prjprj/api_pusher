# Api_pusher

## Description
Tool to generate fake marketing campaign feedback for EFREI School **Data Engineering Applications** course

The goal is to implement a tool to push JSON data on an API endpoint.
Data can be generated with a local Generative AI or with simple random functions depending of the config

## Data Structure
JSON Structure is the following:
```JSON
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Feedback",
  "type": "object",
  "properties": {
    "username": {
      "type": "string"
    },
    "feedback_date": {
      "type": "string",
      "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
    },
    "campaign_id": {
      "type": "string"
    },
    "comment": {
      "type": "string"
    }
  },
  "required": [
    "username",
    "feedback_date",
    "campaign_id",
    "comment"
  ]
}
```

Example:
```JSON
{
  "username": "user_demo",
  "feedback_date": "2025-01-01",
  "campaign_id": "CAMP000",
  "comment": "demo"
}
```

Queries to API will have to send a list of JSON

## How to run this program
```Shell
python __main__.py PUSH <number_of_feedbacks_to_generate>
```

Example:
```Shell
python __main__.py PUSH 10
```

## Configuration
```ini
[API]
endpoint_url = http://localhost:8080/afc/api
method = POST
timeout_seconds = 10

[API_AUTH]
active = False
username = XYZ
password = XYZ

[LOG]
log_level = DEBUG
log_file = app.log
log_format = %%(asctime)s - %%(levelname)s - %%(filename)s - %%(funcName)s - %%(lineno)d - %%(message)s

[OLLAMA]
ollama_url = 127.0.0.1:11434
ollama_model = codellama

[GENERATION]
mode = ollama
```
**ollama_model** must be a model already pulled on your ollama server.

Generation mode can be **ollama** or **manual**


## Dependencies
No Python dependency

For Ollama generation, access to an Ollama server with models pulled
