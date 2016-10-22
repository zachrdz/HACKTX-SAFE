from flask import Flask, render_template
import flask_login
from flask_pymongo import PyMongo
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, validators
from werkzeug.security import generate_password_hash, check_password_hash
from twilio.rest import TwilioRestClient
from flask_mail import Mail, Message
import random
import keys

# The signup form
# feel free to change the string values to something better
class RegisterForm(FlaskForm):
	# the verifcation method choices
	verify_choices = [('email', 'Email'), ('text', 'Text Message')]
	# all the fields
	email = StringField('Email', [validators.DataRequired('Email is required'), validators.Email(), unique_email])
	password = PasswordField('Password', [validators.DataRequired('Password is required'),
		validators.EqualTo('repeat_password', 'Passwords are not the same')])
	repeat_password = PasswordField('Repeat Password', [validators.DataRequired('Must repeat password')])
	verify_method = SelectField('Chose Verification Method', choices=verify_choices)
	submit = SubmitField('Sign Up')
	
	# method to check if the email is unique
	def unique_email(self, field):
		result = user_collect.find_one({'email': field})
		if result is not None:
			raise ValidationError('Email already exists')

# set up the app
app = Flask(__name__)
app.secret_key = keys.app_secret()

# set up the login manager
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

# mongo setup
app.config['MONGO_DBNAME'] = 'safe_db'
mongo = PyMongo(app)
user_collect = None

# email stuff
mail = Mail(app)

# the home page
@app.route('/')
def index():
	return render_template('index.html')

# the signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
	form = RegisterForm(request.form)
	if request.method == 'POST' and form.validate():
		email = request.form['email']
		passwordHash = generate_password_hash(request.form['password'])
		verify_method = dict(RegisterForm.verify_choices).get(form['verify_method'].data)
		unique_code = random.randint(1000, 9999)
		
		#place user in database
		user_collect.insert_one({'email': email, 'password': passwordHash, 'verify_code': unique_code})
		
		# send verification msg
		if verify_method == 'email':
			send_verification_email(unique_code, address)
		elif verify_method == 'text':
			send_verification_email(unique_code, address)
		return redirect(url_for('index'))
	elif request.method == 'POST':
		flash_errors(form)
	return render_template('signup.html', form = form)

# send verification email/text/etc.
def send_verification_text(unique_code, address):
	client = TwilioRestClient(keys.twilioSSIDKey(), keys.twilioAuth())
	msg_body = "Your verification code is: " + unique_code
	message = client.messages.create(body = msg_body,
		to = address,
		from_ = keys.phoneNumber())

def send_verification_email(unique_code, address):
	msg_body = "Your verification code is: " + unique_code
	msg = Message('Verification Code', sender = 'blah@blah.blahblah', recipients = [address])
	msg.body = msg_body
	mail.send(msg)

if __name__ == '__main__':
	app.run()