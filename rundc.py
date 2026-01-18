#!/usr/bin/env python
import argparse
import subprocess
import os
from pathlib import Path
import shlex
import shutil
import glob
import hashlib
# from input_output_parsers import *
from inputs import *
from outputs import *
import json
from defaults import default_json

# Get the current working directory
current_dir = os.getcwd()

# Define the paths relative to the current directory
runPath = '/tmp/'
exePath = current_dir

# Create the output directory if it does not exist
outputFD = os.path.join(runPath, 'outputs')
# remove the output directory if it exists
if os.path.exists(outputFD):
    shutil.rmtree(outputFD)
os.makedirs(outputFD)

def read_last_n_lines(file_path, n):
    """
    Reads the last n lines of a file.

    :param file_path: Path to the file.
    :param n: Number of lines to read from the end of the file.
    :return: List of the last n lines.
    """
    with open(file_path, 'r') as file:
        # Read all lines in the file
        lines = file.readlines()
    
    # Get the last n lines
    last_n_lines = lines[-n:]
    
    # # Print the last n lines
    # for line in last_n_lines:
    #     print(line, end='')
    
    return last_n_lines

def parse_input(input_json):
    '''parse input object into daycent consumable files'''
    dcInput = DCInput(input_json)
    dcInput.parse_schedule(runPath)
    dcInput.parse_site(runPath)
    dcInput.parse_soil(runPath)
    dcInput.parse_weather(runPath)
    dcInput.parse_events(runPath)
    dcInput.parse_extra(runPath)
    dcInput.parse_out(runPath)


def main():
    """
    This function is the main entry point of the program. It parses command line arguments using the argparse module and performs various operations based on the provided arguments. The function takes no parameters and returns nothing.
    The function expects the following command line arguments:
    -s/--schedule: Name of the schedule file without the .sch extension (required)
    -e/--ext: Name of the extended binary file without the .bin extension (optional)
    -se/--siteext: Name of the extended site file without the .100 extension (optional)
    -so/--siteout: Generate the <schedule>_ext.100 site extension (optional)
    -l/--lis: Generate .lis output file (optional)
    The function removes existing files in the runPath directory, creates log files, and builds commands based on the provided arguments. It then executes the commands using subprocess.Popen and waits for them to finish. The function also copies certain files to the outputFD directory.
    Note: The function assumes the existence of certain directories and files, such as runPath, exePath, outputFD, and the files specified in the code.
    Example usage:
    ```
    python rundc.py -s "MySchedule" -e "MyExtended" -x "MySiteExt" -l -so
    ```
    using docker:
    ```
    docker run --rm -it -v /Users/trung/DATA/Data/Ins1:/app/run nhtrung/dcai -s FIELD1 -l
    ```
    """
    parser = argparse.ArgumentParser(description="Command line arguments for DayCent")
#    parser.add_argument("-p", "--password", type=str, required=True, help="Password for running the model (contact nguyentrung1710@gmail.com)")
    parser.add_argument("-i", "--input", type=str, required=False, help="Name of the input json file")
    parser.add_argument("-s", "--schedule", type=str, required=True, help="Name of schedule file without .sch extension")
    # parser.add_argument("-b", "--bin", type=str, required=True,  help="Name of the output binary file without .bin extension")
    parser.add_argument("-e", "--ext", type=str, required=False, help="Name of the extended binary file without .bin extension")
    parser.add_argument("-se", "--siteext", type=str, required=False, help="Name of the extended site file without .100 extension")
    # T/F arguments:
    parser.add_argument("-so", "--siteout", action="store_true", help="Generate the <schedule>_ext.100 site extension ")
    parser.add_argument("-l", "--lis", action="store_true", help="Generate .lis output file")
    parser.add_argument("-o", "--output", action="store_true", help="Generate outputs.json file")
    # parser to copy executables to the run folder
    parser.add_argument("--exe", action="store_true", help="Copy executables to the run folder")
    parser.add_argument("--debug", type=str, help="Print the last n line of log_out.txt and log_error.txt for debug information")
    
    
    args = parser.parse_args()
    cmd_label = f"Run DC for {args.schedule}.sch"
    
    # Check password
