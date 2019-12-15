
from flask import  Flask, request, jsonify, g
from werkzeug.security import generate_password_hash,check_password_hash
import sqlite3
import uuid
from cassandra.cluster import Cluster


app = Flask(__name__)
app.config["DEBUG"] = True
cluster = Cluster(['172.17.0.2'], port=9042)
session = cluster.connect('music_store')
sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes_le=b))
sqlite3.register_adapter(uuid.UUID, lambda u: buffer(u.bytes_le))

#
##
#   Create Key Space
#cqlsh> CREATE KEYSPACE IF NOT EXISTS music_store WITH REPLICATION = { 'class' :
#'NetworkTopologyStrategy', 'datacenter1' : 1 };




#################code will be moved
# def make_dicts(cursor, row):
#     return dict((cursor.description[idx][0], value)
#                 for idx, value in enumerate(row))

# def get_db():
#     db = getattr(g, '_database', None)

#     if db is None:
#         db = g._database = sqlite3.connect('MUSICDATABASE')
#         db.row_factory = make_dicts
#     db.cursor().execute("PRAGMA foreign_keys=ON")
#     return db


@app.teardown_appcontext
def close_connection(exception):
    # session.execute('DROP TABLE IF EXISTS music_store.user;')
    # session.execute('DROP TABLE IF EXISTS music_store.tracks;')
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def query_db(query, args=(), one=False):
    rows=session.execute(query, args)
    # cur.close()
    return (rows[0] if rows else None) if one else rows

