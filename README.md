# WANDA

Weather Analysis and Notification Data Assistant.

## What It Does

Fetches weather data for a given city using Open-Meteo, runs it through a Python state machine to decide whether a notification is warranted, and returns the result via a Node.js server.

## Architecture

| Component | File | Role |
|---|---|---|
| State machine | `weather_notification.py` | Drives the fetch-analyze-notify workflow using the `transitions` library |
| API server | `server.js` | Node.js endpoint that processes weather data requests |
| Dependencies | `requirements.txt` | python-dotenv, transitions, aiohttp, dspy |

The Python process calls the Node server. Both must be running.

## Requirements

- Python 3.7+
- Node.js 14+

## Setup

```bash
git clone https://github.com/jmanhype/WANDA-Weather-Analysis-and-Notification-Data-Assistant.git
cd WANDA-Weather-Analysis-and-Notification-Data-Assistant
pip install -r requirements.txt
npm install
```

Create a `.env` file for any required environment variables. Set the target city in `weather_notification.py`.

## Usage

```bash
# Terminal 1
node server.js

# Terminal 2
python weather_notification.py
```

## Status

Prototype. The Node server uses mock AI capabilities. There are no tests. The `ai_utils_bridge.py` referenced in the code is not included in the repository.

## Data Sources

- OpenStreetMap (geolocation)
- Open-Meteo (weather)

## License

MIT
