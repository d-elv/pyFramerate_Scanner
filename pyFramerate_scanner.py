from pymediainfo import MediaInfo
from collections import Counter
import time
import re
import os
import io
import shutil


LOG_DIRECTORY = "\\\\10.10.52.250\\dropzone\\CTA\\08 PYTHON PROGRAMS\\05_Pyframerate_SCANNER\\LOGGED_OUTPUT"

print("""pyframerate_scanner
This program scans a folder & subfolders, if chosen, and 
prints a list of each files with their frame rates.
Also tells you the most common framerate.""")

illegal_apostrophe = re.compile(r"'")
illegal_quotes = re.compile(r'"')
ghost_file_pattern = re.compile(r'^(\.)[<>-_.,+!?£$%^&*a-zA-Z0-9]*')
accepted_file_types = [
                    '.mov', 
                    '.mxf', 
                    '.avi', 
                    '.mp4', 
                    '.wmv', 
                    '.mkv',
                    '.m4v',
                    ]
accepted_framerates = [
    '23.98',
    '24',
    '25',
    '29.97',
    '50'
]

def get_date():
    from datetime import datetime
    today = datetime.today().strftime('%Y%m%d')
    today = today[2:]
    return today


def get_root_length():
    # Gets the root length of the directory given for scanning,
    # This is later used to ensure no sub folders are scanned.
    for root, dir_path, files in os.walk(input_directory):
        root_splitter = root.split("\\")
        folder_name_for_output_file = root_splitter[-1]
        root_length = len(root_splitter)

        return root_length, folder_name_for_output_file


def format_bit_rate(bit_rate_raw):
    if bit_rate_raw < (1000 * 1000):
        bit_rate_formatted = bit_rate_raw / 1000
        bit_rate_formatted = str(bit_rate_formatted)
        bit_rate_formatted = bit_rate_formatted[:-4] + " KB/s"
    if bit_rate_raw > (1000 * 1000):
        bit_rate_formatted = bit_rate_raw / (1000 * 1000)
        bit_rate_formatted = str(bit_rate_formatted)
        bit_rate_formatted = bit_rate_formatted[:-4] + " MB/s"


def move_file(file_path, input_directory, framerate, framerate_choice):
    created_folder = None
    file_name = file_path.split("\\")[-1]
    if framerate == "23.976":
        framerate = "23.98"
    if framerate == "29.970":
        framerate = "29.97"
    # if framerate != framerate_choice:
    #     return None

    if "0" in framerate:
        framerate_string = str(framerate)
        split_framerate = framerate_string.split(".", 1)
        framerate_string = split_framerate[0]

    check_dir = input_directory + "\\" + framerate_choice
    file_destination = check_dir + "\\" + file_name
    os.chdir(input_directory)
    if os.path.isdir(check_dir):
        shutil.move(file_path, file_destination)
        pass
    else:
        print(f"Making directory a subfolder called '{framerate_choice}'")
        os.mkdir(check_dir)
        created_folder = True
        shutil.move(file_path, file_destination)
        print(f"I have moved {file_name} into this folder: {check_dir}")
    # if created_folder:
    #     print(f"Created a folder called {framerate_choice} in the scanned folder.")


def ingest_codec(bit_rate_raw):
    message = ""
    if bit_rate_raw == None:
        return bit_rate_raw
    if bit_rate_raw > 25000000:
        message = "DNxHR LB (DNx36)"
    elif bit_rate_raw > 13000000:
        message = "AVC Long GOP 25"
    elif bit_rate_raw > 6500000:
        message = "AVC Long GOP 12"
    elif bit_rate_raw > 900000:
        message = "AVC Long GOP 6"
    else:
        message = "H.264 800Kbps Proxy"
    return message


