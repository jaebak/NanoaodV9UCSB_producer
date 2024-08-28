#!/usr/bin/env python
# The ./jobscript_check.py should return 'success' or 'fail' or 'to_submit' for a job_log_string
# The input is given as queue_system.compress_string(job_log_string)
# Example command
#./check_nanoaod_entries.py 789ced95dd6bdb3010c0df0bfd1f44618fd687edd84e460649dcb2747553926cdd304628b256bbb52563c959f3df0f27694220ebc7c65ec6eec1a0d3f977ba3bdd69d64830e1067880043d97f4080637e11cd898747b60da4899cb3b70af16c0f71c1b2809b82aabc6080b5b1e2c14670518a9b264322d7229401f40c4376b9ae6cb3c1535d41980480bc34b2de472b3e4aa5a51a6520dab15b02cd598aa3174c1b4a0153359ff0ca2b3bdbeccd3addac6c447256ff772d96e6dd4481b550b5472346de4787cc18a82f8d74caac1245c7650f8ed52183d57575734b23a987e9c5b3e368a604ce78d14a39b0e25ce5c7cb14a96ded5accaa2abc8aa5626cb5980ae07d793c1249c8d2374f3b9f54f893da86a1b9380b62ec86523459b2f4ab0fd95967c6d530b56e4dae49c2e7d6b49908b31c6a8eb92c0713ddf1a75ddd0c243d7b5869e7f619d3be79e1f627b180c3ab056ca9cbd07b7aa7e68939fe6b5e046d52bd0072853a5d0e87ef19097884956ac74aed7c90c99615a9893782cbfab041ca9410fcc0cab0dd8a852ba358971f2ec4f5b65ef7f0ddf5cc3a7bc8ea2d9ec16fc601a686180510049619051d5f172aecd375f4a30b529216d8a78469e80b793e9271a8ea707cc17afc6694cbc6888fc0e2476344c6260937749dcdfc907f03a496202dd4e271a229d00701a3bf601d5b50fa8fd573a48621b12c7d951dde080ea39bfa23ecb6fa99ee7efa89e7b400d3a2f538f38486207e2f50137d42d700f2618bf09fc242d98387f836bc320e86ec1fb7edf37f07ed8ef1afeb14e7905da9bdc438897da7aac53ebae500b56402e6a097986feb9a60510a1ed80faa3d3537a2c2194fe7e2494ae43a1f4d5b13c3bd7cf65fad6a7e02297b9ce447af213599e6c96 789c7d904f4fe33010c5bf4a954b2eb8b6d3b4690f39a404b445fd83a0a05d5568e4262e351bdb913da9d46f8f5c08ab1512b7796f9ee68d7e84d80edb0e612fbc8456e0318f86341a10520b145e221c54233d2873b097d1082df3e8cd5be3294a8fa02bf81e1d8640b85259ad85a9c1574eb5186e57b63d83b0b51fb6e79050afc63a097fe5d9e7d12efea136be1ac4ffdf0bce9bdd83aafbc9c98374d254b237d029d1f85e7914d8f9f82514ffd379e4bbbd5688b20e8b4f225ad59f4012c633aaabcbb726ac3e6cead13a4975451f3ab358dc8aa6e1d95a185b6ccad398967fee24faad5d2e6145c60c7e6d49c6d072c660db19797d3f063edaca67a245fdea447b5c2d57a43de35189295d17eb4db1291f172b7aff14fa812745eb12c6a7102af85d6764c2f80c384b7e83ae2e192745a33caa0a4e1939719a32c6189da57c3a4a2719b99ea52561f33425f349764b6e463793ac64c97c5a8c87ce5aeca9a83a8fb2c928e9f507c33cdaede260c75703f6f285f08b781e711ebd0372efc242
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

def check_entries(job_argument_string):
  #try:
    print(job_argument_string)
    args = get_args(['dataset_files_info_filename', 'command'], job_argument_string)
    args_command = get_args_command(args['command'])

    print(args)
    print(args_command)
    file_path = get_file_path(args_command['output_path'], "", args_command['input_path'])
    if not os.path.isfile(file_path): 
      # Wait for file to appear on raid
      file_exists = False
      for iWait in range(10):
        print('iWait: '+str(iWait)+'/10 Waiting 10 seconds for file to appear')
        time.sleep(10)
        if os.path.isfile(file_path):
          file_exists = True
          break
      if not file_exists:
        return '[For queue_system] fail: no file named '+file_path

    root_file = ROOT.TFile.Open(file_path)
    if not root_file: return '[For queue_system] fail: Failed in opening '+file_path
    root_tree = root_file.Get('Events')
    root_number_entries = root_tree.GetEntries()

    #print(args['dataset_files_info_filename'][1:-1])
    #datasets_files_info[dataset][filename] = {'number_events':number_events}
    dataset_files_info = nested_dict.load_json_file_py3(args['dataset_files_info_filename'], False)
    path_to_keys_dataset_files_info = datasets.get_path_to_keys_dataset_files_info(dataset_files_info)
    keys = path_to_keys_dataset_files_info[args_command['input_path']]
    #print(keys)
    #print(nested_dict.get_item_nested_dict(dataset_files_info,keys))
    dataset_number_entries = nested_dict.get_item_nested_dict(dataset_files_info,keys)['number_events']

    #print(root_number_entries)
    #print(dataset_number_entries)
    if root_number_entries == dataset_number_entries:
      return '[For queue_system] success'
    else:
      return '[For queue_system] fail: root_number_entries: '+str(root_number_entries)+' and dataset_number_entries: '+str(dataset_number_entries)+' do not match'
  #except:
  #  return '[For queue_system] fail: exception occurred in check_entries'
  

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
