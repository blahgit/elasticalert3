#!/usr/bin/python

import os
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for, make_response, Response
import sys
import yaml
import os.path
import ConfigParser

app = Flask(__name__)
#home_dir=os.environ("HOME")
parser=ConfigParser.SafeConfigParser()
parser.read("../config.conf")
lst=parser.items("minimum")
diksh=dict()
for k,v in lst:
	diksh[k]=v
home_dir=diksh["home_dir"]
base=home_dir+"/elasticalert/"
#base_dir="../"

def validate(es_host, es_port, name, index, num_events, query):
	errors=dict()
	rules_path=base+"elastalert/example_rules"
	files=[f.split('.')[0] for f in os.listdir(rules_path) if os.path.isfile(os.path.join(rules_path, f))]
	if name.strip().lower() in files:
		errors["name_error"]="Rule with name %s already exists. Choose a new name" %(name)
	try:
		int(es_port)
	except ValueError:
		errors["es_port_error"]="Enter a number for port"
	try:
		int(num_events)
		if int(num_events)<1:
			errors["num_events_error"]="Enter an integer greater than 0"
	except ValueError:
		errors["num_events_error"]="Enter a number"

	if not es_host.strip():
		errors["es_host_error"]="Enter a host name"
	if not name.strip():
		errors["name_error"]="Enter a rule name"
	if not index.strip():
		errors["index_error"]="Enter an index name"
	if not query.strip():
		errors["query_error"]="Enter a query"
	return errors

def valid_yaml(tmp_path):
	error_file=base+"elastalert_ui/error.txt"
        dr=base+"elastalert"
	return_code1=os.system("echo > %s; cd %s; python -m elastalert.test_rule %s > %s 2>> %s --schema-only" %(error_file, dr, tmp_path, error_file, error_file))
	with open(error_file, 'r') as f:
		dat=f.read()
		if "Successfully loaded" not in dat:
			return dat

	return_code2=os.system("echo > %s; cd %s; python -m elastalert.test_rule %s > %s 2>> %s" %(error_file, dr,tmp_path, error_file, error_file))
	with open(error_file, 'r') as f:
		dat=f.read()
		if "ERROR" in dat or "elastalert_error" in dat:
			return dat
	return 0

def get_rules(rules_path):
	return [f.split('.')[0] for f in os.listdir(rules_path) if os.path.isfile(os.path.join(rules_path, f))]

def delete_rule(rule_dir, rule, bup_dir):
	success=False
	message=""
	if not rule.strip():
		message="Enter a rule name"
	rule_name=rule.strip().lower()
	if rule_name in get_rules(rule_dir):
		os.system("mkdir -p %s; cp %s/%s.yaml %s" %(bup_dir, rule_dir, rule_name, bup_dir))
		os.remove("%s/%s.yaml" %(rule_dir, rule_name))
		if rule_name in get_rules(rule_dir):
			message="Unable to delete rule- %s" %(rule_name)
		else:
			success=True
			message="Rule removed successfully"
	else:
		message="Rule- %s does not exist" %(rule_name)
	return success,message


def make_dict(es_host, es_port, name, index, num_events, query):
	d=dict()
	d['es_host']= es_host.encode("ascii")
	d['es_port']= int(es_port)
	d['name']=name.encode("ascii")
	d['index']= index.encode("ascii")
	d['num_events']= int(num_events)

	d["filter"]=query
	d['timeframe']= {'hours': 4}
	d['type']= 'frequency'
	#d['alert']= ['command']
	#d['command']= ['/usr/bin/python', '/home/ec2-user/alerter.py']
	#d['alert']= ['hipchat']
	#d['hipchat_auth_token']="bsl8Oehotv10O1qNBPdj3e6WjgYXtIw68PHu09Ma".encode("ascii")
	#d["hipchat_room_id"]= 2878627
	d["alert"]=["email"]
	d["from_addr"]="elasticalert@citrix.com".encode("ascii")
	d["email"]=["kishore.venkatswammy@citrix.com","luis.toruno@citrix.com","ronny.kursawe@citrix.com","maya.shallouf@citrix.com"]



	d["filter"]=[{"query":{"query_string":{"query": query.encode("ascii")}}}]
	return d

def make_filter_value(filter_type, query):
	filter_value=None
	if filter_type=="exact_match":
		filter_vaule=[{"query":{"query_string":{"query": query.encode("ascii")}}}]
	return filter_value

@app.route("/", methods=["GET", "POST"])
def home():
	rule_path=base+"elastalert/example_rules"
	rules=get_rules(rule_path)
	if request.method == "GET":
		es_host="localhost"
		es_port=9200
		return render_template('root.html', es_host=es_host, es_port=es_port, tab=1, rules=rules)
	elif request.method == "POST":
		if "stub" in request.form:
			return render_template('root.html')
			rule_rolldown_list=list()
			for key in request.form.keys():
				if "bt_" in key:
					rule_rolldown_list.append(request.form[key])
			return render_template('root.html', tab=2, rules=rules, rule_rolldown_list=rule_rolldown_list)
		if "rule_name" in request.form:
			bup_dir=base+"elastalert/deleted_rules"
			success,message=delete_rule(rule_path, request.form["rule_name"], bup_dir)
			rules=get_rules(rule_path)
			return render_template('root.html', tab=3, success=success, message=message, rules=rules)

		if "es_host" in request.form:
			d=request.form
			errors=validate(es_host=d["es_host"], es_port=d["es_port"], name=d["name"], index=d["index"], num_events=d["num_events"], query=d["query"])
			if len(errors)==0:
				#filter_value=make_filter_value(d["filter_type"], d["query"])
				filter_value=d["query"]
				yaml_dict=make_dict(d["es_host"], d["es_port"], d["name"].strip().lower(), d["index"], d["num_events"], filter_value)
				tmp_path_full=base+"elastalert_ui/sandbox_rules/%s.yaml" %(d["name"].strip().lower())
				with open(tmp_path_full, 'w') as f:
					f.write(yaml.dump(yaml_dict, default_flow_style=False))
				status=valid_yaml(tmp_path_full)
				#os.remove(tmp_path_full)
				if status!=0:
					error=valid_yaml(tmp_path_full)
					create_response="Rule was not added due to an error"
					es_host="localhost"
					es_port=9200
					return render_template("root.html", es_host=es_host, es_port=es_port, tab=1, rules=rules, create_success=0, create_response=create_response)
				else:
					rule_path_full=base+"elastalert/example_rules/%s.yaml" %(d["name"].strip().lower())
					with open(rule_path_full, 'w') as f:
						f.write(yaml.dump(yaml_dict, default_flow_style=False))
					create_response="Rule added successfully"
					rules=get_rules(rule_path)
					es_host="localhost"
					es_port=9200
					return render_template('root.html', es_host=es_host, es_port=es_port, tab=1, rules=rules, create_success=1, create_response=create_response)
			else:
					return render_template("root.html", rules=rules, tab=1, es_host=d["es_host"], es_port=d["es_port"], name=d["name"], index=d["index"], num_events=d["num_events"], query=d["query"], errors=errors)

		else:
			return render_template("home.html", es_host=es_host, es_port=es_port)






if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True,host='0.0.0.0', port=4444)
