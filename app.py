from flask import Flask, render_template, url_for, jsonify, request
from http import HTTPStatus
from jinja2 import Template

import pymysql.cursors
import json
import os

app = Flask(__name__)

def get_connection():
    connection = pymysql.connect(
            host='localhost',
            user=os.environ['dbuser'],
            password=os.environ['dbpassword'],
            database='laravel',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    return connection


def create_statement(obj):

    template = Template('''SELECT{% for selector in obj['selectors'] %}{% if loop.last %}{% if selector['alias'] != '' %} {{ selector['column'] }} AS '{{ selector['alias'] }}'{% else %} {{ selector['column'] }}{% endif %}{% else %}{% if selector['alias'] != '' %} {{ selector['column'] }} AS '{{ selector['alias'] }}',{% else %} {{ selector['column'] }},{% endif %}{% endif %}{% endfor %} FROM {{ obj['table'] }} {% if obj['filters'] == [] %}{% else %}WHERE{% for filter in obj['filters'] %}{% if loop.first %}{% else %} {{ filter['logicalOperator'] }}{% endif %} {{ filter['filterTarget'] }} {{ operators[filter['operation']] }} {{ filter['filterValue'] }}{% endfor %};{% endif %}''')


    operators = {
        "EQUAL": '=',
        "GREATER THAN": '>',
        "LESS THAN": '<',
        "GREATER THAN OR EQUAL TO": '>='
    }

    sql_statement = template.render(obj=obj, operators=operators)
    return sql_statement

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

        report =""
        data = json.loads(list(request.form)[0])
        
        template = Template('''
<table class="table">
    <thead>
        <tr>
        {% for head in headers %}
            <th class="col">{{ head | upper }}</th>
        {% endfor %}
        </tr>
    </thead>
    <tbody>
        {% for row in rows %}
        <tr>
            {% for head in headers %}
                <td>{{ row[head] }}</td>
            {% endfor %}
        </tr>
        {% endfor %}
    </tbody>
</table>

            ''')

        for obj in data:
            sql = create_statement(obj)
            with get_connection().cursor() as cursor:
                cursor.execute(sql)
                rows = list(cursor.fetchall())
                
                if rows != []:
                    headers = rows[0].keys()
                    report = report + template.render(rows=rows, headers=headers)
    except Exception as e:
        print(e)
    
    return jsonify({'html': report}), HTTPStatus.OK