#    password_encrypted = '88751005012733b261dcd1b8f7ab88d5c406ade5aec3ff4d6395e36ee5816610'
#    password = args.password.encode('utf-8')  # Convert the password to bytes
#    hash_object = hashlib.sha256(password)   # Choose a hashing algorithm (e.g., SHA-256)
#    hex_dig = hash_object.hexdigest()  
#    if str(hex_dig) != str(password_encrypted):
#        exit("Error! Invalid password")
        
        
    # Parse the input.json into consumable files:
    # read json file into a dictionary
    outfiles_dict = None
    if args.input:
        with open(os.path.join(runPath, args.input)) as json_file:
            usr_input = json.load(json_file)
            usr_input = usr_input["data"]
        parse_input(usr_input)
        outfiles_dict = usr_input["output_configs"].get("outfiles")
        if not outfiles_dict:
            outfiles_dict = default_json["output_configs"]["outfiles"]
   
    # remove existing files
    Path(os.path.join(runPath,args.schedule + ".bin")).unlink(missing_ok=True)
    Path(os.path.join(runPath, f'log_out.txt')).unlink(missing_ok=True)
    Path(os.path.join(runPath, f'log_err.txt')).unlink(missing_ok=True)
    # create log files
    log_out = open(os.path.join(runPath, 'log_out.txt'), 'a')
    log_err = open(os.path.join(runPath, 'log_err.txt'), 'a')
    log_out.write(f'Recording model run for {args.schedule}\n')
    log_out.flush()  # <-- here's something not to forget to write custom line like above
    
    # Build CMDs
    cmd = os.path.join(exePath, 'DayCent')
    cmd += ' -s ' + args.schedule + ' -n ' + args.schedule
    if args.ext and args.siteext:
        raise ValueError("Both --ext and --siteext cannot be provided")
    if args.ext:
        cmd += ' -e ' + args.ext
        cmd_label += f" with {args.ext}.bin"
    if args.siteext:
        cmd += ' -x ' + args.siteext
        cmd_label += f" with {args.siteext}.100"
    if args.siteout:
        Path(os.path.join(runPath,args.schedule + '_ext.100')).unlink(missing_ok=True)
        cmd += ' -c ' + args.schedule + '_ext'
        cmd_label += f" | Saving extended data to {args.schedule}_ext.100"
      
    os.chdir(runPath)
    print(cmd_label)
    subprocess.Popen(shlex.split(cmd), stdout=log_out, stderr=log_err, shell=False, cwd=runPath).wait()
    
    if args.lis:
        lis_path = os.path.join(runPath, args.schedule + '.lis')
        Path(lis_path).unlink(missing_ok=True)
        lis_exe = os.path.join(exePath, 'DCList ')
        cmd_list = lis_exe + args.schedule + ' ' + args.schedule + ' outvars.txt'
        print(f"Run List for {args.schedule}.bin")
        subprocess.Popen(shlex.split(cmd_list), stdout=log_out, stderr=log_err, shell=False, cwd=runPath).wait()
        
        # convert lis to csv
        df_lis = pd.read_csv(lis_path, delimiter=r"\s+").dropna(axis=0, how='all')  #  skiprows= 1, header=0, use delimiter = r"\s+" is for white space
        df_lis.to_csv(os.path.join(runPath, 'aggregated_outputs.csv'), index=False)
    
    log_out.close()
    log_err.close()
    
    # Copy *.csv files and *.lis *.bin files to OUTPUTS/
    file_list = ['{}.bin', '{}_ext.100','log_err.txt', 'log_out.txt'] # '{}.lis'
    for file in file_list:
        src_path = os.path.join(runPath, file.format(args.schedule))
        if os.path.exists(src_path):
            base = os.path.basename(src_path)
            dst_path = os.path.join(outputFD, base)
            shutil.move(src_path, dst_path)
    
    for f in os.listdir(runPath):
        if f.endswith('.csv'):
            shutil.move(os.path.join(runPath, f), os.path.join(outputFD, f))
            
    if args.exe:
        print("Copying executables to the output folder")
        shutil.copyfile(os.path.join(exePath,'DayCent'), os.path.join(outputFD, 'DayCent'))
        shutil.copyfile(os.path.join(exePath,'DCList'), os.path.join(outputFD, 'DCList'))
        
    if args.output:
        print("Generating outputs.json")
        output_json = parse_output(output_path=outputFD, outfiles_dict=outfiles_dict)
        with open(os.path.join(outputFD, 'outputs.json'), 'w') as outfile:
            json.dump(output_json, outfile, indent=2)
            
    if args.debug:
        n_out = read_last_n_lines(os.path.join(outputFD, 'log_out.txt'), int(args.debug))
        n_error = read_last_n_lines(os.path.join(outputFD, 'log_err.txt'), int(args.debug))
        
        print(f"************ Debug information ************")
        print(f"Last {args.debug} lines of log_out.txt")
        # Print the last n lines
        for line in n_out:
            print(line, end='')
        print(f"--------------------")
        print(f"Last {args.debug} lines of log_err.txt")
        # Print the last n lines
        for line in n_error:
            print(line, end='')
        print(f"******************************************")

if __name__ == "__main__":
    # run: python rundc.py -s "MySchedule" -e "MyExtended" -x "MySiteExt" -l -so
    main()
