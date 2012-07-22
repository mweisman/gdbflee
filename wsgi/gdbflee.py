#!/usr/bin/python

from flask import Flask, request, redirect, send_from_directory, url_for
from hashlib import sha1
from uuid import uuid1
from werkzeug import secure_filename
import json, fgdb, os, zipfile, glob

UPLOAD_FOLDER = os.environ['HOME'] + '/app-root/data/tmp'
ALLOWED_EXTENSIONS = set(['zip'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.debug = True

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route("/", methods=['POST', 'GET'])
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
            return 'static/output/%s' % store_key
            os.mkdir('static/output/%s' % store_key)
            out_zip = zipfile.ZipFile('static/output/%s/out.zip' % store_key, 'w')
            for root, dirs, files in os.walk(out_path):
                for a_file in files:
                    out_zip.write(os.path.join(root, a_file),
                        os.path.basename(a_file),
                        zipfile.ZIP_DEFLATED)
            out_zip.close()
            
            return '''
            <!doctype html>
            <title>All Done</title>
            <h1><a href=\"/static/output/%s/out.zip\">Your data has been freed!</a></h1>
            <br />
            <br />
            <a href=\"/\">Free some more data</a>
            ''' % store_key
        else:
            return json.dumps({"status": "error",
                "message": "bad zip",
                "filename": filename,
                    "path": path})
            
    return '''
    <!doctype html>
    <title>Upload a zipped File Geodatabase to free</title>
    <h1>Upload a zipped File Geodatabase to free</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
      <br />
         <select name="format"> 
         <option value="GeoJSON">GeoJSON</option>
         <option value="KML">KML</option>
         <option value="ESRI Shapefile">Shapefile</option>
         <option value="PGDump">PostGIS Database Dump</option>
         <option value="GeoRSS">GeoRSS</option>
         <option value="CSV">CSV (attributes only)</option>
         <option value="GML">GML</option>
         <option value="MapInfo File">MapInfo File</option>
         <option value="DGN">DGN</option>
         <option value="Geoconcept">Geoconcept</option>
         </select>
         <br />
         <br />
         <input type=submit value="Free this Data!">
         </p>
    </form>
    '''

if __name__ == "__main__":
    app.run()