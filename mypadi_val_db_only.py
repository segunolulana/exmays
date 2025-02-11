import os
import csv
import random
import re
import argparse
import logging
import subprocess
import snoop
from icecream import ic
from random import Random


"""
Requirements: pip install icecream snoop
Requirements: brew install harelba/q/q
Uses https://harelba.github.io/q/#installation to query sql files
In mac, to generate tables in pdf. First open csv doc in Numbers then print to pdf
"""


@snoop()
def main(args):
    excludeds = []
    try:
        with open(os.path.join(os.path.dirname(__file__), "excluded_numbers.txt"), "r") as ef:
            doc = ef.read()
        excludeds = doc.splitlines()
    except FileNotFoundError:
        print("No excluded numbers")
    exmaydb = f"{os.path.join(os.path.dirname(__file__), 'docs.seg', 'ExMay02','Ex-Mays2002OnlineDatabase-Sheet1.csv')}"
    command = (
        "q -H -d , \"select a.[Phone number], a.[Phone number 2], a.[First Name], a.[Maiden Name], a.[Surname], a.[Student Number], 'Whatsapp', a.[WhatsApp No] from "
        + f"{exmaydb}"
        + f" a where a.Timestamp = (select max(a1.Timestamp) from {exmaydb} a1 where a1.[Student Number] = a.[Student Number]) and (a.Gender = 'Female'"
        ")\" -C read"
    )
    output = subprocess.check_output(command, shell=True).decode("utf-8")
    # print(output)
    ladies = output.splitlines()
    new_ladies = []
    for i in ladies:
        # if not re.search('[a-zA-Z]{2}', i) or any(line in i for line in lines):
        if any(excluded[-10:] in i for excluded in excludeds):
            continue
        new_ladies.append(i)
    ladies = new_ladies
    len_ladies = len(ladies)
    ic(len_ladies)
    random.Random("2025-02-11").shuffle(ladies)
    ic(ladies)

    command = (
        "q -H -d , \"select a.[Phone number], a.[Phone number 2], a.[First Name], a.[Maiden Name], a.[Surname], a.[Student Number], 'Whatsapp', a.[WhatsApp No] from "
        + f"{exmaydb}"
        + f" a where a.Timestamp = (select max(a1.Timestamp) from {exmaydb} a1 where a1.[Student Number] = a.[Student Number]) and (a.Gender = 'Male'"
        ")\" -C read"
    )
    output = subprocess.check_output(command, shell=True).decode("utf-8")
    # print(output)
    men = output.splitlines()
    ic(len(men))
    new_men = []
    for i in men:
        # if not re.search('[a-zA-Z]{2}', i) or any(line in i for line in lines):
        if any(excluded[-10:] in i for excluded in excludeds):
            continue
        new_men.append(i)
    men = new_men
    len_men = len(men)
    ic(len_men)
    random.Random("2025-02-11").shuffle(men)
    ic(men)

    # Pair an element of ladies list with one of men list. Then the outstanding unpaired elements of men should be paired with another one of men with no repeated elements

    i = 0
    j = 1
    print("No;Gender;A;B")
    while i < len_ladies:
        args.debug and ic(i)
        print(f"{j};\"Mixed\";\"{men[i]}\";\"{ladies[i]}\"")
        i += 1
        j += 1
    while i < len_men:
        args.debug and ic(i)
        if j == len_men - len_ladies - 1 and (len_men - len_ladies) % 2 == 1:
            print(f"{j};\"Same\";\"{men[i]}\";\"Also with {men[0]}!\"")
        else:
            print(f"{j};\"Same\";\"{men[i]}\";\"{men[i + 1]}\"")
        i += 2
        j += 1


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true", help="Debug mode")
    parser.add_argument("-s", "--subset", action="store_true", help="Get just subset to test")
    parser.add_argument("--sn", dest="snoop", action="store_true", help="Use Snooper to trace")
    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(
            format="%(asctime)s : {%(pathname)s:%(lineno)d} : %(levelname)s : %(message)s",
            level=logging.DEBUG,
        )
    else:
        logging.basicConfig(format="%(asctime)s : %(levelname)s : %(message)s", level=logging.INFO)
    if args.snoop:
        snoop.install(enabled=True)
    else:
        snoop.install(enabled=False)
    return args


if __name__ == "__main__":
    main_args = parse_arguments()
    main(main_args)
