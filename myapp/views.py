import os
from myapp import app, caffe_net
from flask import render_template
from flask import request,Response,send_file,url_for,redirect
from skimage import io
from werkzeug import secure_filename
from database import database
from extract import extractor

@app.route('/')
def search_image():
    return render_template('upload.html')

@app.route('/bootstrap')
def index():
	return render_template('bootstrap_index.html')

@app.route('/upload',methods=['GET','POST'])
def upload():
	file = request.files['image']
	scale = request.form.get('scale')
	scale = str(scale)
	if file:
		filename = secure_filename(file.filename)
		file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
		img = io.imread(file)
		fine_str, coarse_str, res_dict = caffe_net.extract_features(img)
		data_dealer = database()
		types_tumor = data_dealer.get_types_tumor()
		files = data_dealer.search_top(coarse_str, fine_str, 5)
		print res_dict
		for idx in xrange(6):
			print res_dict[idx]
			res_dict[idx].append(types_tumor[idx])
		res_files = []
		for file in files:
			res_file = []
			res_file.append(url_for('static',filename='train/' + file[0]))
			res_file.append(types_tumor[file[1]])
			res_files.append(res_file)
		return render_template('result.html',ori_file=url_for('static',filename='upload_images/' + filename), res_files=res_files,res_dict=res_dict)
	return redirect(url_for('search_image'))
