import os
import glob
from lsst.ctrl.bps import BpsConfig
from desc.gen3_workflow import start_pipeline, ParslGraph


def find_parsl_graph(bps_config_file):
    bps_config = BpsConfig(bps_config_file)
    pattern = os.path.join(bps_config['submitPath'], '*')
    submit_paths = sorted(glob.glob(pattern))
    if not submit_paths:
        return None, False
    submit_path = submit_paths[-1]
    parsl_graph_file = os.path.join(submit_path, 'parsl_graph_config.pickle')
    if not os.path.isfile(parsl_graph_file):
        parsl_graph_file = None
    finished = not os.path.isdir(os.path.join(submit_path, 'tmp_repos'))
    return parsl_graph_file, finished


with open('bps_config_file_list.txt') as fobj:
    bps_config_files = [_.split('#')[0].strip() for _ in fobj
                        if not _.startswith('#')]


for bps_config_file in bps_config_files:
    parsl_graph_file, finished = find_parsl_graph(bps_config_file)
    if parsl_graph_file is None:
        print('running', bps_config_file, flush=True)
        graph = start_pipeline(bps_config_file)
    elif not finished:
        print('restarting', bps_config_file, flush=True)
        graph = ParslGraph.restore(parsl_graph_file,
                                   parsl_config='bps_parsl_config.yaml')
        jobs = []
        for task in graph._task_list:
            for status in ('launched running failed dep_fail'.split()):
                jobs.extend(graph.get_jobs(task, status))
        graph.run(jobs)
    else:
        print(bps_config_file, 'has completed execution')
        continue
    graph.run(block=True)
    graph._update_status()
    num_failures = len(graph.df.query('status == "failed"'))
    if num_failures > 0:
        raise RuntimeError(f'{bps_config_file} had {num_failures} failed jobs.')
