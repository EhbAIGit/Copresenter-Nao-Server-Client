from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading
import time

# Flask app setup
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

# List to store images
images = [
    {
        "url": "https://upload.wikimedia.org/wikipedia/commons/b/b6/Image_created_with_a_mobile_phone.png",
        "caption": "First Image"
    },
    {
        "url": "https://upload.wikimedia.org/wikipedia/commons/b/b6/Image_created_with_a_mobile_phone.png",
        "caption": "Second Image"
    },
]

# Route to serve the main page
@app.route('/')
def index():
    return render_template('storyboard.html')


# WebSocket event to send initial images
@socketio.on('request_images')
def send_images():
    emit('update_images', {'images': images})


# WebSocket event to handle adding images
@socketio.on('add_image')
def add_image(data):
    images.append({"url": data['url'], "caption": data['caption']})
    emit('update_images', {'images': images})


# Function to add images programmatically
def add_image_to_storyboard(image_url, caption):
    images.append({"url": image_url, "caption": caption})
    print(f"Added image: {image_url}, {caption}")
    socketio.emit('update_images', {'images': images})


# Start the server
def run_server():
    socketio.run(app, host='0.0.0.0', port=5001, debug=False, use_reloader=False)


if __name__ == "__main__":
    # Run the server in a separate thread
    threading.Thread(target=run_server, daemon=True).start()

    # Add images programmatically after some delay
    time.sleep(2)
    add_image_to_storyboard(
        "https://upload.wikimedia.org/wikipedia/commons/b/b6/Image_created_with_a_mobile_phone.png",
        "Programmatically Added Image 1"
    )
    add_image_to_storyboard(
        "https://upload.wikimedia.org/wikipedia/commons/b/b6/Image_created_with_a_mobile_phone.png",
        "Programmatically Added Image 2"
    )

    # Keep the script running
    while True:
        time.sleep(1)
