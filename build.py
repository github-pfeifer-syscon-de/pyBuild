#!/bin/python3
# -*- coding: utf-8 -*-
import os
import subprocess
import datetime
import sys
import pathlib
from Proj import Proj

# the shell verion of the build script
class Cons:
    def out(msg : str) -> None:
        print(msg)

    def err(msg : str) -> None:
        if not msg is None and msg != '':
            print(f'Err: {msg}')

def choice(num, lst) -> bool:
    try:
        n = int(num)
    except Exception as e:
        print(f'{num} is not a number {e}')
        return False
    if n > 0:
        #try:
            cons = Cons
            return lst[n-1].build(cons)
        #except Exception as e:
        #    print(f'Choice {n} processing error: {e}')
    return False

def list():
    dict: list[Proj]=[]
    with os.scandir(Proj.getMainBuildDir()) as d:
        for e in d:
            if e.is_dir() and not e.name.startswith('.'):
                ctime = os.path.getctime(e)
                f = Proj(e.name, e.path, ctime)
                dict.append(f)
    dict = sorted(dict, key=lambda file: file.timestamp)
    i=1
    for f in dict:
        print(f' {i:3}. {repr(f)}')
        i+=1
    return dict

if __name__ == '__main__':
    next=True
    while(next):
        print()
        lst = list()
        num=input("Number? (to exit use 0)")
        next = choice(num, lst)
