import math
import io
import csv

from flask import Blueprint, render_template, request, send_file
from app import db


bp = Blueprint('visits', __name__, url_prefix='/visits')

PER_PAGE = 10

@bp.route('/stat')
def stat():
    download_status = False
    if request.args.get('download_csv'):
        download_status = True
    query = '''
    SELECT visit_logs.path, count(visit_logs.path) AS count
    FROM visit_logs GROUP BY visit_logs.path ORDER BY count DESC
    '''
    with db.connection.cursor(named_tuple = True) as cursor:
        cursor.execute(query)
        print(cursor.statement)
        db_stat = cursor.fetchall()
    if download_status:
        f = io.BytesIO()
        f.write("№,Path,Counter\n".encode("utf-8"))
        for i, row in enumerate(db_stat):
            f.write(f'{i+1},{row.path},{row.count}\n'.encode("utf-8"))
        f.seek(0)
        return send_file(f, as_attachment=True, download_name="stat.csv", mimetype="text/csv")
        
    return render_template('visits/stat.html', stats = db_stat)


@bp.route('/logs')
def logs():
    page = request.args.get('page', 1, type=int)
    query = '''
    SELECT visit_logs.*, users.login
    FROM visit_logs
    LEFT JOIN users ON visit_logs.user_id = users.id
    LIMIT %s
    OFFSET %s
    '''
    query_counter = 'SELECT count(*) as page_count FROM visit_logs'
    with db.connection.cursor(named_tuple = True) as cursor:
        cursor.execute(query,(PER_PAGE, PER_PAGE * (page - 1)))
        print(cursor.statement)
        db_logs = cursor.fetchall()

    with db.connection.cursor(named_tuple = True) as cursor:
        cursor.execute(query_counter)
        print(cursor.statement)
        db_counter = cursor.fetchone().page_count
    
    page_count = math.ceil(db_counter / PER_PAGE)
        
    return render_template('visits/logs.html', logs = db_logs, page = page, page_count = page_count)

