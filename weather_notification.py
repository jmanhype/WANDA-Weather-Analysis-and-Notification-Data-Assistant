"""
WANDA: Weather Analysis and Notification Data Assistant

This module implements a state machine-based weather notification system that
fetches real-time weather data and provides notifications based on conditions.
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from transitions import Machine
from dspy import Signature, InputField, OutputField
from ai_utils_bridge import AIUtilsBridge

load_dotenv()

class WeatherNotificationSignature(Signature):
    city = InputField(desc="The city to check the weather for")
    notification = OutputField(desc="The notification message to be sent")
    notify: bool = OutputField(desc="True if a notification should be sent, False otherwise")

class WeatherAgent(Machine):
    """
    State machine-based weather notification agent.

    This agent manages the workflow of fetching weather data, processing it,
    and determining whether to send notifications based on weather conditions.

    Attributes:
        name (str): The name/identifier of the agent
        city (str): The city to fetch weather data for
        weather_data (Optional[Dict[str, Any]]): Cached weather data from the API
        notification (Optional[str]): Generated notification message
        ai_utils_bridge (AIUtilsBridge): Bridge to Node.js AI utilities server
    """

    def __init__(self, name: str, city: str, ai_utils_bridge: AIUtilsBridge) -> None:
        """
        Initialize the Weather Agent.

        Args:
            name: The name/identifier for this agent instance
            city: The city to fetch weather data for
            ai_utils_bridge: Bridge instance for communicating with Node.js server
        """
        self.name: str = name
        self.city: str = city
        self.weather_data: Optional[Dict[str, Any]] = None
        self.notification: Optional[str] = None
        self.ai_utils_bridge: AIUtilsBridge = ai_utils_bridge
        states = ['start', 'fetching_weather', 'processing_data', 'notifying', 'completed']
        Machine.__init__(self, states=states, initial='start')
        self.add_transition('fetch_weather', 'start', 'fetching_weather')
        self.add_transition('process_data', 'fetching_weather', 'processing_data')
        self.add_transition('notify_user', 'processing_data', 'notifying')
        self.add_transition('complete', 'notifying', 'completed')

    async def fetch_weather(self) -> None:
        """
        Fetch weather data for the specified city.

        Updates the agent's state to 'fetching_weather' and stores weather data.

        Raises:
            Exception: If weather data cannot be fetched from the Node.js server
        """
        print(f"{self.name} is fetching weather data for {self.city}...")
        try:
            self.weather_data = await self.call_node_js(self.city)
            self.state = 'fetching_weather'
        except Exception as e:
            print(f"Error in fetch_weather: {str(e)}")
            raise

    async def call_node_js(self, city: str) -> Dict[str, Any]:
        """
        Call the Node.js server to fetch weather data via AI tools.

        Args:
            city: The city name to fetch weather data for

        Returns:
            Dictionary containing weather data with location and current conditions

        Raises:
            Exception: If the Node.js server request fails
        """
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get-weather",
                    "description": "Gets weather information of a particular city",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city": {
                                "type": "string",
                                "description": "The city name"
                            }
                        },
                        "required": ["city"]
                    }
                }
            }
        ]
        messages = [
            {"role": "user", "content": f"Get the weather information for {city}"}
        ]
        config = {
            "strictValidation": True,
            "maxRecursiveToolRuns": 1,
            "streamFinalResponse": False,
            "verbose": True,
            "trimFunction": None
        }

        print(f"Sending payload to Node.js server: {json.dumps({'messages': messages, 'tools': tools, 'config': config}, indent=2)}")

        try:
            result = await self.ai_utils_bridge.run_tool(messages, tools, config)
            print(f"Received response from Node.js server: {result}")
            return result
        except Exception as e:
            print(f"Error in call_node_js: {str(e)}")
            raise

    async def process_data(self) -> None:
        """
        Process the fetched weather data and generate a notification message.

        Extracts temperature, condition, and wind speed from weather data
        and formats them into a human-readable notification message.
        """
        print(f"{self.name} is processing weather data...")
        if self.weather_data:
            temp = self.weather_data['current']['temp_c']
            condition = self.weather_data['current']['condition']['text']
            wind_speed = self.weather_data['current']['wind_kph']
            
            self.notification = (
                f"Current weather in {self.city}:\n"
                f"Temperature: {temp}°C\n"
                f"Condition: {condition}\n"
                f"Wind Speed: {wind_speed} km/h"
            )
            self.state = 'processing_data'
        else:
            print("No weather data available to process")

    async def notify_user(self) -> None:
        """
        Determine if notification should be sent based on weather conditions.

        Checks if the weather condition contains 'rain' or 'overcast' and
        sends a notification if true. Updates state to 'notifying'.
        """
        print(f"{self.name} is notifying the user...")
        if self.weather_data:
            condition = self.weather_data['current']['condition']['text'].lower()
            notify = "rain" in condition or "overcast" in condition

            if notify:
                print(f"Notification: {self.notification}")
            else:
                print(f"No notification sent. Current condition: {condition}")
            self.state = 'notifying'
        else:
            print("No weather data available for notification")

    async def execute(self) -> None:
        """
        Main execution loop for the agent.

        Runs the state machine through all states from 'start' to 'completed',
        handling each state transition and any errors that occur.
        """
        while self.state != 'completed':
            try:
                if self.state == 'start':
                    await self.fetch_weather()
                elif self.state == 'fetching_weather':
                    await self.process_data()
                elif self.state == 'processing_data':
                    await self.notify_user()
                elif self.state == 'notifying':
                    self.state = 'completed'
            except Exception as e:
                print(f"Error in execute: {str(e)}")
                self.state = 'completed'

async def main() -> None:
    """
    Main entry point for the WANDA weather notification system.

    Creates a WeatherAgent instance and executes the full workflow
    to fetch and process weather data for Austin, TX.
    """
    city = "Austin"
    ai_utils_bridge = AIUtilsBridge(url="http://localhost:3000/run-tool")
    agent = WeatherAgent(name="WeatherAgent1", city=city, ai_utils_bridge=ai_utils_bridge)
    await agent.execute()


if __name__ == "__main__":
    asyncio.run(main())