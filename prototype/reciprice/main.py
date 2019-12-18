import re

from flask import Blueprint, render_template
from bson.json_util import dumps
from .extentions import mongo

from . import models
from datetime import datetime, timezone

main = Blueprint("main", __name__)


@main.route('/')
def index():
    userlist = models.get_usernames()
    return render_template("main/index.html", userlist=userlist)


@main.route("/login")
def login():
    return render_template("main/login.html")


@main.route("/user/<username>")
def user_profile(username):
    username_capitalized = str(username).capitalize()
    user = models.load_user_or_404(username_capitalized)
    return '<h1>%s</h1>' % user


@main.route("/user/<username>/create")
def create_user(username):
    users = mongo.db.users
    users.insert({'_id': username, 'created': datetime.now(timezone.utc)})
    return '<h1>Created %s!</h1>' % str(username)


@main.route("/recipe/<name>/create")
def create_recipe(name):
    re = models.Recipe(name, 'prode', ['fdd', 'fdds'], 'dk-kogebogen.dk', datetime.utcnow())
    re.insert()
    return '<h1>Created %s!</h1>' % 'lol'


@main.route("/recipe/<name>")
def recipe_get(name):
    name_slash_restored = name.replace('%2F', '/')
    return '<h1>found %s!</h1>' % models.get_recipe(name_slash_restored)


@main.route("/recipes/")
def list_recipes():
    recipes = mongo.db.recipes.distinct('name')
    return render_template("main/recipes.html", recipes=[(re.sub("\d+$", "", i).strip(), i.replace('/', '%2F')) for i in recipes])


@main.route("/ingredients_json/")
def ingredients_json():
    ingredients = mongo.db.ingredients.find({"name": {"$in": ["h"]}})
    dict_ingredient = dict()
    for item in ingredients:
        dict_ingredient[item["name"]] = item

    return dict_ingredient


@main.route("/ingredients/")
def list_ingredients():
    ingredients = mongo.db.ingredients.find()
    return render_template('main/ingredients.html', ingredients=ingredients)


@main.route("/json/ingredients/")
def list_ingredients_json():
    ingredient_dict = dict()
    ingredients = mongo.db.ingredients.find()
    ingredient_dict["ingredients"] = list(ingredients)
    return dumps(ingredient_dict, ensure_ascii=False)


@main.route("/json/ingredients/<name>")
def list_specific_ingredient_json(name):
    ingredient_dict = dict()
    regex = r'%s' % name
    ingredients = mongo.db.ingredients.find({"name": {"$regex": regex}})
    ingredient_dict["ingredients"] = ingredients
    return dumps(ingredient_dict, ensure_ascii=False)


@main.route("/ingredients/<name>")
def get_ingredient(name):
    ingredient = mongo.db.ingredients.find_one_or_404({"name": name})
    return render_template("main/ingredient.html", ingredient=ingredient)
