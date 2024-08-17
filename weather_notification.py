import os
import json
import asyncio
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
    """Defines states and transitions for the weather notification system."""

    def __init__(self, name, city, ai_utils_bridge):
        self.name = name
        self.city = city
        self.weather_data = None
        self.notification = None
        self.ai_utils_bridge = ai_utils_bridge
        states = ['start', 'fetching_weather', 'processing_data', 'notifying', 'completed']
        Machine.__init__(self, states=states, initial='start')
        self.add_transition('fetch_weather', 'start', 'fetching_weather')
        self.add_transition('process_data', 'fetching_weather', 'processing_data')
        self.add_transition('notify_user', 'processing_data', 'notifying')
        self.add_transition('complete', 'notifying', 'completed')

    async def fetch_weather(self):
        """Fetch weather data for the specified city."""
        print(f"{self.name} is fetching weather data for {self.city}...")
        try:
            self.weather_data = await self.call_node_js(self.city)
            self.state = 'fetching_weather'
        except Exception as e:
            print(f"Error in fetch_weather: {str(e)}")
            raise

    async def call_node_js(self, city):
        """Call the Node.js script to fetch weather data."""
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
        try:
            result = await self.ai_utils_bridge.run_tool(messages, tools, config)
            print(f"Received response from Node.js server: {result}")
            return result
        except Exception as e:
            print(f"Error in call_node_js: {str(e)}")
            raise

    async def process_data(self):
        """Process the fetched weather data."""
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

    async def notify_user(self):
        """Notify the user based on processed data."""
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

    async def execute(self):
        """Main execution loop for the agent."""
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

async def main():
    city = "Austin"
    ai_utils_bridge = AIUtilsBridge(url="http://localhost:3000/run-tool")
    agent = WeatherAgent(name="WeatherAgent1", city=city, ai_utils_bridge=ai_utils_bridge)
    await agent.execute()

if __name__ == "__main__":
    asyncio.run(main())