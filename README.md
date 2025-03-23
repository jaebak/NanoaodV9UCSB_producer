Versions  
UCSB1: Added photon variables to nanoaod  
UCSB2: Fixed scale factor file for electrons and photons for 2016APV data  


Makes nanoaodv9 from miniaod on cmsconnect

1. Code setup
```
git clone --recurse-submodules git@github.com:jaebak/NanoaodV9UCSB_producer.git
# If did not use recurse at clone, use following command: git submodule update --init --remote --recursive
cd NanoaodV9UCSB_producer
source set_env.sh
voms-proxy-init -voms cms -rfc -valid 192:00 --out $(pwd)/voms_proxy.txt
```

2. Setup cmssw for NanoAODv9UCSB
```
export WORK_DIR=$(readlink -f $PWD)
singularity shell -B /cvmfs -B /etc/grid-security -B $HOME/.globus -B $WORK_DIR -B /etc/cvmfs /cvmfs/singularity.opensciencegrid.org/cmssw/cms:rhel7
cd $WORK_DIR
voms-proxy-init --voms cms --out $(pwd)/voms_proxy.txt -valid 172:0
export X509_USER_PROXY=$(pwd)/voms_proxy.txt
export SCRAM_ARCH=slc7_amd64_gcc700
source /cvmfs/cms.cern.ch/cmsset_default.sh
scram p CMSSW CMSSW_10_6_26
cd CMSSW_10_6_26/src
cmsenv
git cms-addpkg PhysicsTools/NanoAOD
# To update cmsssw code
git remote add nanoaodv9UCSB https://github.com/jaebak/cmssw_nanoaodv9UCSB.git
git pull nanoaodv9UCSB from-CMSSW_10_6_26
# https://twiki.cern.ch/twiki/bin/view/CMS/EgammaUL2016To2018#Scale_and_smearing_corrections_f
git clone -b ULSSfiles_correctScaleSysMC https://github.com/jainshilpi/EgammaAnalysis-ElectronTools.git EgammaAnalysis/ElectronTools/data/
git cms-addpkg EgammaAnalysis/ElectronTools
scram b
cd ../../
tar -zcvf CMSSW_10_6_26.tar.gz CMSSW_10_6_26
exit
```

3. Making cl file
```
source set_env.sh
source /cvmfs/cms.cern.ch/cmsset_default.sh
voms-proxy-init -voms cms -rfc -valid 192:00 --out $(pwd)/voms_proxy.txt
export X509_USER_PROXY=$(pwd)/voms_proxy.txt
mkdir jsons
#ln -s /net/cms18/cms18r0/pico/NanoAODv9UCSB2 nanoaod
mkdir nanoaod
./make_cl_files.py -i txt/2016apvdata_nanoaod_datasets.txt
```

4. Running cl file
```
screen
source set_env.sh

voms-proxy-init -voms cms -rfc -valid 192:00 --out $(pwd)/voms_proxy.txt
export X509_USER_PROXY=$(pwd)/voms_proxy.txt

export SCRAM_ARCH=el9_amd64_gcc12
cmsrel CMSSW_13_3_1_patch1
cd CMSSW_13_3_1_patch1/src
cmsenv
cd -

convert_cl_to_jobs_info.py ./cl_nanoaodv9UCSB2 cl_nanoaodv9UCSB2.json
mkdir logs
auto_submit_jobs.py cl_nanoaodv9UCSB2.json -c scripts/check_nanoaod_entries.py -ci 'voms_proxy.txt,CMSSW_10_6_26.tar.gz,run_scripts.tar.gz' -cn 2;sendTelegramMessage.py "Finished 2018 nanoaodv9UCSB2"
```

If the `auto_submit_jobs.py` was interrupted, one can resume by
```
auto_submit_jobs.py auto_cl_nanoaodv9UCSB2.json -o auto_cl_nanoaodv9UCSB2.json -c scripts/check_nanoaod_entries.py -ci 'voms_proxy.txt,CMSSW_10_6_26.tar.gz,run_scripts.tar.gz' -cn 2
```
