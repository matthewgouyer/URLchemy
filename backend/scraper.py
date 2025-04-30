import requests
from bs4 import BeautifulSoup

def scrape_metadata(url: str) -> dict:
    """
    metadata scraper (title and description) from the given URL.

    @args:
        url (str): The target URL to scrape metadata from.

    @returns:
        dict: A dictionary containing the title and description of the page.
              If an error occurs, returns a dictionary with an error message.
    """
    try:
        response = requests.get(url, timeout=5) # hang santity check
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser") # use built in parser from bs4
        title = soup.title.string if soup.title else "No Title" # simple title extract
        # extraction description w/ simple exception
        description = (
            soup.find("meta", attrs={"name": "description"}) or {}
        ).get("content", "No Description")
        return {"title": title, "description": description}
    except Exception as e:
        return {"title": "Error", "description": str(e)}