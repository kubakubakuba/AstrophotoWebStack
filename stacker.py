import toml
import os
from dotenv import load_dotenv
import logging
from contextlib import redirect_stdout
from wrapper import SirilWrapper

load_dotenv()

DOC_ROOT = os.getenv("HOME_DIR")
STACK_FOLDER = os.path.join(DOC_ROOT, ".stack")

def get_toml_files():
	# Get all .toml files in the DOC_ROOT folder
	toml_files = []
	for root, dirs, files in os.walk(DOC_ROOT):
		for f in files:
			if f.endswith('.toml'):
				toml_files.append(f)
	return toml_files

if __name__ == "__main__":
	files = get_toml_files()
	
	for f in files:

		data = toml.load(os.path.join(STACK_FOLDER, f))
		# Replace "None" with None
		for key in data:
			if data[key] == "None":
				data[key] = ''
		
		# Same name as the toml file but with a .log extension
		log_file = os.path.join(STACK_FOLDER, f.replace('.toml', '.log'))

		# Set up logging
		logger = logging.getLogger()
		logger.setLevel(logging.INFO)

		# File handler
		file_handler = logging.FileHandler(log_file)
		file_handler.setLevel(logging.INFO)
		file_handler.setFormatter(logging.Formatter('%(message)s'))

		# Console handler
		console_handler = logging.StreamHandler()
		console_handler.setLevel(logging.INFO)
		console_handler.setFormatter(logging.Formatter('%(message)s'))

		# Add handlers to the logger
		logger.addHandler(file_handler)
		logger.addHandler(console_handler)

		sw = SirilWrapper(data)

		# Redirect stdout to the logging system
		class StreamToLogger:
			def __init__(self, logger, log_level=logging.INFO):
				self.logger = logger
				self.log_level = log_level
				self.linebuf = ''

			def write(self, buf):
				for line in buf.rstrip().splitlines():
					self.logger.log(self.log_level, line.rstrip())

			def flush(self):
				pass

		stream_to_logger = StreamToLogger(logger)
		with redirect_stdout(stream_to_logger):
			sw.stack()

		with open(log_file, 'a') as f:
			f.write(f"Created at {f}\n")
			f.write(f"Result file: {os.path.join(DOC_ROOT, data['root_folder'], 'result.fit')}\n")

		# Remove the .toml file
		#os.remove(os.path.join(STACK_FOLDER, current))