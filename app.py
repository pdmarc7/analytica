from flask import Flask, render_template, url_for
import pymysql.cursors

app = Flask(__name__)

@app.route("/")
def home():
    connection = pymysql.connect(
            host='localhost',
            user='root',
            password='coldkov-97',
            database='laravel',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

    with connection.cursor() as cursor:
        # Read a single record
        sql = "show tables;"
        cursor.execute(sql)
        
        response = cursor.fetchall()
        tables = [res['Tables_in_laravel'] for res in response]

    return render_template('index.html', tables=tables)