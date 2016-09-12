import yaml
import os
import ConfigParser
def update_config(fname, path):
    with open(fname) as f:
        d=yaml.load(f)
        print d
        parser=ConfigParser.SafeConfigParser()
        parser.read(path)
        lst=parser.items("minimum")
        diksh=dict()
        for k,v in lst:
            diksh[k]=v
        d["es_host"]=diksh["es_host"]
        d["es_port"]=int(diksh["es_port"])
    with open(fname, "w") as f:
    	yaml.dump(d, f, default_flow_style=False)

if __name__=="__main__":
    #home="/home/kvenkatswammy"
    #home_dir=os.environ["HOME"]
    home_dir="/opt"
    base_path=home_dir+"/elasticalert"
    update_config(base_path+"/elastalert/config.yaml", base_path+"/config.conf")
