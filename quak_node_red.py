import asyncio
import websockets

# Queues for message passing between servers
server1_to_server2_q = asyncio.Queue()
server2_to_server1_q = asyncio.Queue()

# Sets to keep track of connected clients
server1_clients = set()
server2_clients = set()

async def handler_server1_to_server2():
    while True:
        message = await server1_to_server2_q.get()
        # Send message to all clients connected to server 2
        if server2_clients:
            await asyncio.gather(*(client.send(message) for client in server2_clients))

async def handler_server2_to_server1():
    while True:
        message = await server2_to_server1_q.get()
        # Send message to all clients connected to server 1
        if server1_clients:
            await asyncio.gather(*(client.send(message) for client in server1_clients))

async def server1(websocket, path):
    # Register client
    server1_clients.add(websocket)
    try:
        async for message in websocket:
            await server1_to_server2_q.put(message)
    finally:
        # Unregister client
        server1_clients.remove(websocket)

async def server2(websocket, path):
    # Register client
    server2_clients.add(websocket)
    try:
        async for message in websocket:
            await server2_to_server1_q.put(message)
    finally:
        # Unregister client
        server2_clients.remove(websocket)

async def main():
    server_1 = websockets.serve(server1, "localhost", 8765)
    server_2 = websockets.serve(server2, "localhost", 8766)
    asyncio.create_task(handler_server1_to_server2())
    asyncio.create_task(handler_server2_to_server1())
    print("Servers running...")
    async with server_1, server_2:
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
