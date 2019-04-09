#!/usr/local/bin/python3

"""
Hex 1.1.1
=========

Copyright 2019, Tony Smith (@smittytone)
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

APP_VERSION = "1.1.1"


##########################################################################
# Application globals                                                    #
##########################################################################

verbose = False
line_max = 32
ignored = ["pxm", "py", "txt", "text", "html", "md", "markdown"]
prefs_path = ".config/hexpy"


##########################################################################
# Functions                                                              #
##########################################################################

def process_file(path):
    """
    Process the specified file to generate the hex output.

    Parameters
    ----------
    path : str
        The path of the file to process
    """

    file_bytes = []
    output = ""

    if verbose is True: print("Processing file: " + path)

    if os.path.exists(path):
        with open(path, 'rb') as file:
            byte_count = 1
            byte = file.read(1)
            if verbose is True:
                # NOTE this is the syntax for printing multiple statements to one line
                print("Byte 1 read", end="\r", flush=True)
            while byte:
                file_bytes.append(byte)
                byte = file.read(1)
                if verbose is True:
                    byte_count += 1
                    print(" Byte " + str(byte_count) + " read", end="\r", flush=True)
    else:
        if verbose is True: print("File " + path + " does not exist, skipping")
        return

    if file_bytes:
        # We have bytes, so generate a hex string
        if verbose is True: print("File length: " + str(len(file_bytes)) + " bytes")
        line_count = 0
        for byte in file_bytes:
            byte_value = int.from_bytes(byte, byteorder='little', signed=False)
            output += ("\\x" + int_to_hex_str(byte_value))
            line_count += 1
            if line_count == line_max:
                line_count = 0
                #output = output + "\n"
    else:
        print("File " + path + " has no bytes, skipping")
        return

    # Output the hex string
    if output: print(output)


def get_files():
    """
    Get processable files in the current directory.

    Gather all of the files in the current working directory, checking them
    to ensure they are not files of types that should be ignored, and passing
    them on to 'process_file()' for individual processing.
    """

    file_count = 0
    pwd = os.getcwd()
    found_files = [file for file in os.listdir(pwd) if os.path.isfile(os.path.join(pwd, file))]

    for file in found_files:
        if check_extension(file) is True: file_count += 1

    if file_count == 1:
        print("Processing 1 file found in " + pwd)
    elif file_count > 1:
        print("Processing " + str(file_count) + " files found in " + pwd)
    else:
        print("No suitable files found in " + pwd)
        return

    # Process the files
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

    # Check for the present of the prefs directory and make it if it's not there
    make_prefs = False
    path = os.path.expanduser("~") + "/" + prefs_path
    if os.path.exists(path) is False: os.makedirs(path)

    # Check for the presence of the prefs file
    path += "/ignored"
    if os.path.exists(path) is False:
        # Create the prefs file if it's not there. Use default values
        prefs_file = open(path, 'w')
        for item in ignored: prefs_file.write(item + "\n")
        prefs_file.close()
        make_prefs = True
    else:
        # Prefs file is there, so read it into 'ignored'
        ignored = []
        with open(path, 'r') as prefs_file:
            for line in prefs_file: ignored.append(line.rstrip())

    if make_prefs is True and verbose is True: print("List of ignored file types saved")


def update_ignored(extensions, should_add):
    """
    Add/remove one or more file extensions to/from the list of those to be ignored during file
    processing.

    Parameters
    ----------
    extensions : str or list
        The extensions to be added/removed from the exclusion list
    shouldAdd : boolean
        Should the extensions be added or removed?
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
        print((str(count) if count > 0 else "No") + " file extension" + (" " if count == 1 else "s ") + ("added" if should_add else "removed") + ": " + extension_list)


    # Replace the prefs file with the updated list
    # TODO Make this safer
    os.remove(os.path.expanduser("~") + "/" + prefs_path + "/ignored")

    # Call 'check_prefs()' to write the amended prefs file
    check_prefs()


def check_extension(file):
    """
    Check whether a specified file has an extension that is excluded.

    Parameters
    ----------
    file : str
        The path of the file

    Returns
    -------
    bool
        Whether the file should be processed (True) or ignored (False)
    """

    extension = ""

    # Reject hidden files
    if file[0] == ".": return False

    parts = file.split(".")
    if len(parts) > 1:
        extension = parts[len(parts) - 1]
    else:
        return False

    if extension in ignored: return False
    return True


def int_to_hex_str(value, length=2):
    """
    Convert an integer to a hex string.

    Parameters
    ----------
    value : int
        The value to be converted
    length : bool
        The number of characters of the output string. Default: 2
    """

    # Make sure 'length' is of even length
    if length % 2 != 0: length += 1

    # Generate the format string
    format_string = "%0" + str(length) + "X"

    # Return hex string
    return format_string % value


def show_help():
    """
    Display a help message. Triggered by the -h switch.
    """

    print("\nHex " + APP_VERSION)
    print("Place one or more files in this directory")
    print(" ")
    print("Options:")
    print("  -a / --add <file extension>    - Add a file extension to the list of those that Hex will ignore,")
    print("                                   or an unspaced list of comma-separated extensions, eg. 'pdf,rtf'")
    print("  -r / --remove <file extension> - Remove a file extension from the list of those that Hex will ignore,")
    print("                                   or an unspaced list of comma-separated extensions, eg. 'pdf,rtf'")
    print("  -v / --verbose                 - Display verbose output")
    print("  -h / --help                    - Display help information")
    print(" ")
    print("Ignored file types:")
    ext_types = "  "
    for item in ignored: ext_types += (item + ", ")
    ext_types = ext_types[0:len(ext_types) - 2]
    print(ext_types)
    print(" ")


##########################################################################
# Main entry point                                                       #
##########################################################################

if __name__ == '__main__':

    did_show_version = False
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
                    print("[ERROR] missing parameter for option: " + cmd_arg + ": " + value_arg)
                    sys.exit(0)
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
                print("[ERROR] unrecognized option: " + cmd_arg)
                sys.exit(0)

            i += 1

            if i >= len(args):
                if get_next_arg is True:
                    print("[ERROR] missing parameter for option: " + cmd_arg)
                    sys.exit(0)
                done = True

        # If no version info shown, show welcome
        if did_show_version is False: print("\nHex " + APP_VERSION)

        # Load in the prefs
        check_prefs()

        # Update the prefs with any added at the command line
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
                print("Getting file: " + arg_file)
                process_file(arg_file)
        else:
            # Get all files
            get_files()
    else:
        # If no version info shown, show welcome
        if did_show_version is False: print("\nHex " + APP_VERSION)

        # Get the prefs and then get all files
        check_prefs()
        get_files()

    sys.exit(0)
