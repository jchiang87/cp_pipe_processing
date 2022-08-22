from collections import defaultdict
import time
import multiprocessing
import numpy as np
import pandas as pd
import lsst.daf.butler as daf_butler

def extract_timing_info(butler, dsref_info):
    data = defaultdict(list)
    for pipeline, dstype, dsref in dsref_info:
        try:
            log_data = butler.get(dsref)
        except Exception as eobj:
            print("Error from butler:", eobj)
            continue
        final_message = list(log_data)[-1].message
        tokens = final_message.split()
        if tokens[-3] == "took" and tokens[-1] == "seconds":
            data['wall_time'].append(float(tokens[-2]))
            data['dstype'].append(dstype)
            data['pipeline'].append(pipeline)
    return pd.DataFrame(data=data)

def get_dsref_log_info(repo, outputs):
    collections = []
    dsref_info = []
    for (pipeline, collection), dstypes in outputs.items():
        if not collections or collection not in collections:
            collections = [collection]
            butler = daf_butler.Butler(repo, collections=collections)
        for dstype in dstypes:
            dsrefs = list(set(butler.registry.queryDatasets(dstype + '_log')))
            for dsref in dsrefs:
                dsref_info.append((pipeline, dstype, dsref))
    return dsref_info

repo = '/sdf/group/lsst/camera/IandT/repo_gen3/BOT_data'

outputs = {('cpBias', 'u/jchiang/bias_13162_w_2022_34/20220820T001939Z'):
           ['isr', 'cpBiasCombine'],
           ('cpDark', 'u/jchiang/dark_13162_w_2022_34/20220820T011957Z'):
           ['isr', 'cpDark', 'cpDarkCombine'],
           ('cpFlat', 'u/jchiang/flat_13162_w_2022_34/20220820T020329Z'):
           ['isr', 'cpFlatCombine', 'cpFlatMeasure', 'cpFlatNorm'],
           ('cpPtc', 'u/jchiang/ptc_13162_w_2022_34/20220820T033126Z'):
           ['isr', 'ptcExtract', 'ptcSolve']}

t0 = time.time()
dsref_info = get_dsref_log_info(repo, outputs)
print("# dsrefs:", len(dsref_info))
print("get_dsref_info:", time.time() - t0)

butler = daf_butler.Butler(repo, collections=['u/jchiang/ptc_13162_w_2022_34'])

processes = 16

indexes = np.linspace(0, len(dsref_info), processes + 1, dtype=int)

with multiprocessing.Pool(processes=processes) as pool:
    workers = []
    for imin, imax in zip(indexes[:-1], indexes[1:]):
        workers.append(pool.apply_async(extract_timing_info,
                                        (butler, dsref_info[imin:imax],)))
    pool.close()
    pool.join()
    dfs = [_.get() for _ in workers]

df = pd.concat(dfs)
df.to_pickle('cp_pipe_wall_times.pickle')
