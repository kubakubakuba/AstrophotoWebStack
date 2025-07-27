from flask import Flask, render_template, session, redirect, url_for, request, jsonify, send_file
from markupsafe import escape
from markdown import markdown
from datetime import datetime
import toml
import os
from dotenv import load_dotenv
import re
import hashlib

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

DOC_ROOT = os.getenv("HOME_DIR")
LOG_DIR = os.getenv("LOG_DIR")

# def read_folders_rec(level, curr_dir):
# 	folders = {}
# 	for root, dirs, files in os.walk(curr_dir):
# 		if root == curr_dir:
# 			for d in dirs:
# 				folders[d] = {}

# 	if level == 0:
# 		#read all folders in the current directory
# 		return folders
	
# 	ret = {}

# 	for f in folders:
# 		ret[f] = read_folders_rec(level - 1, os.path.join(curr_dir, f))

# 	return ret


@app.route("/")
def index():
	return render_template('index.html')

@app.route('/stack', methods=['GET', 'POST'])
def stack():

	#folders = read_folders_rec(2, DOC_ROOT)

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
		if not os.path.exists(LOG_DIR):
			os.makedirs(LOG_DIR)

		with open(os.path.join(LOG_DIR, filename), 'w') as f:
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

		log_file = os.path.join(LOG_DIR, f"stack_{current_timestamp}.log")

		with open(log_file, 'w') as f:
			f.write(f"Created at {current_timestamp} in {DOC_ROOT}/{root_folder}\n")

		#redirect to status page with the stack_id
		return redirect(url_for('status', stack_id=current_timestamp))

	return render_template('stack.html', folders=folders)

#status/int:stack_id
@app.route('/status/<int:stack_id>')
def status(stack_id):
	file = f"stack_{stack_id}.toml"
	log =  f"stack_{stack_id}.log"
	stack_file = os.path.join(LOG_DIR, file)

	if not os.path.exists(stack_file):
		return render_template('404.html'), 404
	
	if not os.path.exists(os.path.join(LOG_DIR, log)):
		return render_template('404.html'), 404

	stack = toml.load(stack_file)

	data_names = ["Root Folder", "Masters Folder", "Master Bias", "Master Dark", "Master Flat",
			 "Bias Folder", "Dark Folder", "Flat Folder", "Light Folder", "Image Type",
			 "Sigma Low", "Sigma High"]

	return render_template('status.html', data=stack, stack_folder=LOG_DIR, stack_id=stack_id, data_names=data_names)

@app.route('/log/<int:stack_id>')
def get_log(stack_id):
	log_path = os.path.join(LOG_DIR, f"stack_{stack_id}.log")
	with open(log_path, 'r') as file:
		log_content = file.read()
	return jsonify(log_content=log_content)

@app.route('/thumbnail/<int:stack_id>')
def get_thumbnail(stack_id):
	log_path = os.path.join(LOG_DIR, f"stack_{stack_id}.log")
	if not os.path.exists(log_path):
		return render_template('404.html'), 404

	with open(log_path, 'r') as f:
		log_content = f.read()
		match = re.search(r"Thumbnail created at (.+)", log_content)
		
		if not match:
			return render_template('404.html'), 404
		
		thumb_path = match.group(1).strip()

	if not os.path.exists(thumb_path):
		return render_template('404.html'), 404

	return send_file(thumb_path)

@app.route('/preview/<int:stack_id>')
def get_preview(stack_id):
	log_path = os.path.join(LOG_DIR, f"stack_{stack_id}.log")
	if not os.path.exists(log_path):
		return render_template('404.html'), 404
	
	with open(log_path, 'r') as f:
		log_content = f.read()
		match = re.search(r"Preview created at (.+)", log_content)

		if not match:
			return render_template('404.html'), 404

		preview_path = match.group(1).strip()

	if not os.path.exists(preview_path):
		return render_template('404.html'), 404

	return send_file(preview_path)

