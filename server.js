import express from 'express';
import bodyParser from 'body-parser';
import fetch from 'node-fetch';
import { runWithTools } from '@cloudflare/ai-utils';

const app = express();
app.use(bodyParser.json());

async function getCoordinates(city) {
    const response = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(city)}`);
    const data = await response.json();
    if (data.length > 0) {
        return { lat: data[0].lat, lon: data[0].lon };
    }
    throw new Error('City not found');
}

async function getWeatherData(lat, lon) {
    const response = await fetch(`https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current_weather=true&temperature_unit=celsius`);
    return await response.json();
}

function getWeatherCondition(weathercode) {
    const weatherCodes = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 48: "Depositing rime fog", 51: "Light drizzle", 53: "Moderate drizzle",
        55: "Dense drizzle", 61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    };
    return weatherCodes[weathercode] || "Unknown";
}

const agentTools = {
    'get-weather': async (args) => {
        console.log('get-weather tool called with args:', args);
        const { city } = args;
        const { lat, lon } = await getCoordinates(city);
        const weatherData = await getWeatherData(lat, lon);
        const result = JSON.stringify({
            location: { name: city, lat, lon },
            current: {
                temp_c: weatherData.current_weather.temperature,
                wind_kph: weatherData.current_weather.windspeed,
                condition: { text: getWeatherCondition(weatherData.current_weather.weathercode) }
            }
        });
        console.log('get-weather tool result:', result);
        return result;
    },
    'attraction-expert': async (args) => {
        // Simulate fetching attractions (replace with real API call in production)
        return JSON.stringify({
            attractions: [
                "Eiffel Tower",
                "Louvre Museum",
                "Notre-Dame Cathedral"
            ]
        });
    },
    'transportation-expert': async (args) => {
        // Simulate transportation options (replace with real API call in production)
        return JSON.stringify({
            options: [
                { type: "Metro", cost: "€1.90 per ticket" },
                { type: "Bus", cost: "€2.00 per ticket" },
                { type: "Taxi", cost: "€1.06 per km + €2.60 pickup fee" }
            ]
        });
    }
};

const mockAI = {
    run: async (model, params) => {
        console.log('mockAI.run called with params:', JSON.stringify(params, null, 2));
        if (!params.messages || !Array.isArray(params.messages)) {
            throw new Error('Invalid messages parameter in mockAI.run');
        }
        if (!params.tools || !Array.isArray(params.tools)) {
            throw new Error('Invalid tools parameter in mockAI.run');
        }
        
        // Simulate AI generating a tool call
        const lastMessage = params.messages[params.messages.length - 1];
        const cityMatch = lastMessage.content.match(/for\s+(\w+)/);
        const city = cityMatch ? cityMatch[1] : 'Unknown';
        
        console.log('Looking for get-weather tool...');
        const tool = params.tools.find(t => t.function && t.function.name === 'get-weather');
        if (!tool) {
            console.log('Available tools:', JSON.stringify(params.tools, null, 2));
            throw new Error('Weather tool not found');
        }
        console.log('Found get-weather tool:', JSON.stringify(tool, null, 2));

        const toolCall = {
            id: "call_123",
            type: "function",
            function: {
                name: tool.function.name,
                arguments: JSON.stringify({ city })
            }
        };

        // Execute the tool call
        if (agentTools[toolCall.function.name]) {
            const result = await agentTools[toolCall.function.name](JSON.parse(toolCall.function.arguments));
            return JSON.stringify({
                id: "chatcmpl-123",
                object: "chat.completion",
                created: Date.now(),
                model: model,
                choices: [{
                    index: 0,
                    message: {
                        role: "assistant",
                        content: null,
                        tool_calls: [toolCall]
                    },
                    finish_reason: "tool_calls"
                }],
                usage: {
                    prompt_tokens: 0,
                    completion_tokens: 0,
                    total_tokens: 0
                }
            });
        }
        return JSON.stringify({ error: `Tool ${toolCall.function.name} not found` });
    }
};

app.post('/run-tool', async (req, res) => {
    console.log('Received request:', JSON.stringify(req.body, null, 2));
    const { messages, tools } = req.body;

    if (!Array.isArray(tools) || tools.length === 0) {
        return res.status(400).send('Tools parameter must be a non-empty array');
    }

    try {
        const lastMessage = messages[messages.length - 1];
        const cityMatch = lastMessage.content.match(/for\s+(\w+)/);
        const city = cityMatch ? cityMatch[1] : 'Unknown';

        const weatherData = await agentTools['get-weather']({ city });
        
        console.log('Weather data:', weatherData);
        res.json(JSON.parse(weatherData));
    } catch (error) {
        console.error('Error details:', error);
        res.status(500).json({ error: error.toString(), stack: error.stack });
    }
});

const port = process.env.PORT || 3000;
app.listen(port, () => {
    console.log(`Server running on port ${port}`);
});
