#!/usr/local/bin/python3

import sys, os
pathname = os.path.dirname(sys.argv[0])
cpath = os.path.abspath(pathname)
cpath += "/lib/python3"
sys.path.append(cpath)

import networkx as nx
import proc
import CodeGen

# Making Design set for test

HW_G = nx.Graph()

HW_G.add_node("CPU0")
HW_G.node["CPU0"]["type"] = "PROCESSOR"
HW_G.node["CPU0"]["name"] = "MICROBLAZE"
readbmp = proc.Process()
readbmp.set_name("readbmp")
readbmp.set_cfile("/func_model_srcs/readbmp.c")
readbmp.set_cfile("/func_model_srcs/ReadBmp_aux.c")
readbmp.set_hfile("/func_model_srcs/ReadBmp_aux.h")
readbmp.set_process_port("r2c_if", "FIFO_CH_BW", "send_r2c")
HW_G.node["CPU0"]["process"] = [readbmp]

HW_G.add_node("CPU1")
HW_G.node["CPU1"]["type"] = "PROCESSOR"
HW_G.node["CPU1"]["name"] = "MICROBLAZE"
chendct = proc.Process()
chendct.set_name("chendct")
chendct.set_cfile("/func_model_srcs/chendct.c")
chendct.set_hfile("/func_model_srcs/ChenDCT_aux.h")
chendct.set_process_port("r2c_if", "FIFO_CH_BR", "recv_r2c")
chendct.set_process_port("c2q_if", "FIFO_CH_BW", "send_c2q")
HW_G.node["CPU1"]["process"] = [chendct]

HW_G.add_node("CPU2")
HW_G.node["CPU2"]["type"] = "PROCESSOR"
HW_G.node["CPU2"]["name"] = "MICROBLAZE"
quantize = proc.Process()
quantize.set_name("quantize")
quantize.set_cfile("/func_model_srcs/quantize.c")
quantize.set_cfile("/func_model_srcs/Quantize_aux.c")
quantize.set_hfile("/func_model_srcs/Quantize_aux.h")
quantize.set_process_port("c2q_if", "FIFO_CH_BR", "recv_c2q")
quantize.set_process_port("q2z_if", "FIFO_CH_BW", "send_q2z")
HW_G.node["CPU2"]["process"] = [quantize]

HW_G.add_node("CPU3")
HW_G.node["CPU3"]["type"] = "PROCESSOR"
HW_G.node["CPU3"]["name"] = "MICROBLAZE"
zigzag = proc.Process()
zigzag.set_name("zigzag")
zigzag.set_cfile("/func_model_srcs/zigzag.c")
zigzag.set_cfile("/func_model_srcs/Zigzag_aux.c")
zigzag.set_hfile("/func_model_srcs/Zigzag_aux.h")
zigzag.set_process_port("q2z_if", "FIFO_CH_BR", "recv_q2z")
zigzag.set_process_port("z2h_if", "FIFO_CH_BW", "send_z2h")
HW_G.node["CPU3"]["process"] = [zigzag]

HW_G.add_node("CPU4")
HW_G.node["CPU4"]["type"] = "PROCESSOR"
HW_G.node["CPU4"]["name"] = "MICROBLAZE"
huffencode = proc.Process()
huffencode.set_name("huffencode")
huffencode.set_cfile("/func_model_srcs/huffencode.c")
huffencode.set_cfile("/func_model_srcs/HuffEncode_aux.c")
huffencode.set_hfile("/func_model_srcs/HuffEncode_aux.h")
huffencode.set_process_port("z2h_if", "FIFO_CH_BR", "recv_z2h")
HW_G.node["CPU4"]["process"] = [huffencode]

HW_G.add_node("OPB0")
HW_G.node["OPB0"]["type"] = "BUS"
HW_G.node["OPB0"]["name"] = "OPB"

HW_G.add_node("TX0")
HW_G.node["TX0"]["type"] = "TX"
HW_G.node["TX0"]["name"] = "ESETX"

HW_G.add_edge("CPU0","OPB0")
HW_G.add_edge("CPU1","OPB0")
HW_G.add_edge("CPU2","OPB0")
HW_G.add_edge("CPU3","OPB0")
HW_G.add_edge("CPU4","OPB0")
HW_G.add_edge("TX0","OPB0")

print(HW_G.nodes())
print(HW_G.edges())

PROC_G = nx.DiGraph()

PROC_G.add_nodes_from(["readbmp", "chendct", "quantize", "zigzag", "huffencode"])
PROC_G.node['readbmp']['HW'] = "CPU0"
PROC_G.node['chendct']['HW'] = "CPU1"
PROC_G.node['quantize']['HW'] = "CPU2"
PROC_G.node['zigzag']['HW'] = "CPU3"
PROC_G.node['huffencode']['HW'] = "CPU4"

PROC_G.add_edge("readbmp", "chendct")
PROC_G["readbmp"]["chendct"]["name"] = "r2c"
PROC_G["readbmp"]["chendct"]["writer_if"] = "r2c_if"
PROC_G["readbmp"]["chendct"]["reader_if"] = "r2c_if"
PROC_G["readbmp"]["chendct"]["size"] = 256

