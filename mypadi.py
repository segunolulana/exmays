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
2023-03-06 Used https://chrome.google.com/webstore/detail/contact-download-for-what/gbbpfmmjcaakdmhlnjfdlhlehoeikbic to download Whatsapp contacts from Whatsapp Web in Chrome
2025-02-10 Used https://chromewebstore.google.com/detail/wappmaster-contacts-extra/moeihekkmkijlgmmablmbkjeojmkaagh?hl=en to download Whatsapp contacts from Whatsapp Web in Chrome but it doesn't usually give results for unsaved contacts
TODO Add myself manually since downloaded contacts doesn't include person logged into Whatsapp?
Manually removed group name from exported Whatsapp to ease merging of Main and Quiet groups
2023-03-04 Also manually sort Whatsapp contact list
2023-07-02 Stopped redownloading contacts from Whatsapp
2025-02-10 Resumed redownloading contacts from Whatsapp
In mac, to generate tables in pdf. First open csv doc in Numbers then print to pdf
"""


@snoop()
def main(args):
    with open(os.path.join(os.path.dirname(__file__), 'docs.seg', 'ExMay-Whatsapp-Contacts.csv')) as f:
        main_whatsapp_contacts = f.read().splitlines()[1:]
    joint_whatsapp_contacts = list(main_whatsapp_contacts)
    ic(len(main_whatsapp_contacts))
    # with open(os.path.expanduser("~/Downloads/ExMay02/ExMay02Quiet/WhatsApp All Contacts.csv")) as f:
    #     quiet_whatsapp_contacts = f.read().splitlines()[1:]
    # ic(len(quiet_whatsapp_contacts))
    # joint_whatsapp_contacts = sorted(set(joint_whatsapp_contacts + quiet_whatsapp_contacts))
    joint_whatsapp_contacts = sorted(set(joint_whatsapp_contacts))
    whatsapp_contacts_reader = csv.reader(
        joint_whatsapp_contacts,
        delimiter=',',
    )
    final_contacts = []
    no_names = []

    # First run to cache db for speed
    phone = "08000"
    command = (
        "q -H -d , \"select a.[Phone number], a.[Other Names], a.[Surname] from "
        + f"{os.path.join(os.path.dirname(__file__), 'docs.seg', 'NumbersFromBallot.csv')}"
        + " a where instr('{phone}', a.[Phone number]) > 0\" -C readwrite"
    )
    output = subprocess.check_output(command, shell=True).decode("utf-8")
    print(output)
    command = (
        "q -H -d , \"select a.[Phone number], a.[Phone number 2], a.[First Name], a.[Maiden Name], a.[Surname] from "
        + os.path.join(os.path.dirname(__file__), 'docs.seg', 'ExMay02', 'Ex-Mays2002OnlineDatabase-Sheet1.csv')
        + " a where instr('{phone}', substr(a.[Phone number], length(a.[Phone number]) - 9)) > 0 or instr('{phone}', substr(a.[Phone number 2], length(a.[Phone number 2]) - 9)) > 0\" -C readwrite"
    )
    output = subprocess.check_output(command, shell=True).decode("utf-8")
    print(output)
    whatsapp_contacts = list(whatsapp_contacts_reader)
    len_whatsapp_contacts = len(whatsapp_contacts)
    ic(whatsapp_contacts)

    lines = []
    try:
        with open(os.path.join(os.path.dirname(__file__), "excluded_numbers.txt"), "r") as ef:
            doc = ef.read()
        lines = doc.split("\n")
    except FileNotFoundError:
        print("No excluded numbers")
    for index, row in enumerate(whatsapp_contacts):
        if args.subset and index < len_whatsapp_contacts - 15:
            continue
        name = row[1]
        if row[1].strip() == "":
            name = row[2]
        # name = name.replace(" ExMay", "")
        name = re.sub(' ExMay', "", name, flags=re.IGNORECASE)
        # name = name.replace("ExMay ", "")
        name = re.sub('ExMay ', "", name, flags=re.IGNORECASE)
        name = re.sub(' (C|M)$', "", name)
        phone = row[0]
        ignore_list = {line.split(",")[1] for line in lines if line.strip() != ""}
        if phone in ignore_list:
            print(f"Excluded {phone}")
            continue
        print(name, phone, end=" ")
        command = (
            "q -H -d , \"select a.[Phone number], a.[Other Names], a.[Surname] from "
            + f"{os.path.join(os.path.dirname(__file__), 'docs.seg', 'NumbersFromBallot.csv')}"
            + " a where instr('{phone}', a.[Phone number]) > 0\" -C read"
        )
        output = subprocess.check_output(command, shell=True).decode("utf-8").strip()
        print(output)
        contact = f"{name} {phone} {output}"
        if not re.search('[a-zA-Z]{2}', contact):
            command = (
                "q -H -d , \"select a.[Phone number], a.[Phone number 2], a.[First Name], a.[Maiden Name], a.[Surname] from "
                + f"{os.path.join(os.path.dirname(__file__), 'docs.seg', 'ExMay02','Ex-Mays2002OnlineDatabase-Sheet1.csv')}"
                + " a where (instr('{phone}', substr(a.[Phone number], length(a.[Phone number]) - 9)) > 0 and a.[Phone number] <> ''"
                ") or (instr('{phone}', substr(a.[Phone number 2], length(a.[Phone number 2]) - 9)) > 0 and a.[Phone number 2] <> '') or (instr('{phone}', substr(a.[WhatsApp No], length(a.[WhatsApp No]) - 9)) > 0 and a.[WhatsApp No] <> '' and a.[WhatsApp No] <> '∞'"  # To fix. ∞ seems to be causing query to fail
                ")\" -C read"
            )
            output = subprocess.check_output(command, shell=True).decode("utf-8").strip()
            print(output)
            contact = f"{name} {phone} {output}"
            if not re.search('[a-zA-Z]{2}', contact):
                no_names.append(contact.strip())
                continue
        final_contacts.append(contact)
    # random.shuffle(
    #     final_contacts, lambda: 0.5
    # )  # Temporary. This has been removed from latest python stdlib as not accurate
    random.Random("2025-02-11").shuffle(final_contacts)
    len_final_contacts = len(final_contacts)
    ic(len_final_contacts)
    args.debug and ic(final_contacts)
    i = 0
    j = 1
    print("No;A;B")
    while i < len_final_contacts:
        args.debug and ic(i)
        if i == len_final_contacts - 1:
            print(f"{j};\"{final_contacts[i]}\";\"ALSO with {final_contacts[0]}!\"")
        else:
            print(f"{j};\"{final_contacts[i]}\";\"{final_contacts[i + 1]}\"")
        i += 2
        j += 1
    print(f"{len(no_names)} contacts have no names")
    # print("no names")
    for no_name in no_names:
        output = no_name
        no_name = no_name.replace(" +", ",+")
        for contact in main_whatsapp_contacts:
            args.debug and ic(contact, no_name)
            if contact in no_name:
                output += " main"
                break
        # for contact in quiet_whatsapp_contacts:
        #     args.debug and ic(contact, no_name)
        #     if contact in no_name:
        #         output += " quiet"
        #         break
        print(output)


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
