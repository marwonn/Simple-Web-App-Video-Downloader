from __future__ import unicode_literals
from flask import Flask, render_template, request, redirect, url_for, session, g, Response
import youtube_dl 
from re import search
import urllib.request

global_username = "private"
global_password = "private"
global_user_id = 999

radio_button = ""
url = ""

app = Flask(__name__)
app.secret_key = 'jkfhleafaegjebjehgeagerohgier'

@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        g.user = global_user_id


@app.route("/")
def index():
    if not g.user:
        return redirect(url_for('login'))

    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user_id', None)

        username = request.form['username']
        password = request.form['password']
        
        if global_username == username and global_password == password:
            session['user_id'] = global_user_id
            return redirect(url_for('index'))
        
        return redirect(url_for('login'))

    return render_template('login.html')


@app.route("/download", methods=["POST"])
def download():
    if (request.method == "POST" 
        and request.form.get("url") != ""
        and search("http", (request.form.get("url")))):

        global url
        url = ""
        url = request.form.get("url")

        global radio_button
        radio_button = request.form["option"]
        
        ydl_opts = {}
        file_format = []

        if radio_button == "option1":
            ydl_opts.update({      
                    'format':'best',
                    'noplaylist':True,
                    })
            file_format.append("HD Video")

        else:
             ydl_opts.update({      
                    'format':'bestaudio/best',
                    'noplaylist':True,
                    'extractaudio':True,
                    'audioformat':"mp3"
                    })
        file_format.append("Audio")

        meta = youtube_dl.YoutubeDL(ydl_opts).extract_info(url, download=False)

        thumbnail_url = meta.get("thumbnail")
        title = meta.get("title")
        extension = meta.get("ext")
        download_url = meta.get("url")
        file_format = file_format[0]


        return render_template("download.html", 
                                thumbnail_url = thumbnail_url,
                                title = title,
                                download_url = download_url,
                                extension = extension,
                                file_format = file_format)

    else:   
        return render_template("index.html")

@app.route("/start_download", methods=["GET", "POST"])
def start_download():
    ydl_opts = {}

    if radio_button == "option1":
        ydl_opts.update({      
                'format':'best',
                'noplaylist':True,
                })

    else:
            ydl_opts.update({      
                'format':'bestaudio/best',
                'noplaylist':True,
                'extractaudio':True,
                'audioformat':"mp3"
                })

    if "yout" in url:

        meta = youtube_dl.YoutubeDL(ydl_opts).extract_info(url, download=False)
        download_url = meta.get("url")
        title = meta.get("title")

        r = urllib.request.urlopen(download_url)
        content_type = r.info().get_content_type()
        extension = r.info().get_content_subtype()

        attachment = f"attachment; filename={title}.{extension}"

        return Response(
            r,
            mimetype=content_type,
            headers={"Content-disposition":
                    attachment})

    else:
        with youtube_dl.YoutubeDL(dict(forceurl=True)) as ydl:
            urls_mp4 = ydl.extract_info(url, download=False)
            url_mp4 = [format['url'] for format in urls_mp4['formats'] if format["url"].endswith(".mp4")][-1]
            r = urllib.request.urlopen(url_mp4)
            content_type = r.info().get_content_type()
            extension = r.info().get_content_subtype()
            title = urls_mp4.get("title")
            attachment = f"attachment; filename={title}.{extension}"
           
        return Response(
            r,
            mimetype=content_type,
            headers={"Content-disposition":
                    attachment})


app.run(host='127.0.0.1',port=8000,debug=True)

# if __name__ == '__main__':
#     app.run()