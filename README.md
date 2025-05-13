# Multi-User Chat Application

This is a feature-rich chat application that supports multiple users, private messaging, file transfers, and video/audio chat.

## Features

- User registration and login with password authentication
- Group chat and private messaging
- File transfers between users
- Image sharing and emoji support
- Real-time video and audio chat
- Chat with AI Robot

## Installation

### Prerequisites

- Python 3.6+
- Required Python packages:
  - tkinter
  - socket
  - threading
  - PIL (Pillow)
  - netifaces
  - pyaudio
  - opencv-python (cv2)

### Install required packages

```bash
pip install pillow netifaces pyaudio opencv-python
```

## Usage

### Starting the Server

1. Run the server script:

```bash
python server.py
```

The server will start on port 50007 by default.

### Connecting as a Client

1. Run the client script:

```bash
python client-test.py
```

2. In the login window:
   - Enter the server address (default: 127.0.0.1:50007)
   - Enter your username
   - Enter your password
   - Choose to login or register a new account

3. Once logged in, you'll see the chat interface:
   - Group chat is available to all users
   - Click on a user's name to start a private chat
   - Use the various buttons to share files, images, or start a video call

## Directory Structure

- `server.py` - The main server application
- `client-test.py` - The client application
- `vachat.py` - Video and audio chat functionality
- `user_auth.py` - User authentication module
- `/user_data` - Stores user account information
- `/Server_image_cache` - Stores shared images
- `/resources` - Stores various application resources
- `/emoji` - Stores emoji images for chat

## Security

- Passwords are hashed using SHA-256 before transmission and storage
- User data is stored in a CSV file in the `/user_data` directory

## Notes

Make sure the required ports are open if you're running the server on a remote machine or across a network.
