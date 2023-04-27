from flask import Flask, render_template, request, redirect, url_for, session
import os
from werkzeug.utils import secure_filename
import numpy
from PIL import Image
from colorthief import ColorThief
import pandas as pd


app = Flask(__name__)

IMG_FOLDER = os.path.join('static')

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


app.config['UPLOAD_FOLDER'] = IMG_FOLDER

app.secret_key = 'This is your secret key to utilize session in Flask'


uploaded_path = ''
dict_color_perc = {}


@app.route("/", methods=["POST", "GET"])
def home():
    global uploaded_path, dict_color_perc

    if request.method == "POST":
        #UPLOAD AND SVAE THE IMAGE
        image = request.files['image-file']
        img_filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], img_filename))
        session['uploaded_img_file_path'] = os.path.join(app.config['UPLOAD_FOLDER'], img_filename)
        img_path = session.get('uploaded_img_file_path', None)
        uploaded_path = img_path
        color_thief = ColorThief(img_path)
        # TAKE NUMBER OF COLOR TO EXTRACT
        quantity = int(request.form.get('quantity'))

        palette = color_thief.get_palette(color_count=quantity)

        #CONVERT IMAGE TO AN ARRAY
        img = Image.open(img_path)
        numpy_img = numpy.array(img)
        #CONVERT NUMPY RGB IMAGE TO HEX
        numpy_img_hex = [tuple(col[0]) for col in numpy_img]

        numpy_img_hex = ['#%02x%02x%02x' % col for col in numpy_img_hex]
        dominant_palette = ['#%02x%02x%02x' % col for col in palette]
        print(dominant_palette)


        #CREATE DATAFRAME TO CHECK MOST COMMON COLORS
        color_df = pd.Index(numpy_img_hex)



        colors_count = color_df.value_counts()[:quantity]
        colors_perc = (color_df.value_counts(normalize=True)[:quantity])

        colors_perc = colors_perc.values
        colors_perc = ['%.6f' % per for per in colors_perc]


        colors = colors_count.index.values


        dict_color_perc = dict(zip(dominant_palette, colors_perc))


        return redirect(url_for('home', image=img_path, colors=dict_color_perc))
    return render_template('index.html', image=uploaded_path, colors=dict_color_perc)



if "__main__" == __name__:
    app.run(debug=True)