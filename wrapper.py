import sys
import os
import shutil

from pysiril.siril   import *
from pysiril.wrapper import *

from dotenv import load_dotenv
load_dotenv()

SIRIL_EXEC = os.getenv("SIRIL_CLI")

class SirilWrapper():
	def __init__(self, data):
		self.data = data

		self.has_master_bias = self.data["master_bias"] != ''
		self.has_master_dark = self.data["master_dark"] != ''
		self.has_master_flat = self.data["master_flat"] != ''

		self.has_flats = self.data["flat_folder"] != '' or self.has_master_flat
		self.has_bias = self.data["bias_folder"] != '' or self.has_master_bias
		self.has_dark = self.data["dark_folder"] != '' or self.has_master_dark

		self.cfa = self.data["image_type"] == 'cfa'

		self.data["workdir"] = os.path.join(self.data["doc_root"], self.data["root_folder"])
		self.data["masters_folder"] = os.path.join(self.data["doc_root"], self.data["root_folder"], self.data["masters_folder"])

	def stack(self):

		app = Siril(f"{SIRIL_EXEC}")

		try:
			self.cmd = Wrapper(app)

			app.Open()

			process_dir = os.path.join(self.data["doc_root"], self.data["root_folder"], 'process')
			root_dir = os.path.join(self.data["doc_root"], self.data["root_folder"])
			if not os.path.exists(process_dir):
				os.makedirs(process_dir)

			self.cmd.set16bits()
			self.cmd.setext('fit')

			##### BIASES #####

			if self.has_master_bias:
				master_bias_path = os.path.join(self.data["masters_folder"], self.data["master_bias"])
				stacked_bias_dir = os.path.join(root_dir, '__bias_stacked__')
				if not os.path.exists(stacked_bias_dir):
					os.makedirs(stacked_bias_dir)

				shutil.copy(master_bias_path, stacked_bias_dir)

				self.cmd.cd(stacked_bias_dir)
				self.cmd.convert("bias_stacked", out=process_dir, fitseq=True)
				self.cmd.cd(process_dir)

				shutil.rmtree(stacked_bias_dir)

			if self.data["bias_folder"] != '':
				bias_path = os.path.join(self.data["workdir"], self.data["bias_folder"])
				self.master_bias(bias_path, process_dir)

			##### FLATS #####

			if self.has_master_flat:
				master_flat_path = os.path.join(self.data["masters_folder"], self.data["master_flat"])

				stacked_flat_dir = os.path.join(root_dir, '__pp_flat_stacked__')
				if not os.path.exists(stacked_flat_dir):
					os.makedirs(stacked_flat_dir)

				shutil.copy(master_flat_path, stacked_flat_dir)

				self.cmd.cd(stacked_flat_dir)
				self.cmd.convert("pp_flat_stacked", out=process_dir, fitseq=True)
				self.cmd.cd(process_dir)

				shutil.rmtree(stacked_flat_dir)

			if self.data["flat_folder"] != '' and self.has_bias:
				flat_path = os.path.join(self.data["workdir"], self.data["flat_folder"])
				self.master_flat(flat_path, process_dir)
			
			##### DARKS #####
			
			if self.has_master_dark:
				master_dark_path = os.path.join(self.data["masters_folder"], self.data["master_dark"])
				
				stacked_dark_dir = os.path.join(root_dir, '__dark_stacked__')
				if not os.path.exists(stacked_dark_dir):
					os.makedirs(stacked_dark_dir)

				shutil.copy(master_dark_path, stacked_dark_dir)

				self.cmd.cd(stacked_dark_dir)
				self.cmd.convert("dark_stacked", out=process_dir, fitseq=True)
				self.cmd.cd(process_dir)

				shutil.rmtree(stacked_dark_dir)

			if self.data["dark_folder"] != '' and self.has_bias:
				dark_path = os.path.join(self.data["workdir"], self.data["dark_folder"])
				self.master_dark(dark_path, process_dir)

			##### LIGHTS #####

			light_path = os.path.join(self.data["workdir"], self.data["light_folder"])
			self.light(light_path, process_dir)

			
		except Exception as e :
			print("\n**** ERROR *** " +  str(e) + "\n" )    

		app.Close()
		del app

	def master_bias(self, bias_dir, process_dir):
		self.cmd.cd(bias_dir)
		self.cmd.convert('bias', out=process_dir, fitseq=True)
		self.cmd.cd(process_dir)
		self.cmd.stack('bias', type='rej', sigma_low=3, sigma_high=3, norm='no')
		
	def master_flat(self, flat_dir, process_dir):
		self.cmd.cd(flat_dir)
		self.cmd.convert( 'flat', out=process_dir, fitseq=True)
		self.cmd.cd(process_dir)
		self.cmd.calibrate( 'flat', bias='bias_stacked' )
		self.cmd.stack('pp_flat', type='rej', sigma_low=3, sigma_high=3, norm='mul')
		
	def master_dark(self, dark_dir, process_dir):
		self.cmd.cd(dark_dir)
		self.cmd.convert( 'dark', out=process_dir, fitseq=True)
		self.cmd.cd(process_dir)
		self.cmd.stack('dark', type='rej', sigma_low=3, sigma_high=3, norm='no')
		
	def light(self, light_dir, process_dir):
		self.cmd.cd(light_dir)
		self.cmd.convert('light', out=process_dir, fitseq=True)
		self.cmd.cd(process_dir)

		if self.has_flats and self.has_dark:
			self.cmd.calibrate('light', dark='dark_stacked', flat='pp_flat_stacked', cfa=self.cfa, equalize_cfa=self.cfa, debayer=self.cfa)

		elif self.has_darks:
			self.cmd.calibrate('light', dark='dark_stacked', cfa=self.cfa, equalize_cfa=self.cfa, debayer=self.cfa)

		elif self.has_flats:
			self.cmd.calibrate('light', flat='pp_flat_stacked', cfa=self.cfa, equalize_cfa=self.cfa, debayer=self.cfa)

		else:
			self.cmd.calibrate('light', cfa=self.cfa, equalize_cfa=self.cfa, debayer=self.cfa)

		self.cmd.register('pp_light')
		self.cmd.stack('r_pp_light', type='rej', sigma_low=self.data["sigma_low"], sigma_high=self.data["sigma_high"], norm='addscale', output_norm=True, out='../result')
		self.cmd.close()
		