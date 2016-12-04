import sqlite3
from flask import Flask, render_template, request
app = Flask(__name__)


@app.route("/")
def main():
    return render_template('index.html')

@app.route("/submit_form", methods=['GET','POST'])
def submit_form():
    conn = sqlite3.connect("email.sqlite")
    c = conn.cursor()
    if request.method == 'POST':
        print request.form
        print "TEST"
        email = request.form['email']
        check_number = c.execute("""SELECT count(*) FROM email WHERE email_address = ?""", (email,))
        duplicate_check = check_number.fetchone()[0]
        if duplicate_check > 0:
            return "Sorry, you are already signed up!"
        else:
            c.execute("""INSERT INTO email(email_address) VALUES (?)""", (email,))
        conn.commit()
        conn.close()
        return email
    return render_template('submit_form.html')

@app.route("/preferences/<int:user_id>", methods=['GET','POST'])
def user_preferences(user_id):
    conn = sqlite3.connect("email.sqlite")
    c = conn.cursor()
    if request.method == 'GET':
        record = c.execute("""SELECT * from email where id = ?""", (user_id,))
        ind = [dict(email_address=row[0], id=row[1], ny_times=row[2], weather=row[3]) for row in record.fetchall()]
        print ind
        conn.close()

        return render_template('preferences.html', ind=ind)


@app.route("/preferences/<int:user_id>/update", methods=['GET','POST'])
def update_pref(user_id):
    conn = sqlite3.connect("email.sqlite")
    c = conn.cursor()
    print request.method
    print user_id
    user_query = c.execute("""SELECT email_address FROM email WHERE id=?""", (user_id,))
    user = [dict(email_address=row[0]) for row in user_query.fetchall()]
    if request.method == 'POST':
        email_address = request.form['email']
        weather = request.form['weather']
        ny_times = request.form['ny_times']
        c.execute("""UPDATE email SET email_address=?, ny_times=?, weather=? WHERE id=?""", (email_address, ny_times, weather, user_id,))
        conn.commit()
        conn.close()
        return render_template('update_preferences.html', user_id=user_id)
    elif request.method == 'GET':
        return render_template('update_preferences.html', user=user)

if __name__ == "__main__":
    app.run()

