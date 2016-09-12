import yaml
import os
import ConfigParser
def update_config(fname, diksh):
    with open(fname) as f:
        d=yaml.load(f)
        print d
        d["es_host"]=diksh["es_host"]
        d["es_port"]=int(diksh["es_port"])
    with open(fname, "w") as f:
    	yaml.dump(d, f, default_flow_style=False)

if __name__=="__main__":
    #home="/home/kvenkatswammy"
    #home_dir=os.environ["HOME"]
    parser=ConfigParser.SafeConfigParser()
    parser.read(path)
    lst=parser.items("default")
    diksh=dict()
    for k,v in lst:
        diksh[k]=v
    home_dir=diksh["home_dir"]
    base_path=home_dir+"/elasticalert"
    update_config(base_path+"/elastalert/config.yaml", diksh)
