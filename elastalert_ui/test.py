#

import os
import os.path

path="/home/ec2-user/elastalert/example_rules"
files=[f.split('.')[0] for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
print files
