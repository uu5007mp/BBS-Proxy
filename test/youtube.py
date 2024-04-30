from flask import Flask, render_template, request, send_file
from pytube import YouTube
from urllib.parse import urlparse, parse_qs

app = Flask(__name__)

def get_video_id(url):
    query = urlparse(url)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in {'www.youtube.com', 'youtube.com'}:
        if query.path == '/watch':
            return parse_qs(query.query)['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        video_id = get_video_id(url)
        if video_id:
            try:
                yt = YouTube(f'https://www.youtube.com/watch?v={video_id}')
                stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
                video_url = stream.url
                title = yt.title
                return render_template('index.html', video_url=video_url, title=title, url=url)
            except Exception as e:
                error_message = str(e)
                return render_template('index.html', error_message=error_message)
        else:
            error_message = 'Invalid YouTube URL'
            return render_template('index.html', error_message=error_message)
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    video_id = get_video_id(url)
    if video_id:
        try:
            yt = YouTube(f'https://www.youtube.com/watch?v={video_id}')
            stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
            filename = f"{yt.title.replace('/', '-')}.mp4"
            stream.download(filename)
            return send_file(filename, as_attachment=True)
        except Exception as e:
            error_message = str(e)
            return render_template('index.html', error_message=error_message)
    else:
        error_message = 'Invalid YouTube URL'
        return render_template('index.html', error_message=error_message)

if __name__ == '__main__':
    app.run(debug=True)
