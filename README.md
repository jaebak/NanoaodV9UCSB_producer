Makes nanoaodv9 from miniaod

Setup
```
export WORK_DIR=$(readlink -f $PWD)
singularity shell -B /cvmfs -B /etc/grid-security -B $HOME/.globus -B $WORK_DIR -B /etc/cvmfs /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/cc7:x86_64
cd $WORK_DIR
export SCRAM_ARCH=slc7_amd64_gcc700
source /cvmfs/cms.cern.ch/cmsset_default.sh
scram p CMSSW CMSSW_10_6_26
cd CMSSW_10_6_26/src
cmsenv
git cms-addpkg PhysicsTools/NanoAOD
#git remote add nanoaodv9UCSB git@github.com:jaebak/cmssw_nanoaodv9UCSB.git
git remote add nanoaodv9UCSB https://github.com/jaebak/cmssw_nanoaodv9UCSB.git
git pull nanoaodv9UCSB from-CMSSW_10_6_26
```

Making cl file
```
source /cvmfs/cms.cern.ch/cmsset_default.sh
voms-proxy-init --voms cms --out $(pwd)/voms_proxy.txt -valid 172:0
export X509_USER_PROXY=$(pwd)/voms_proxy.txt
make_cl_files.py
```

Running cl file
