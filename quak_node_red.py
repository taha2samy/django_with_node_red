import asyncio
import logging
import websockets
import ssl  # Import SSL module
from websockets.exceptions import ConnectionClosed

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Queues for message passing between servers
server1_to_server2_q = asyncio.Queue()
server2_to_server1_q = asyncio.Queue()

# Sets to keep track of connected clients
server1_clients = set()
server2_clients = set()

# Example token for demonstration
VALID_TOKEN = "sss"

# SSL configuration (use your own certificate and key)
SSL_CERT = "path/to/your/certificate.pem"  # Replace with your certificate path
SSL_KEY = "path/to/your/private.key"        # Replace with your key path
USE_SSL = False  # Set to True to use SSL; False otherwise

async def handler_server1_to_server2():
    while True:
        message = await server1_to_server2_q.get()
        # Send message to all clients connected to server 2
        if server2_clients:
            await asyncio.gather(*(client.send(message) for client in server2_clients))
            logger.info(f"Message sent from Server 1 to Server 2: {message}")

async def handler_server2_to_server1():
    while True:
        message = await server2_to_server1_q.get()
        # Send message to all clients connected to server 1
        if server1_clients:
            await asyncio.gather(*(client.send(message) for client in server1_clients))
            logger.info(f"Message sent from Server 2 to Server 1: {message}")

async def authenticate(websocket):
    # Retrieve the token from the headers
    token = websocket.request_headers.get("Authorization")
    if token != VALID_TOKEN:
        logger.warning(f"Connection refused due to invalid token: {token}")
        await websocket.close(code=4001)  # Close connection with a custom error code
        return False
    logger.info(f"Connection authenticated with token: {token}")
    return True

async def server1(websocket, path):
    # Authenticate the connection
    if not await authenticate(websocket):
        return

    # Register client
    server1_clients.add(websocket)
    logger.info("Client connected to Server 1")
    try:
        async for message in websocket:
            await server1_to_server2_q.put(message)
            logger.info(f"Message received from Client on Server 1: {message}")
    except ConnectionClosed:
        logger.info("Client disconnected from Server 1")
    finally:
        # Unregister client
        server1_clients.remove(websocket)

async def server2(websocket, path):
    # Authenticate the connection
    if not await authenticate(websocket):
        return

    # Register client
    server2_clients.add(websocket)
    logger.info("Client connected to Server 2")
    try:
        async for message in websocket:
            await server2_to_server1_q.put(message)
            logger.info(f"Message received from Client on Server 2: {message}")
    except ConnectionClosed:
        logger.info("Client disconnected from Server 2")
    finally:
        # Unregister client
        server2_clients.remove(websocket)

async def main():
    # Create SSL context if SSL is enabled
    ssl_context = None
    if USE_SSL:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(certfile=SSL_CERT, keyfile=SSL_KEY)

    # Start WebSocket servers
    server_1 = websockets.serve(server1, "localhost", 8765, ssl=ssl_context)
    server_2 = websockets.serve(server2, "localhost", 8766, ssl=ssl_context)
    
    asyncio.create_task(handler_server1_to_server2())
    asyncio.create_task(handler_server2_to_server1())
    
    logger.info("Servers running...")
    async with server_1, server_2:
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
