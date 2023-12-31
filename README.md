Makes nanoaodv9 from miniaod

1. Code setup
```
git clone --recurse-submodules git@github.com:jaebak/NanoaodV9UCSB_producer.git
```

2. Setup cmssw for NanoAODv9UCSB
```
export WORK_DIR=$(readlink -f $PWD)
singularity shell -B /cvmfs -B /etc/grid-security -B $HOME/.globus -B $WORK_DIR -B /etc/cvmfs -B /etc/vomses -B /data/localsite/SITECONF/local /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/cc7:x86_64
cd $WORK_DIR
voms-proxy-init --voms cms --out $(pwd)/voms_proxy.txt -valid 172:0
export X509_USER_PROXY=$(pwd)/voms_proxy.txt
export SCRAM_ARCH=slc7_amd64_gcc700
source /cvmfs/cms.cern.ch/cmsset_default.sh
scram p CMSSW CMSSW_10_6_26
cd CMSSW_10_6_26/src
cmsenv
git cms-addpkg PhysicsTools/NanoAOD
# git remote add nanoaodv9UCSB git@github.com:jaebak/cmssw_nanoaodv9UCSB.git
git remote add nanoaodv9UCSB https://github.com/jaebak/cmssw_nanoaodv9UCSB.git
git pull nanoaodv9UCSB from-CMSSW_10_6_26
scram b
cd ../../
exit
```

3. Making cl file
```
source set_env.sh
source /cvmfs/cms.cern.ch/cmsset_default.sh
voms-proxy-init --voms cms --out $(pwd)/voms_proxy.txt -valid 172:0
export X509_USER_PROXY=$(pwd)/voms_proxy.txt
./make_cl_files.py
```

4. Running cl file
```
ln -s /net/cms11/cms11r0/pico/NanoAODv9UCSB nanoaod
screen
source set_env.sh
convert_cl_to_jobs_info.py cl_nanoaodv9UCSB_v1 nanoaodv9UCSB_v1.json
auto_submit_jobs.py nanoaodv9UCSB_v1.json -c scripts/check_nanoaod_entries.py
auto_submit_jobs.py nanoaodv9UCSB_v1.json -c scripts/check_nanoaod_entries.py;sendTelegramMessage.py "Finished nanoaodv9UCSB_v1 for ZG"
auto_submit_jobs.py nanoaodv9UCSB_v1.json -n cms11 -c scripts/check_nanoaod_entries.py;sendTelegramMessage.py "Finished 2018 nanoaodv9UCSB_v1 for ZG"
```
