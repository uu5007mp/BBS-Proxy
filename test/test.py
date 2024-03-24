from flask import Flask, request, Response, render_template_string
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import base64

app = Flask(__name__)

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

@app.route('/proxy', methods=['GET'])
def proxy():
    url = request.args.get('url', '')
    if not url:
        return "URLが指定されていません", 400

    response = requests.get(url)

    soup = BeautifulSoup(response.text, 'html.parser')
    for tag in soup.find_all('a', href=True):
        tag['href'] = '/proxy?url=' + urljoin(url, tag['href'])
    for tag in soup.find_all(['link', 'script', 'img'], src=True):
        if not tag['src'].startswith(('http://', 'https://')):
            resource_url = urljoin(url, tag['src'])
            resource_response = requests.get(resource_url)
            content_type = resource_response.headers.get('content-type', 'application/octet-stream')
            if 'text' in content_type or 'html' in content_type:
                tag['src'] = f'data:{content_type};base64,{base64.b64encode(resource_response.content).decode()}'
            else:
                tag['src'] = resource_url
    for tag in soup.find_all('link', rel='stylesheet', href=True):
        if not tag['href'].startswith(('http://', 'https://')):
            resource_url = urljoin(url, tag['href'])
            resource_response = requests.get(resource_url)
            content_type = resource_response.headers.get('content-type', 'text/css')
            tag['href'] = f'data:{content_type};base64,{base64.b64encode(resource_response.content).decode()}'

    for tag in soup.find_all('video', src=True):
        if not tag['src'].startswith(('http://', 'https://')):
            resource_url = urljoin(url, tag['src'])
            resource_response = requests.get(resource_url)
            content_type = resource_response.headers.get('content-type', 'video/mp4')
            tag['src'] = f'data:{content_type};base64,{base64.b64encode(resource_response.content).decode()}'

    for tag in soup.find_all('link', rel='icon', href=True):
        if not tag['href'].startswith(('http://', 'https://')):
            resource_url = urljoin(url, tag['href'])
            resource_response = requests.get(resource_url)
            content_type = resource_response.headers.get('content-type', 'image/jpeg')
            tag['href'] = f'data:{content_type};base64,{base64.b64encode(resource_response.content).decode()}'

    response = Response(str(soup))
    response.headers['Access-Control-Allow-Origin'] = '*'  
    return response

if __name__ == '__main__':
    app.run(debug=True)
