from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import mysql.connector
import pandas as pd
 
app = Flask(__name__)
#CORS(app,origins="http://localhost:8080")
cors = CORS(app, resources={r"/*": {"origins": "*"}})
#@app.route('/register_user', methods=['OPTIONS'])
#def test_option():
#    return jsonify({'status': "ok"})

@app.route('/', methods=['GET'])
def index():
    return render_template('register.html')


@app.route('/register_user', methods=['POST','OPTIONS'])
def register_user():
    if request.method == 'OPTIONS':
        response = jsonify()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Origin'] = 'Content-Type'
        return response

    data = request.get_json()
 
    username = data['username']
    password = data['password']
    
    # connect radius server
    raddb = mysql.connector.connect(
        user='localuser', 
        host='localhost', 
        database='radius',
	password='localuser_pwd'
    )
 
    cursor = raddb.cursor()
    cmd = 'INSERT INTO radcheck (username, attribute, op, value) VALUES (%s, %s, %s, %s)'
    val = (username, "Cleartext-Password", ":=", password)
    cursor.execute(cmd, val)
 
    raddb.commit()
    print(cursor.rowcount, ', user: {} inserted'.format(username))
 
    raddb.close()
    
	
    response = jsonify({'status': "ok"})
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response
 
@app.route('/get_traffic', methods=['POST'])
def get_traffic():
    data = request.get_json()
 
    username = data['username']
 
    # connect radius server
    raddb = mysql.connector.connect(
        user='root', 
        host='localhost', 
        database='radius'
    )
 
    cursor = raddb.cursor()
 
    df = pd.read_sql("SELECT * FROM radacct", con=raddb)
 
    input_traffic = df.loc[df['username'] == username, 'acctinputoctets']
    output_traffic = df.loc[df['username'] == username, 'acctoutputoctets']
 
    raddb.close()
 
    return jsonify({'input_traffic': input_traffic, 'output_traffic': output_traffic})
 
if __name__ == '__main__':
    app.run(host='10.1.0.1', port=8081)
