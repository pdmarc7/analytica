from flask import Flask, render_template, url_for, jsonify, request
from http import HTTPStatus
import pymysql.cursors
import json



app = Flask(__name__)


def get_connection():
    connection = pymysql.connect(
            host='localhost',
            user='root',
            password='coldkov-97',
            database='laravel',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    return connection

@app.route('/')
def home():
    return render_template('index.html')

@app.route("/tables")
def tables():
    with get_connection().cursor() as cursor:
        # Read a single record
        sql = "show tables;"
        cursor.execute(sql)
        
        response = cursor.fetchall()
    return jsonify([res['Tables_in_laravel'] for res in response]), HTTPStatus.OK

@app.route("/columns", methods=['POST', 'GET'])
def columns():
    table = request.form['table_name']
    with get_connection().cursor() as cursor:
        # Read a single record
        sql = f"describe {table};"
        cursor.execute(sql)
        
        response = cursor.fetchall()
        cols = [res['Field'] for res in response]
        cols.pop(0)
    return jsonify(cols), HTTPStatus.OK


@app.route("/build_report", methods=['POST'])
def build_report():
    try:
        data = list(request.form)[0]
    except Exception as e:
        print(e)
    
    return jsonify("Success"), HTTPStatus.OK