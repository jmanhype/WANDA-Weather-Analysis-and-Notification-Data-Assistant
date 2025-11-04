"""Bridge module for interfacing between Python and Node.js AI utilities server."""

import aiohttp
from typing import Dict, List, Any, Optional


class AIUtilsBridge:
    """
    Bridge class to communicate with the Node.js AI utilities server.

    This class handles HTTP communication with the Node.js server that processes
    weather data requests using AI tools.

    Attributes:
        url (str): The URL endpoint of the Node.js server
        session (Optional[aiohttp.ClientSession]): Persistent HTTP session
    """

    def __init__(self, url: str) -> None:
        """
        Initialize the AI Utils Bridge.

        Args:
            url: The URL endpoint of the Node.js server (e.g., "http://localhost:3000/run-tool")
        """
        self.url = url
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    async def run_tool(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send a request to the Node.js server to run AI tools.

        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            tools: List of tool definitions for the AI to use
            config: Configuration dictionary for tool execution

        Returns:
            Dict containing the weather data response from the server

        Raises:
            aiohttp.ClientError: If there's a network or HTTP error
            ValueError: If the server response is invalid
        """
        payload = {
            "messages": messages,
            "tools": tools,
            "config": config
        }

        # Create session if it doesn't exist (for standalone usage)
        close_session = False
        if self.session is None:
            self.session = aiohttp.ClientSession()
            close_session = True

        try:
            async with self.session.post(self.url, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise ValueError(
                        f"Server returned status {response.status}: {error_text}"
                    )

                result = await response.json()
                return result

        except aiohttp.ClientError as e:
            raise aiohttp.ClientError(
                f"Failed to connect to Node.js server at {self.url}: {str(e)}"
            ) from e
        finally:
            # Close session if we created it in this method
            if close_session and self.session:
                await self.session.close()
                self.session = None
