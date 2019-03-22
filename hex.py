#!/usr/local/bin/python3

"""
Hex 1.1.0
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

APP_VERSION = "1.1.0"


##########################################################################
# Application globals                                                    #
##########################################################################

verbose = False
linemax = 32
ignored = ["pxm", "py", "txt", "text", "html", "md", "markdown"]
prefsPath = ".config/hexpy"


##########################################################################
# Functions                                                              #
##########################################################################

def processFile(path):
    """
    Process the specified file to generate the hex output.

    Parameters
    ----------
    path : str
        The path of the file to process
    """
    
    bytes = []
    output = ""

    if verbose is True: print("Processing file: " + path)

    if os.path.exists(path):
        with open(path, 'rb') as file:
            x = 1
            byte = file.read(1)
            if verbose is True:
                # NOTE this is the syntax for printing multiple statements to one line
                print("Byte 1 read", end="\r", flush=True)
            while byte:
                bytes.append(byte)
                byte = file.read(1)
                if verbose is True:
                    x += 1
                    print(" Byte " + str(x) + " read", end="\r", flush=True)
    else:
        if verbose is True: print("File " + path + " does not exist, skipping")
        return

    if len(bytes) > 0:
        # We have bytes, so generate a hex string
        if verbose is True: print("File length: " + str(len(bytes)) + " bytes")
        linecount = 0
        for i in range (0, len(bytes)):
            byte = int.from_bytes(bytes[i], byteorder='little', signed=False)
            output += ("\\x" + integerToHexString(byte))
            linecount += 1
            if linecount == linemax:
                linecount = 0
                #output = output + "\n"
    else:
        print("File " + path + " has no bytes, skipping")
        return
        
    # Output the hex string
    if len(output) > 0: print(output)


def getFiles():
    """
    Get processable files in the current directory.

    Gather all of the files in the current working directory, checking them 
    to ensure they are not files of types that should be ignored, and passing 
    them on to 'processFile()' for individual processing.
    """
    
    filecount = 0
    pwd = os.getcwd()
    files = [file for file in os.listdir(pwd) if os.path.isfile(os.path.join(pwd, file))]
    
    for file in files:
        if checkExtension(file) is True: filecount += 1
    
    if filecount == 1:
        print("Processing 1 file found in " + pwd)
    elif filecount > 1:
        print("Processing " + str(filecount) + " files found in " + pwd)
    else:
        print("No suitable files found in " + pwd)
        return
    
    # Process the files
    for file in files:
        if checkExtension(file) is True: processFile(file)


def checkPrefs():
    """
    Load or create the script preferences file.

    The script preferences file lists file extensions that should be ignored 
    during file processing. The file's location is ~/.config/hexpy/ignored
    If the file doesn't exist, it is created with default values. 
    If it does exist, its contents are read into the list 'ignored'.
    """
    
    global ignored
    
    # Check for the present of the prefs directory and make it if it's not there
    makePrefs = False
    path = os.path.expanduser("~") + "/" + prefsPath
    if os.path.exists(path) is False: os.makedirs(path)
    
    # Check for the presence of the prefs file
    path += "/ignored"
    if os.path.exists(path) is False:
        # Create the prefs file if it's not there. Use default values
        prefsFile = open(path, 'w')
        for i in range(0, len(ignored)): prefsFile.write(ignored[i] + "\n")
        prefsFile.close()
        makePrefs = True
    else:
        # Prefs file is there, so read it into 'ignored'
        ignored = []
        with open(path, 'r') as prefsFile:
            for line in prefsFile: ignored.append(line.rstrip())

    if makePrefs is True and verbose is True: print("List of ignored file types saved") 
    return


def updateIgnored(extensions, shouldAdd):
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
    extensionsToProcess = []
    count = 0
    extList = ""
    for i in range(0, len(extensions)):
        extension = extensions[i]
        parts = extension.split(",")
        for item in parts: extensionsToProcess.append(item)
    
    # Now process the unified list of extensions, matching them against the 
    # current list, 'ignored'
    for i in range(0, len(extensionsToProcess)):
        extension = extensionsToProcess[i]
        got = extension in ignored
        if got != shouldAdd:
            if shouldAdd is True:
                # New extension, so add to 'ignored'
                ignored.append(extension)
            else:
                # Found a matching extension, so remove it from 'ignored'
                ignored.pop(ignored.index(extension))
            count += 1
            extList += (extension + ", ")
    
    if verbose is True: 
        extList = extList[0:-2]
        print((str(count) if count > 0 else "No") + " file extension" + (" " if count == 1 else "s ") + ("added" if shouldAdd else "removed") + ": " + extList) 

    
    # Replace the prefs file with the updated list
    # TODO Make this safer
    os.remove(os.path.expanduser("~") + "/" + prefsPath + "/ignored")

    # Call 'checkPrefs()' to write the amended prefs file
    checkPrefs()


def checkExtension(file):
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
    
    a = file.split(".")  
    if len(a) > 1: 
        extension = a[len(a) - 1]
    else:
        return False

    if extension in ignored: return False
    return True


def integerToHexString(value, length = 2):
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
    fs = "%0" + str(length) + "X"

    # Return hex string 
    return (fs % value)


def showHelp():
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
    bs = "  "
    for i in range(0, len(ignored)): bs += (ignored[i] + ", ")
    bs = bs[0:len(bs) - 2]
    print(bs)
    print(" ")
    return


##########################################################################
# Main entry point                                                       #
##########################################################################

if __name__ == '__main__':
    """
    The main script entry point.
    """
    
    showedVersion = False

    args = sys.argv
    if len(args) > 1:
        # Run through the args to find options only
        i = 1
        fs = ""
        c = ""
        addPrefs = []
        remPrefs = []
        done = False
        getNext = False

        while done is False:
            # We're getting the next argument as an option parameter
            if getNext is True:
                getNext = False
                a = args[i]
                if a[0] == "-":
                    # The parameter is actually an option, so bail
                    print("[ERROR] missing parameter for option: " + c + ": " + a)
                    sys.exit(0)
                if c == "-a" or c == "--add":
                    addPrefs.append(a)
                    args[i] = "?"
                elif c == "-r" or c == "--remove":
                    remPrefs.append(a)
                    args[i] = "?"
                continue
            else:
                c = sys.argv[i]

            if c == "-h" or c == "--help":
                # Print Help
                showHelp()
                sys.exit(0)
            elif c == "-v" or c == "--verbose":
                # Set verbose mode
                verbose = True
            elif c == "-a" or c == "--add" or c == "-r" or c == "--remove":
                # Get the ext arg as a parameter: further file extensions to ignore
                getNext = True
            elif c[0] == "-":
                # Mis-formed option
                print("[ERROR] unrecognized option: " + c)
                sys.exit(0)

            i += 1
            
            if i >= len(args):
                if getNext is True:
                    print("[ERROR] missing parameter for option: " + c)
                    sys.exit(0)
                done = True
        
        # If no version info shown, show welcome
        if showedVersion is False: print("\nHex " + APP_VERSION)

        # Load in the prefs
        checkPrefs()

        # Update the prefs with any added at the command line
        if len(addPrefs) > 0: updateIgnored(addPrefs, True)
        if len(remPrefs) > 0: updateIgnored(remPrefs, False)
        
        # Run through the args to find the files
        # NOTE Assume any value not already dealt with as an option parameter is a file
        files = []
        for i in range(1, len(sys.argv)):
            c = sys.argv[i]
            if c[0] != "-" and c[0] != "?": files.append(c)

        if len(files) > 0:
            # At least one file named - get them
            for i in range(0, len(files)):
                print("Getting file: " + files[i])
                processFile(files[i])
        else:
            # Get all files
            getFiles()
    else:
        # If no version info shown, show welcome
        if showedVersion is False: print("\nHex " + APP_VERSION)
        
        # Get the prefs and then get all files
        checkPrefs()
        getFiles()
    
    sys.exit(0)
