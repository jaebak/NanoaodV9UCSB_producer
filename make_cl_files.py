#!/usr/bin/env python3
# Setup env: 
#   source /cvmfs/cms.cern.ch/cmsset_default.sh
#   voms-proxy-init --voms cms --out $(pwd)/voms_proxy.txt -valid 172:0 
#   export X509_USER_PROXY=$(pwd)/voms_proxy.txt
import subprocess
import time
import os
import stat
import multiprocessing

def query_das(query, verbose=True):
  for iRetry in range(5):
    try:
      if verbose: print(f'Query: {query}')
      result = subprocess.check_output(f'dasgoclient -query="{query}"', shell=True, universal_newlines=True).split()
      break
    except subprocess.CalledProcessError as e:
      print(e.output)
      print('Trying again '+str(iRetry+1)+' Query: '+query)
      time.sleep(3)
  if verbose: print('  Result: ' + str(result))
  return result

# parsed_mc_filename: WZTo3LNu_TuneCUETP8M1_13TeV-powheg-pythia8__RunIISummer16NanoAODv5__PUMoriond17_Nano1June2019_102X_mcRun2_asymptotic_v7-v1__120000__222071C0-CF04-1E4B-B65E-49D18B91DE8B.root
# mc_filename: /store/mc/RunIISummer16NanoAODv5/WZTo3LNu_TuneCUETP8M1_13TeV-powheg-pythia8/NANOAODSIM/PUMoriond17_Nano1June2019_102X_mcRun2_asymptotic_v7-v1/120000/222071C0-CF04-1E4B-B65E-49D18B91DE8B.root
def filename_to_parsed(filename):
  input_split = filename.split('/')
  output_path = input_split[4]+'__'+input_split[3]+'__'+input_split[6]+'_UCSB'+'__'+input_split[7]+'__'+input_split[8]
  return output_path

def find_era(nanoaod_filename):
  if 'RunIISummer20UL18NanoAODv9' in nanoaod_filename: return '2018'
  if 'RunIISummer20UL17NanoAODv9' in nanoaod_filename: return '2017'
  if 'RunIISummer20UL16NanoAODv9' in nanoaod_filename: return '2016'
  if 'RunIISummer20UL16NanoAODAPVv9' in nanoaod_filename: return '2016APV'

def get_miniaod_files(argument):
  nanoaod_filename = argument
  return query_das(f'parent file={nanoaod_filename}', verbose=False)

