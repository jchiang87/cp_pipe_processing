import glob
from lsst.ctrl.bps import BpsConfig

for config_file in glob.glob('bps*.yaml'):
    print(config_file)
    config = BpsConfig(config_file)
    for key in config:
        config[key]
