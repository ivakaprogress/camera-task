# Mouse Tracker and Webcam Capture Application

This application uses parallel processes and Python libraries to visualize the current mouse cursor coordinates and capture images from a webcam when the left mouse button is pressed. The data is then stored in a SQLite database for future reference.

## Features

- Real-time visualization of mouse cursor coordinates in a browser environment.
- Capture images from a connected webcam when the left mouse button is pressed.
- Store mouse coordinates and image file paths in a SQLite database.

## Installation

1. Clone the repository from GitHub:

    ```bash
    git clone <repository_url>
    ```

2. Install the required Python packages listed in the `requirements.txt` file:

    ```bash
    pip install -r requirements.txt
    ```

3. Make sure you have a webcam connected to your system.

## Usage

1. Before running the application, ensure that the baud rate of your serial port is correctly configured:
    - Go to Device Manager -> Ports(COM & LPT).
    - Right-click on the port corresponding to your serial device and select Properties.
    - In the Port Settings tab, verify the baud rate settings.
    - in main.py on line 60 modify based on your machine.

2. Run the main Python script to start the application:

    ```bash
    python main.py
    ```

3. Access the web interface by navigating to `http://localhost:8080` in your web browser.

4. Move the mouse cursor to see real-time coordinates and click the left mouse button to capture images.

## Repository Structure

- **main.py**: Main Python script containing the application logic.
- **index.html**: HTML file for the web interface.
- **images/**: Directory to store captured images (will be created automatically).
- **mouse_data.db**: SQLite database file to store mouse coordinates and image file paths.
- **README.md**: README file containing instructions for running the program.

## Dependencies

- `asyncio`: For asynchronous programming.
- `aiohttp`: For creating a web server.
- `websockets`: For handling WebSocket connections.
- `pyserial`: For communication with the serial port.
- `opencv-python`: For capturing images from the webcam.
- `sqlite3`: For interacting with the SQLite database.

