import os
if __name__=="__main__":
	home_dir="/opt"
	base_dir=home_dir+"/elasticalert"
	count=os.system("ps -ef |grep -v 'grep' | grep -c 'ESAlerter'")
	print count
	if count:
		os.system("python %s/elastalert_ui/ESAlerter.py &" %(base_dir))
	count=os.system("ps -ef |grep -v 'grep' | grep -c 'elastalert.elastalert'")
	print count
	if count:
		os.system("cd %s/elastalert; python -m elastalert.elastalert --verbose &" %(base_dir))
	print "Done."
