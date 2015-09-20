from flask import Flask, request
import requests
import os

app = Flask(__name__)

@app.route("/hackthenorth/<string:song_url>", methods=["GET"])
def hackthenorth(song_url):
    base_url = "https://api.soundcloud.com/resolve.json"
    client_id = os.environ.get("SOUNDCLOUD_ID")
    d = {"url": song_url, "client_id": client_id}
    resulting_json = requests.get(base_url, params=d)
    location_url = resulting_json["location"]
    track_json = requests.get(location_url)
    download_url = track_json['download_url']
    return download_url

if __name__ == "__main__":
    app.run(debug = True)
