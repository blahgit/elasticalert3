import os
import ConfigParser
if __name__=="__main__":
	#home_dir=os.environ("HOME")
	parser=ConfigParser.SafeConfigParser()
	parser.read("./config.conf")
	lst=parser.items("default")
	diksh=dict()
	for k,v in lst:
		diksh[k]=v
	home_dir=diksh["home_dir"]
	count=os.system("ps -ef |grep -v 'grep' | grep -c 'ESAlerter'")
	print count
	if count:
		os.system("python %s/elasticalert/elastalert_ui/ESAlerter.py &" %(home_dir))
	count=os.system("ps -ef |grep -v 'grep' | grep -c 'elastalert.elastalert'")
    print count
	if count:
		os.system("cd %s/elasticalert/elastalert; python -m elastalert.elastalert --verbose &" %(home_dir))
	print "Done."
