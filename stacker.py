import toml
import os
from dotenv import load_dotenv
import logging
from contextlib import redirect_stdout
from wrapper import SirilWrapper
from PIL import Image

load_dotenv()

DOC_ROOT = os.getenv("HOME_DIR")
LOG_DIR = os.getenv("LOG_DIR")
STACKING_DIRECTORY = os.getenv("STACKING_DIRECTORY")

print(f"Using DOC_ROOT: {DOC_ROOT}")
print(f"Using LOG_DIR: {LOG_DIR}")
if STACKING_DIRECTORY:
	print(f"Stacking directory enabled. Using STACKING_DIRECTORY: {STACKING_DIRECTORY}")
else:
	print("Stacking directory disabled - working directly in data directory")

def get_toml_files():
	# Get all .toml files in the DOC_ROOT folder
	# toml_files = []
	# for root, dirs, files in os.walk(DOC_ROOT):
	# 	for f in files:
	# 		print(f"Found file: {f}")
	# 		if f.endswith('.toml'):
	# 			toml_files.append(f)
	# print(f"Found {len(toml_files)} .toml files.")

	#get all toml files in LOG_DIR
	toml_files = [f for f in os.listdir(LOG_DIR) if f.endswith('.toml')]
	print(f"Found {len(toml_files)} .toml files in {LOG_DIR}.")

	return toml_files

if __name__ == "__main__":
	files = get_toml_files()
	
	for current in files:

		filepath = os.path.join(LOG_DIR, current)
		data = toml.load(filepath)
		# Replace "None" with None
		for key in data:
			if data[key] == "None":
				data[key] = ''
		
		# Same name as the toml file but with a .log extension
		log_file = os.path.join(LOG_DIR, current.replace('.toml', '.log'))

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

		try:
			large_jpg_path = os.path.join(data["workdir"], 'result.jpg')
			if os.path.exists(large_jpg_path):
				thumb_path = os.path.join(data["workdir"], 'result.thumb.jpg')
				with Image.open(large_jpg_path) as img:
					img.thumbnail((800, 800))
					img.save(thumb_path, "JPEG")
				logger.info(f"Preview created at {large_jpg_path}")
				logger.info(f"Thumbnail created at {thumb_path}")

		except Exception as e:
			logger.error(f"Failed to create thumbnail: {e}")

		with open(log_file, 'a') as f:
			f.write(f"Created with {filepath}\n")
			# Log the actual result location (could be in stacking directory or original location)
			result_path = os.path.join(data['workdir'], 'result.fit')
			f.write(f"Result file: {result_path}\n")

		# rename the toml file to .toml.done
		done_file = os.path.join(LOG_DIR, current.replace('.toml', '.toml.done'))
		os.rename(filepath, done_file)