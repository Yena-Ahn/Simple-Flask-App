from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

#db config
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def convert_ms_to_text(ms):
    min = ms // 60000
    sec = (ms % 60000) // 1000
    ms = ms % 1000
    if min > 0 and sec > 0:
        return f"{min:03d}m {sec:02d}s {ms:03d}ms"
    if sec > 0:
        return f"{sec}s {ms}ms"
    return f"{ms}ms"

def convert_ms_to_minsecms(ms):
    min = ms // 60000
    sec = (ms % 60000) // 1000
    ms = ms % 1000
    if min > 0 and sec > 0:
        return min, sec, ms
    if sec > 0:
        return 0, sec, ms
    return 0, 0, ms

def convert_to_ms(min, sec, ms):
    return int(min) * 60000 + int(sec) * 1000 + int(ms)

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/view")
def view():
    conn = get_db_connection()
    records = conn.execute('SELECT * FROM leaderboard ORDER BY time_taken').fetchall()
    records = [(record['id'], record['player_name'], convert_ms_to_text(record['time_taken']), record['date'], record['difficulty']) for record in records]
    conn.close()
    return render_template('view.html', records=records)

@app.route("/add")
def add():
    return render_template('add.html')

@app.route("/edit/<int:id>", methods=['GET', 'POST'])
def edit(id):
    conn=get_db_connection()
    record = conn.execute("SELECT * FROM leaderboard WHERE id=?", (id,)).fetchone()
    
    converted_min, converted_sec, converted_ms = convert_ms_to_minsecms(record['time_taken'])
    
    if request.method == "POST":
        
        if request.form['action'] == "save":
            player_name = request.form['player_name']
            time_taken_min = request.form['time_taken_min']
            time_taken_sec = request.form['time_taken_sec']
            time_taken_ms = request.form['time_taken_ms']
            date = request.form['date']
            difficulty = request.form['difficulty']
            converted_ms = convert_to_ms(time_taken_min, time_taken_sec, time_taken_ms)
            conn.execute('UPDATE leaderboard SET player_name = ?, time_taken = ?, date = ?, difficulty = ? WHERE id = ?', 
                    (player_name, converted_ms, date, difficulty, id))
            conn.commit()
            conn.close()
            return redirect(url_for('view'))
        
        elif request.form['action'] == 'delete':
            conn.execute("DELETE FROM leaderboard WHERE id=?", (id,))
            conn.commit()
            conn.close()
            return redirect(url_for('view'))   
        
    conn.close()
    return render_template('edit.html', record=record, converted_min=converted_min, converted_sec=converted_sec, converted_ms=converted_ms)
    


if __name__ == "__main__":
    app.run(debug=True)