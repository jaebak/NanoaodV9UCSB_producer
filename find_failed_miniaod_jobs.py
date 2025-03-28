#!/usr/bin/env python3
import argparse
import nested_dict
import subprocess
import multiprocessing
import os
import sys

def check_file(miniaod):
  command = f'crab checkfile --lfn {miniaod}'

  nTrials = 0
  while nTrials != 10:
    print(f'Running: {command}')
    try: 
      result = subprocess.run(command.split(), capture_output=True, timeout=10)
      break
    except:
      nTrials += 1
      print(f'Failed running command {nTrials} times')

  # In the case crab checkfile was not able to run
  if 'result' not in locals():
    result = subprocess.CompletedProcess(args=command.split(), returncode=-1, stdout='Failed in running crab checkfile'.encode('utf-8'))

  # Find if there is OK in the output
  #print(result.returncode)
  log = result.stdout.decode('utf-8')
  log_is_okay = False
  for line in log.split('\n'):
    #print(line)
    if 'OK' in line: log_is_okay = True
  return miniaod, log_is_okay, log

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='''Finds MiniAOD files for failed jobs.''', formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument('-i','--input_job_json', required=True, help='Name of json file for jobs', default='./auto_cl_nanoaodv9UCSB2.json')
  parser.add_argument('-o','--output_miniaods_json', help='Name of json file for scanned miniaods', default='scanned_miniaods.json')
  parser.add_argument('-p', '--print_results', action="store_true", help='Do not find, just print results')
  args = parser.parse_args()

  failed_job_miniaods = []
  n_failed_jobs = 0
  
  # Load json for jobs
  jobs_info = nested_dict.load_json_file(args.input_job_json)
  for job_info in jobs_info:
    if 'job_status' not in job_info: continue
    # Find failed jobs
    if job_info['job_status'] == 'fail':
      command_file = job_info['command'].split()[0]
      n_failed_jobs += 1

      # Find miniAOD files for failed jobs
      for line in open(command_file):
        if 'rucio download' in line:
          files = line.split()[3:] # Get rid of rucio download --ndownloader=1
          files = [name[4:] for name in files] # Get rid of cms:
          failed_job_miniaods.extend(files)

  print(f'There were {n_failed_jobs} failed jobs')
  print(f'Will check the status of {len(failed_job_miniaods)} miniAOD files')
  #failed_job_miniaods = failed_job_miniaods[:2]

  # Load already scanned miniaods
  # scanned_miniaod_info[miniaod] = [log_is_okay, log]
  scanned_miniaod_info = {}
  to_scan_files = []
  if os.path.isfile(args.output_miniaods_json):
    scanned_miniaod_info = nested_dict.load_json_file(args.output_miniaods_json)
    print(f'Have already scanned {len(scanned_miniaod_info)} files')

    # Ignore files that were scanned
    for miniaod in failed_job_miniaods:
      if miniaod not in scanned_miniaod_info: 
        to_scan_files.append(miniaod)
    failed_job_miniaods = to_scan_files
  print(f'Should check {len(failed_job_miniaods)} files')

  if not args.print_results:
    # Check files using multiple cpus
    with multiprocessing.Pool(5) as process:
      results = process.map(check_file, failed_job_miniaods)
      #print(results)

    # Save results
    for result in results:
      miniaod, log_is_okay, log = result
      scanned_miniaod_info[miniaod] = [log_is_okay, log]
    nested_dict.save_json_file(scanned_miniaod_info, args.output_miniaods_json)
      
    # Find bad logs
    n_bad_miniaods = 0
    for miniaod in scanned_miniaod_info:
      log_is_okay, log = scanned_miniaod_info[miniaod]
      if not log_is_okay: 
        print(log)
        n_bad_miniaods += 1
    print(f'There were {n_failed_jobs} failed jobs')
    print(f'Found {n_bad_miniaods} bad miniAOD files')

  else:
    # Print results
    scanned_miniaod_info = nested_dict.load_json_file(args.output_miniaods_json)
    n_bad_miniaods = 0
    for miniaod in scanned_miniaod_info:
      log_is_okay, log = scanned_miniaod_info[miniaod]
      if not log_is_okay:
        print(miniaod)
        print(scanned_miniaod_info[miniaod][1])
        n_bad_miniaods += 1

    for miniaod in scanned_miniaod_info:
      log_is_okay, log = scanned_miniaod_info[miniaod]
      if not log_is_okay:
        print(miniaod)

    print(f'There were {n_failed_jobs} failed jobs')
    print(f'Found {n_bad_miniaods} bad miniAOD files')
