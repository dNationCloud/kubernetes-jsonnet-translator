import sys
import os
import tempfile
import json
from dataclasses import dataclass, field
from kubernetes.client.api import core_v1_api
import pytest

from translator.main import *
from translator.arg_parser import get_parser

def test_group_annotations():

	#Create empty Annotations
	@dataclass
	class Annotations:
		build: dict = field(default_factory=dict)
		translator: dict = field(default_factory=dict)
		other: dict = field(default_factory=dict)
		
	# annotations (dict of str: str), which will be added to the Annotations
	annotations = {
	"brand": "Ford",
	"model": "Mustang",
	"year": 1964
	}
	result = group_annotations(annotations)
	expected_result = "Annotations(build={}, translator={}, other={'brand': 'Ford', 'model': 'Mustang', 'year': 1964})"
	assert f"{result}" == expected_result

def test_update_labels():
	user_labels = {
	"key1" : "value1", 
	"key2" : "value2"
	}
	user_labels_expected = {
	"key1" : "test", 
	"key2" : "value2", 
	}
	result = update_labels(user_labels, "key1=value1", "key1=test")
	assert result == user_labels_expected
	
def test_parse_json_with_files():
	# Create a temporary .json file
	file_desc, test_file = tempfile.mkstemp(suffix = '.json')

	#data to .json file
	data = { 
		"size": "medium",
		"price": 15.67,
		"toppings": ["mushrooms", "pepperoni", "basil"],
		"client": {
		"name": "Jane Doe",
		}
	}

	with open(test_file, 'w') as f:
  		json.dump(data, f, ensure_ascii=False, indent=4)

	file_path = test_file
	result = parse_json_with_files(file_path)
	expected_result = "dict_items([('size', 'medium'), ('price', 15.67), ('toppings', ['mushrooms', 'pepperoni', 'basil']), ('client', {'name': 'Jane Doe'})])"
	assert f"{result}" == expected_result

	#delete file 
	os.remove(test_file)
	
def test_get_config_maps(kube):
	# Create a temporary .yaml file
	file_desc, test_file = tempfile.mkstemp(suffix = '.yaml')
	#append data
	f = open(test_file,"a") 
	f.write('apiVersion: v1\nkind: ConfigMap\nmetadata:\n  name: jsonnet-cm\n  labels:\n    grafana_dashboard_jsonnet: "1"\n  annotations:\n    grafana_label: "grafana_dashboard=1"') 
	f.close()

	configmap = kube.load_configmap(test_file)
	configmap.create()
	configmap.wait_until_ready(timeout=50)
	configmap.refresh()
	configmap_is_ready = configmap.is_ready()
	cm = get_config_maps(label_selector="grafana_dashboard_jsonnet=1")
	assert len(cm.items) == 1

	#delete file 
	os.remove(test_file)

def test_delete_generated_resources(kube):
	configmap = kube.load_configmap('/home/miso/IFNE/kubernetes-jsonnet-translator/examples/grafana-jsonnet.yaml')
	configmap.create()
	configmap.wait_until_ready(timeout=50)
	configmap.refresh()
	args_ = get_parser().parse_args()
	delete_generated_resources(args_)
	configmap_is_ready = configmap.is_ready()
	
