from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from bs4 import BeautifulSoup
import requests
app = FastAPI()

@app.get("/")
def index(url: str = None):
    if url is None:
        return {"error": "Please provide a URL"}
    page = requests.get(url)
    bs = BeautifulSoup(page.text, 'html.parser')
    for i in bs.find_all(True):
        if 'href' in i.attrs:
            i["href"] = "http://127.0.0.1:8000/?url=" + i["href"]
    page = bs.prettify()
    return HTMLResponse(content=page, status_code=200)