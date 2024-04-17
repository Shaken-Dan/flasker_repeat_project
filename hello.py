from datetime import datetime, date

from flask import Flask, render_template, flash, request, redirect, url_for
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, EqualTo
from wtforms.widgets.core import TextArea

app = Flask(__name__)
# Add database
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db' # that one had problem with file directory location
# Old SQLite DB
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.getcwd(), 'users.db')
# New MySQL DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://shd:Astana2013!#@localhost/our_users'
app.config['SECRET_KEY'] = "thisismysupersecretkeyever3498398439843984349"
# Initialize The Database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Login Flask Stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


# JSON things
@app.route('/date')
def get_current_date():
    return {"Date": date.today()}


# Create a Blog Post Model
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))


# Create Blog Post Form
class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = StringField('Content', validators=[DataRequired()], widget=TextArea())
    author = StringField('Author', validators=[DataRequired()])
    slug = StringField('Slug', validators=[DataRequired()])
    submit = SubmitField('Submit')


# Create Model for Data Base
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(200), nullable=False, unique=True)
    favorite_color = db.Column(db.String(200))
    date_time = db.Column(db.DateTime, default=datetime.utcnow)
    # Do some password stuff!
    password_hash = db.Column(db.String(128))

    # password_hash2 = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('password is not readable!')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Create a String
    def __repr__(self):
        return '<Name %r>' % self.name


# Create a form class
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    favorite_color = StringField("Favorite Color")
    password_hash = PasswordField("Password", validators=[DataRequired(),
                                                          EqualTo("password_hash2", message="Passwords must match")])
    password_hash2 = PasswordField("Confirm password", validators=[DataRequired()])
    submit = SubmitField('Submit')


class PasswordForm(FlaskForm):
    email = StringField('What is your email?', validators=[DataRequired()])
    password_hash = PasswordField('What is your password?', validators=[DataRequired()])
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            # Hash the password!!!
            hashed_pw = generate_password_hash(form.password_hash.data, "pbkdf2:sha256")
            user = Users(name=form.name.data,
                         email=form.email.data,
                         favorite_color=form.favorite_color.data,
                         password_hash=hashed_pw,
                         username=form.username.data
                         )
            db.session.add(user)
            db.session.commit()
            name = form.name.data
            form.name.data = ''
            form.email.data = ''
            form.favorite_color.data = ''
            form.password_hash.data = ''
            form.username.data = ''

            flash(f"User {name} added successfully!")  # Improvement suggestion 1
    our_users = Users.query.order_by(Users.date_time)
    return render_template('add_user.html', form=form, name=name, our_users=our_users)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/user/<name>')
def user_view(name):
    return render_template('user.html', user_name=name)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500


# Creat3
@app.route('/name', methods=['GET', 'POST'])
def name_view():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("Form Submitted Successfully")

    return render_template('name.html',
                           name=name,
                           form=form)


@app.route("/update/<int:id>", methods=['POST', 'GET'])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        try:
            db.session.commit()
            flash("User Updated Successfully")
            return render_template('update.html',
                                   form=form,
                                   name_to_update=name_to_update)
        except:
            flash("Error! Looks like there is a problem! Please try again.")
            return render_template('update.html',
                                   form=form,
                                   name_to_update=name_to_update)
    else:
        return render_template('update.html',
                               form=form,
                               name_to_update=name_to_update,
                               id=id)


@app.route('/delete/<int:id>', methods=['POST', 'GET'])
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()

    try:
        if user_to_delete:
            db.session.delete(user_to_delete)
            db.session.commit()
            flash("User deleted successfully!")
            our_users = Users.query.order_by(Users.date_time)
            return render_template('add_user.html', form=form, name=name, our_users=our_users)
    except:
        flash("Oops! There was a problem deleting user! Try again.")
        return render_template('add_user.html', form=form, name=name, our_users=our_users)


# Create Password Test Page
@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data

        form.email.data = ''
        form.password_hash.data = ''

        pw_to_check = Users.query.filter_by(email=email).first()

        # Check hashed password
        passed = check_password_hash(pw_to_check.password_hash, password)

    return render_template('test_pw.html',
                           form=form,
                           email=email,
                           pw_to_check=pw_to_check,
                           passed=passed,
                           password=password)


# Add a post page
@app.route('/add-post', methods=['GET', 'POST'])
def add_post():
    form = PostForm()
    try:
        if form.validate_on_submit():
            post = Post(title=form.title.data,
                        content=form.content.data,
                        author=form.author.data,
                        slug=form.slug.data)

            # Clear page data
            form.title.data = ''
            form.content.data = ''
            form.author.data = ''
            form.slug.data = ''

            # Send data to database
            db.session.add(post)
            db.session.commit()

            flash("You have successfully send post!")
    except Exception as e:
        flash('Error is: ' + str(e))

    return render_template('add_post.html', form=form)


@app.route('/posts', methods=['GET', 'POST'])
def posts():
    all_posts = Post.query.order_by(Post.date_posted)

    return render_template('posts.html', all_posts=all_posts)


@app.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post_id = Post.query.get_or_404(id)
    return render_template('post.html', post_id=post_id)


# Editing the post
@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
def edit_post(id):
    post_edit = Post.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post_edit.title = form.title.data
        post_edit.author = form.author.data
        post_edit.slug = form.slug.data
        post_edit.content = form.content.data

        # Update the database
        db.session.add(post_edit)
        db.session.commit()
        flash('Post has been updated!')
        return redirect(url_for('post', id=post_edit.id))

    # To show on a screen current data of a post
    form.title.data = post_edit.title
    form.author.data = post_edit.author
    form.slug.data = post_edit.slug
    form.content.data = post_edit.content

    return render_template('edit_post.html', form=form)


@app.route('/posts/delete/<int:id>')
def delete_post(id):
    # Grab post from database by id
    post_to_delete = Post.query.get_or_404(id)
    try:
        db.session.delete(post_to_delete)
        db.session.commit()
        flash("Post has been deleted")
        all_posts = Post.query.order_by(Post.date_posted)
        return render_template('posts.html', all_posts=all_posts)

    except:
        flash('Some problems!')
        all_posts = Post.query.order_by(Post.date_posted)
        return render_template('posts.html', all_posts=all_posts)


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            # Check the hash, hash is taken from database unhashed and compared to password entered by user
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Login Successfull!!")
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong Password or Username, please try again.")
        else:
            flash("User does not exist!")

    return render_template('login.html', form=form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("Logged out ")
    return redirect(url_for('login'))


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')


if __name__ == "__main__":
    app.run(debug=True)
