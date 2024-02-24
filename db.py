import pymysql

conn = pymysql.connect(
    host="localhost",
    port=3306,
    database="test",
    user="root",
    password="1qaz2wsx!QAZ@WSX",
    cursorclass=pymysql.cursors.DictCursor
)

cursor = conn.cursor()
sql_query="""CREATE TABLE music(
id INTEGER PRIMARY KEY AUTO_INCREMENT,
musician text NOT NULL,
language text NOT NULL,
title text NOT NULL
)"""
cursor.execute(sql_query)
conn.close()
