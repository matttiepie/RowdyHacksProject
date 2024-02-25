from flask import Flask, request, jsonify, render_template,redirect,url_for,request
import json
import pymysql

app = Flask(__name__)

def db_connection():
    conn=None
    try:
       conn = pymysql.connect(
        host="partygoer.mysql.database.azure.com",
        database="herewego",
        user="matthewmartinez",
        password="1qaz2wsx!QAZ@WSX",
        cursorclass=pymysql.cursors.DictCursor
        )
    
    except pymysql.Error as e:
        print(e)
    return conn

# selector functionality
plList = []
songs = []
playlists = {}

@app.route('/')
def print_hello():
    return render_template('index.html')


@app.route('/music', methods=['GET', 'POST'])
def music():
    conn=db_connection()
    cursor=conn.cursor()
    
    if request.method == 'GET':
        cursor.execute("SELECT * FROM music")
        musics= [
            dict(id=row['id'], musician=row['musician'],
            language=row['language'],title=row['title'])
            for row in cursor.fetchall()
        ]
        if musics is not None:
            return jsonify(musics)

    if request.method == "POST":
        new_musician = request.form['musician']
        new_lang = request.form['language']
        new_title = request.form['title']
        sql="""INSERT INTO music (musician, language, title) VALUES (%s,%s,%s)"""
        cursor=cursor.execute(sql,(new_musician,new_lang,new_title))
        conn.commit()
        return "complete"
    
@app.route('/addUser', methods=['POST'])
def addUser():
    conn=db_connection()
    cursor=conn.cursor()
   # Retrieve data from the form
    new_user = request.form['USERNAME']
    new_password = request.form['PASSWORD']

# Check if the username already exists
    check_sql = "SELECT * FROM login WHERE USERNAME = %s"
    cursor.execute(check_sql, (new_user,))
    existing_user = cursor.fetchone()

    if existing_user:
        error_message = "Username already exists. Please choose a different username."
        return render_template('next.html')
    else:
        # Insert the new user if the username doesn't exist
        sql = "INSERT INTO login (USERNAME, PASSWORD) VALUES (%s, %s)"
        cursor.execute(sql, (new_user, new_password))
        conn.commit()
        return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