while True:
    choice = ""
    deep_scan_choice = ""
    framerate_choice = ""
    print('-'*60)
    print()
    # while True:
    #     choice = input("Would you like to perform a deep scan? (y/n): ")
    #     choice = choice.lower()
    #     if choice == "y" or choice == "n":
    #         break
    #     else:
    #         continue

    while True:
        framerate_folder = input("Would you like to move a certain framerate into a subfolder? (y/n): ")
        framerate_folder = framerate_folder.lower()
        if framerate_folder == "y" or framerate_folder == "n":
            break
        else:
            continue

    if framerate_folder == "y":
        while True:
            framerate_choice = input("What framerate would you like to move into a subfolder? ")
            if framerate_choice in accepted_framerates:
                break
            else: 
                print("Please choose from these options: ")
                for framerate in accepted_framerates:
                    print(framerate)
                continue
    
    if framerate_folder == "n":
        while True:    
            deep_scan_choice = input("Would you like to perform a deep scan? (y/n): ")
            deep_scan_choice = deep_scan_choice.lower()
            if deep_scan_choice == "y" or deep_scan_choice == "n":
                break
            else:
                continue

    input_directory = input('Please drag in a folder to scan framerates: ')

    if illegal_apostrophe.search(input_directory):
        input_directory = input_directory.replace("'","")
    if illegal_quotes.search(input_directory):
        input_directory = input_directory.replace('"',"")

    root_length, folder_name_for_output_file = get_root_length()
    os.chdir(LOG_DIRECTORY)
    with open(folder_name_for_output_file + "_framerate_scanner_output.txt", "a") as log_file:

        log_file.write(f"FOLDER NAME: {folder_name_for_output_file}\n\n")

    
    file_count = 0
    error_count = 0
    framerate_list = []
    for root, dir_path, files in os.walk(input_directory):
        for file in files:
            
            file_name, ext = os.path.splitext(file)
            ext = ext.lower()
            if ext not in accepted_file_types:
                continue

            writing_to_file_list = []
            
            current_root_split = root.split("\\")
            
            if deep_scan_choice == "n":
                if len(current_root_split) > root_length:
                    continue
            
            if ghost_file_pattern.match(file):
                continue

            file_path = os.path.join(root, file)

            try:
                file_media_info = MediaInfo.parse(file_path)
            except FileNotFoundError:
                print("Your file path is incorrect or your filename ", end="")
                print("is missing its extension, please try again. ")
                
                break
            
            for track in file_media_info.tracks:
                if track.track_type == "General":

                    file_name = track.complete_name
                    file_name = file_name.replace('\\', '/')
                    file_name = file_name.split('/')
                    file_name = file_name[-1]

                    current_file_path = track.complete_name
                    
                    file_size_raw = track.file_size

                    if track.file_size == 0 or track.file_size == None:
                        print(f"{file_name} is a corrupt file, please ", end="")
                        print(f"investigate, resupply and try scanning again.")
                        error_count += 1
                        break
                    else:
                        pass

                elif track.track_type == "Video":

                    if track.frame_rate == None:
                        framerate = track.original_framerate
                    else:
                        framerate = track.frame_rate

                    try:
                        raw_bit_rate = track.bit_rate
                    except:
                        raw_bit_rate = None
                    ingest_message = ingest_codec(raw_bit_rate)
                    framerate_list.append(framerate)
                    writing_to_file_list.append(framerate + " " + file_name)
                    print(f"{framerate} - {file_name} | {ingest_message}")

                    # writing_to_file_list.append("Bit Rate: " + str(bit_rate))
            if framerate:
                move_file(file_path, input_directory, framerate, framerate_choice)

            def write_log():
                os.chdir(LOG_DIRECTORY)
                with io.open(folder_name_for_output_file + "_framerate_scanner_output.txt", "a", encoding="utf8") as log_file:

                    for attribute in writing_to_file_list:
                        log_file.write(str(attribute))
                        log_file.write("\n")

            file_count += 1
            if file_size_raw == 0 or file_size_raw == None:
                with open(folder_name_for_output_file + "_framerate_scanner_output.txt", "a") as log_file:

                    log_file.write(file_name)
                    log_file.write(" is a corrupt file. Please resupply and rescan.\n")
            else:
                write_log()


    occurrence_count = Counter(framerate_list)
    try:
        most_common = occurrence_count.most_common(1)[0][0]
    except IndexError:
        print("An IndexError occurred. Likely because no framerates have been found.")
        time.sleep(10)
    unique_framerates = set(framerate_list)
    unique_framerates = list(unique_framerates)
    unique_framerates.sort()

    print()
    print(f"Most Common Framerate: {most_common}")
    print("Unique Framerates: ", end="")
    for framerate in unique_framerates:
        if framerate == unique_framerates[-1]:
            print(framerate)
        else:
            print(framerate, end=", ")
    print()
    with open(folder_name_for_output_file + "_framerate_scanner_output.txt", "a") as log_file:
        log_file.write("\n")
        log_file.write("Total files in selection: " + str(file_count) + "\n")
        log_file.write("Total errors in selection: " + str(error_count) + "\n")
        log_file.write("\n")

    print(f"Total files scanned in this folder: {file_count}")
    print(f"Total error files in this folder: {error_count}")
    print(f"\nYour folder's framerates have been written to a text file ", end="")
    print(f"to copy from here: {LOG_DIRECTORY}\n")