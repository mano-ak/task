from flask import Flask, render_template,request,session,redirect,url_for
from flask_mysqldb import MySQL
from flask_session import Session
import bcrypt
import pymongo
import redis

app = Flask(__name__, template_folder='HTML',static_url_path='/static',static_folder='static')
app.secret_key = 'hello'


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Mano@2026'
app.config['MYSQL_DB'] = 'logindata'
mysql = MySQL(app)

app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_REDIS'] = redis.Redis(host='localhost', port=6379, password='mano2026') 
Session(app)

mongo_client = pymongo.MongoClient('mongodb://localhost:27017/')
mongo_db = mongo_client['user_profiles']
mongo_collection = mongo_db['users']



@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
        email = request.form['email']
        age= request.form['age']
        contact= request.form['contact']
        
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO users (username, password, email, age, contact) VALUES (%s, %s, %s, %s, %s)', (username, password, email, age, contact))
        mysql.connection.commit()
        cursor.close()

        user_profile={
            'username':username,
            'email':email,
            'age': age,
            'contact':contact
        }
        mongo_collection.insert_one(user_profile)
        
        return redirect(url_for('login')) 
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        
        username = request.form['username']
        password = request.form['password'].encode('utf-8')
        
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT password FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        cursor.close()

        
        if user and bcrypt.checkpw(password, user[0].encode('utf-8')):
            session['username'] = username
            session['password'] = password
            return redirect(url_for('profile'))
        else:
            return 'Invalid username or password'
    return render_template('login.html')

@app.route('/profile')
def profile():
    if 'username' in session:
        username = session['username']
        user_profiles=mongo_collection.find_one({'username':username})
        if user_profiles:
            return render_template('profile.html', username=username, email=user_profiles['email'],age=user_profiles['age'], contact=user_profiles['contact'])
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
