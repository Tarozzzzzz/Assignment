from flask import Flask, render_template, request, redirect, session, flash
import mysql.connector
from contextlib import closing

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Database connection configuration
DB_HOST = "localhost"
DB_USER = "root"
DB_PASS = ""
DB_NAME = "bank"

# หน้าแรก
@app.route("/")
def index():
    if 'user' not in session:
        return redirect("/login")

    with closing(mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )) as my_db:
        with closing(my_db.cursor(dictionary=True)) as my_cursor:
            sql = "SELECT balance FROM bank_atm WHERE username = %s"
            my_cursor.execute(sql, (session['user'],))
            account = my_cursor.fetchone()

    return render_template("index.html", balance=account['balance'])

# หน้าเข้าสู่ระบบ
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        session['user'] = username
        return redirect("/")
    return render_template("login.html")

# สร้างบัญชีผู้ใช้
@app.route("/create_account", methods=["GET", "POST"])
def create_account():
    if request.method == "POST":
        account_number = request.form['account_number']
        username = request.form['username']
        balance = float(request.form['balance'])

        try:
            with closing(mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASS,
                database=DB_NAME
            )) as my_db:
                with closing(my_db.cursor()) as my_cursor:
                    sql = "INSERT INTO bank_atm (account_number, username, balance) VALUES (%s, %s, %s)"
                    my_cursor.execute(sql, (account_number, username, balance))
                    my_db.commit()
            flash("บัญชีผู้ใช้สร้างเรียบร้อยแล้ว!", "success")
            return redirect("/")

        except mysql.connector.IntegrityError:
            flash("หมายเลขบัญชีหรือชื่อผู้ใช้นี้มีอยู่แล้ว กรุณาลองใหม่อีกครั้ง.", "danger")

    return render_template("create_account.html")

# ฝากเงิน
@app.route("/deposit", methods=["POST"])
def deposit():
    account_number = request.form['account_number']
    amount = float(request.form['amount'])

    with closing(mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )) as my_db:
        with closing(my_db.cursor()) as my_cursor:
            sql = "UPDATE bank_atm SET balance = balance + %s WHERE account_number = %s"
            my_cursor.execute(sql, (amount, account_number))
            my_db.commit()

    return redirect("/")

# ถอนเงิน
@app.route("/withdraw", methods=["POST"])
def withdraw():
    account_number = request.form['account_number']
    amount = float(request.form['amount'])

    with closing(mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )) as my_db:
        with closing(my_db.cursor()) as my_cursor:
            sql = "UPDATE bank_atm SET balance = balance - %s WHERE account_number = %s"
            my_cursor.execute(sql, (amount, account_number))
            my_db.commit()

    return redirect("/")

# ลบบัญชีผู้ใช้
@app.route("/delete_account", methods=["POST"])
def delete_account():
    username = session['user']
    with closing(mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )) as my_db:
        with closing(my_db.cursor()) as my_cursor:
            sql = "DELETE FROM bank_atm WHERE username = %s"
            my_cursor.execute(sql, (username,))
            my_db.commit()

    session.pop('user', None)
    return redirect("/")

# ล็อกเอาต์
@app.route("/logout")
def logout():
    session.pop('user', None)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)