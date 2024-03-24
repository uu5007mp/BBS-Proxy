from flask import Flask, request, Response
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import os
import base64

app = Flask(__name__)

@app.route('/')
def home():
    return "Proxyサイトへようこそ"

@app.route('/proxy', methods=['GET'])
def proxy():
    url = request.args.get('url', '')
    if not url:
        return "URLが指定されていません", 400

    # 入力されたURLにリクエストを送信
    response = requests.get(url)

    # HTML内のURLを絶対URLに変換し、`/proxy?url=`に追加
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

    # 動画ファイルもdata:の形式で返す
    for tag in soup.find_all('video', src=True):
        if not tag['src'].startswith(('http://', 'https://')):
            resource_url = urljoin(url, tag['src'])
            resource_response = requests.get(resource_url)
            content_type = resource_response.headers.get('content-type', 'video/mp4')
            tag['src'] = f'data:{content_type};base64,{base64.b64encode(resource_response.content).decode()}'

    # iconファイルもdata:の形式で返す
    for tag in soup.find_all('link', rel='icon', href=True):
        if not tag['href'].startswith(('http://', 'https://')):
            resource_url = urljoin(url, tag['href'])
            resource_response = requests.get(resource_url)
            content_type = resource_response.headers.get('content-type', 'image/jpeg')
            tag['href'] = f'data:{content_type};base64,{base64.b64encode(resource_response.content).decode()}'

    # 変換後のHTMLを返す
    response = Response(str(soup))
    response.headers['Access-Control-Allow-Origin'] = '*'  # CORS設定
    return response

if __name__ == '__main__':
    app.run(debug=True)
