#This is to create a xspf file for playing music from minio
#localhost:5600/api/v2/resources/music.xspf?playlist_title=All&username=

from flask import  Flask, request, jsonify, g,Response
from pymemcache.client import base
import requests
import xspf
import json

app = Flask(__name__)
app.config["DEBUG"] = True

#get user full name and info(homepage_url)
def get_user_info(username):
    querry_url = 'http://localhost:8000/api/v1/resources/user?username='+username
    user_service_resp = requests.get(querry_url)
    if user_service_resp.status_code != 200:
        return '',''
    user_resp = user_service_resp.json()
    return user_resp[0]['display_name'],user_resp[0]['homepage_url']

#get description for a track
def get_description(username,trackID):
    querry_url = 'http://localhost:8000/api/v1/resources/descriptions?username='+username+'&track_uuid='+trackID
    descriptions_service_resp = requests.get(querry_url)
    if descriptions_service_resp.status_code != 200:
        return ''
    descriptions_resp = descriptions_service_resp.json()
    return descriptions_resp[0]['description']

#get track details
def get_track(trackUUID):
    #querry_url = 'http://localhost:8000/api/v1/resources/tracks?track_url='+trackID
    querry_url = 'http://localhost:8000/api/v1/resources/tracks?track_uuid='+trackUUID
    track_service_resp = requests.get(querry_url)
    if track_service_resp.status_code != 200:
        return False
    track_details = {}
    track_resp = track_service_resp.json()
    track_details['title'] = track_resp[0]['track_title']
    track_details['album'] = track_resp[0]['album_title']
    track_details['creator'] = track_resp[0]['artist']
    track_details['duration'] = str(track_resp[0]['length'])
    track_details['location'] = track_resp[0]['track_url']
    track_details['image'] = track_resp[0]['album_art_url']
    return track_details

## Convert the JSON value to XSPF
def Convert_JsonToXSPF(json_value):
    json_value = json.loads(json_value)
    x = xspf.Xspf()
    x.title = json_value['title']
    x.info = json_value['info']
    x.creator = json_value['creator']
    x.annotation = json_value['annotation']
    for track_details in json_value['all_tracks']:
        x.add_track(title=track_details['title'],creator=track_details['creator'],
                location = track_details['location'], album=track_details['album'],
                annotation=track_details['annotation'], duration=track_details['duration'],
                image=track_details['image'])
    return str.encode('<?xml version="1.0" encoding="UTF-8"?>')+x.toXml()

def serviceCallsToGetXSPF(playlist_id):
    playlist_service_resp = requests.get('http://localhost:8000/api/v1/resources/playlist?playlist_id='+playlist_id)
    if playlist_service_resp.status_code != 200:
        return None#jsonify(message="Playlist not found"),404
    playlist_resp = playlist_service_resp.json()
    username = playlist_resp[0]['username']
    creator,info = get_user_info(username)
    playlist_name = playlist_resp[0]['playlist_title']
    playlist_description = playlist_resp[0]['description']
    playlist_json = { }
    playlist_json['title']= playlist_name
    playlist_json['info'] = info
    playlist_json['creator'] = creator
    playlist_json['annotation'] = playlist_description
    all_tracks = playlist_resp[0]['all_tracks']
    list_track_details = []
    for tracks in all_tracks:
        val = tracks['track_uuid'].split('/api/v1/resources/tracks?track_uuid=')
        if len(val) == 1:
            track_uuid = val[0]
        else:
            track_uuid = val[1]
        track_details= get_track(track_uuid)
        if track_details:
            annotation = get_description(username,track_uuid)
            track_details['annotation'] = annotation
            track_location_url = track_details['location'].split('http://localhost:8000/media/')
            if len(track_location_url) == 1:
                location = 'http://localhost:8000/media/'+ track_location_url[0]
            else:
                location = track_details['location']
            track_details['location'] = location
            '''x.add_track(title=track_details['title'], creator=track_details['creator'],
                    location = location, album=track_details['album'],
                    annotation=annotation, duration=track_details['duration'],
                     image=track_details['image'])'''
            list_track_details.append(track_details)
    playlist_json['all_tracks'] = list_track_details
    return json.dumps(playlist_json, indent=4)


# To prepare XSPF
@app.route('/api/v1/resources/music.xspf',methods=['GET'])
def Generate_XSPF():
    query_parameters = request.args
    playlist_id= query_parameters.get('playlist_id')
    #username = query_parameters.get('username')
    client = base.Client(('localhost', 11211))
    key = playlist_id
    playlist_json = client.get(key)
    if not playlist_json:
        print("calling services..................")
        playlist_json = serviceCallsToGetXSPF(playlist_id)
        if playlist_json:
            client.set(str(key), playlist_json,expire =60)
        else:
            return jsonify(message="Playlist not found"),404
    else:
        print("Its in buffer,.....................")

    y = Convert_JsonToXSPF(playlist_json)
    #f = open("playlist.xspf","w+")
    #f.write(str(y.decode("utf-8")))
    #f.close()
    return Response(y,mimetype='application/xspf+xml',status=200)#playlist_service_resp.json())
