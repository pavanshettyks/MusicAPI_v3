from flask import  Flask, request, jsonify, g
import sqlite3
from cassandra.cluster import Cluster
import uuid


app = Flask(__name__)
app.config["DEBUG"] = True
cluster = Cluster(['172.17.0.2'], port=9042)
session = cluster.connect('music_store')

def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('MUSICDATABASE')
        db.row_factory = make_dicts
    db.cursor().execute("PRAGMA foreign_keys=ON")
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()



@app.cli.command('init')
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('music_store_main.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()



def query_db(query,args=(),one=False):
    cur = get_db().execute(query,args)
    rv = cur.fetchall()
    cur.close()
    return(rv[0] if rv else None) if one else rv



# #TO create new playlist
# def generate_multiple_insert(all_tracks,username,playlist_title):
#     querry = "INSERT INTO playlist (username, playlist_title,track_uuid) VALUES"
#     value_querry = ""
#     track_uuid =""
#     for track in all_tracks:
#          val = track['track_uuid'].split('/api/v1/resources/tracks?track_uuid=')

#          if len(val) == 1:
#              track_uuid = val[0]
#          else:
#              track_uuid = val[1]
#          value_querry = value_querry + "('"+username+"','"+playlist_title+"','"+track_uuid+"') ,"
#     value_querry = value_querry[:-1]+';'
#     querry = querry + value_querry
#     #print(querry)
#     return querry


#TO create new playlist
@app.route('/api/v1/resources/playlist',methods=['POST'])
def InsertPlaylist():
        if request.method == 'POST':
            data =request.get_json(force= True)
            to_filter = []
            playlist_title = data['playlist_title']
            username = data['username']
            description = data['description']
            all_tracks = data['all_tracks']
            playlist_id = uuid.uuid4()
            executionState:bool = False
            query = "SELECT playlist_title FROM playlist WHERE playlist_title=%s AND username =%s ALLOW FILTERING;"
            # to_filter.append(playlist_title)
            # to_filter.append(username)
            results = session.execute(query, (playlist_title, username))
            if not results:
                #query ="INSERT INTO playlist(playlist_title,username, description) VALUES('"+playlist_title+"','"+username+"','"+description+"');"
                query ="INSERT INTO playlist(playlist_id, playlist_title,username, description) VALUES(%s, %s, %s, %s);"
                #cur = get_db().cursor()
                #cur2 = get_db().cursor()
                try:
                    session.execute(query,(playlist_id, playlist_title,username, description))
                    #if(cur.rowcount >=1):
                    executionState = True
                    if all_tracks:
                        query = "UPDATE playlist SET all_tracks = track_uuid + {%s} WHERE playlist_id=%s;"
                        for track in all_tracks:
                            session.execute(query,(uuid.UUID(track['track_uuid']),playlist_id))
                        # multi_insert_querry = generate_multiple_insert(all_tracks,username,playlist_title)
                        #print(multi_insert_querry)
                        #session.execute(multi_insert_querry)
                    #get_db().commit()
                except:
                    #get_db().rollback()
                    executionState = False
                    #print("error")
                finally:
                    if executionState:
                        resp = jsonify(message="Data Instersted Sucessfully"+ "playlist_id:"+playlist_id.hex)
                        resp.headers['Location'] = 'http://127.0.0.1:5300/api/v1/resources/playlist?playlist_title='+playlist_title+'&'+'username='+username
                        resp.status_code = 201
                        return resp
                    else:
                        return jsonify(message="Failed to insert data"), 409
            else:
                return jsonify(message="Failed to insert data."), 409


# #to delete a playlist
# def delete_all_tracks(playlist_title,username):
#     to_filter = []
#     query = "SELECT * FROM playlist_tracks WHERE username=? AND playlist_title=?;"
#     to_filter.append(username)
#     to_filter.append(playlist_title)
#     res = query_db(query, to_filter)
#     cur = get_db().cursor()
#     if res:

#         try:
#             cur.execute("DELETE FROM playlist_tracks WHERE playlist_title=? AND username =?;",(playlist_title,username,))
#             if cur.rowcount >= 1:
#                 executionState = True

#             get_db().commit()
#         except:
#                 get_db().rollback()

#         finally:
#             print("deleted relevant playlist_tracks data")



#to delete a playlist
@app.route('/api/v1/resources/playlist', methods=['DELETE'])
def DeletePlaylist():
    if request.method == 'DELETE':
        query_parameters = request.args
        playlist_id = query_parameters.get('playlist_id')
        executionState:bool = False
        # cur = get_db().cursor()
        try:
            session.execute("DELETE FROM playlist WHERE playlist_id=%s;",(uuid.UUID(playlist_id), ))
            # if cur.rowcount >= 1:
            executionState = True
            # get_db().commit()
        except:
            executionState= False
            # get_db().rollback()
            #print("Error")
        finally:
            if executionState:
                #delete_all_tracks(playlist_title,username)
                return jsonify(message="Data SucessFully deleted"), 200
            else:
                return jsonify(message="Failed to delete data"), 409



#to list  playlists
@app.route('/api/v1/resources/playlist', methods=['GET'])
def GetAllPlaylist():
    if request.method=='GET':
        query_parameters = request.args
        playlist_id = query_parameters.get('playlist_id')
        username = query_parameters.get('username')
        to_filter = []
        if playlist_id:
            query = "SELECT playlist_title,username,description FROM playlist WHERE playlist_id= %s;"
            #to_filter.append(username)
            #to_filter.append(playlist_title)

            results = session.execute(query, (uuid.UUID(playlist_id),))
            if not results:
                return jsonify(message="No playlist present"), 404
            else:
                mmap ={}
                query = "SELECT all_tracks FROM playlist WHERE playlist_id= %s;"
                track_uuid = session.execute(query, (uuid.UUID(playlist_id), ))
                track_uuid = track_uuid[0]
                track_uuid = track_uuid.track_uuid
                rv=list()
                for track in track_uuid:
                    output={'http://127.0.0.1:5200/api/v1/resources/tracks?track_uuid='+track.hex}
                    #output['track_uuid'] = 'http://127.0.0.1:5200/api/v1/resources/tracks?track_uuid='+track.hex
                    rv+=output
                    #track['track_uuid'] = 'http://127.0.0.1:5200/api/v1/resources/tracks?track_uuid='+track['track_uuid']
                #results[0]['all_tracks']= track_uuid

                resp = jsonify(rv)

                resp.headers['Location']='http://127.0.0.1:5300/api/v1/resources/playlist?playlist_id='+playlist_id
                resp.status_code = 200
                return resp

        elif username:
            query = "SELECT playlist_title,username,description FROM playlist WHERE username=%s ALLOW FILTERING;"
            to_filter.append(username)
            results = session.execute(query, (username,))
            rv=list()
            for row in results:
                output={row}
                rv += output
            if not rv:
                return jsonify(message="No playlist present"), 404
            else:
                resp = jsonify(rv)
                resp.headers['Location']='http://127.0.0.1:5300/api/v1/resources/playlist?username='+username
                resp.status_code = 200
                return resp
        else:
            query = "SELECT playlist_title,username,description FROM playlist;"

            rv=list()
            rows = session.execute(query)
            for row in rows:
                output={row}
                rv += output
            if not rv:
                return jsonify(message="No playlist present"), 404
            else:
                resp = jsonify(rv)
                resp.headers['Location']='http://127.0.0.1:5300/api/v1/resources/playlist'
                resp.status_code = 200
                return resp



app.run()
