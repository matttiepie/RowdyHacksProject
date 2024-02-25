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

def get_user_playlist():
  userPlaylist = []
  for i in range (0,10):
    userPlaylist.append(songs[rand.randint(0, len(songs) - 1)])
  return userPlaylist

def fit_func(state, usrPL, target):
  fitness = 0
  count = 0

  for item in state[0]:
    try:
      if item[1] in usrPL:
        count = count + 1
    except:
        continue
  if count > 0:
    percent = count / len(state[0])
    if percent >= target:
      fitness = ((-1 * (1/(1 - target)) * abs(percent - target)) + 1)
    else:
      fitness = (-1 * (1 / target) * abs(percent - target) + 1)
  fitness = fitness + (1/len(usrPL))
  if fitness < 0:
    fitness = 0
  elif fitness > 1:
    fitness = 1
  state[1] = fitness
  return state

def init_state(size, spikedPL):
  try:
    init = []
    for i in range(0, min(len(spikedPL),size)):
      newMember = playlists[spikedPL[rand.randint(0, len(spikedPL) - 1)]]
      init.append([newMember, 0])
    return init
  except:
    print(f"Exception")
    return -1

def splice_playlists(state):
  state = [member for member in state]
  newState = []
  splitInd = 0

  for i in range(0, len(state), 2):
    child_1 = []
    child_2 = []
    splitInd = rand.randint(0, min(len(state[i][0]), len(state[i + 1][0])) - 1)
    child_1.append(state[i][0][:splitInd] + state[i + 1][0][splitInd:])
    child_1.append(0.0)
    child_2.append(state[i + 1][0][:splitInd] + state[i][0][splitInd:])
    child_2.append(0.0)

    chance = rand.randint(0,20)
    if chance == 0:
      child_1[0][rand.randint(0, len(child_1[0]) - 1)] = songs[rand.randint(0, len(songs) - 1)]
    elif chance == 1:
      child_2[0][rand.randint(0, len(child_2[0]) - 1)] = songs[rand.randint(0, len(songs) - 1)]

    newState.append(child_1)
    newState.append(child_2)
  return newState

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

@app.route('/playlist.html/search')
def song_search():
    found = []
    song_name = request.form.get("song_name")
    for song in songs:
        if song_name in song:
            found.append(song)
    return render_template('playlist.html', found=found)


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
