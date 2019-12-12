
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
    session.execute("CREATE TABLE IF NOT EXISTS user (username VARCHAR primary key, hashed_password VARCHAR, display_name VARCHAR, homepage_url VARCHAR, email VARCHAR)")
    session.execute("CREATE TABLE IF NOT EXISTS tracks (track_title VARCHAR, album_title VARCHAR, artist VARCHAR, length INT, track_url VARCHAR, album_art_url VARCHAR, track_uuid uuid primary key,descriptions map<VARCHAR, VARCHAR>)")
    session.execute("CREATE TABLE IF NOT EXISTS playlist (playlist_id uuid PRIMARY KEY,playlist_title VARCHAR, username VARCHAR, description VARCHAR, track_uuid set<uuid>)")
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
                    resp = jsonify(results[0])
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
