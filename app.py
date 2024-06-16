from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, PasswordField
from wtforms.validators import DataRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # Replace with your MySQL username
app.config['MYSQL_PASSWORD'] = 'password'  # Replace with your MySQL password
app.config['MYSQL_DB'] = 'byjus_app'  # Replace with your MySQL database name

mysql = MySQL(app)

# Define MySQL tables
class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

class Course:
    def __init__(self, id, title, description):
        self.id = id
        self.title = title
        self.description = description

class EnrollmentForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    payment_method = SelectField('Payment Method', choices=[
        ('credit_card', 'Credit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('upi', 'UPI')
    ], validators=[DataRequired()])

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    message = TextAreaField('Message', validators=[DataRequired()])

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=50)])
    password = PasswordField('Password', validators=[DataRequired()])

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=50)])
    password = PasswordField('Password', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])


@app.route('/')
def home():
    
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM courses')
    courses_data = cursor.fetchall()
    cursor.close()
    courses = [Course(id=course['id'], title=course['title'], description=course['description']) for course in courses_data]
    return render_template('home.html', courses=courses)

@app.route('/course/<int:course_id>', methods=['GET', 'POST'])
def course(course_id):
    form = EnrollmentForm()

    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        payment_method = form.payment_method.data

       
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO enrollments (course_id, name, email, payment_method) VALUES (%s, %s, %s, %s)',
                       (course_id, name, email, payment_method))
        mysql.connection.commit()
        cursor.close()

        flash('Enrollment successful!', 'success')
        return redirect(url_for('home'))

   
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM courses WHERE id = %s', (course_id,))
    course_data = cursor.fetchone()
    cursor.close()
    course = Course(id=course_data['id'], title=course_data['title'], description=course_data['description'])

    return render_template('course.html', course=course, form=form)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()

    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        message = form.message.data

        
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO contacts (name, email, message) VALUES (%s, %s, %s)', (name, email, message))
        mysql.connection.commit()
        cursor.close()

        flash('Message sent successfully!', 'success')
        return redirect(url_for('home'))

    return render_template('contact.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

      
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user_data = cursor.fetchone()
        cursor.close()

        if user_data and check_password_hash(user_data['password'], password):
            session['user_id'] = user_data['id']
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'error')

    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data

        hashed_password = generate_password_hash(password)

        
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO users (username, email, password) VALUES (%s, %s, %s)',
                       (username, email, hashed_password))
        mysql.connection.commit()
        cursor.close()

        flash('Signup successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html', form=form)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out', 'success')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
