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

# Making Design set for test
PROC_G = nx.DiGraph()

PROC_G.add_nodes_from(["readbmp", "chendct", "quantize", "zigzag", "huffencode"])
readbmp = proc.Process()
readbmp.set_name("readbmp")
readbmp.set_cfile("/func_model_srcs/readbmp.c")
readbmp.set_cfile("/func_model_srcs/ReadBmp_aux.c")
readbmp.set_hfile("/func_model_srcs/ReadBmp_aux.h")
readbmp.set_process_port("r2c_if", "FIFO_CH_BW", "send_r2c")
PROC_G.node['readbmp']['info'] = readbmp

chendct = proc.Process()
chendct.set_name("chendct")
chendct.set_cfile("/func_model_srcs/chendct.c")
chendct.set_hfile("/func_model_srcs/ChenDCT_aux.h")
chendct.set_process_port("r2c_if", "FIFO_CH_BR", "recv_r2c")
chendct.set_process_port("c2q_if", "FIFO_CH_BW", "send_c2q")
PROC_G.node['chendct']['info'] = chendct

quantize = proc.Process()
quantize.set_name("quantize")
quantize.set_cfile("/func_model_srcs/quantize.c")
quantize.set_cfile("/func_model_srcs/Quantize_aux.c")
quantize.set_hfile("/func_model_srcs/Quantize_aux.h")
quantize.set_process_port("c2q_if", "FIFO_CH_BR", "recv_c2q")
quantize.set_process_port("q2z_if", "FIFO_CH_BW", "send_q2z")
PROC_G.node['quantize']['info'] = quantize

zigzag = proc.Process()
zigzag.set_name("zigzag")
zigzag.set_cfile("/func_model_srcs/zigzag.c")
zigzag.set_cfile("/func_model_srcs/Zigzag_aux.c")
zigzag.set_hfile("/func_model_srcs/Zigzag_aux.h")
zigzag.set_process_port("q2z_if", "FIFO_CH_BR", "recv_q2z")
zigzag.set_process_port("z2h_if", "FIFO_CH_BW", "send_z2h")
PROC_G.node['zigzag']['info'] = zigzag

huffencode = proc.Process()
huffencode.set_name("huffencode")
huffencode.set_cfile("/func_model_srcs/huffencode.c")
huffencode.set_cfile("/func_model_srcs/HuffEncode_aux.c")
huffencode.set_hfile("/func_model_srcs/HuffEncode_aux.h")
huffencode.set_process_port("z2h_if", "FIFO_CH_BR", "recv_z2h")
PROC_G.node['huffencode']['info'] = huffencode

PROC_G.add_edge("readbmp", "chendct", name = 'r2c', writer_if = 'r2c_if', reader_if = "r2c_if", size = 256)
PROC_G.add_edge("chendct", "quantize", name = 'c2q', writer_if = 'c2q_if', reader_if = 'c2q_if', size = 256)
PROC_G.add_edge("quantize", "zigzag", name = 'q2z', writer_if = 'q2z_if', reader_if = 'q2z_if', size = 256)
PROC_G.add_edge("zigzag", "huffencode", name = 'z2h', writer_if = 'z2h_if', reader_if = 'z2h_if', size = 256)

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

