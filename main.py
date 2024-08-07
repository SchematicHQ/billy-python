import os
from forms import SearchForm
from flask import Flask, render_template
from flask import Flask
from flask import redirect, url_for
from flask import request
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from vendors import schematic_python as schematic
from vendors import flickr
from models import db, Company, Favorites, Users

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SQL_DATABASE")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

# client = StripeClient("sk_test_...")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "Please log in to access this page"

# Initialize app with extension
db.init_app(app)
# Create database within app context
with app.app_context():
    db.create_all()


@app.context_processor
def set_global_html_variable_values():
    user = current_user
    # company = Company.query.get(user.company_id)

    template_config = {}

    company_id = user.company.id if hasattr(user, "company") else None
    company_name = user.company.company if hasattr(user, "company") else None
    search_feature = schematic.check_flag(company_id, "search-queries")
    favorite_feature = schematic.check_flag(company_id, "favorites")

    template_config = {
        "company_name": company_name,
        "search_feature": search_feature,
        "favorite_feature": favorite_feature,
    }

    return template_config


######
## Page routes
######


@app.route("/", methods=["GET", "POST"])
@login_required
def main():
    form = SearchForm()
    user = current_user
    search_feature = schematic.check_flag(user.company.id, "search-queries")
    schematic.send_identify_event(user)

    return render_template(
        "index.html",
        form=form,
        search_feature=search_feature,
        current_path=request.path,
    )


@app.route("/search", methods=["POST"])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        searched_data = form.search.data
        photo_array = flickr.retrieve_images_by_keyword(searched_data)

        # send event to schematic
        schematic.send_track_event(current_user, "search-query")

        return render_template(
            "search.html", form=form, search=searched_data, photos=photo_array
        )
    return render_template("search.html")


@app.route("/settings")
def settings():
    user = current_user

    response = schematic.get_company(user)

    return render_template("settings.html", current_path=request.path)


@app.route("/settings/change_plan/<plan_id>")
def change_plan(plan_id):
    user = current_user

    if request.method == "GET":
        schematic.company_create_update(user, plan=plan_id)

        return plan_id

    return render_template("settings.html", current_path=request.path)


@app.route("/favorites")
def favorites():
    user = current_user
    company = Company.query.get(current_user.company_id)
    favorites = company.favorites
    photo_array = flickr.retrieve_images_by_photo_id(favorites)

    return render_template(
        "favorites.html", photos=photo_array, current_path=request.path
    )


@app.route("/submit_favorite/<photo_id>", methods=["GET", "POST"])
def add_favorite(photo_id):
    user = current_user

    # POST request -- check if company is at limit already
    if request.method == "GET" and schematic.check_flag(
        user.company.id, "favorites"
    ):
        company = Company.query.get(user.company_id)
        favorite = Favorites(photo_id=photo_id)
        company.favorites.append(favorite)
        db.session.add(favorite)
        db.session.commit()

        # update favorite count
        schematic.company_create_update(
            user,
            favorite_count=Favorites.query.filter_by(company_id=company.id).count(),
        )

        return photo_id
    return photo_id


######
# Authentication Routes - Login, logout, registration
######
@app.route("/login", methods=["GET", "POST"])
def login():
    # If a post request was made, find the user by filtering for the username
    if request.method == "POST":
        user = Users.query.filter_by(username=request.form.get("username")).first()

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


@app.route("/register", methods=["GET", "POST"])
def register():
    # If the user made a POST request, create a new user and company
    if request.method == "POST":
        user = Users(
            username=request.form.get("username"), password=request.form.get("password")
        )
        # Add the user to the database
        company = Company(company=request.form.get("company"), users=user)

        db.session.add(company)
        db.session.add(user)
        # Commit the changes made
        db.session.commit()

        # Create Schematic user and company on registration
        schematic.company_create_update(user, plan="basic")
        schematic.user_create_update(user)

        # Once user account created, redirect them to login route
        return redirect(url_for("login"))
    # Renders sign_up template if user made a GET request
    return render_template("sign_up.html")


@login_manager.user_loader
def loader_user(user_id):
    return Users.query.get(user_id)


if __name__ == "__main__":
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)