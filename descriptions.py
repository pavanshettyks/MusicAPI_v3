from flask import  Flask, request, jsonify, g
from cassandra.cluster import Cluster
import sqlite3
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


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.cli.command('init')
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('music_store_main.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


#  To get user Description
@app.route('/api/v1/resources/descriptions',methods=['GET'])
def GetDescription():
    if request.method == 'GET':
        query_parameters = request.args
        username = query_parameters.get('username')
        track_uuid = uuid.UUID(query_parameters.get('track_uuid')).hex
        #return jsonify(uuid.UUID(track_uuid)),404
        to_filter = []
        if username and track_uuid:
            #call the db and check user's is present and get the description
            query = "SELECT descriptions FROM tracks WHERE track_uuid=%s ;"
            #to_filter.append(username)
            #to_filter.append(track_uuid)

            results = session.execute(query, (uuid.UUID(track_uuid), ))
            if not results:
                return jsonify(message="No description present"),404
            result=results[0]
            result= result.descriptions
            desc = None
            if result and username in result:
                desc= result[username]
            if desc == None:
                return jsonify(message="No description present"),404
            else:
                output={}
                output['username']=username
                output['description']=desc
                result = []
                result.append(output)
                resp = jsonify(result)
                resp.headers['Location'] = 'http://127.0.0.1:5100/api/v1/resources/descriptions?username='+username+'&'+'track_uuid='+track_uuid
                resp.status_code = 200
                return resp



#TO create new description
@app.route('/api/v1/resources/descriptions',methods=['POST'])
def InserDesc():
    if request.method == 'POST':
        data =request.get_json(force= True)
        to_filter = []
        username = data['username']
        track_uuid = data['track_uuid']
        description = data['description']
        executionState:bool = False
        query = "SELECT * FROM tracks WHERE track_uuid= %s;"
        results = session.execute(query, (uuid.UUID(track_uuid), ))
        if results:
            #query ="INSERT INTO (username, track_uuid, description) VALUES('"+username+"','"+track_uuid+"','"+description+"');"
            query ="UPDATE tracks SET descriptions = descriptions + { %s: %s } WHERE track_uuid = %s;"

            print(query)
            #cur = get_db().cursor()
            try:
                session.execute(query,(username, description, uuid.UUID(track_uuid)))
                #if(cur.rowcount >=1):
                #    executionState = True
                #get_db().commit()
                executionState = True
            except:
                # get_db().rollback()
                executionState = False
                print("Error")
            finally:
                if executionState:
                    resp = jsonify(message="Data Instersted Sucessfully")
                    resp.headers['Location'] = 'http://127.0.0.1:5100/api/v1/resources/descriptions?username='+username+'&'+'track_uuid='+track_uuid
                    resp.status_code = 201
                    return resp
                else:
                    return jsonify(message="Failed to insert data"), 409
        else:
            return jsonify(message="Failed to insert data. Track does not exist"), 409


app.run()
