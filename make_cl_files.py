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
import json
import nested_dict
import pathlib
import re


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

def query_number_events_file(nanoaod_filename):
  try:
    result = subprocess.check_output(f'dasgoclient -query="{nanoaod_filename}" -json', shell=True)
  except subprocess.CalledProcessError as e:
    print(e.output)
    print('Trying again '+str(iRetry+1)+' Query: '+nanoaod_filename)
    time.sleep(3)
  result_dict_list = json.loads(result)
  number_of_events = int(result_dict_list[0]['file'][0]['nevents'])
  return number_of_events, nanoaod_filename

def query_number_events_dataset(nanoaod_filename):
  try:
    result = subprocess.check_output(f'dasgoclient -query="{nanoaod_filename}" -json', shell=True)
  except subprocess.CalledProcessError as e:
    print(e.output)
    print('Trying again '+str(iRetry+1)+' Query: '+nanoaod_filename)
    time.sleep(3)
  result_dict_list = json.loads(result)
  #print(result_dict_list)
  for result_dict in result_dict_list:
    if 'dataset' in result_dict:
      if 'nevents' in result_dict['dataset'][0]:
        number_of_events = int(result_dict['dataset'][0]['nevents'])
  return number_of_events, nanoaod_filename

# parsed_mc_filename: WZTo3LNu_TuneCUETP8M1_13TeV-powheg-pythia8__RunIISummer16NanoAODv5__PUMoriond17_Nano1June2019_102X_mcRun2_asymptotic_v7-v1__120000__222071C0-CF04-1E4B-B65E-49D18B91DE8B.root
# mc_filename: /store/mc/RunIISummer16NanoAODv5/WZTo3LNu_TuneCUETP8M1_13TeV-powheg-pythia8/NANOAODSIM/PUMoriond17_Nano1June2019_102X_mcRun2_asymptotic_v7-v1/120000/222071C0-CF04-1E4B-B65E-49D18B91DE8B.root
def filename_to_parsed(filename):
  input_split = filename.split('/')
  output_path = input_split[4]+'__'+input_split[3]+'__'+input_split[6]+'_UCSB'+'__'+input_split[7]+'__'+input_split[8]
  return output_path

# nanoaod_name: /ZGToLLG_01J_5f_lowMLL_lowGPt_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v1/NANOAODSIM
def make_nanoaod_custom_name(nanoaod_name, nanoaod_custom_name_index):
  _, dataset_name, era_version_name, _ = nanoaod_name.split('/')
  era_name, version_name = era_version_name.split('-',1)
  return f'{dataset_name}__{era_name}__{version_name}__{nanoaod_custom_name_index:03}.root'

def find_era(nanoaod_filename):
  if 'RunIISummer20UL18NanoAODv9' in nanoaod_filename: return '2018'
  if 'RunIISummer20UL17NanoAODv9' in nanoaod_filename: return '2017'
  if 'RunIISummer20UL16NanoAODv9' in nanoaod_filename: return '2016'
  if 'RunIISummer20UL16NanoAODAPVv9' in nanoaod_filename: return '2016APV'

def find_datatype(nanoaod_filename):
  if 'NANOAODSIM' in nanoaod_filename: return 'mc'
  else: return 'data'

def get_miniaod_files(argument):
  nanoaod_filename = argument
  return query_das(f'parent file={nanoaod_filename}', verbose=False), nanoaod_filename

