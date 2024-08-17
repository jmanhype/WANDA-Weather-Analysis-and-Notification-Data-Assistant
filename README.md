# WANDA: Weather Analysis and Notification Data Assistant

## Overview

WANDA (Weather Analysis and Notification Data Assistant) is an intelligent system that fetches weather data for a specified city and provides notifications based on current weather conditions. It combines a Python-based state machine for handling the weather analysis workflow with a Node.js server for processing weather data requests.

## Features

- Fetches real-time weather data for any city
- Analyzes weather conditions to determine if a notification is necessary
- Uses a state machine to manage the workflow
- Implements a Node.js server with mock AI capabilities for processing weather requests

## Prerequisites

- Python 3.7+
- Node.js 14+
- npm (Node Package Manager)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/WANDA.git
   cd WANDA
   ```

2. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Install Node.js dependencies:
   ```
   npm install
   ```

## Configuration

1. Create a `.env` file in the project root and add any necessary environment variables.

2. Modify the `city` variable in `weather_notification.py` to set your desired location.

## Usage

1. Start the Node.js server:
   ```
   node server.js
   ```

2. In a separate terminal, run the Python script:
   ```
   python weather_notification.py
   ```

## Project Structure

- `weather_notification.py`: Main Python script containing the WANDA agent
- `server.js`: Node.js server for processing weather data requests
- `ai_utils_bridge.py`: Bridge between Python and Node.js (not provided in the given files)
- `requirements.txt`: Python dependencies
- `package.json`: Node.js dependencies (not provided in the given files)

## Contributing

Contributions to WANDA are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenStreetMap for geolocation data
- Open-Meteo for weather data
- Cloudflare AI Utils for AI capabilities simulation
