import os
from forms import SearchForm, LoginForm
from flask import Flask, render_template
from flask import Flask
from flask import redirect, url_for
from flask import request
import flickr_api
from flickr_api.api import flickr
import sys
import xmltodict, json
from flask_simplelogin import SimpleLogin, get_username, login_required
import config

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
flickr_api.set_keys(api_key = os.environ.get("FLICKR_API_KEY"), api_secret=os.environ.get("FLICKR_SECRET_KEY"))

simple_login = SimpleLogin(app)

# set config variables
#SECRET_KEY = os.urandom(32)
#app.config['SECRET_KEY'] = SECRET_KEY

@app.route('/', methods=['GET', 'POST'])
@login_required()
def main():
    form = SearchForm()
    return render_template('index.html', form=form)

@app.route('/search', methods=['POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        print("in", file=sys.stderr)
        searched_data = form.search.data
        photo_array = search_flickr(searched_data)
        return render_template('search.html', 
                               form = form,
                               search=searched_data,
                               photos = photo_array)
    return render_template('search.html')

@app.route('/settings')
def settings():
    render_template('settings.html')

@app.route('/favorites')
def favorites():
    render_template('favorites.html')

# function to perform flickr search
def search_flickr(search):
    photo_array = {}

    photos = xmltodict.parse(flickr.photos.search(text = search, per_page = 20, page = 1, safe_search = 1))

    for photo in photos['rsp']['photos']['photo']:
        photo_array[photo['@id']] = {"owner" : photo['@owner'], "id" : photo['@id'], "url" : "https://live.staticflickr.com/"+photo['@server']+"/"+photo["@id"]+"_"+photo['@secret']+".jpg"}
    
    print(photo_array, file=sys.stderr)

    return photo_array

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)