from flask import Flask, request, jsonify
import json
import pymysql

app = Flask(__name__)

music_list = [
    {
        "id": 0,
        "musician": "Tame Impala",
        "language": "English",
        "title": "The Less I Know The Better"
    },
    {
        "id": 1,
        "musician": "Kanye West",
        "language": "English",
        "title": "Runaway"
    },
    {
        "id": 2,
        "musician": "Creed",
        "language": "English",
        "title": "My Sacrifice"
    },
    {
        "id": 3,
        "musician": "The Eagles",
        "language": "English",
        "title": "Hotel California"
    }
]
def db_connection():
    conn=None
    try:
       conn = pymysql.connect(
        host="localhost",
        port=3306,
        database="test",
        user="root",
        password="1qaz2wsx!QAZ@WSX",
        cursorclass=pymysql.cursors.DictCursor
        )
    
    except pymysql.Error as e:
        print(e)
    return conn

@app.route('/')
def print_hello():
    return 'hello world'


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

if __name__ == '__main__':
    app.run(debug=True)
