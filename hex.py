#!/usr/local/bin/python3

"""
Hex 1.2.0
=========

Copyright 2020, Tony Smith (@smittytone)
License: MIT (terms attached to this repo)

About Hex
---------

This script reads in a file and outputs it as a hex string formatted
for use in, for example, Electric Imp Squirrel applications.

Examples of the script's use can be found in the following repos:

- https://github.com/smittytone/BigClock
- https://github.com/smittytone/BigClock
- https://github.com/smittytone/MatrixClock
- https://github.com/smittytone/Clock

"""


##########################################################################
# Program library imports                                                #
##########################################################################

import os
import sys


##########################################################################
# Application-specific constants                                         #
##########################################################################

APP_VERSION = "1.2.0"


##########################################################################
# Application globals                                                    #
##########################################################################

verbose = False
ignored = ["pxm", "py", "txt", "text", "html", "md", "markdown"]
prefs_path = ".config/hexpy"


##########################################################################
# Functions                                                              #
##########################################################################

def process_file(path):
    """
    Process the specified file to generate the hex output.

    Args:
        path (str): The path of the file to process
    """

    file_bytes = []
    output = ""

    write_info("Processing file: " + path)
    if os.path.exists(path):
        # Get the file's bytes
        with open(path, 'rb') as file:
            byte = file.read(1)
            while byte:
                file_bytes.append(byte)
                byte = file.read(1)
    else:
        write_info("File " + path + " cannot be read -- skipping")
        return

    if file_bytes:
        # We have bytes, so generate a hex string
        write_info("File length: " + str(len(file_bytes)) + " bytes")
        for byte in file_bytes:
            byte_value = int.from_bytes(byte, byteorder='little', signed=False)
            output += ("\\x" + int_to_hex_str(byte_value))
    else:
        write_info("File " + path + " has no bytes -- skipping")
        return

    # Output the hex string to stdout
    if output: print(output, file=sys.stdout)


def get_files():
    """
    Get processable files in the current directory.

    Gather all of the files in the current working directory, checking them
    to ensure they are not files of types that should be ignored, and passing
    them on to 'process_file()' for individual processing.
    """

    # Get the directory's files
    file_count = 0
    pwd = os.getcwd()
    write_info("Processing files in " + pwd)
    found_files = [file for file in os.listdir(pwd) if os.path.isfile(os.path.join(pwd, file))]

    # Tally files
    for file in found_files:
        if check_extension(file) is True: file_count += 1

    # Display info based on file count
    if file_count == 1:
        write_info("Processing 1 file found in " + pwd)
    elif file_count > 1:
        write_info("Processing " + str(file_count) + " files found in " + pwd)
    else:
        write_info("No suitable files found in " + pwd)
        return

    # Process the (valid) files
    for file in found_files:
        if check_extension(file) is True: process_file(file)


def check_prefs():
    """
    Load or create the script preferences file.

    The script preferences file lists file extensions that should be ignored
    during file processing. The file's location is ~/.config/hexpy/ignored
    If the file doesn't exist, it is created with default values.
    If it does exist, its contents are read into the list 'ignored'.
    """

    global ignored

    # Check for the presence of the preferences directory
    # and create it if it's not there
    make_prefs = False
    path = os.path.expanduser("~") + "/" + prefs_path
    if os.path.exists(path) is False: os.makedirs(path)

    # Check for the presence of the preferences file
    path += "/ignored"
    if os.path.exists(path) is False:
        # Create the preferences file with default values
        prefs_file = open(path, 'w')
        for item in ignored: prefs_file.write(item + "\n")
        prefs_file.close()
        make_prefs = True
    else:
        # Preferences file is there, so read it into 'ignored'
        ignored = []
        with open(path, 'r') as prefs_file:
            for line in prefs_file: ignored.append(line.rstrip())

    if make_prefs is True: write_info("List of ignored file types saved")


def update_ignored(extensions, should_add):
    """
    Add/remove one or more file extensions to/from the list of those to be ignored during file
    processing.

    Args:
        extensions (str/list): The extensions to be added/removed from the exclusion list
        should_add (bool):     Should the extensions be added or removed?
    """

    # Generate a full list of extensions to remove
    # The list may contain multiple extensions, eg. ["nut", "rtf,pdf", "jpeg"],
    # so we need to generate a unified list, ie. ["nut", "rtf", "pdf", "jpeg"]
    extensions_to_process = []
    count = 0
    extension_list = ""
    for extension in extensions:
        parts = extension.split(",")
        for item in parts: extensions_to_process.append(item)

    # Now process the unified list of extensions, matching them against the
    # current list, 'ignored'
    for extension in extensions_to_process:
        got = extension in ignored
        if got != should_add:
            if should_add is True:
                # New extension, so add to 'ignored'
                ignored.append(extension)
            else:
                # Found a matching extension, so remove it from 'ignored'
                ignored.pop(ignored.index(extension))
            count += 1
            extension_list += (extension + ", ")

    if verbose is True:
        extension_list = extension_list[0:-2]
        write_info((str(count) if count > 0 else "No") + " file extension" + (" " if count == 1 else "s ") + ("added" if should_add else "removed") + ": " + extension_list)


    # Replace the prefs file with the updated list
    # TODO Make this safer
    os.remove(os.path.expanduser("~") + "/" + prefs_path + "/ignored")

    # Call 'check_prefs()' to write the amended prefs file
    check_prefs()