@app.cli.command('init')
def init_db():
    session.execute("DROP TABLE IF EXISTS music_store.user;")
    session.execute("DROP TABLE IF EXISTS music_store.tracks;")
    session.execute("DROP TABLE IF EXISTS music_store.playlist;")
    session.execute("CREATE TABLE IF NOT EXISTS user (username VARCHAR primary key, hashed_password VARCHAR, display_name VARCHAR, homepage_url VARCHAR, email VARCHAR)")
    session.execute("CREATE TABLE IF NOT EXISTS tracks (track_title VARCHAR, album_title VARCHAR, artist VARCHAR, length INT, track_url VARCHAR, album_art_url VARCHAR, track_uuid uuid primary key,descriptions map<VARCHAR, VARCHAR>)")
    session.execute("CREATE TABLE IF NOT EXISTS playlist (playlist_id uuid PRIMARY KEY,playlist_title VARCHAR, username VARCHAR, description VARCHAR, all_tracks set<uuid>)")
    session.execute("INSERT INTO user(username, display_name, hashed_password, homepage_url, email) VALUES ('user_anthony','Anthony','pbkdf2:sha256:150000$bGSxegkS$7598256a7ff683743b0dbe182ee77eec4afce1c8339914f482e4e626491b28b3' ,'useranthony.com', 'anthony@csu.fullerton.edu');")
    session.execute("INSERT INTO user(username, display_name, hashed_password, homepage_url, email) VALUES('user_pavan','Pavan', 'pbkdf2:sha256:150000$bGSxegkS$7598256a7ff683743b0dbe182ee77eec4afce1c8339914f482e4e626491b28b3','userpavan.com','pavan@csu.fullerton.edu');")
    session.execute("INSERT INTO user(username, display_name, hashed_password, homepage_url, email) VALUES('user_priyanka','Priyanka','pbkdf2:sha256:150000$bGSxegkS$7598256a7ff683743b0dbe182ee77eec4afce1c8339914f482e4e626491b28b3', 'userpriyanka.com','priyanka@csu.fullerton.edu');")
    session.execute("INSERT INTO tracks(track_uuid,track_title, album_title, artist, length, track_url,album_art_url, descriptions) VALUES(65bf6758-50f0-4c9f-937e-0b453721def6,'Stronger','Graduation', 'Kanye West', 000511,'http://localhost:8000/media/Waka_waka.mp3','https://i.ytimg.com/vi/pRpeEdMmmQ0/maxresdefault.jpg', {'user_pavan':'workout song by kanye west','user_priyanka':'favorite usher song1'});")
    session.execute("INSERT INTO tracks(track_uuid,track_title, album_title, artist, length, track_url,album_art_url, descriptions) VALUES(275fc399-a955-403d-acb1-58cdb6f273b5,'Stronger','Graduation', 'Kanye West', 000511,'http://localhost:8000/media/Waka_waka.mp3','https://i.ytimg.com/vi/pRpeEdMmmQ0/maxresdefault.jpg', {'user_pavan':'workout song by kanye west','user_priyanka':'favorite usher song1'});")
    session.execute("INSERT INTO tracks(track_uuid,track_title, album_title, artist, length, track_url,album_art_url,descriptions) VALUES(ac3d3e62-d611-4013-8bc9-22d90623d5db,'Yeah!','Confessions', 'Usher', 000410,'http://localhost:8000/media/tokyo_drift.mp3','https://images-na.ssl-images-amazon.com/images/I/81cw8NVT36L._SX342_.jpg', {'user_pavan':'favorite usher song','user_priyanka':'favorite usher song'});")
    session.execute("INSERT INTO tracks(track_uuid,track_title, album_title, artist, length, track_url,album_art_url,descriptions) VALUES(32de3075-797a-4356-9437-9909451645a5,'I Gotta Feeling','The E.N.D.', 'The Black Eyed Peas', 000448,'http://localhost:8000/media/waving_flag.mp3','http://images.genius.com/2d335571e608b43f30bd8a89e1fa6d38.1000x1000x1.jpg',{'user_priyanka':'favorite usher song2','user_anthony':'classic black eyed peas song'});")
    session.execute("INSERT INTO playlist(playlist_id,playlist_title, username, description, all_tracks) VALUES (a1f9d26f-acbd-48cd-b6e5-7b52caae73e7,'All','user_priyanka','This playlist contains all of my songs',{275fc399-a955-403d-acb1-58cdb6f273b5,ac3d3e62-d611-4013-8bc9-22d90623d5db,32de3075-797a-4356-9437-9909451645a5});")
    session.execute("INSERT INTO playlist(playlist_id,playlist_title, username, description, all_tracks) VALUES (d6b647fb-f8d7-49ac-b0f5-68eaa62f1ce4,'All','user_priyanka','This playlist contains all of my songs',{275fc399-a955-403d-acb1-58cdb6f273b5,ac3d3e62-d611-4013-8bc9-22d90623d5db,32de3075-797a-4356-9437-9909451645a5});")
    session.execute("INSERT INTO playlist(playlist_id,playlist_title, username, description, all_tracks) VALUES (3733c647-73d5-4983-9745-1accb3aa0c4f,'Some','user_anthony','This playlist contains some of my songs',{275fc399-a955-403d-acb1-58cdb6f273b5,ac3d3e62-d611-4013-8bc9-22d90623d5db});")
    session.execute("INSERT INTO playlist(playlist_id,playlist_title, username, description, all_tracks) VALUES (6ba5d5ca-0859-44dd-9b2f-6392141e993b,'Some','user_anthony','This playlist contains some of my songs',{275fc399-a955-403d-acb1-58cdb6f273b5,ac3d3e62-d611-4013-8bc9-22d90623d5db});")
    # with app.app_context():
    #     db = get_db()
    #     with app.open_resource('music_store_main.sql', mode='r') as f:
    #         db.cursor().executescript(f.read())
    #     db.commit()



##################################

def authenticate_user(username,password):
    query = "SELECT hashed_password FROM user WHERE username=%s;"
    to_filter= []
    to_filter.append(username)
    results = query_db(query, to_filter)
    if not results:
        return jsonify(message="User Authentication unsuccessful. Try with new password"),401

    authenticated = check_password_hash(results[0][0],password)
    if authenticated:
        return jsonify(message="User Authentication successful"),200

    return jsonify(message="User Authentication unsuccessful. Try with new password"),401


