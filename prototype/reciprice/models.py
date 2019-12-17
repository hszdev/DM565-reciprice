from datetime import datetime, timezone

from .extentions import mongo


class User:
    def __init__(self, username, created):
        self.username = username
        self.created = created

    # Returns the dictionary key that identifies this user
    def get_id(self):
        return {'_id': self._id}

    # Replaces the database user date with data from this object.
    # Will create the user, if it does not already exist.
    def replace(self):
        mongo.db.users.replace_one(self.get_id(), self.__dict__, upsert=True)

    # Changes the username, and optionally updates the database as well
    def set_username(self, username, update_db=True):
        if update_db:
            mongo.db.users.update_one(self.get_id(), {'_id': username})
        self.username = username

    # Changes the creation time, and optionally updates the database as well
    def set_created(self, created, update_db=True):
        if update_db:
            mongo.db.users.update_one(self.get_id(), {'created': created})
        self.created = created

    def __repr__(self):
        return 'User(%s, %s)' % (self._id, self.created)


# Returns a user object with data populated from the database
def load_user(username):
    user = mongo.db.users.find_one({'_id': username})
    return User(user['_id'], user['created'])


# Returns a user object or cause 404 error
def load_user_or_404(username):
    user = mongo.db.users.find_one_or_404({'_id': username})
    return User(user['_id'], user['created'])


# Creates a new user in the database and returns it as an object
# Warning: This will replace any existing user by that name
def create_user(username):
    user = User(username, datetime.now(timezone.utc))
    user.replace()
    return user


# Returns a list of each username in the database
def get_usernames():
    return list(map(str, mongo.db.users.distinct('_id')))


# Returns the count of users
def user_count():
    return mongo.db.users.count_documents({})


class Recipe:
    def __init__(self, name, procedure, ingredient_list, source, created):
        self.name = name
        self.procedure = procedure
        self.ingredient_list = ingredient_list
        self.source = source
        self.created = created

    def insert(self):
        recipes = mongo.db.recipes
        recipes.insert(self.__dict__)


def get_recipe(name):
    recipe = mongo.db.recipes.find_one_or_404(name)
    return Recipe(name=recipe['_id'], procedure=recipe['procedure'], ingredient_list=recipe['ingredient_list'], source=recipe['source'],
                  created=recipe['created'])


"""
The Ingredient class holds the name of the ingredient, a list of product identifiers, and if it has an alias.
"""


class Ingredient:
    def __init__(self, name, product_list, alias=[]):
        self.name = name
        self.alias = alias  # different names that are the same ingredient
        self.product_list = product_list  # link the products we have scraped from bilkas website

    def insert(self):
        ingredients = mongo.db.ingredients
        return ingredients.insert(self.__dict__)


def get_ingredient(name):
    ingredient = mongo.db.ingredients.find_one_or_404({'name': name})
    return Ingredient(name=ingredient['name'], alias=['alias'], product_list=['product_list'])


class Product:
    def __init__(self, name, amount, unit, price, price_history, ean=0):
        self.ean = ean
        self.name = name
        self.amount = amount
        self.unit = unit
        self.price = price
        self.price_history = price_history

    def insert(self):
        products = mongo.db.products
        return products.insert(self.__dict__)
