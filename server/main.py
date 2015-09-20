from flask import Flask, request
import requests
from os import system
import re
import sys
import json
import httplib
import hmac
import hashlib
import time
import os
import base64
print os.environ.get("ACR_ACCESS_KEY")

access_key = os.environ.get("ACR_ACCESS_KEY")

access_secret = os.environ.get("ACR_ACCESS_SECRET")

app = Flask(__name__)

@app.route("/", methods=["GET"])
def hackthenorth():
    song_url = request.args.get('song_url')
    base_url = "https://api.soundcloud.com/resolve.json"
    client_id = str(os.environ.get("SOUNDCLOUD_ID"))
    d = {"url": song_url, "client_id": client_id}
    
    resulting_json = requests.get(base_url, params=d).json()
    location_url = resulting_json["uri"]
    client_dict = {'client_id',client_id}
    track_json = requests.get(location_url + '/?client_id=' + client_id).json()

    if track_json['streamable'] ==  False:
        return "Track not streamable!"
    download_url = track_json['stream_url']
    download_response = requests.get(download_url + '/?client_id=' + client_id, stream=True,)
    file_name = 'somemp3.mp3'
    with open(file_name, 'wb') as f:
        for chunk in download_response.iter_content(1024):
            f.write(chunk)
    system('rm -rf out')
    system('mp3splt -f -t 0.10 -d out ' + file_name)
    mp3_files = os.listdir("out")
    song_names = list()
    for mp3_file_name in mp3_files:
        print "doing " + str(mp3_file_name) + " now"
        song_json = identify_song(mp3_file_name)
        if song_json == {}:
            continue
        is_success = song_json['status']['code'] == 0
        if not is_success:
            print "Couldn't find it!"
            continue
        print str(json.dumps(song_json['metadata'], indent = 4))
        song_name = song_json['metadata']['music'][0]['title']
        both_times = get_minute_second_tuple_start(mp3_file_name)
        first_min = both_times[0][0]
        first_sec = both_times[0][1]
        sec_min = both_times[1][0]
        sec_sec = both_times[1][1]
        song_names.append(song_name + "{}m:{}s to {}m:{}s".format(first_min,first_sec,sec_min,sec_sec))
    return '<br>'.join(song_names)

def get_minute_second_tuple_start(stri):
    first_min = 0
    first_sec = 0
    sec_min = 0
    sec_sec = 0
    for index, splice in enumerate(stri.split('_')):
        if index == 0:
            continue
        if index == 1:
            first_min = int(splice[:-1])
        if index == 2:
            first_sec  = int(splice[:-1])
        if index == 3:
            continue
        if index == 4:
            sec_min  = int(splice[:-1])
        if index == 5:
            sec_sec = int(splice[:2])
    return ((first_min,first_sec),(sec_min,sec_sec))

def post_multipart(host, selector, fields, files):
    content_type, body = encode_multipart_formdata(fields, files)
    while True:
        try:
            h = httplib.HTTPConnection(host)
            h.putrequest('POST', selector)
            h.putheader('content-type', content_type)
            h.putheader('content-length', str(len(body)))
            h.endheaders()
            h.send(body)
            break
        except:
            continue
    # errcode, errmsg, headers = h.getreply()
    response = h.getresponse()
    # return h.file.read()
    return response.read().decode('utf-8')

def encode_multipart_formdata(fields, files):
    boundary = b"fhajlhafjdhjkfadsjhkfhajsfdhjfdhajkhjsfdakl"
    CRLF = b'\r\n'
    L = []
    for (key, value) in fields.items():
        L.append(b'--' + boundary)
        L.append(('Content-Disposition: form-data; name="%s"' % key).encode('utf-8'))
        L.append(b'')
        L.append(value)
    for (key, value) in files.items():
        L.append(b'--' + boundary)
        L.append(('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, key)).encode('utf-8'))
        L.append(b'Content-Type: application/octet-stream')
        L.append(b'')
        L.append(value)
    L.append(b'--' + boundary + b'--')
    L.append(b'')
    body = CRLF.join(L)
    content_type = ('multipart/form-data; boundary=%s' % boundary.decode('utf-8')).encode('utf-8')
    return content_type, body


def identify_song(file_name):
    file_name =  'out/' + file_name
    f = open(file_name, "rb")
    sample_bytes = os.path.getsize(file_name)
    content = f.read()
    f.close()

    http_method = "POST"
    http_uri = "/v1/identify"
    data_type = "audio"
    signature_version = "1"
    timestamp = time.time()

    print "access key is : " + access_key
    string_to_sign = http_method+"\n"+http_uri+"\n"+access_key+"\n"+data_type+"\n"+signature_version+"\n"+str(timestamp)
    sign = base64.b64encode(hmac.new(access_secret.encode('utf-8'), string_to_sign.encode('utf-8'), digestmod=hashlib.sha1).digest())

    fields = {'access_key':access_key.encode('utf-8'),
              'sample_bytes':str(sample_bytes).encode('utf-8'),
              'timestamp':str(timestamp).encode('utf-8'),
              'signature':sign,
              'data_type':data_type.encode('utf-8'),
              "signature_version":signature_version.encode('utf-8')}

    print "requesting multipart"
    res = post_multipart("ap-southeast-1.api.acrcloud.com", "/v1/identify", fields, {"sample":content})
    try:
        res = json.loads(res)
    except:
        res = {} 
    return res
    result = json.loads(res)
    if result['status']['code']==0: # Success!
        title = result['metadata']['music'][0]['title']
        artists = [i['name'] for i in result['metadata']['music'][0]['artists']]
        if len(artists) == 1:
            artists_string = artists[0]
        else:
            artists = ", ".join(artists[:-1])+" and "+artists[-1]
        if "spotify" in result['metadata']['music'][0]['external_metadata']:
            pv_url = json.loads(urllib2.urlopen("https://api.spotify.com/v1/tracks/"+result['metadata']['music'][0]['external_metadata']['spotify']['track']['id']).read().decode("utf-8"))["preview_url"]
            return "It sounds like "+title+", by "+artists_string+".|"+"spot_preview|"+pv_url
        elif "itunes" in result['metadata']['music'][0]['external_metadata']:
            pv_url = json.loads(urllib2.urlopen("https://itunes.apple.com/lookup?id="+result['metadata']['music'][0]['external_metadata']['itunes']['track']['id']).read().decode("utf-8"))["results"][0]["previewUrl"]
        else:
            return "It sounds like "+title+", by "+artists_string+"."

    elif result['status']['code']==1001:
        return "I don't recognize it."
    else:
        return "I can't find out, the server gave me a "+str(result['status']['code'])+" error."

if __name__ == "__main__":
    app.run(debug = True)
