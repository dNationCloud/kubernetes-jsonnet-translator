import tempfile
import shutil
import os.path
from os import path
from datetime import datetime
import pytest

from translator.utils import *

def test_timestamp():
	result = timestamp()
	assert result == datetime.now().strftime("[%Y-%m-%d %X]")
	 
def test_save_text_to_file():
	# Create a temporary .txt file
	file_desc, test_file = tempfile.mkstemp(suffix = '.txt')

	# Directory of the file
	temp_dir = tempfile.gettempdir()

	filename = os.path.basename(test_file)
	f = open(test_file, "r")
	save_text_to_file(temp_dir, filename, "TEST!")
	expected_result = "TEST!"
	assert f.read() == expected_result
	f.close()

	#delete file 
	os.remove(test_file)
	 
def test_remove_file():
	# Create a temporary .txt file
	file_desc, test_file = tempfile.mkstemp(suffix = '.txt')

	# Directory of the file
	temp_dir = tempfile.gettempdir()

	filename = os.path.basename(test_file)
	remove_file(temp_dir, filename)
	result = os.path.isfile(test_file)
	expected_result = False
	assert result == expected_result

def test_remove_folder():
	# Create a temporary directory
	temp_f = tempfile.mkdtemp()

	remove_folder(temp_f)
	result = os.path.isdir(temp_f)
	expected_result = False
	assert result == expected_result
		
def test_replace_extension():
	# Create a temporary .txt file
	file_desc, test_file = tempfile.mkstemp(suffix = '.txt')
	full_filename = os.path.basename(test_file)
	filename, old_extension = os.path.splitext(full_filename)
		
	result = replace_extension(full_filename, "png")
	expected_result = filename + ".png"
	assert result == expected_result

	#delete file 
	os.remove(test_file)

def test_extract_archive_data():
	# Create a temporary base64 encoded .txt file
	file_desc, test_file = tempfile.mkstemp(suffix = '.txt')
	f = open(test_file,"a") 
	f.write("UEsDBBQAAAAAANVkZFIAAAAAAAAAAAAAAAAKACAAanNvbm5ldF9mL1VUDQAHwsZAYMTGQGDCxkBgdXgLAAEE6AMAAAToAwAAUEsDBBQACAAIAOBKZFIAAAAAAAAAAFoEAAAXACAAanNvbm5ldF9mL2ZpcnN0Lmpzb25uZXRVVA0AB+WYQGB3mUBg5ZhAYHV4CwABBOgDAAAE6AMAAGVTXU/bQBB8z69YRUIkabARjyCkugFaC+pIcShCqA8Xe+0cte/c+4iJEP+dXduoUPLinHdudmZ2Hc5GAAvd7I0stw5Ojk+OYb1FyBPhpFZw7TdoFDq08FMr6bSRqoTIu602NoCoqmDFNy2s0KLZYR4Q4Y3MUFnMwascDTgijBqR0WOozOEXGssNToJjmDBgPJTG0zNi2GsPtdiD0g68RaKQFgpZIeBTho0DqSDTdVNJoTKEVrpt12YgYRH3A4XeOEFoQfiGTsV7HAhHSP5tnWtOw7Bt20B0UgNtyrDqYTa8iReXSXp5RHLpwq2q0Fow+NdLQzY3exANacnEhhRWogVtQJQGqeY0a22NdJTcHKwuXCsMEksurTNy492HoN6Ukd/3AIpKKBhHKcTpGL5FaZzOieMuXv9Y3q7hLlqtomQdX6awXMFimVzE63iZ0OkKouQeruPkYg5IMVEbfGoM6yeRkiPsh5YifhBQ6F6QbTCThczIlyq9KBFKvaOl4EVo0NTS8iAtycuJpZK1dN3u2M+mgtEsHI3CGe1S7ikpnqCRlG8HqnRJXSivEhUa4RAeLdnmqVuCKh5j19ToGumCpwl4rhX0osPSogJ3GBVeZaxhknnrdL3QqpDl+fPLlBSGM955mMH3tzb/E3blHvO1EUbU8J5mOLAiOnnTfyg7YSRPn6yIP6h6TeyKPNYUDQWjKF/dHFW4wwqEKX2NytlgaGTQeaM+aeEyWaJgdSYqyIUTcA6T3viXQURQoymxlzcZXuVYCF+5/uX8g4PpNPjXZsVMZ/A86j6Eh8MDG3CUh3AAStT4+7Tr+dD97yC8F3zitbYuD/TmETN3JbHK7YSxHPLL6BVQSwcIwiOj0oMCAABaBAAAUEsBAhQDFAAAAAAA1WRkUgAAAAAAAAAAAAAAAAoAIAAAAAAAAAAAAP1BAAAAAGpzb25uZXRfZi9VVA0AB8LGQGDExkBgwsZAYHV4CwABBOgDAAAE6AMAAFBLAQIUAxQACAAIAOBKZFLCI6PSgwIAAFoEAAAXACAAAAAAAAAAAAC0gUgAAABqc29ubmV0X2YvZmlyc3QuanNvbm5ldFVUDQAH5ZhAYHeZQGDlmEBgdXgLAAEE6AMAAAToAwAAUEsFBgAAAAACAAIAvQAAADADAAAAAA==") 
	f.close()

	with open(test_file, "rb") as file1:
		d = file1.read()
			
	extract_archive_data(d, 'output_file.zip', 'try')
		
	path = './try/jsonnet_f/first.jsonnet'
	result = result = os.path.isfile(path)
	expected_result = True
	assert result == expected_result

	#delete file 
	os.remove(test_file)
	#delete folder 
	shutil.rmtree('./try')