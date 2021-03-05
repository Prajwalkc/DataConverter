#!/usr/bin/python3

import os
import shutil
from pathlib import Path
 
ROOT_DIR = 'c:/workspace/amm-data-convertor/sample_data'
OUTPUT_DIR = ROOT_DIR + '/Output'

def repeat_to_length(string_to_expand, length):
    if len(string_to_expand) > length:
        return string_to_expand[0: length]
    else:
        repeat = length - len(string_to_expand)
        return string_to_expand + (string_to_expand[-1] * repeat)

def get_subject_name(first, last):
    subject_name = ""
    for f, l in zip(repeat_to_length(first, 3), repeat_to_length(last, 3)):
        if len(subject_name) <= 5:
            subject_name += l + f
    return subject_name.lower()

def is_valid_directory(directory):
    path = Path(directory)
    return path.exists() and path.is_dir()

def create_output_directory():
    # Create Output Directory
    if is_valid_directory(OUTPUT_DIR):
        output_path = os.path.join(ROOT_DIR, OUTPUT_DIR)
        shutil.rmtree(output_path) 
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(parents=True, exist_ok=True)
    print("Directory '% s' has been created successfully" % output_path)

def main():
    try:
        print("Starting Data conversion process ...")
        print('Scanning data root directory: ' + ROOT_DIR)

        if not is_valid_directory(ROOT_DIR):
            print('Data root directory does not exist: ' + ROOT_DIR)
            return
        
        # Create Output directory
        create_output_directory()

        ###### Start process to conversion ################
        for root, subdirectories, files in os.walk(ROOT_DIR, topdown=True):
            subdirectories[:] = [d for d in subdirectories if d not in OUTPUT_DIR]

            for directory in subdirectories:
                print('     > Querying sub-directories: ' + directory)

                subject_file = Path(ROOT_DIR, directory).rglob('*.sbj')
                rw3_files = Path(ROOT_DIR, directory).rglob('~*.rw3')
            
                for path in subject_file:
                    with open(path) as sbjFile:
                        sbjlines = sbjFile.readlines()

                        first_name = sbjlines[2].split("=", 1)[1].replace("\n","")
                        number = sbjlines[1].split("=", 1)[1].replace("\n","")
                        last_name = sbjlines[4].split("=", 1)[1].replace("\n","")
                        height = sbjlines[9].split("=", 1)[1]
                        weight = sbjlines[10].split('=', 1)[1]
                        age = sbjlines[11].split('=', 1)[1]
                        handicap = sbjlines[13].split('=', 1)[1]
                    print('         > first_name: ' + first_name + ' last_name: ' + last_name + ' - number: ' + number)

                subject_name = get_subject_name(first_name, last_name)

                for rw3_file in rw3_files:
                    # Define new name for convrted rw3 file
                    fn = subject_name + os.path.basename(rw3_file.name)
                    print('         > Converted file: ' + fn)
                    new_rw3_file = OUTPUT_DIR + '/' + fn.lower()

                    with open(rw3_file, 'r') as rw3PathReadFile:
                        line_data = rw3PathReadFile.read()
                        if 'Full Body 12R TPI 7-14-04' in line_data:
                            replace_projectname = line_data.replace("Full Body 12R TPI 7-14-04", "Full Body w Extra VFrames")
                            with open(new_rw3_file, 'w') as rw3PathWriteFile:
                                rw3PathWriteFile.write(replace_projectname)
                            with open(new_rw3_file, 'r') as appendFile:
                                line = appendFile.readlines()
                            with open(new_rw3_file, 'w') as writeFile:
                                line.insert(4, "[Height]\n" + height)
                                line.insert(5, "[Weight]\n" + weight)
                                line.insert(6, "[Age]\n" + age)
                                line.insert(7, "[Handicap]\n" + handicap)
                                writeFile.writelines(line)
                        else:
                            pass   
    except Exception as error:
        print('Excption raised during parsing AMM System data to Sportbox Format.' + repr(error))

# Run main method
if __name__ == '__main__':
    main()