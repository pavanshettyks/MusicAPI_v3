#This is to create a xspf file for playing music from minio
#localhost:5600/api/v2/resources/music.xspf?playlist_title=All&username=

from flask import  Flask, request, jsonify, g,Response
import requests
import xspf




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

#print(get_user_info('user_pavan'))
#print(get_track('/home/student/Music/tracks/Stronger.mp3')['artist'])
#print(get_description(username,'/home/student/Music/tracks/Yeah.mp3'))


# To prepare XSPF
@app.route('/api/v1/resources/music.xspf',methods=['GET'])
def Generate_XSPF():
    query_parameters = request.args
    playlist_title= query_parameters.get('playlist_title')
    username = query_parameters.get('username')
    playlist_service_resp = requests.get('http://localhost:8000/api/v1/resources/playlist?playlist_title='+playlist_title+'&username='+username)
    if playlist_service_resp.status_code != 200:
        return jsonify(message="Playlist not found"),404
    playlist_resp = playlist_service_resp.json()
    username = playlist_resp[0]['username']
    creator,info = get_user_info(username)

    playlist_name = playlist_resp[0]['playlist_title']
    playlist_description = playlist_resp[0]['description']
    #print(get_user_info(username))
    x = xspf.Xspf()
    x.title = playlist_name
    x.info = info
    x.creator = creator
    x.annotation = playlist_description
    # Finally, get the XML contents

    all_tracks = playlist_resp[0]['all_tracks']

    for tracks in all_tracks:
        val = tracks['track_uuid'].split('/api/v1/resources/tracks?track_uuid=')
        print(val)
        if len(val) == 1:
            track_uuid = val[0]
        else:
            track_uuid = val[1]
        #print(tracks['track_url'])
        track_details= get_track(track_uuid)
        if track_details:
            annotation = get_description(username,track_uuid)
            track_location_url = track_details['location'].split('http://localhost:8000/media/')
            if len(track_location_url) == 1:
                location = 'http://localhost:8000/media/'+ track_location_url[0]
            else:
                location = track_details['location']
            #track_uuid = val[1]
            #location = 'http://localhost:8000/media/'+ track_details['location']

            #print('user description',get_description(username,track_url))
            x.add_track(title=track_details['title'],       creator=track_details['creator'],   location = location, album=track_details['album'],
                    annotation=annotation, duration=track_details['duration'], image=track_details['image'])

    #print(x)
    y = str.encode('<?xml version="1.0" encoding="UTF-8"?>') + x.toXml()
    #y.write(f, encoding='utf-8', xml_declaration=True)
    #print(y)
    #f = open("playlist.xspf","w+")
    #f.write(str(y.decode("utf-8")))
    #f.close()
    #resp = jsonify(x.toXml())
    #resp.headers['Location'] = 'http://127.0.0.1:5000/api/v1/resources/user?username='+username
    #resp.status_code = 200
    #resp.headers['mimetype']='application/json'
    return Response(y,mimetype='application/xspf+xml',status=200)#playlist_service_resp.json())
