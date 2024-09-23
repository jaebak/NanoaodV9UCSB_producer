#!/usr/bin/env python3
# The ./jobscript_check.py should return 'success' or 'fail' or 'to_submit' for a job_log_string
# The input is given as queue_system.compress_string(job_log_string)
# Example command
# ./scripts/check_nanoaod_entries.py 789cad51cb4ec33010bcf72bf6075c27210f253708482da20551ca25aa568ebd550dad1dad9348fc3d0a54e2d2deb8edec687646b3cdd2edfd0eb43f9d943368ec680d3154b0e915f7f08b0d9ef926dacd9a6b8a7a602637699874eff9ab02e943e7fd51ea53104320961f8a5af529d7ca79e5cd7bb9ad3777d8b1378326be7efabca980078741b3edfa201fa95fbc21be0e2e89e2bc465c2c5f56b87d9a10aeacb3b7cff7638293d734fd7825624c10a3289a870308e16824d70788a3b848b37826038fb24d4997b9694512e77b9196a5126d91b5c2a8f82629b24c5359ccc3a182a37504d9ff86aa60ed210cfa007b7b24f0fc57e7f57a1e9cb9f4a96f1567a073 789c558f3d4fc3301086ff4ae5a593e324cd8732648032144401016541e864c717d5a5b12b9f9305f1df9153b512dbddfbe8de47c7b99641120630b677d09b235a3960cb84a3937347d10dc447422f0e1295fc164fd23ae9f447b35bbfddc2c93b3d769192b324ec194e33cc9318b205e79d1b066975cbfc68813a6f4e81c40386cd3bc0eb68f334abd6009bfb972dec1ee3065b63cdcdf3dd9443f4c5e95cc9a71c204dd384f60bce2d4e68032db234ab8b328baa8353404186915a46a31a4c08a82f2078238fd4b2cf655554ab2249215d7efd87e05192b32dfbf9bd00a3d106d31bf42dbbde4538f7131967e1fae1ec9fbd978c842ab06b2aad789e553d2f9a467255978a6b99adf2ba2c3b6cea84f6ec0f27da83af
import sys
import queue_system
import argparse
import nested_dict
import ROOT
import shlex
import os
import time
import re

def get_args(keys, job_argument_string):
  parser = argparse.ArgumentParser()
  for key in keys:
    parser.add_argument('--'+key)
  args, unknown_args = parser.parse_known_args(shlex.split(job_argument_string))
  return vars(args)

def get_args_command(job_argument_string):
  parser = argparse.ArgumentParser()
  parser.add_argument('base_command')
  parser.add_argument('input_path')
  parser.add_argument('output_path')
  args, unknown_args = parser.parse_known_args(shlex.split(job_argument_string))
  return vars(args)

def get_file_path(base_path, mid_path, input_path):
  input_split = input_path.split('/')
  return base_path+'/'+mid_path+'/'+input_split[4]+'__'+input_split[3]+'__'+input_split[6]+'__'+input_split[7]+'__'+input_split[8]


if __name__ == "__main__":
  ignore_error = False

  job_log_string = queue_system.decompress_string(sys.argv[1])
  job_argument_string = queue_system.decompress_string(sys.argv[2])

  #print(job_log_string)
  print(job_argument_string)
  # args = {'dataset_info_filename':, 'command':}
  args = get_args(['dataset_info_filename', 'command'], job_argument_string)
  command_args = get_args(['nevents'], args['command'])
  command = args['command'].split()[0]
  #print(args)

  # Untar file
  if os.path.isfile(f'{os.path.basename(command)}.tar.gz'):
    print(f'Untaring {os.path.basename(command)}.tar.gz')
    os.system(f'tar -zxvf {os.path.basename(command)}.tar.gz')
    os.system(f'rm -f {os.path.basename(command)}.tar.gz')

  # Find fileout in command file
  nanoaod_file_path = ''
  with open(command) as command_file:
    for line in command_file:
      if 'fileout' not in line: continue
      nanoaod_file_path = re.findall('--fileout file:(.*?root)', line)[0]
  # Find nevent in root NanoAOD
  root_file = ROOT.TFile.Open(nanoaod_file_path)
  if not root_file: 
    print ('[For queue_system] fail: Failed in opening '+nanoaod_file_path)
    sys.exit()
  root_tree = root_file.Get('Events')
  root_number_entries = root_tree.GetEntries()
  print(root_number_entries)
  # Find nevent command argument that is from json
  json_number_entries = int(command_args['nevents'])
  # Compare nevents
  if root_number_entries != json_number_entries:
    print('[For queue_system] fail: Number of events in root '+str(root_number_entries)+' and das '+str(json_number_entries)+' differ')
  else:
    print('[For queue_system] success')
