"""
Simple HTTP server for Proxiverse status page.

This runs alongside the WebSocket server to provide a web interface.
"""

import asyncio
import aiohttp
from aiohttp import web
import logging

logger = logging.getLogger(__name__)


class HTTPStatusServer:
    """HTTP server for serving the Proxiverse status page."""
    
    def __init__(self, world_engine, port=8766):
        """Initialize the HTTP server.
        
        Args:
            world_engine: The WorldEngine instance
            port: HTTP server port
        """
        self.world_engine = world_engine
        self.port = port
        self.app = web.Application()
        self.app.router.add_get('/', self.status_page)
        self.app.router.add_get('/status', self.status_page)
        
    def get_status_html(self):
        """Generate the status HTML page."""
        world_state = self.world_engine.get_world_state()
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Proxiverse Server Status</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .status {{ background: #e8f5e8; padding: 20px; border-radius: 5px; border-left: 4px solid #4CAF50; }}
                .connected {{ color: #4CAF50; font-weight: bold; }}
                .disconnected {{ color: #f44336; font-weight: bold; }}
                .code {{ background: #f0f0f0; padding: 10px; border-radius: 3px; font-family: monospace; }}
                .section {{ margin: 20px 0; padding: 15px; background: #f9f9f9; border-radius: 5px; }}
                h1 {{ color: #333; text-align: center; }}
                h2 {{ color: #666; }}
                h3 {{ color: #888; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 Proxiverse AI Arena</h1>
                
                <div class="status">
                    <h2>Server Status: <span class="connected">🟢 Online</span></h2>
                    <p><strong>WebSocket URL:</strong> <span class="code">ws://localhost:8765</span></p>
                    <p><strong>World Tick:</strong> {world_state['tick']}</p>
                    <p><strong>World Size:</strong> {world_state['dimensions'][0]}x{world_state['dimensions'][1]}</p>
                    <p><strong>Total Resources:</strong> {world_state['resources']}</p>
                </div>
                
                <div class="section">
                    <h3>🚀 How to Connect Your AI Agent</h3>
                    <ol>
                        <li>Connect to <span class="code">ws://localhost:8765</span></li>
                        <li>Send JSON commands to control your agent</li>
                        <li>Receive game state updates in real-time</li>
                    </ol>
                </div>
                
                <div class="section">
                    <h3>🎮 Available Actions</h3>
                    <ul>
                        <li><span class="code">{{"action": "move", "params": {{"dx": 1, "dy": 0}}}}</span> - Move agent</li>
                        <li><span class="code">{{"action": "harvest", "params": {{}}}}</span> - Harvest resources</li>
                        <li><span class="code">{{"action": "craft", "params": {{}}}}</span> - Craft components</li>
                    </ul>
                </div>
                
                <div class="section">
                    <h3>🧪 Testing</h3>
                    <p>Run <span class="code">python test_client.py</span> to test the connection.</p>
                </div>
                
                <div class="section">
                    <h3>📚 API Reference</h3>
                    <p><strong>Client → Server:</strong> Send JSON actions</p>
                    <p><strong>Server → Client:</strong> Receive game state updates</p>
                    <p>Example response:</p>
                    <div class="code">
                        {{<br>
                        &nbsp;&nbsp;"type": "game_state",<br>
                        &nbsp;&nbsp;"tick": 150,<br>
                        &nbsp;&nbsp;"agent_state": {{<br>
                        &nbsp;&nbsp;&nbsp;&nbsp;"x": 5, "y": 7,<br>
                        &nbsp;&nbsp;&nbsp;&nbsp;"inventory": {{"ORE": 10, "FUEL": 5}}<br>
                        &nbsp;&nbsp;}}<br>
                        }}
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
    
    async def status_page(self, request):
        """Handle status page requests."""
        return web.Response(
            text=self.get_status_html(),
            content_type='text/html'
        )
    
    async def start_server(self):
        """Start the HTTP server."""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', self.port)
        await site.start()
        
        logger.info(f"HTTP status server started on http://localhost:{self.port}")
        return runner
    
    async def stop_server(self, runner):
        """Stop the HTTP server."""
        await runner.cleanup()
        logger.info("HTTP status server stopped")


async def run_http_server(world_engine, port=8766):
    """Run the HTTP status server."""
    server = HTTPStatusServer(world_engine, port)
    runner = await server.start_server()
    return server, runner 