from flask import Flask, render_template, session, redirect, url_for, request, jsonify
from markupsafe import escape
from datetime import datetime
import toml
import os

app = Flask(__name__)
app.secret_key = 'e4ed89f02f3aa07a4309daaadb454bfff'

DOC_ROOT = "/mnt/c/Users/Jakub/Desktop/astrotmp/"
STACK_FOLDER = os.path.join(DOC_ROOT, ".stack")

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

	#remove .stack folder from the list
	if ".stack" in folders:
		del folders[".stack"]

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
		sigma_low = request.form.get('sigmaLow')
		sigma_high = request.form.get('sigmaHigh')

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
		print(f"Sigma Low: {sigma_low}")
		print(f"Sigma High: {sigma_high}")

		current_timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

		filename = f"stack_{current_timestamp}.toml"

		#put the file in .stack folder

		#if .stack folder does not exist, create it
		if not os.path.exists(STACK_FOLDER):
			os.makedirs(STACK_FOLDER)

		with open(os.path.join(STACK_FOLDER, filename), 'w') as f:
			f.write(f"doc_root = \"{DOC_ROOT}\"\n")
			f.write(f"root_folder = \"{root_folder}\"\n")
			f.write(f"masters_folder = \"{masters_folder}\"\n")
			f.write(f"master_bias = \"{master_bias}\"\n")
			f.write(f"master_dark = \"{master_dark}\"\n")
			f.write(f"master_flat = \"{master_flat}\"\n")
			f.write(f"bias_folder = \"{bias_folder}\"\n")
			f.write(f"dark_folder = \"{dark_folder}\"\n")
			f.write(f"flat_folder = \"{flat_folder}\"\n")
			f.write(f"light_folder = \"{light_folder}\"\n")
			f.write(f"image_type = \"{image_type}\"\n")
			f.write(f"sigma_low = {sigma_low}\n")
			f.write(f"sigma_high = {sigma_high}\n")

		log_file = os.path.join(STACK_FOLDER, f"stack_{current_timestamp}.log")

		with open(log_file, 'w') as f:
			f.write(f"Created at {current_timestamp}\n")

		#redirect to status page with the stack_id
		return redirect(url_for('status', stack_id=current_timestamp))

	return render_template('stack.html', folders=folders)

#status/int:stack_id
@app.route('/status/<int:stack_id>')
def status(stack_id):
	file = f"stack_{stack_id}.toml"
	log =  f"stack_{stack_id}.log"
	stack_file = os.path.join(STACK_FOLDER, file)

	if not os.path.exists(stack_file):
		return render_template('404.html'), 404
	
	if not os.path.exists(os.path.join(STACK_FOLDER, log)):
		return render_template('404.html'), 404

	stack = toml.load(stack_file)

	return render_template('status.html', data=stack, stack_folder=STACK_FOLDER, stack_id=stack_id)

@app.route('/log/<int:stack_id>')
def get_log(stack_id):
	log_path = os.path.join(STACK_FOLDER, f"stack_{stack_id}.log")
	with open(log_path, 'r') as file:
		log_content = file.read()
	return jsonify(log_content=log_content)

@app.route('/about')
def about():
	return render_template('about.html')

@app.errorhandler(400)
def page_bad_request(e):
	return render_template('400.html'), 400

@app.errorhandler(403)
def page_forbidden(e):
	return render_template('403.html'), 403

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404