def check_extension(file_path):
    """
    Check whether a specified file has an extension that is excluded.

    Args:
        file_path (str): The path of the file

    Returns:
        bool: Whether the file should be processed (True) or ignored (False)
    """

    extension = ""

    # Reject hidden files
    if file_path[0] == ".": return False

    parts = file_path.split(".")
    if len(parts) > 1:
        extension = parts[len(parts) - 1]
    else:
        return False

    if extension in ignored: return False
    return True


def int_to_hex_str(value, length=2):
    """
    Convert an integer to a hex string.

    Args:
        value  (int): The value to be converted
        length (int): The number of characters of the output string. Default: 2
    """

    # Make sure 'length' is of even length
    if length % 2 != 0: length += 1

    # Generate the format string
    format_string = "%0" + str(length) + "X"

    # Return hex string
    return format_string % value


def write_info(text):
    """
    Write a message to stderr, but only if permitted

    Args:
        text (str): The line to be written.
    """

    if verbose is True: write_to_stderr(text)


def report_error_and_exit(msg, code=1):
    """
    Write an error message to stderr then quit.

    Args:
        msg  (str): The value to be converted
        code (int): The exit code. Default: 1
    """

    write_to_stderr("Error -- " + msg)
    sys.exit(code)


def write_to_stderr(line):
    """
    Write any message to stderr.

    Args:
        line (str): The line to be written.
    """

    print(line, file=sys.stderr)


def show_help():
    """
    Display a help message. Triggered by the -h switch.
    """

    write_to_stderr("Hex " + APP_VERSION)
    write_to_stderr("Convert binary files to Squirrel hex string literals\n")
    write_to_stderr("Usage:")
    write_to_stderr("  hex.py [-a] [-r] [-v] [-h] file_1 file_2 ... file_n\n")
    write_to_stderr("Options:")
    write_to_stderr("  -a / --add <file extension>    - Add a file extension to the list of those that Hex will ignore,")
    write_to_stderr("                                   or an unspaced list of comma-separated extensions, eg. 'pdf,rtf'")
    write_to_stderr("  -r / --remove <file extension> - Remove a file extension from the list of those that Hex will ignore,")
    write_to_stderr("                                   or an unspaced list of comma-separated extensions, eg. 'pdf,rtf'")
    write_to_stderr("  -v / --verbose                 - Display verbose output")
    write_to_stderr("  -h / --help                    - Display help information")
    write_to_stderr(" ")
    write_to_stderr("Ignored file types:")
    ext_types = "  "
    for item in ignored: ext_types += (item + ", ")
    ext_types = ext_types[0:len(ext_types) - 2]
    write_to_stderr(ext_types)
    write_to_stderr(" ")


##########################################################################
# Main entry point                                                       #
##########################################################################

if __name__ == '__main__':

    args = sys.argv

    if len(args) > 1:
        # Run through the args to find options only
        i = 1
        cmd_arg = ""
        add_prefs = []
        remove_prefs = []
        done = False
        get_next_arg = False

        while done is False:
            # We're getting the next argument as an option parameter
            if get_next_arg is True:
                get_next_arg = False
                value_arg = args[i]
                if value_arg[0] == "-":
                    # The parameter is actually an option, so bail
                    report_error_and_exit("missing parameter for option: " + cmd_arg + ": " + value_arg)
                if cmd_arg in ("-a", "--add"):
                    add_prefs.append(value_arg)
                    args[i] = "?"
                elif cmd_arg in ("-r", "--remove"):
                    remove_prefs.append(value_arg)
                    args[i] = "?"
                continue
            else:
                cmd_arg = sys.argv[i]

            if cmd_arg in ("-h", "--help"):
                # Print Help
                show_help()
                sys.exit(0)
            elif cmd_arg in ("-v", "--verbose"):
                # Set verbose mode
                verbose = True
            elif cmd_arg in ("-a", "--add", "-r", "--remove"):
                # Get the ext arg as a parameter: further file extensions to ignore
                get_next_arg = True
            elif cmd_arg[0] == "-":
                # Mis-formed option
                report_error_and_exit("unrecognized option: " + cmd_arg)

            i += 1
            if i >= len(args):
                if get_next_arg is True:
                    report_error_and_exit("missing parameter for option: " + cmd_arg)
                done = True

        # If no version info shown, show welcome
        write_info("Hex " + APP_VERSION)

        # Load in the prefs
        check_prefs()

        # Update the prefs with any added at the command line
        # TODO Check for mutually exclusive changes
        if add_prefs: update_ignored(add_prefs, True)
        if remove_prefs: update_ignored(remove_prefs, False)

        # Run through the args to find the files
        # NOTE Assume any value not already dealt with as an option parameter is a file
        arg_files = []
        for index in range(1, len(sys.argv)):
            possible_file = sys.argv[index]
            if possible_file[0] != "-" and possible_file[0] != "?": arg_files.append(possible_file)

        if arg_files:
            # At least one file named - get them
            for arg_file in arg_files:
                write_info("Getting file: " + arg_file)
                process_file(arg_file)
        else:
            # Get all files in the directory
            get_files()
    else:
        # If no version info shown, show welcome
        write_info("Hex " + APP_VERSION)

        # Get the prefs and then get all files
        check_prefs()
        get_files()

    sys.exit(0)
