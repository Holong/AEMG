#!/usr/local/bin/python3

import sys, os
pathname = os.path.dirname(sys.argv[0])
cpath = os.path.abspath(pathname)
cpath += "/lib/python3"
sys.path.append(cpath)

import networkx as nx
import proc
import CodeGen
import PlatformGen
import shutil

## Get raw App graph
PROC_G = PlatformGen.parse_xml('platform.xml')

## Get Application Performance Graph
PROC_G = PlatformGen.get_app_graph(PROC_G)

## Get Hardware and Process Graph
HW_G, PROC_G = PlatformGen.get_platform_graph(PROC_G)

## Make platform & simulate
Design = {'name':'test', 'HW' : HW_G, 'PROC' : PROC_G}

shutil.copytree('func_model_srcs', 'result/func_model_srcs')
os.chdir('result')
CodeGen.CodeGenerator(Design)

pid = os.fork()
if pid:
    pid, status = os.wait()
else:
    os.execl(Design['name'] + '.py', Design['name'] + '.py')
print("eds making complete")

pid = os.fork()
if pid:
    pid, status = os.wait()
else:
    os.execlp('tlmest', 'tlmest', Design['name'] + '.eds')
print("Making Timed TLM complete")

pid = os.fork()
if pid:
    pid, status = os.wait()
else:
    os.execl(Design['name'] + '_timed_TLM/tlm', 'tlm')
print("Estimate complete")

