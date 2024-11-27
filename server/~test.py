import threading
import time
from flask_server import start_flask_server, add_image_to_storyboard

# Function to run the Flask server in a thread
def run_flask_server():
    flask_thread = threading.Thread(target=run_server, daemon=True)
    flask_thread.start()
    print("Flask server is running...")


if __name__ == "__main__":
    # Start the Flask server
    run_flask_server()

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

    # Keep the script running to keep the server alive
    print("Server is running. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)  # Prevent CPU-intensive looping
    except KeyboardInterrupt:
        print("Shutting down the server.")