#  To get user profile details &
# To match user name and hashed password
@app.route('/api/v1/resources/user',methods=['GET'])
def GetUser():
        if request.method == 'GET':
            query_parameters = request.args
            username = query_parameters.get('username')
            password = query_parameters.get('password')
            to_filter= []
            if username and password:
                #call the db and check user is present and get the hashed password and match it
                return authenticate_user(username,password)

            elif username:
                #call the db and check user . If yes retrieve the data
                query = "SELECT username,display_name,email,homepage_url FROM user WHERE username=%s;"
                to_filter.append(username)
                results = query_db(query, to_filter)
                if not results:
                    return jsonify(message="No user present. Please provide valid username"),404
                else:
                    resp = jsonify(list(results))
                    resp.headers['Location'] = 'http://127.0.0.1:5000/api/v1/resources/user?username='+username
                    resp.status_code = 200
                    #resp.headers['mimetype']='application/json'
                    return resp




#TO create new user
@app.route('/api/v1/resources/user',methods=['POST'])
def InserUser():
    if request.method == 'POST':
        data = request.get_json(force= True)
        #print(type(data))
        required_fields = ['username', 'display_name', 'password', 'homepage_url', 'email']
        username = data['username']
        password = data['password']

        #To check username and password matching
        if not all([field in data for field in required_fields]):
            return authenticate_user(username,password)

        display_name  = data['display_name']
        email  = data['email']
        homepage_url  = data['homepage_url']
        hashed_password = generate_password_hash(password)
        executionState:bool = False
        #query ="INSERT INTO user(username, display_name, hashed_password, homepage_url, email) VALUES('"+username+"','"+display_name+"','"+hashed_password+"','"+homepage_url+"','"+email+"');"
        query ="INSERT INTO user(username, display_name, hashed_password, homepage_url, email) VALUES (%s, %s, %s, %s, %s)"

        #cur = get_db().cursor()
        try:
            #cur.execute(query)
            print(session)
            session.execute(query,(username, display_name, hashed_password, homepage_url, email))
            executionState=True
            # get_db().commit()
        except:
            # get_db().rollback()
            executionState=False
            print("Error")
        finally:
            if executionState:
                resp = jsonify(message="Data Instersted Sucessfully")
                resp.headers['Location'] = 'http://127.0.0.1:5000/api/v1/resources/user?username='+username
                resp.status_code = 201
                return resp
            else:
                return jsonify(message="Failed to insert data."), 409


#To update user password
@app.route('/api/v1/resources/user',methods=['PATCH'])
def UpdateUserPwd():
        if request.method == 'PATCH':
            to_filter = []
            query_parameters = request.args
            username = query_parameters.get('username')
            data = request.get_json(force= True)
            #print(type(data))
            password = data['password']
            hashed_password = generate_password_hash(password)
            query = "SELECT * FROM user WHERE username=%s;"
            to_filter.append(username)
            results = query_db(query, to_filter)
            if not results:
                return jsonify(message="No user present. Please provide valid username"),404
            else:
                executionState:bool = False
                #cur = get_db().cursor()
                try:
                    session.execute("UPDATE user SET hashed_password=%s WHERE username=%s",(hashed_password,username,))
                    #if cur.rowcount >= 1:
                    executionState = True
                    #get_db().commit()

                except:
                        executionState = True
                        #get_db().rollback()
                        #print("Error")
                finally:
                        if executionState:
                            resp = jsonify(message="Password updated successfully")
                            resp.headers['Location'] = 'http://127.0.0.1:5000/api/v1/resources/user?username='+username
                            resp.status_code = 200
                            return resp

                        else:
                            return jsonify(message="Failed to update password"), 409




#To delete user
@app.route('/api/v1/resources/user',methods=['DELETE'])
def DeleteUser():
        if request.method == 'DELETE':
            query_parameters = request.args
            username = query_parameters.get('username')
            executionState:bool = False
            #cur = get_db().cursor()
            try:
                #session.execute("DELETE FROM user WHERE username=?",(username,))
                session.execute("DELETE FROM music_store.user WHERE username = %s",(username, ))
                #if session.rowcount >= 1:
                executionState = True
                #get_db().commit()

            except:
                executionState=False
                #get_db().rollback()
                #print("Error")
            finally:
                    if executionState:
                        return jsonify(message="Data deleted sucessFully "), 200
                    else:
                        #possibly no user data . so 404
                        return jsonify(message="Failed to delete data"), 404

app.run()
