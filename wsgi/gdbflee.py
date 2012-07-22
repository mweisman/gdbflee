#!/usr/bin/python

from flask import Flask, request, redirect, send_from_directory, url_for, render_template
from hashlib import sha1
from uuid import uuid1
from werkzeug import secure_filename
import json, fgdb, os, zipfile, glob

UPLOAD_FOLDER = os.environ['HOME'] + '/app-root/data/tmp'
static = os.environ['HOME'] + '/app-root/repo/wsgi/static/'
ALLOWED_EXTENSIONS = set(['zip'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route("/", methods=['GET'])
def index():
    return render_template('index.html')


@app.route("/freeme", methods=['POST'])
def upload_file():
    if request.method == 'POST':
        store_key = sha1(str(uuid1())).hexdigest()
        file = request.files['file']
        format = request.values['format']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], store_key)
            tmp_path = os.path.join(app.config['UPLOAD_FOLDER'], store_key, "tmp")
            gdb_path = os.path.join(app.config['UPLOAD_FOLDER'], store_key, "in")
            out_path = os.path.join(app.config['UPLOAD_FOLDER'], store_key, "out")
            os.mkdir(path)
            os.mkdir(tmp_path)
            os.mkdir(gdb_path)
            os.mkdir(out_path)
            up_file = os.path.join(tmp_path, filename)
            file.save(up_file)
            if zipfile.is_zipfile(up_file):
                zip = zipfile.ZipFile(up_file, "r")
                for item in zip.namelist():
                    if '.gdb/' in item:
                        zip.extract(item, gdb_path)
                for gdb in os.listdir(gdb_path):
                    gdb_name = os.path.splitext(gdb)[0]
                    gdb_location = os.path.join(gdb_path, gdb)
                    fgdb.convert(gdb_location, gdb_name, format, out_path)
            os.mkdir(static + '/output/' + store_key)
            out_zip = zipfile.ZipFile('%s/output/%s/out.zip' % (static, store_key), 'w')
            for root, dirs, files in os.walk(out_path):
                for a_file in files:
                    out_zip.write(os.path.join(root, a_file),
                        os.path.basename(a_file),
                        zipfile.ZIP_DEFLATED)
            out_zip.close()
            
            return render_template('done.html', store_key=store_key)
        else:
            return render_template('error.html')

if __name__ == "__main__":
    app.run()