import vlc
import time

# VLC Media Player to run Tapo's rtsp stream with "Sound" enabled

stream_url = "rtsp://tapoadmin:ailabo123$@10.2.172.155/stream1"

player = vlc.Instance('--network-caching=1000')

media_player = player.media_player_new()

media = player.media_new(stream_url)
media_player.set_media(media)

media_player.play()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Stream stopped")
