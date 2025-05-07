from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import requests
from dotenv import load_dotenv
import os
from typing import Optional, List, Dict

load_dotenv()

app = Flask(__name__)

API_BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")

def fetch_urls_table() -> List[Dict]:
    """Fetch the URLs table from the backend API."""
    try:
        response = requests.get(f"{API_BASE_URL}/data/urls")
        if response.status_code == 200:
            return response.json().get("data", [])
    except requests.exceptions.RequestException:
        pass
    return []

def create_shortened_url(target_url: str) -> Optional[str]:
    """
    Send a URL to the backend API to create a shortened URL.

    Args:
        target_url (str): The URL to be shortened.

    Returns:
        Optional[str]: The shortened URL if successful, otherwise None.
    """
    try:
        response = requests.post(f"{API_BASE_URL}/url", json={"target_url": target_url})
        if response.status_code == 200:
            return response.json().get("shortened_url", {}).get("url")
        else:
            error_detail = response.json().get("detail", "Unknown error")
            raise ValueError(f"Error: {error_detail}")
    except (requests.exceptions.RequestException, ValueError):
        return None

@app.route("/", methods=["GET", "POST"])
def index():
    """
    Handle the main page of the application.

    On GET:
        - Fetch and display the URLs table.
        - Display a shortened URL if provided in the query string.

    On POST:
        - Process the form to create a shortened URL.

    Returns:
        str: Rendered HTML template for the index page.
    """

    if request.method == "POST":
        target_url = request.form.get("target_url")
        if target_url:
            shortened_url = create_shortened_url(target_url)
            if shortened_url:
                return redirect(url_for("index", shortened_url=shortened_url))
            return "Error: Unable to create shortened URL", 400

    shortened_url = request.args.get("shortened_url")
    urls_table = fetch_urls_table()

    return render_template("index.html", shortened_url=shortened_url, urls_table=urls_table)

if __name__ == "__main__":
    app.run(debug=True)