if __name__ == "__main__":
  # Make cl file and json file for checking

  datasets_name = ["/ZGToLLG_01J_5f_lowMLL_lowGPt_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v1/NANOAODSIM",
                   "/ZGToLLG_01J_5f_lowMLL_lowGPt_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIISummer20UL17NanoAODv9-106X_mc2017_realistic_v9-v1/NANOAODSIM",
                   "/ZGToLLG_01J_5f_lowMLL_lowGPt_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIISummer20UL16NanoAODv9-106X_mcRun2_asymptotic_v17-v1/NANOAODSIM",
                   "/ZGToLLG_01J_5f_lowMLL_lowGPt_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIISummer20UL16NanoAODAPVv9-106X_mcRun2_asymptotic_preVFP_v11-v1/NANOAODSIM",
                  ]
  #datasets_name = ["/ZGToLLG_01J_5f_lowMLL_lowGPt_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIISummer20UL17NanoAODv9-106X_mc2017_realistic_v9-v1/NANOAODSIM"]
  # Makes below json file including nanoaod[miniaods, event]
  command_lines_filename = f'cl_nanoaodv9UCSB_v1'
  datasets_json_filename = 'jsons/nanoaodv9UCSB_v1.json'
  tmp_folder = 'tmp_scripts'
  run_script_folder = 'run_scripts'
  output_folder = 'nanoaod'
  number_of_events = '-1'
  do_query = False
  #number_of_events = '100'

  if do_query:
    # datasets_json = {nanoaod_name: {'nevents':, 'miniaod_name':, 'miniaods': {'filename': nevent}, 'nano_to_mini': {nanoaod_custom_name: {miniaod_name}} }}
    datasets_json = {}
    # Get nevents, miniaod dataset name, and miniaod filenames
    print('Getting nevents, miniaod dataset name, and miniaod filenames')
    for nanoaod_name in datasets_name:
      nevents = query_number_events_dataset(nanoaod_name)[0]
      miniaod_name = query_das(f'parent dataset={nanoaod_name}')[0]
      datasets_json[nanoaod_name] = {'nevents': nevents, 'miniaod_name': miniaod_name, 'miniaods': {}}
      # Get miniaod filenames
      miniaod_filenames = query_das(f'file dataset={miniaod_name}')
      for miniaod_filename in miniaod_filenames:
        datasets_json[nanoaod_name]['miniaods'][miniaod_filename] = -1
    nested_dict.save_json_file(datasets_json, datasets_json_filename)

    datasets_json = nested_dict.load_json_file_py3(datasets_json_filename)
    # Get number of events of MiniAOD with multicore
    print('Getting number of events for MiniAOD')
    for nanoaod_name in datasets_json:
      ncpu = multiprocessing.cpu_count()
      if ncpu > 8: ncpu = 8
      pool = multiprocessing.Pool(ncpu)
      miniaod_filenames = datasets_json[nanoaod_name]['miniaods'].keys()
      nevents_miniaods = pool.map(query_number_events_file, miniaod_filenames)
      for nevents, miniaod_filename in nevents_miniaods:
        datasets_json[nanoaod_name]['miniaods'][miniaod_filename] = nevents
    nested_dict.save_json_file(datasets_json, datasets_json_filename)

    # datasets_json = {nanoaod_name: {'nevents':, 'miniaod_name':, 'miniaods': {'filename': nevent}}}
    datasets_json = nested_dict.load_json_file_py3(datasets_json_filename)
    #print(datasets_json)
    

    # datasets_json = {nanoaod_name: {'nevents':, 'miniaod_name':, 'miniaods': {'filename': nevent}, 'nano_to_mini': {nanoaod_custom_name: {'miniaods': [miniaod_name], 'nevents': }} }}
    # Divide miniaods according to events. Divide so that each nanoaod has at least 1,000,000 events = 13evt/sec = 21 hours
    for nanoaod_name in datasets_json:
      datasets_json[nanoaod_name]['nano_to_mini'] = {}
      accumulated_events = 0
      nanoaod_custom_name_index = 0
      nanoaod_custom_name = make_nanoaod_custom_name(nanoaod_name, nanoaod_custom_name_index)
      datasets_json[nanoaod_name]['nano_to_mini'][nanoaod_custom_name] = {'miniaods': [], 'nevents': -1}
      for miniaod_filename in datasets_json[nanoaod_name]['miniaods']:
        miniaod_events = int(datasets_json[nanoaod_name]['miniaods'][miniaod_filename])
        accumulated_events += miniaod_events
        datasets_json[nanoaod_name]['nano_to_mini'][nanoaod_custom_name]['miniaods'].append(miniaod_filename)
        if accumulated_events > 1000000:
          datasets_json[nanoaod_name]['nano_to_mini'][nanoaod_custom_name]['nevents'] = accumulated_events
          accumulated_events = 0
          nanoaod_custom_name_index += 1
          nanoaod_custom_name = make_nanoaod_custom_name(nanoaod_name, nanoaod_custom_name_index)
          datasets_json[nanoaod_name]['nano_to_mini'][nanoaod_custom_name] = {'miniaods': [], 'nevents': -1}
      if datasets_json[nanoaod_name]['nano_to_mini'][nanoaod_custom_name]['nevents'] == -1: datasets_json[nanoaod_name]['nano_to_mini'][nanoaod_custom_name]['nevents'] = accumulated_events

    nested_dict.save_json_file(datasets_json, datasets_json_filename)
    for nanoaod_name in datasets_json:
      print(f"Dataset: {nanoaod_name} will have {len(datasets_json[nanoaod_name]['nano_to_mini'].keys())} custom nanoaod files")

  # datasets_json = {nanoaod_name: {'nevents':, 'miniaod_name':, 'miniaods': {'filename': nevent}, 'nano_to_mini': {nanoaod_custom_name: {'miniaods': [miniaod_name], 'nevents': }} }}
  datasets_json = nested_dict.load_json_file_py3(datasets_json_filename)

  # Compare number of events between miniaod and nanoaod
  for nanoaod_name in datasets_json:
    miniaod_events = 0
    for miniaod_filename in datasets_json[nanoaod_name]['miniaods']:
      miniaod_events += int(datasets_json[nanoaod_name]['miniaods'][miniaod_filename])
    if miniaod_events != datasets_json[nanoaod_name]['nevents']: print('[WARNING] Below nanoaod and miniaod events do not match')
    print(f"Dataset: {nanoaod_name}\n  nanoaod nEvents: {datasets_json[nanoaod_name]['nevents']} miniaod nEvents: {miniaod_events}")

  # Create cl script
  existing_folders = []
  # Make scripts to run nanoaod
  command_paths = []
  # - run_script makes run_script_in_env
  # - run_script_in_env makes cfg
  for nanoaod_name in datasets_json:
    for nanoaod_custom_name in datasets_json[nanoaod_name]['nano_to_mini']:
      era = find_era(nanoaod_custom_name)
      data_type = find_datatype(nanoaod_name)
      nanoaod_folder = f'{output_folder}/nano/{era}/{data_type}'
      if nanoaod_folder not in existing_folders:
        if not os.path.exists(nanoaod_folder): print(f'Creating {nanoaod_folder} folder')
        pathlib.Path(nanoaod_folder).mkdir(parents=True, exist_ok=True)
        existing_folders.append(nanoaod_folder)
      nevents = datasets_json[nanoaod_name]['nano_to_mini'][nanoaod_custom_name]['nevents']
      miniaod_filenames = datasets_json[nanoaod_name]['nano_to_mini'][nanoaod_custom_name]['miniaods']
      miniaod_filenames_string = ','.join(miniaod_filenames)
      #miniaod_filenames_string = ','.join(miniaod_filenames).replace('/store','root://cms-xrd-global.cern.ch//store')
      nanoaod_cfg_path = f'{tmp_folder}/{nanoaod_custom_name.replace(".root","")}_cfg.py'
      # https://cmsweb.cern.ch/das/request?view=list&limit=50&instance=prod%2Fglobal&input=%2FZGToLLG_01J_5f_lowMLL_lowGPt_TuneCP5_13TeV-amcatnloFXFX-pythia8*%2F*UL*%2FNANOAODSIM
      # 2016: https://cms-pdmv-prod.web.cern.ch/mcm/public/restapi/requests/get_setup/EXO-RunIISummer20UL16NanoAODv9-02444
      # 2016APV: https://cms-pdmv-prod.web.cern.ch/mcm/public/restapi/requests/get_setup/EXO-RunIISummer20UL16NanoAODAPVv9-02070
      # 2017: https://cms-pdmv-prod.web.cern.ch/mcm/public/restapi/requests/get_setup/EXO-RunIISummer20UL17NanoAODv9-02656
      # 2018: https://cms-pdmv-prod.web.cern.ch/mcm/public/restapi/requests/get_setup/EXO-RunIISummer20UL18NanoAODv9-02439
      if era == '2018': # 
        cmsCfg_command = f'cmsDriver.py --python_filename {nanoaod_cfg_path} --eventcontent NANOAODSIM --customise Configuration/DataProcessing/Utils.addMonitoring --datatier NANOAODSIM --fileout file:{nanoaod_folder}/{nanoaod_custom_name} --conditions 106X_upgrade2018_realistic_v16_L1v1 --step NANO --filein "{miniaod_filenames_string}" --era Run2_2018,run2_nanoAOD_106Xv2 --no_exec --mc -n {number_of_events}'
      elif era == '2016':
        cmsCfg_command = f'cmsDriver.py  --python_filename {nanoaod_cfg_path} --eventcontent NANOAODSIM --customise Configuration/DataProcessing/Utils.addMonitoring --datatier NANOAODSIM --fileout file:{nanoaod_folder}/{nanoaod_custom_name} --conditions 106X_mcRun2_asymptotic_v17 --step NANO --filein "{miniaod_filenames_string}" --era Run2_2016,run2_nanoAOD_106Xv2 --no_exec --mc -n {number_of_events}'
      elif era == '2016APV':
        cmsCfg_command = f'cmsDriver.py  --python_filename {nanoaod_cfg_path} --eventcontent NANOAODSIM --customise Configuration/DataProcessing/Utils.addMonitoring --datatier NANOAODSIM --fileout file:{nanoaod_folder}/{nanoaod_custom_name} --conditions 106X_mcRun2_asymptotic_preVFP_v11 --step NANO --filein "{miniaod_filenames_string}" --era Run2_2016_HIPM,run2_nanoAOD_106Xv2 --no_exec --mc -n {number_of_events}'
      elif era == '2017':
        cmsCfg_command = f'cmsDriver.py  --python_filename {nanoaod_cfg_path} --eventcontent NANOAODSIM --customise Configuration/DataProcessing/Utils.addMonitoring --datatier NANOAODSIM --fileout file:{nanoaod_folder}/{nanoaod_custom_name} --conditions 106X_mc2017_realistic_v9 --step NANO --filein "{miniaod_filenames_string}" --era Run2_2017,run2_nanoAOD_106Xv2 --no_exec --mc -n {number_of_events}'
      cmsRun_command = f'cmsRun {nanoaod_cfg_path}'
      run_script_name = f'{nanoaod_custom_name.replace(".root","")}.sh'
      run_script_path = f'{run_script_folder}/{run_script_name}'
      with open(run_script_path, 'w') as run_script:
        run_script.write(f'''#!/bin/bash
export WORK_DIR=$(readlink -f $PWD)
cat <<EndOfTestFile > {tmp_folder}/{run_script_name}.cmd_in_env
# Make script
cd $WORK_DIR
export SCRAM_ARCH=slc7_amd64_gcc700
source /cvmfs/cms.cern.ch/cmsset_default.sh
#scram p CMSSW CMSSW_10_6_26
cd CMSSW_10_6_26/src
cmsenv
cd ../../
{cmsCfg_command}
{cmsRun_command}
EndOfTestFile
singularity exec -B /cvmfs -B /etc/grid-security -B $HOME/.globus -B $WORK_DIR -B /etc/cvmfs -B /data/localsite/SITECONF/local -B /net/cms11/cms11r0/pico -B /net/cms18/cms18r0/store /cvmfs/unpacked.cern.ch/registry.hub.docker.com/cmssw/cc7:x86_64 bash {tmp_folder}/{run_script_name}.cmd_in_env
''')
      os.chmod(run_script_path, os.stat(run_script_path).st_mode | stat.S_IEXEC)
      command_paths.append([run_script_path, nevents])
      #break

  # All commands for running scripts
  with open(command_lines_filename, 'w') as command_lines_file:
    command_lines_file.write(f'echo "# [global_key] dataset_info_filename : {os.path.abspath(datasets_json_filename)}"\n')
    for command_path, nevents in command_paths:
      command_lines_file.write(f'echo {command_path} --nevents {nevents}\n')
  os.chmod(command_lines_filename, os.stat(command_lines_filename).st_mode | stat.S_IEXEC)
  print(f'{command_lines_filename} created')
