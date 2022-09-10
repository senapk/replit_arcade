#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import os

tk_path = "tk"

def validate_label(label):
    if len(label) != 3:
        return False
    for c in label:
        if not c.isdigit():
            return False
    return True

def ask_and_load_label():
    last_label_file = ".label.txt"
    last_label = ""
    if os.path.exists(last_label_file):
        last_label = open(last_label_file).read()
    
    label = input("label(" + last_label + "): ")
    if label == "":
        label = last_label
    
    elif not validate_label(label):
        print("fail: label devem ser 3 números: ")
        return ask_and_load_label()

    open(last_label_file, "w").write(label)
    return label


def main(): 
    # diff_mode = "-v"
    label = ask_and_load_label()
    if not os.path.exists(label) or not os.path.isdir(label):
        discp = "fup"
        if os.path.exists(".discp.txt"):
            discp = open(".discp.txt").read().split("\n")[0]
        print("Problem " + label + " not found, creating...")
        subprocess.run([tk_path, "down", discp, label])
    else:
        print("Problem " + label + " found, running")
        tk_config = ".tk.cfg"
        param = []
        if os.path.exists(tk_config):
            param = open(tk_config).read().split("\n")[0].split(" ")
        cmd = [tk_path, "run", "-f", label]
        param = [x for x in param if x != ""]
        if len(param) > 0:
            cmd += param
        subprocess.run(cmd)

main()
