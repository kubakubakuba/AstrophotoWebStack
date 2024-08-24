from flask import Flask, render_template, session, redirect, url_for, request
from markupsafe import escape
import os

app = Flask(__name__)
app.secret_key = 'e4ed89f02f3aa07a4309daaadb454bfff'

DOC_ROOT = "/mnt/c/Users/Jakub/Desktop/astrotmp/"

@app.route("/")
def index():
	return render_template('index.html')

@app.route('/stack', methods=['GET', 'POST'])
def stack():
	# folders = {
	# 	"ngc7000": {
	# 		"light": ["light1.fit", "light2.fit", "light3.cr2"],
	# 		"dark": ["dark1.fit", "dark2.fit", "dark3.cr2"],
	# 		"flat": ["flat1.fit", "flat2.fit", "flat3.cr2"],
	# 		"bias": ["bias1.fit", "bias2.fit", "bias3.cr2"],
	# 		"masters": ["master_light.xisf", "master_dark.xisf", "master_flat.xisf", "master_bias.xisf"]
	# 	},
	# 	"test222": {
	# 		"light": ["light1.fit", "light2.fit", "light3.cr2"],
	# 		"dark": ["dark1.fit", "dark2.fit", "dark3.cr2"],
	# 		"flat": ["flat1.fit", "flat2.fit", "flat3.cr2"],
	# 		"bias": ["bias1.fit", "bias2.fit", "bias3.cr2"],
	# 		"masters": ["master_light.xisf", "master_dark.xisf", "master_flat.xisf", "master_bias.xisf"]
	# 	},
	# 	"ic1234": {
	# 		"light": ["light1.fit", "light2.fit", "light3.cr2"],
	# 		"dark": ["dark1.fit", "dark2.fit", "dark3.cr2"],
	# 		"flat": ["flat1.fit", "flat2.fit", "flat3.cr2"],
	# 		"bias": ["bias1.fit", "bias2.fit", "bias3.cr2"],
	# 		"masters": ["master_light.xisf", "master_dark.xisf", "master_flat.xisf", "master_bias.xisf"]
	# 	},
	# 	"m1": {
	# 		"light": ["light1.fit", "light2.fit", "light3.cr2"],
	# 		"dark": ["dark1.fit", "dark2.fit", "dark3.cr2"],
	# 		"flat": ["flat1.fit", "flat2.fit", "flat3.cr2"],
	# 		"bias": ["bias1.fit", "bias2.fit", "bias3.cr2"],
	# 		"masters": ["master_light.xisf", "master_dark.xisf", "master_flat.xisf", "master_bias.xisf"]
	# 	}
	# }

	#read folders and files recursively (up to 2 levels) from the DOC_ROOT folder

	folders = {}
	for root, dirs, files in os.walk(DOC_ROOT):
		if root == DOC_ROOT:
			for d in dirs:
				folders[d] = {}
				for root2, dirs2, files2 in os.walk(os.path.join(DOC_ROOT, d)):
					if root2 == os.path.join(DOC_ROOT, d):
						for d2 in dirs2:
							folders[d][d2] = []
							for root3, dirs3, files3 in os.walk(os.path.join(DOC_ROOT, d, d2)):
								if root3 == os.path.join(DOC_ROOT, d, d2):
									for f in files3:
										folders[d][d2].append(f)

	print(folders)

	if request.method == 'POST':
		root_folder = request.form.get('rootFolder')
		masters_folder = request.form.get('mastersFolder')
		master_bias = request.form.get('masterBias')
		master_dark = request.form.get('masterDark')
		master_flat = request.form.get('masterFlat')
		bias_folder = request.form.get('biasFolder')
		dark_folder = request.form.get('darkFolder')
		flat_folder = request.form.get('flatFolder')
		light_folder = request.form.get('lightFolder')
		image_type = request.form.get('imageType')

		# Process the form data here
		# For example, you can print the values or save them to a database
		print(f"Root Folder: {root_folder}")
		print(f"Masters Folder: {masters_folder}")
		print(f"Master Bias: {master_bias}")
		print(f"Master Dark: {master_dark}")
		print(f"Master Flat: {master_flat}")
		print(f"Bias Folder: {bias_folder}")
		print(f"Dark Folder: {dark_folder}")
		print(f"Flat Folder: {flat_folder}")
		print(f"Light Folder: {light_folder}")
		print(f"Image Type: {image_type}")

		# Redirect to a new page or render a template with a success message
		return redirect(url_for('index'))

	return render_template('stack.html', folders=folders)

@app.route('/about')
def about():
	return render_template('about.html')