set -x
test_repo=./test_repo

if [[ ! -d ${test_repo} ]];
then
    butler create ${test_repo}
    butler register-instrument ${test_repo} lsst.obs.lsst.LsstCam
    butler write-curated-calibrations test_repo lsst.obs.lsst.LsstCam
fi
butler ingest-raws --transfer direct ${test_repo} raw_files/*
