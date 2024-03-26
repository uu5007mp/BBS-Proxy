from flask import Flask, request, Response, render_template_string, redirect
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import base64
import time

app = Flask(__name__)

blocked_ip = None
block_duration = 10

url_request_counts = {}

def block_ip():
    global blocked_ip
    blocked_ip = request.remote_addr
    time.sleep(block_duration)
    blocked_ip = None

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
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
        }

        h1 {
            text-align: center;
            padding-top: 20px;
            color: #333;
        }

        form {
            max-width: 600px;
            margin: 20px auto;
            padding: 20px;
            background: #fff;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        label {
            font-size: 16px;
            color: #333;
        }

        input[type="text"] {
            width: 100%;
            padding: 8px;
            margin-top: 5px;
            margin-bottom: 10px;
            box-sizing: border-box;
            border: 1px solid #ccc;
            border-radius: 4px;
        }

        input[type="submit"] {
            width: 100%;
            padding: 10px;
            background-color: #333;
            color: #fff;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }

        input[type="submit"]:hover {
            background-color: #555;
        }
    </style>
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
    global blocked_ip
    if blocked_ip == request.remote_addr:
        return "一時的にアクセスが制限されています。しばらくしてから再度お試しください。", 403

    url = request.args.get('url', '')
    if not url:
        return "URLが指定されていません", 400

    url_request_counts[url] = url_request_counts.get(url, 0) + 1
    if url_request_counts[url] > 5:
        block_ip()
        return "一時的にアクセスが制限されています。しばらくしてから再度お試しください。", 403

    try:
        response = requests.get(url, verify=False, timeout=15)
    except requests.Timeout:
        return "タイムアウトしました", 504
    except Exception as e:
        return f"エラーが発生しました: {e}", 500

    if 'youtube.com' in url:
        video_id = url.split('v=')[-1].split('&')[0]
        return f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>YouTube動画</title>
        </head>
        <body style="margin: 0; padding: 0; overflow: hidden; background-color: #000;">
            <iframe width="100%" height="100%" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allowfullscreen></iframe>
        </body>
        </html>
        '''

    soup = BeautifulSoup(response.text, 'html.parser')
    for tag in soup.find_all('a', href=True):
        tag['href'] = '/proxy?url=' + urljoin(url, tag['href'])
    for tag in soup.find_all(['link', 'script', 'img'], src=True):
        if tag['src'].startswith('data:'):
            continue
        if not tag['src'].startswith(('http://', 'https://')):
            resource_url = urljoin(url, tag['src'])
            resource_response = requests.get(resource_url, verify=False)
            content_type = resource_response.headers.get('content-type', 'application/octet-stream')
            tag['src'] = f'data:{content_type};base64,{base64.b64encode(resource_response.content).decode()}'
    for tag in soup.find_all('link', rel='stylesheet', href=True):
        if tag['href'].startswith('data:'):
            continue
        if not tag['href'].startswith(('http://', 'https://')):
            resource_url = urljoin(url, tag['href'])
            resource_response = requests.get(resource_url, verify=False)
            content_type = resource_response.headers.get('content-type', 'text/css')
            tag['href'] = f'data:{content_type};base64,{base64.b64encode(resource_response.content).decode()}'
    for tag in soup.find_all('link', rel='icon', href=True):
        if tag['href'].startswith('data:'):
            continue
        if not tag['href'].startswith(('http://', 'https://')):
            resource_url = urljoin(url, tag['href'])
            resource_response = requests.get(resource_url, verify=False)
            content_type = resource_response.headers.get('content-type', 'image/jpeg')
            tag['href'] = f'data:{content_type};base64,{base64.b64encode(resource_response.content).decode()}'

    response = Response(str(soup))
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/search')
def search():
    q_param = request.args.get('q', '')
    if not q_param:
        return "検索クエリが指定されていません", 400

    google_url = f'https://www.google.co.jp/search?q={q_param}'
    return redirect(f'/proxy?url={google_url}')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3523)
