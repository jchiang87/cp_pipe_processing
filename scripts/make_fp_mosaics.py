import numpy as np
import lsst.afw.cameraGeom.utils as cgu
from lsst.afw.math import rotateImageBy90
import lsst.daf.butler as daf_butler
from lsst.obs.lsst import LsstCam


def orientation_callback(image, det, *args, **kwds):
    print(" ", det.getId())
    image = rotateImageBy90(image, det.getOrientation().getNQuarter())
    return image


class Flattener:
    def __init__(self, butler, physical_filter, dstype='flat'):
        self.dsrefs = {dsref.dataId['detector']: dsref for dsref in
                       set(butler.registry.queryDatasets(
                           dstype, physical_filter=physical_filter))}
        self.flats = {}

    def __call__(self, im, det, imageSource=None, *args, **kwds):
        detector = det.getId()
        print(" ", detector)
        if detector not in self.flats:
            self.flats[detector] \
                = butler.get(self.dsrefs[detector]).getMaskedImage().getImage()
        image = im.Factory(im, deep=True)
        image.array /= self.flats[detector].array
        image = rotateImageBy90(image, det.getOrientation().getNQuarter())
        return image


acq_run = 13162
repo = '/sdf/group/lsst/camera/IandT/repo_gen3/BOT_data'
collections = 'u/jchiang/flat_13162_w_2022_34'
butler = daf_butler.Butler(repo, collections=collections)
camera = LsstCam.getCamera()
verbose = True
binSize = 16
detectorNameList = None

## Superbias
#dstype = 'bias'
#print("processing", dstype)
#bi = cgu.ButlerImage(butler, dstype, verbose=verbose,
#                     callback=orientation_callback)
#im = cgu.showCamera(camera, imageSource=bi,
#                    detectorNameList=detectorNameList, binSize=binSize)
#im.writeFits(f'fp_super{dstype}_{acq_run}.fits')
#
## Superdark
#dstype = 'dark'
#print("processing", dstype)
#bi = cgu.ButlerImage(butler, dstype, verbose=verbose,
#                     callback=orientation_callback)
#im = cgu.showCamera(camera, imageSource=bi,
#                    detectorNameList=detectorNameList, binSize=binSize)
#im.writeFits(f'fp_super{dstype}_{acq_run}.fits')
#
## Superflat
#dstype = 'flat'
#physical_filters = ('SDSSi', 'SDSSi~ND_OD1.0')
#for physical_filter in physical_filters:
#    print("processing", dstype, physical_filter)
#    bi = cgu.ButlerImage(butler, dstype, verbose=verbose,
#                         callback=orientation_callback,
#                         physical_filter=physical_filter)
#    im = cgu.showCamera(camera, imageSource=bi,
#                        detectorNameList=detectorNameList, binSize=binSize)
#    im.writeFits(f'fp_super{dstype}_{physical_filter}_{acq_run}.fits')

# unflattened and flattened sflat exposures
dstype = 'cpFlatProc'
print("processing", dstype)
exposures = (3021121200234, 3021121200249)
for exposure in exposures:
    physical_filter = list(butler.registry.queryDatasets(
        dstype, exposure=exposure))[0].dataId['physical_filter']
    print('processing', exposure, physical_filter)
    callbacks = (orientation_callback, Flattener(butler, physical_filter))
    states = ('unflattened', 'flattened')
    for state, callback in zip(states, callbacks):
        bi = cgu.ButlerImage(butler, dstype, verbose=verbose,
                             callback=callback, exposure=exposure)
        im = cgu.showCamera(camera, imageSource=bi,
                            detectorNameList=detectorNameList, binSize=binSize)
        outfile = f'fp_{state}_{exposure}_{physical_filter}_{acq_run}.fits'
        im.writeFits(outfile)
