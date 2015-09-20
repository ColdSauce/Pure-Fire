from flask import Flask, request
import requests
import os

app = Flask(__name__)

@app.route("/hackthenorth/", methods=["GET"])
def hackthenorth():
    song_url = request.args.get('song_url')
    base_url = "https://api.soundcloud.com/resolve.json"
    client_id = str(os.environ.get("SOUNDCLOUD_ID"))
    d = {"url": song_url, "client_id": client_id}
    
    resulting_json = requests.get(base_url, params=d).json()
    location_url = resulting_json["uri"]
    client_dict = {'client_id',client_id}
    track_json = requests.get(location_url + '/?client_id=' + client_id).json()
    download_url = track_json['stream_url']
    return str(download_url)

if __name__ == "__main__":
    app.run(debug = True)
