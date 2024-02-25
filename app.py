from flask import Flask, request, jsonify, render_template,redirect,url_for,request
import json
import pymysql
import random as rand

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

songs = []
plList = []
playlists = {}

def parse_file():
    dataFile = open("data/spotify_dataset.csv",'r')
    lines = dataFile.readlines()
    datasetLines = lines[1:]
    playlists = {}
    songSet = set()
    plSet = set()
    for line in datasetLines:
        lineFormat = line.split("\",\"")
        plName = lineFormat[3].replace('\"', '').replace('\n', '').replace(',','').strip()
        if not(plName in playlists):
            playlists[plName] = []
        playlists[plName].append((lineFormat[1], lineFormat[2]))
        songSet.add(lineFormat[2])
        plSet.add(plName)
    
    plList = [item for item in plSet]
    songs = [item for item in songSet]
    plSet = {}
    songSet = {}

def get_usr_recs():
    i = 0
    fitness_threshold = 0.2
    usrPL = get_user_playlist()
    recSongs = True
    temp = init_state(1000, plList)
    userRecs = set()

    while recSongs:
        if i > 500:
            temp = init_state(1000, plList)

        try:
            for member in temp:
                tempMember = fit_func(member, usrPL, fitness_threshold)
                member = tempMember
                if member[1] > fitness_threshold:
                    for song in member[0]:
                        if song[1] in usrPL:
                            continue
                        userRecs.add(song)
                elif member[1] > max:
                    max = member[1]
        except:
            print(f"Exception")
        
        try:
            tempSorted = sorted(temp, key=lambda x: x[1], reverse=True)
        except:
            print(f"Exception")

        temp = splice_playlists(temp)

        i = i + 1
        if len(userRecs) >= 10:
            recSongs = False

@app.route('/')
def print_hello():
    return render_template('index.html')

@app.route('/login.html')
def user_login():
    return render_template('login.html')

@app.route('/playlist.html')
def playlist():
    return render_template('playlist.html', songs=songs)

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
        return render_template('playlist.html')
    else:
        # Insert the new user if the username doesn't exist
        sql = "INSERT INTO login (USERNAME, PASSWORD) VALUES (%s, %s)"
        cursor.execute(sql, (new_user, new_password))
        conn.commit()
        return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