PROC_G.add_edge("chendct", "quantize", name = 'c2q', writer_if = 'c2q_if', reader_if = 'c2q_if', size = 256)
PROC_G.add_edge("quantize", "zigzag", name = 'q2z', writer_if = 'q2z_if', reader_if = 'q2z_if', size = 256)
PROC_G.add_edge("zigzag", "huffencode", name = 'z2h', writer_if = 'z2h_if', reader_if = 'z2h_if', size = 256)

print(PROC_G.nodes())
print(PROC_G.edges())

Design = {'name':'test1', 'HW' : HW_G, 'PROC' : PROC_G}

CodeGen.CodeGenerator(Design)


# Making Design set for test

HW_G = nx.Graph()

HW_G.add_node("CPU0")
HW_G.node["CPU0"]["type"] = "PROCESSOR"
HW_G.node["CPU0"]["name"] = "MICROBLAZE"
readbmp = proc.Process()
readbmp.set_name("readbmp")
readbmp.set_cfile("/func_model_srcs/readbmp.c")
readbmp.set_cfile("/func_model_srcs/ReadBmp_aux.c")
readbmp.set_hfile("/func_model_srcs/ReadBmp_aux.h")
readbmp.set_process_port("r2c_if", "FIFO_CH_BW", "send_r2c")
chendct = proc.Process()
chendct.set_name("chendct")
chendct.set_cfile("/func_model_srcs/chendct.c")
chendct.set_hfile("/func_model_srcs/ChenDCT_aux.h")
chendct.set_process_port("r2c_if", "FIFO_CH_BR", "recv_r2c")
chendct.set_process_port("c2q_if", "FIFO_CH_BW", "send_c2q")
quantize = proc.Process()
quantize.set_name("quantize")
quantize.set_cfile("/func_model_srcs/quantize.c")
quantize.set_cfile("/func_model_srcs/Quantize_aux.c")
quantize.set_hfile("/func_model_srcs/Quantize_aux.h")
quantize.set_process_port("c2q_if", "FIFO_CH_BR", "recv_c2q")
quantize.set_process_port("q2z_if", "FIFO_CH_BW", "send_q2z")
HW_G.node["CPU0"]["process"] = [readbmp, chendct, quantize]

HW_G.add_node("CPU1")
HW_G.node["CPU1"]["type"] = "PROCESSOR"
HW_G.node["CPU1"]["name"] = "MICROBLAZE"
zigzag = proc.Process()
zigzag.set_name("zigzag")
zigzag.set_cfile("/func_model_srcs/zigzag.c")
zigzag.set_cfile("/func_model_srcs/Zigzag_aux.c")
zigzag.set_hfile("/func_model_srcs/Zigzag_aux.h")
zigzag.set_process_port("q2z_if", "FIFO_CH_BR", "recv_q2z")
zigzag.set_process_port("z2h_if", "FIFO_CH_BW", "send_z2h")
huffencode = proc.Process()
huffencode.set_name("huffencode")
huffencode.set_cfile("/func_model_srcs/huffencode.c")
huffencode.set_cfile("/func_model_srcs/HuffEncode_aux.c")
huffencode.set_hfile("/func_model_srcs/HuffEncode_aux.h")
huffencode.set_process_port("z2h_if", "FIFO_CH_BR", "recv_z2h")
HW_G.node["CPU1"]["process"] = [zigzag, huffencode]

HW_G.add_node("OPB0")
HW_G.node["OPB0"]["type"] = "BUS"
HW_G.node["OPB0"]["name"] = "OPB"

HW_G.add_node("TX0")
HW_G.node["TX0"]["type"] = "TX"
HW_G.node["TX0"]["name"] = "ESETX"

HW_G.add_edge("CPU0","OPB0")
HW_G.add_edge("CPU1","OPB0")
HW_G.add_edge("TX0","OPB0")

print(HW_G.nodes())
print(HW_G.edges())

PROC_G = nx.DiGraph()

PROC_G.add_nodes_from(["readbmp", "chendct", "quantize", "zigzag", "huffencode"])
PROC_G.node['readbmp']['HW'] = "CPU0"
PROC_G.node['chendct']['HW'] = "CPU0"
PROC_G.node['quantize']['HW'] = "CPU0"
PROC_G.node['zigzag']['HW'] = "CPU1"
PROC_G.node['huffencode']['HW'] = "CPU1"

PROC_G.add_edge("readbmp", "chendct")
PROC_G["readbmp"]["chendct"]["name"] = "r2c"
PROC_G["readbmp"]["chendct"]["writer_if"] = "r2c_if"
PROC_G["readbmp"]["chendct"]["reader_if"] = "r2c_if"
PROC_G["readbmp"]["chendct"]["size"] = 256

PROC_G.add_edge("chendct", "quantize", name = 'c2q', writer_if = 'c2q_if', reader_if = 'c2q_if', size = 256)
PROC_G.add_edge("quantize", "zigzag", name = 'q2z', writer_if = 'q2z_if', reader_if = 'q2z_if', size = 256)
PROC_G.add_edge("zigzag", "huffencode", name = 'z2h', writer_if = 'z2h_if', reader_if = 'z2h_if', size = 256)

print(PROC_G.nodes())
print(PROC_G.edges())

Design = {'name':'test2', 'HW' : HW_G, 'PROC' : PROC_G}

CodeGen.CodeGenerator(Design)
