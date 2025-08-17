from flask import Flask, render_template, request, redirect, url_for, session
from dotenv import load_dotenv
import os
import requests

# Load API key from .env
load_dotenv()
API_KEY = os.getenv("API_KEY")

app = Flask(__name__)
app.secret_key = 'supersecretkey123'  # Needed for session handling

# Dummy user credentials (replace with database later)
USER_CREDENTIALS = {"username": "Aish@123", "password": "siddiqa"}

# Function to fetch recipes from Spoonacular API
def fetch_recipes(ingredient=None):
    url = "https://api.spoonacular.com/recipes/complexSearch"
    params = {
        "apiKey": API_KEY,
        "number": 10,
        "addRecipeInformation": True
    }
    if ingredient:
        params["includeIngredients"] = ingredient

    response = requests.get(url, params=params)
    data = response.json()
    recipes_list = []

    for r in data.get("results", []):
        nutrients_list = r.get("nutrition", {}).get("nutrients", [])
        protein = next((n['amount'] for n in nutrients_list if n['name'] == "Protein"), 0)
        carbs = next((n['amount'] for n in nutrients_list if n['name'] == "Carbohydrates"), 0)
        fat = next((n['amount'] for n in nutrients_list if n['name'] == "Fat"), 0)
        calories = next((n['amount'] for n in nutrients_list if n['name'] == "Calories"), 0)

        recipes_list.append({
            "name": r.get("title"),
            "ingredients": [ing['name'] for ing in r.get("extendedIngredients", [])],
            "image": r.get("image"),
            "calories": calories,
            "nutrients": f"Protein: {protein}g, Carbs: {carbs}g, Fat: {fat}g"
        })
    return recipes_list

# Routes
@app.route("/")
def home():
    if "username" in session:
        return render_template("homepage.html", username=session["username"])
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username != USER_CREDENTIALS["username"]:
            error = "Username not found"
        elif password != USER_CREDENTIALS["password"]:
            error = "Incorrect password"
        else:
            session["username"] = username
            return redirect(url_for("home"))
        
        return render_template("login.html", error=error)
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

@app.route("/recipes", methods=["GET"])
def show_recipes():
    if "username" not in session:
        return redirect(url_for("login"))
    
    ingredient = request.args.get("ingredient")
    recipes = fetch_recipes(ingredient)
    return render_template("recipe.html", recipes=recipes)

@app.route("/search", methods=["GET"])
def search():
    if "username" not in session:
        return redirect(url_for("login"))

    ingredient = request.args.get("ingredient")
    recipes = fetch_recipes(ingredient)
    return render_template("recipe.html", recipes=recipes)

if __name__ == "__main__":
    app.run(debug=True)