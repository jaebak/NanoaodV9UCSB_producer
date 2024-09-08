Versions  
UCSB1: Added photon variables to nanoaod  
UCSB2: Fixed scale factor file for electrons and photons for 2016APV data  


Makes nanoaodv9 from miniaod

0. Download MINIAOD files due to unstable xrootd connection. Works only if server /cvmfs/cms.cern.ch/SITECONF/local is setup correctly. cms18 is setup correctly.
```
source /cvmfs/cms.cern.ch/cmsset_default.sh
source /cvmfs/cms.cern.ch/rucio/setup-py3.sh
voms-proxy-init -voms cms -rfc -valid 192:00
export RUCIO_ACCOUNT=jaebak
cd /net/cms18/cms18r0/store
rucio download --ndownloader=5 cms:/GluGluHToZG_ZToLL_M-125_TuneCP5_13TeV-powheg-pythia8/RunIISummer20UL16MiniAODAPVv2-106X_mcRun2_asymptotic_preVFP_v11-v2/MINIAODSIM
```

1. Code setup
```
git clone --recurse-submodules git@github.com:jaebak/NanoaodV9UCSB_producer.git
```

2. Setup cmssw for NanoAODv9UCSB
```
export WORK_DIR=$(readlink -f $PWD)
singularity shell -B /cvmfs -B /etc/grid-security -B $HOME/.globus -B $WORK_DIR -B /etc/cvmfs -B /etc/vomses -B /data/localsite/SITECONF/local /cvmfs/singularity.opensciencegrid.org/cmssw/cms:rhel7
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
# git remote add nanoaodv9UCSBgit git@github.com:jaebak/cmssw_nanoaodv9UCSB.git
# git push --set-upstream nanoaodv9UCSBgit from-CMSSW_10_6_26
git remote add nanoaodv9UCSB https://github.com/jaebak/cmssw_nanoaodv9UCSB.git
git pull nanoaodv9UCSB from-CMSSW_10_6_26
# https://twiki.cern.ch/twiki/bin/view/CMS/EgammaUL2016To2018#Scale_and_smearing_corrections_f
git clone -b ULSSfiles_correctScaleSysMC https://github.com/jainshilpi/EgammaAnalysis-ElectronTools.git EgammaAnalysis/ElectronTools/data/
git cms-addpkg EgammaAnalysis/ElectronTools
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
mkdir run_scripts
mkdir jsons
mkdir tmp_scripts
ln -s /net/cms18/cms18r0/pico/NanoAODv9UCSB2 nanoaod
./make_cl_files.py
```

4. Running cl file
```
screen
source set_env.sh
convert_cl_to_jobs_info.py cl_nanoaodv9UCSB2 cl_nanoaodv9UCSB2.json
mkdir logs
# Limiting number of jobs to 128 seems to reduce issues
auto_submit_jobs.py cl_nanoaodv9UCSB2.json -n cms18 -r 128 -c scripts/check_nanoaod_entries.py;sendTelegramMessage.py "Finished 2018 nanoaodv9UCSB2"
```