@app.route('/new', methods=['GET', 'POST'])
def new_project():
	if request.method == 'POST':
		creation_method = request.form.get('creation_method')
		dir_name = ''

		if creation_method == 'custom':
			dir_name = request.form.get('custom_name')

		elif creation_method == 'structured':
			proj_date = request.form.get('project_date')
			obj_type = request.form.get('object_type')
			obj_number = request.form.get('object_number')
			dir_name = f"{proj_date}_{obj_type}_{obj_number}"

		if not dir_name:
			return redirect(url_for('new_project'))

		dir_name = re.sub(r'[./\\]', '', dir_name)

		if not dir_name:
			return redirect(url_for('new_project'))

		project_path = os.path.join(DOC_ROOT, dir_name)
		
		os.makedirs(project_path, exist_ok=True)

		if request.form.get('create_subdirs'):
			subdirs = ['light', 'dark', 'flat', 'bias', 'master']
			for subdir in subdirs:
				os.makedirs(os.path.join(project_path, subdir), exist_ok=True)

		return redirect(url_for('stack'))

	today_date = datetime.now().strftime('%m-%d-%y')
	object_types = ['M', 'NGC', 'IC', 'SH', 'VDB', 'LBN', 'PGC', 'B', 'C', 'LDN']
	return render_template('new.html', today_date=today_date, object_types=object_types)

@app.route('/browse')
def browse():
	n = 10  # Number of recent stacks to display
	log_files = [f for f in os.listdir(LOG_DIR) if f.endswith('.log')]
	
	# Sort files by date, most recent first
	log_files.sort(reverse=True)

	jobs = []
	for log_file in log_files[:n]:
		match = re.match(r"stack_(\d+)\.log", log_file)
		if not match:
			continue

		stack_id = match.group(1)
		log_path = os.path.join(LOG_DIR, log_file)
		toml_path = os.path.join(LOG_DIR, f"stack_{stack_id}.toml")
		
		status = ''
		folder = ''
		url = ''

		# Determine status and URL
		if os.path.exists(toml_path):
			status = 'In Progress'
			url = url_for('status', stack_id=stack_id)
		else:  # Job is finished
			url = url_for('result', stack_id=stack_id)
			try:
				with open(log_path, 'r') as f:
					log_content = f.read()
				if '[status: error]' in log_content:
					status = 'Errored'
				else:
					status = 'Completed'
			except IOError:
				status = 'Unknown'

		# Extract folder from the first line
		try:
			with open(log_path, 'r') as f:
				first_line = f.readline()
				folder_match = re.search(r" in (.+)", first_line)
				if folder_match:
					folder = folder_match.group(1).strip()
				else:
					folder = 'N/A'
		except (IOError, IndexError):
			folder = 'N/A'

		# Format the timestamp for display
		try:
			date_obj = datetime.strptime(stack_id, "%Y%m%d%H%M%S")
			display_date = date_obj.strftime('%Y-%m-%d %H:%M:%S')
		except ValueError:
			display_date = stack_id

		jobs.append({
			'id': stack_id,
			'display_date': display_date,
			'status': status,
			'url': url,
			'dir': folder
		})

	return render_template('browse.html', jobs=jobs)

@app.route('/result/<int:stack_id>')
def result(stack_id):
	log_file = os.path.join(LOG_DIR, f"stack_{stack_id}.log")
	#get the hash of the log file
	log_md5 = None
	if os.path.exists(log_file):
		hasher = hashlib.md5()
		with open(log_file, 'rb') as f:
			hasher.update(f.read())
		log_md5 = hasher.hexdigest()

	#get the first char number of the md5 hash and convert it from hex to dec int
	log_check = str(int(log_md5[0], 16))

	return render_template('result.html', stack_id=stack_id, log_check=log_check)

@app.route('/download/<int:stack_id>')
def download(stack_id):
	#serve the file for download

	file = f"stack_{stack_id}.log"
	log_file = os.path.join(LOG_DIR, file)

	with open(log_file, 'r') as f:
		lines = f.readlines()
		last_line = lines[-1]
		result_file = last_line.split(": ")[1].strip()

	if not os.path.exists(result_file):
		return render_template('404.html'), 404
	
	return send_file(result_file, as_attachment=True)

@app.route('/about')
def about():
	#load markdown from docs/tutorial.md

	file = os.path.join('docs', 'tutorial.md')
	content = ''

	try:
		with open(file, 'r') as f:
			content = f.read()
	except FileNotFoundError:
		content = "# Error\nCould not find `docs/tutorial.md`."

	content = markdown(content, extensions=['fenced_code', 'codehilite'])

	return render_template('about.html', content=content)

@app.errorhandler(400)
def page_bad_request(e):
	return render_template('400.html'), 400

@app.errorhandler(403)
def page_forbidden(e):
	return render_template('403.html'), 403

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404
