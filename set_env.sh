#!/bin/bash
source $(dirname $(readlink -e "$BASH_SOURCE"))/modules/queue_system/set_env.sh
source $(dirname $(readlink -e "$BASH_SOURCE"))/modules/jb_utils/set_env.sh
source /cvmfs/cms.cern.ch/cmsset_default.sh
voms-proxy-init --voms cms --out $(pwd)/voms_proxy.txt -valid 172:0
export X509_USER_PROXY=$(pwd)/voms_proxy.txt
