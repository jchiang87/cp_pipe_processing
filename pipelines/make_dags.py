import os
import glob
import subprocess

pipelines = sorted(glob.glob('*.yaml'))
pngfiles = set(glob.glob('*.png'))

for pipeline in pipelines:
    dotfile = pipeline.replace('.yaml', '.dot')
    pngfile = dotfile.replace('.dot', '.png')
    if pngfile in pngfiles:
        continue
    print("processing:", pipeline)
    command = (f"pipetask build --pipeline {pipeline} "
               f"--pipeline-dot {dotfile}; dot -Tpng {dotfile} > {pngfile}")
    subprocess.check_call(command, shell=True)
    os.remove(dotfile)
