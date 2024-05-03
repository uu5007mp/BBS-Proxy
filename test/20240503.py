from flask import Flask, request, Response, render_template_string
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse, urljoin
import re

app = Flask(__name__)

def normalize_url(url):
    parsed_url = urlparse(url)
    clean_url = parsed_url.scheme + '://' + parsed_url.netloc + parsed_url.path
    return clean_url

@app.route('/')
def home():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Proxyサイト</title>
    </head>
    <body>
        <h1>Proxyサイト</h1>
        <form action="/proxy" method="get">
            <label for="url">URLを入力してください:</label><br>
            <input type="text" id="url" name="url"><br><br>
            <input type="submit" value="Submit">
        </form>
    </body>
    </html>
    ''')

@app.route('/proxy', methods=['GET', 'POST'])
def proxy():
    url = normalize_url(request.args.get('url', ''))
    if not url:
        return "URLが指定されていません", 400

    response = requests.get(url)
    response.encoding = 'utf-8'

    soup = BeautifulSoup(response.text, 'html.parser')

    meta_tag = soup.new_tag('meta', charset='UTF-8')
    soup.head.insert(0, meta_tag)

    for tag in soup.find_all('a', href=True):
        tag['href'] = '/proxy?url=' + urljoin(url, tag['href'])
    for tag in soup.find_all(['link', 'script', 'img'], src=True):
        if tag['src'].startswith('data:'):
            continue
        tag['src'] = urljoin(url, tag['src'])
    for tag in soup.find_all('link', rel='stylesheet', href=True):
        if tag['href'].startswith('data:'):
            continue
        tag['href'] = urljoin(url, tag['href'])
    for tag in soup.find_all('link', rel='icon', href=True):
        if tag['href'].startswith('data:'):
            continue
        tag['href'] = urljoin(url, tag['href'])

    for script in soup.find_all('script'):
        if script.string:
            redirect_match = re.search(r'window\.location\.href\s*=\s*"(.+?)"', script.string)
            if redirect_match:
                redirect_url = redirect_match.group(1)
                if not redirect_url.startswith(('http://', 'https://')):
                    redirect_url = urljoin(url, redirect_url)
                script.string.replace_with(f'window.location.href = "/proxy?url={redirect_url}"')

    response = Response(str(soup))
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3523)
