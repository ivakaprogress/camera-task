import asyncio
import serial
import serial.tools.list_ports
import websockets
import cv2
import sqlite3
import datetime
from aiohttp import web
import threading
import json
import os

# Ensure the images directory exists
os.makedirs('images', exist_ok=True)

# Initialize the SQLite database
conn = sqlite3.connect('mouse_data.db')
c = conn.cursor()
c.execute(
    '''CREATE TABLE IF NOT EXISTS mouse_data (timestamp TEXT, x INTEGER, y INTEGER, image_path TEXT, serial_data TEXT)''')
conn.commit()


# Function to save data to SQLite
def save_to_db(x, y, image_path, timestamp, serial_data):
    # Open a new connection within the thread
    conn = sqlite3.connect('mouse_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO mouse_data (timestamp, x, y, image_path, serial_data) VALUES (?, ?, ?, ?, ?)",
              (timestamp, x, y, image_path, serial_data))
    conn.commit()
    conn.close()


# Webcam capture function
def capture_image():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    image_path = ""
    if ret:
        image_path = f'images/capture_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        cv2.imwrite(image_path, frame)
    cap.release()
    return image_path


# Function to handle mouse movement and capture
async def handle_mouse_movement(websocket, path):
    async for message in websocket:
        data = message.split(',')
        x, y = int(data[0]), int(data[1])
        print(f"Mouse moved to: {x}, {y}")
        if len(data) > 2 and data[2] == 'click':
            # Capture image in a separate thread to avoid blocking
            thread = threading.Thread(target=process_click, args=(x, y, websocket))
            thread.start()


def find_mouse_port():
    baud_rate = 9600

    for port in serial.tools.list_ports.comports():
        try:
            ser = serial.Serial(port.device, baud_rate, timeout=2, xonxoff=False, rtscts=False, dsrdtr=False)
            print(f"Attempting to read from {port.device} at {baud_rate} baud...")
            if ser.readable():
                print(ser.readable())
                print(f"Mouse connected at {port.device} with baud rate: {baud_rate}")
                return ser, baud_rate

        except (serial.SerialException, OSError) as e:
            print(f"Failed to open port: {port.device}, {e}")
    raise Exception("No available serial ports found.")


def process_click(x, y, websocket):
    ser, baud_rate = find_mouse_port()
    image_path = capture_image()
    bytes_to_read = ser.in_waiting
    print(bytes_to_read)
    serial_data = ser.read(bytes_to_read).decode()  # Read serial data
    print(f'SERIAL: {serial_data}')
    save_to_db(x, y, image_path, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), serial_data)
    # Send the image path back to the client
    asyncio.run(send_image_path(websocket, image_path))


async def send_image_path(websocket, image_path):
    await websocket.send(json.dumps({'imagePath': f'/images/{os.path.basename(image_path)}'}))


# Start the websocket server
async def start_server():
    server = await websockets.serve(handle_mouse_movement, "localhost", 6789)
    await server.wait_closed()


# Serve the HTML file for mouse tracking
async def handle_index(request):
    return web.FileResponse('index.html')


# Serve the captured images
async def handle_image(request):
    image_name = request.match_info['name']
    return web.FileResponse(f'images/{image_name}')


# Create an aiohttp web server
app = web.Application()
app.add_routes([web.get('/', handle_index)])
app.add_routes([web.get('/images/{name}', handle_image)])


async def main():
    # Run the WebSocket server and web server concurrently
    server_task = asyncio.create_task(start_server())
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()

    print("Server started at http://localhost:8080")

    await server_task


# Run the asyncio event loop
if __name__ == '__main__':
    asyncio.run(main())
