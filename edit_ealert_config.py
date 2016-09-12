import yaml
import os
import ConfigParser
def update_config(fname, path):
    with open(fname) as f:
        d=yaml.load(f)
        print d
        parser=ConfigParser.SafeConfigParser(path)
        parser.read(path)
        lst=parser.items("elasticsearch")
        diksh={k:v for k,v in lst}
        d["es_host"]=diksh["host"]
        d["es_port"]=int(diksh["port"])
    with open(fname, "w") as f:
    	yaml.dump(d, f, default_flow_style=False)

if __name__=="__main__":
    #home="/home/kvenkatswammy"
    home_dir=os.environ["HOME"]
    base_path=home_dir+"/elasticalert"
    #base_path="."
    update_config(base_path+"/elastalert/config.yaml", base_path+"/esearch.conf")
