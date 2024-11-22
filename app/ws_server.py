import json
import ssl
import io
from PIL import Image

import asyncio
from websockets import serve

from yoloV8 import YOLOProcessor
processor = YOLOProcessor()

async def handle_websocket(websocket):
    try:
        print("WebSocket Connected")
        async for message in websocket:
            if isinstance(message, str):
                print("Parameters received")
                data = json.loads(message)
                # Utiliser les paramètres reçus si nécessaire
            else:
                print("Webcam data received")
                if isinstance(message, bytes):
                    image = Image.open(io.BytesIO(message))
                    image = image.convert('RGB')

                    try:
                        jsonData = processor.process_image_webcam(image)
                        await websocket.send(jsonData)
                    except Exception as e:
                        print("An inference error occurred:", e)
                else:
                    print("Unknown message type received")
    except Exception as e:
        print('WebSocket Closed or Error:', e)


async def start_websocket_server():
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(certfile='./ssl/fullchain.pem', keyfile='./ssl/privkey.pem')
    server = await serve(handle_websocket, "0.0.0.0", 5443, ssl=ssl_context, subprotocols=["wss"])
    await server.wait_closed()

if __name__ == "__main__":
    # Start WebSocket server
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    print("WSS server running on port 5443")
    loop.run_until_complete(start_websocket_server())

