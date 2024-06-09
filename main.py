import os
import config
from forms import SearchForm, LoginForm
from flask import Flask, render_template
from flask import Flask
from flask import redirect, url_for
from flask import request
import flickr_api
from flickr_api.api import flickr
import sys
import xmltodict, json
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from stripe import StripeClient
from vendors import schematic_python as schematic 

app = Flask(__name__)
flickr_api.set_keys(api_key = os.environ.get("FLICKR_API_KEY"), api_secret=os.environ.get("FLICKR_SECRET_KEY"))
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SQL_DATABASE")
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
db = SQLAlchemy()
#client = StripeClient("sk_test_...")

login_manager = LoginManager()
login_manager.init_app(app)

# Initialize app with extension
db.init_app(app)
# Create database within app context
with app.app_context():
    db.create_all()

# model classes
class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(250), unique=True, nullable=False)
    users = db.relationship('Users', backref='company', lazy=True, uselist=False)
    favorites = db.relationship('Favorites', backref='company', lazy=True)

class Favorites(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(250), unique=True, nullable=False)
    photo_id = db.Column(db.String(250), unique=True, nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)

class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)

## routes

@app.route('/', methods=['GET', 'POST'])
def main():
    form = SearchForm()
    user = current_user
    schematic.send_identify_event(user)
    return render_template('index.html', form=form)

@app.route('/search', methods=['POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        searched_data = form.search.data
        photo_array = retrieve_images_by_keyword(searched_data)

        # send event to schematic
        schematic.send_track_event(current_user,'search-query')

        return render_template('search.html', 
                               form = form,
                               search=searched_data,
                               photos = photo_array)
    return render_template('search.html')

@app.route('/settings')
def settings():
    render_template('settings.html')

@app.route('/submit_favorite/<photo_id>', methods=['GET','POST'])
def add_favorite(photo_id):
    user = current_user

    # POST request -- check if company is at limit already
    if request.method == 'GET' and schematic.check_flag(user.company.id,'favorite-flag'):
        company = Company.query.get(user.company_id)
        favorite = Favorites(photo_id=photo_id)
        company.favorites.append(favorite)
        db.session.add(favorite)
        db.session.commit()

        # update favorite count
        schematic.company_create_update(user, favorite_count=Favorites.query.filter_by(company_id=company.id).count())

        return photo_id
    return photo_id

@app.route('/favorites')
def favorites():
    user = current_user
    company = Company.query.get(current_user.company_id)
    favorites = company.favorites
    photo_array = retrieve_images_by_photo_id(favorites)
    return render_template('favorites.html', 
                               photos = photo_array)

# login, logout, registration

@app.route("/login", methods=["GET", "POST"])
def login():
    # If a post request was made, find the user by filtering for the username
    if request.method == "POST":
        user = Users.query.filter_by(
            username=request.form.get("username")).first()
        # Check if the password entered is the same as the user's password
        if user.password == request.form.get("password"):
            # Use the login_user method to log in the user
            login_user(user)
            # Redirect the user back to the home
            return redirect(url_for("main"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route('/register', methods=["GET", "POST"])
def register():
    # If the user made a POST request, create a new user and company
    if request.method == "POST":        
        user = Users(username=request.form.get("username"),
                     password=request.form.get("password"))
        # Add the user to the database
        company = Company(company=request.form.get("company"),
                          users=user)

        db.session.add(company)
        db.session.add(user)
        # Commit the changes made
        db.session.commit()

        # Create Schematic user and company on registration
        schematic.company_create_update(user)
        schematic.user_create_update(user)

        # Once user account created, redirect them to login route
        return redirect(url_for("login"))
    # Renders sign_up template if user made a GET request
    return render_template("sign_up.html")

# flickr integration
def retrieve_images_by_keyword(search):
    photo_array = {}

    photos = xmltodict.parse(flickr.photos.search(text = search, per_page = 20, page = 1, safe_search = 1))

    for photo in photos['rsp']['photos']['photo']:
        photo_array[photo['@id']] = {"owner" : photo['@owner'], "id" : photo['@id'], "url" : "https://live.staticflickr.com/"+photo['@server']+"/"+photo["@id"]+"_"+photo['@secret']+".jpg"}
    
    return photo_array

def retrieve_images_by_photo_id(photos):
    photo_array = {}
    
    for photo in photos:
        if photo.photo_id:
            photo_metadata = xmltodict.parse(flickr.photos.getInfo(photo_id = photo.photo_id))
            photo_metadata = photo_metadata['rsp']['photo']
            photo_array[photo_metadata['@id']] = {"owner" : photo_metadata['owner']['@nsid'], "id" : photo_metadata['@id'], "url" : "https://live.staticflickr.com/"+photo_metadata['@server']+"/"+photo_metadata["@id"]+"_"+photo_metadata['@secret']+".jpg"}
    
    return photo_array
 
@login_manager.user_loader
def loader_user(user_id):
    return Users.query.get(user_id)
 
if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)