if __name__ == "__main__":
  dataset_name = "/ZGToLLG_01J_5f_lowMLL_lowGPt_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v1/NANOAODSIM"

  ## Get miniaod files with single core
  #nanoaod_filenames = query_das(f'file dataset={dataset_name}')
  #nanoaod_to_miniaod = {}
  #for nanoaod_filename in nanoaod_filenames:
  #  nanoaod_to_miniaod[nanoaod_filename] = query_das(f'parent file={nanoaod_filename}', verbose=False)
  #  #break
  ##print(nanoaod_to_miniaod)

  # Get miniaod files with multicore
  nanoaod_filenames = query_das(f'file dataset={dataset_name}')
  #print(nanoaod_filenames)
  ncpu = multiprocessing.cpu_count()
  if ncpu > 8: ncpu = 8
  pool = multiprocessing.Pool(ncpu)
  miniaod_filenames_array = pool.map(get_miniaod_files, nanoaod_filenames)
  #print(miniaod_filenames_array)
  nanoaod_to_miniaod = {}
  for ifile, filename in enumerate(nanoaod_filenames):
    nanoaod_filename = filename
    miniaod_filenames = miniaod_filenames_array[ifile]
    nanoaod_to_miniaod[nanoaod_filename] = miniaod_filenames
  #print(nanoaod_to_miniaod)

  ## Example
  ##print(nanoaod_to_miniaod)
  #nanoaod_to_miniaod = {'/store/mc/RunIISummer20UL16NanoAODAPVv9/ZGToLLG_01J_5f_lowMLL_lowGPt_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/106X_mcRun2_asymptotic_preVFP_v11-v1/30000/BEEA26B9-1A25-714C-8072-DF2C15774C67.root': \
  #  ['/store/mc/RunIISummer20UL16MiniAODAPVv2/ZGToLLG_01J_5f_lowMLL_lowGPt_TuneCP5_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/106X_mcRun2_asymptotic_preVFP_v11-v2/2550000/1D817778-1C17-DE4C-8D51-14EFD9226CFE.root', '/store/mc/RunIISummer20UL16MiniAODAPVv2/ZGToLLG_01J_5f_lowMLL_lowGPt_TuneCP5_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/106X_mcRun2_asymptotic_preVFP_v11-v2/2550000/204AE9BC-B08E-D745-988D-745CC31AF9AE.root', '/store/mc/RunIISummer20UL16MiniAODAPVv2/ZGToLLG_01J_5f_lowMLL_lowGPt_TuneCP5_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/106X_mcRun2_asymptotic_preVFP_v11-v2/2550000/26D5F2B8-D16F-7E46-9DC1-E4742AC973F6.root']}
  #nanoaod_to_miniaod = {'/store/mc/RunIISummer20UL18NanoAODv9/ZGToLLG_01J_5f_lowMLL_lowGPt_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/106X_upgrade2018_realistic_v16_L1v1-v1/2520000/3363228C-76B3-9245-AEE9-8644875EE6D0.root': ['/store/mc/RunIISummer20UL18MiniAODv2/ZGToLLG_01J_5f_lowMLL_lowGPt_TuneCP5_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/30000/08CE698B-E5F3-3546-B473-980C874FC3D1.root', '/store/mc/RunIISummer20UL18MiniAODv2/ZGToLLG_01J_5f_lowMLL_lowGPt_TuneCP5_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/30000/0B86829D-7BEE-F244-BC59-713FF5DD4C3E.root']}

  # Make scripts to run nanoaod
  command_paths = []
  # - run_script -> run_script_in_env
  # - run_script_in_env -> cfg
  tmp_folder = 'tmp_scripts'
  run_script_folder = 'run_scripts'
  output_folder = 'nanoaod'
  for nanoaod_file in nanoaod_to_miniaod:
    era = find_era(nanoaod_file)
    miniaod_filenames = nanoaod_to_miniaod[nanoaod_file]
    miniaod_filenames_string = ','.join(miniaod_filenames).replace('/store','root://cms-xrd-global.cern.ch//store')
    nanoaod_filename = f'{filename_to_parsed(nanoaod_file)}'
    nanoaod_cfg_path = f'{tmp_folder}/{nanoaod_filename.replace(".root","")}_cfg.py'
    # https://cmsweb.cern.ch/das/request?view=list&limit=50&instance=prod%2Fglobal&input=%2FZGToLLG_01J_5f_lowMLL_lowGPt_TuneCP5_13TeV-amcatnloFXFX-pythia8*%2F*UL*%2FNANOAODSIM
    # 2016: https://cms-pdmv-prod.web.cern.ch/mcm/public/restapi/requests/get_setup/EXO-RunIISummer20UL16NanoAODv9-02444
    # 2016APV: https://cms-pdmv-prod.web.cern.ch/mcm/public/restapi/requests/get_setup/EXO-RunIISummer20UL16NanoAODAPVv9-02070
    # 2017: https://cms-pdmv-prod.web.cern.ch/mcm/public/restapi/requests/get_setup/EXO-RunIISummer20UL17NanoAODv9-02656
    # 2018: https://cms-pdmv-prod.web.cern.ch/mcm/public/restapi/requests/get_setup/EXO-RunIISummer20UL18NanoAODv9-02439
    if era == '2018': # 
      cmsCfg_command = f'cmsDriver.py --python_filename {nanoaod_cfg_path} --eventcontent NANOAODSIM --customise Configuration/DataProcessing/Utils.addMonitoring --datatier NANOAODSIM --fileout file:{output_folder}/{nanoaod_filename} --conditions 106X_upgrade2018_realistic_v16_L1v1 --step NANO --filein "{miniaod_filenames_string}" --era Run2_2018,run2_nanoAOD_106Xv2 --no_exec --mc -n -1'
    elif era == '2016':
      cmsCfg_command = f'cmsDriver.py  --python_filename {nanoaod_cfg_path} --eventcontent NANOAODSIM --customise Configuration/DataProcessing/Utils.addMonitoring --datatier NANOAODSIM --fileout file:{output_folder}/{nanoaod_filename} --conditions 106X_mcRun2_asymptotic_v17 --step NANO --filein "{miniaod_filenames_string}" --era Run2_2016,run2_nanoAOD_106Xv2 --no_exec --mc -n -1'
    elif era == '2016APV':
      cmsCfg_command = f'cmsDriver.py  --python_filename {nanoaod_cfg_path} --eventcontent NANOAODSIM --customise Configuration/DataProcessing/Utils.addMonitoring --datatier NANOAODSIM --fileout file:{output_folder}/{nanoaod_filename} --conditions 106X_mcRun2_asymptotic_preVFP_v11 --step NANO --filein "{miniaod_filenames_string}" --era Run2_2016_HIPM,run2_nanoAOD_106Xv2 --no_exec --mc -n -1'
    elif era == '2017':
      cmsCfg_command = f'cmsDriver.py  --python_filename {nanoaod_cfg_path} --eventcontent NANOAODSIM --customise Configuration/DataProcessing/Utils.addMonitoring --datatier NANOAODSIM --fileout file:{output_folder}/{nanoaod_filename} --conditions 106X_mc2017_realistic_v9 --step NANO --filein "{miniaod_filenames_string}" --era Run2_2017,run2_nanoAOD_106Xv2 --no_exec --mc -n -1'
    cmsRun_command = f'cmsRun {nanoaod_cfg_path}'
    run_script_name = f'{nanoaod_filename.replace(".root","")}.sh'
    run_script_path = f'{run_script_folder}/{run_script_name}'
    with open(run_script_path, 'w') as run_script:
      run_script.write(f'''#!/bin/bash
cat <<EndOfTestFile > {tmp_folder}/{run_script_name}.cmd_in_env
# Make script
export WORK_DIR=$(readlink -f $PWD)
export SCRAM_ARCH=slc7_amd64_gcc700
source /cvmfs/cms.cern.ch/cmsset_default.sh
#scram p CMSSW CMSSW_10_6_26
cd CMSSW_10_6_26/src
cmsenv
cd ../../
{cmsCfg_command}
{cmsRun_command}
EndOfTestFile
singularity exec -B /cvmfs -B /etc/grid-security -B $HOME/.globus -B $WORK_DIR -B /etc/cvmfs /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/cc7:x86_64 bash {tmp_folder}/{run_script_name}.cmd_in_env
''')
    os.chmod(run_script_path, os.stat(run_script_path).st_mode | stat.S_IEXEC)
    command_paths.append(run_script_path)

  # All commands for running scripts
  command_lines_filename = f'cl_{"__".join(dataset_name.split("/")[1:])}'
  with open(command_lines_filename, 'w') as command_lines_file:
    for command_path in command_paths:
      command_lines_file.write(f'echo {command_path}\n')
  os.chmod(command_lines_filename, os.stat(command_lines_filename).st_mode | stat.S_IEXEC)
