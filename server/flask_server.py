from flask import Flask, render_template
from flask_socketio import SocketIO, emit
# from flask_cors import CORS

# Create Flask app and SocketIO instance
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

# Enable CORS
# CORS(app)  # Allow cross-origin requests


# List to store images
images = [
    {
        "url": "https://i.ibb.co/7nQSn71/nao-storyteller.png",
        "caption": "Verhalen vertellen met Nao, de humanoïde robot!"
    }
    # },
    # {
    #     "url": "https://upload.wikimedia.org/wikipedia/commons/b/b6/Image_created_with_a_mobile_phone.png",
    #     "caption": "Second Image"
    # },
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


# WebSocket endpoint to trigger reload
@socketio.on('trigger_reload')
def handle_reload():
    print("Received reload trigger!")
    socketio.emit('reload_page', {}, room=None)  # Notify all clients to reload

def reload_clients():
    """Trigger reload for all connected clients."""
    socketio.emit('reload_page', {}, room=None)
    print("Reload event emitted to all clients.")
    
# Function to add images programmatically
def add_image_to_storyboard(image_url, caption):
    images.append({"url": image_url, "caption": caption})
    # print(f"Added image: {image_url}, {caption}")
    socketio.emit('update_images', {'images': images})


# Start the server
def start_flask_server():
    socketio.run(app, host='0.0.0.0', port=5001, debug=False, use_reloader=False)


# if __name__ == "__main__":
#     # Run the server in a separate thread
#     threading.Thread(target=start_flask_server, daemon=True).start()

#     # Add images programmatically after some delay
#     time.sleep(2)
#     add_image_to_storyboard(
#         "https://upload.wikimedia.org/wikipedia/commons/b/b6/Image_created_with_a_mobile_phone.png",
#         "Programmatically Added Image 1"
#     )
#     add_image_to_storyboard(
#         "https://upload.wikimedia.org/wikipedia/commons/b/b6/Image_created_with_a_mobile_phone.png",
#         "Programmatically Added Image 2"
#     )

#     # Keep the script running
#     while True:
#         time.sleep(1)


# # Define the routes
# @app.route('/')
# def index():
#     """Serve the main HTML page."""
#     return render_template('storyboard.html', images=images)

# # Define the WebSocket event for adding images
# @socketio.on('add_image')
# def add_image(data):
#     """Handle the addition of a new image and notify clients."""
#     images.append({"url": data['url'], "caption": data['caption']})
#     emit('update_images', {'images': images}, broadcast=True)

# # # New function to add images directly
# # def add_image_to_storyboard(image_url, caption):
# #     """Add an image to the storyboard and notify clients."""
# #     # Add the image to the server's images list
# #     images.append({"url": image_url, "caption": caption})
# #     # Emit the update to all connected clients
# #     socketio.emit('update_images', {'images': images})
# #     print(f"Image added: URL={image_url}, Caption={caption}")

# def add_image_to_storyboard(image_url, caption):
#     """Add an image to the storyboard and notify clients."""
#     # Add the image to the server's images list
#     images.append({"url": image_url, "caption": caption})
#     print(f"Image added: URL={image_url}, Caption={caption}")  # Debug log

#     # Emit the update to all connected clients
#     socketio.emit('update_images', {'images': images})
#     print("Update emitted to all connected clients.")  # Debug log

# # Define a function to start the Flask server
# def start_flask_server():
#     """Run the Flask server."""

#     socketio.run(app, host='0.0.0.0', port=5001, debug=False, use_reloader=False)

# if __name__ == "__main__":
    # start_flask_server()



#######


# # from flask import Flask, render_template

# # app = Flask(__name__)

# # @app.route('/')
# # def home():
# #     return '<h1>Hello from Flask!</h1><p>This is accessible from other devices on your network.</p>'

# # if __name__ == '__main__':
# #     # Use '0.0.0.0' to make it accessible from other devices
# #     app.run(host='0.0.0.0', port=5000, debug=True)
    