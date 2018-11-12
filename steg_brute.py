#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from subprocess import Popen, PIPE, DEVNULL
from progress.bar import Bar
from argparse import ArgumentParser
import os
import sys


class Color:
    FAIL = '\033[91m'
    BLUE = '\033[94m'
    BLUE2 = '\033[1;36m'
    INFO = '\033[93m'
    ENDC = '\033[0m'
    GREEN = '\033[1;32m'

    
VERSION = "1.0"

SAMPLES = """
Type ./steg_brute.py -h to show help

Command line examples:

    1- Get info of file
    ./steg_brute.py -i -f <file>

    2- Extract hide info of file with password
    ./steg_brute.py -e -p <password> -f <file>

    3- Brute force attack with dictionary to
       extract hide info of file
    ./steg_brute.py -b -d <dictionary> -f <file>

    """


def check_file(file):
    return os.path.exists(file)


def check_steghide():
    try:
        Popen(['steghide', '--help'], stdout=DEVNULL, stderr=DEVNULL)
    except FileNotFoundError:
        print("Is steghide installed?")
        print("     sudo apt-get install steghide")
        print("     sudo yum install steghide")
        print("     sudo dnf install steghide")
        sys.exit()


def count_lines(fname):
    i = 1
    with open(fname, 'rb') as f:
        for i, l in enumerate(f):
            pass
    return i + 1


def steg_brute(ifile, dicc):
    nlines = count_lines(dicc)
    ofile = ifile.split('.')[0] + "_flag.txt"
    bar = Bar('Searching', max=nlines)
    print('\n')
    with open(dicc, 'r') as passFile:
        for pass_line in passFile:
            password = pass_line.strip('\n')
            results = extract_secret(ifile, password, ofile)
            if not results:
                bar.next()
            else:
                bar.finish()
                print_results(results, password, ofile)
                return
        bar.finish()
        print("Password not in list...")


def steghide(ifile, passwd):
    ofile = ifile.split('.')[0] + "_flag.txt"
    results = extract_secret(ifile, passwd, ofile)
    if not results[0]:
        print(Color.FAIL + "\n\n " + results[1] + Color.ENDC)


def extract_secret(ifile, passwd, ofile):
    r = Popen(['steghide', 'extract', '-sf', ifile, '-p', passwd, '-xf', ofile], stdout=PIPE, stderr=PIPE)
    output = r.communicate()[1].decode('utf-8')
    if "no pude extraer" not in output and "could not extract" not in output:
        return output


def print_results(results, passwd, ofile):
    print(Color.GREEN + "\n " + results + Color.ENDC)
    print("\n\n [+] " + Color.INFO +
          "Information obtained with password:" + Color.GREEN + " {}\n".format(passwd + Color.ENDC))
    if check_file(ofile):
        with open(ofile, 'r') as outfile:
            for line in outfile.readlines():
                print(line)


def arguments():
    argp = ArgumentParser(description="Steghide Brute Force Tool v" + VERSION)

    argp.add_argument('-i', '--info', dest='info', action='store_true',
                      help='Get info of file')

    argp.add_argument('-f', '--file', dest='file', required=True,
                      help='Path of file')

    argp.add_argument('-e', '--extract', dest='extract', action='store_true',
                      help='Extract hide info with password')

    argp.add_argument('-p', '--password', dest='password',
                      help='Password to extract hide info')

    argp.add_argument('-b', '--brute', dest='brute', action='store_true',
                      help='Brute force attack with dictionary')

    argp.add_argument('-d', '--dictionary', dest='dicc',
                      help='Path of dictionary to brute force attack')

    return argp.parse_args()


def main():

    check_steghide()
    args = arguments()

    if args.info and not args.extract and not args.brute:
        os.system("steghide info {}".format(args.file))

    elif args.extract and not args.info and not args.brute:
        steghide(args.file, args.password)

    elif args.brute and not args.info and not args.extract:
        if not check_file(args.dicc):
            print("No dictionary file found at {}".format(args.dicc))
        else:
            print("\n [i] " + Color.INFO + "Searching..." + Color.ENDC)
            steg_brute(args.file, args.dicc)

    else:
        print(SAMPLES)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('\n\nStopping...')
        sys.exit(0)
