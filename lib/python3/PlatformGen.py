import networkx as nx
import CodeGen
import proc
import os, shutil

def get_app_graph(PROC_G):

    HW_G = make_default_HW_graph(PROC_G)
    Design = {'name':'getPerf', 'HW' : HW_G, 'PROC' : PROC_G}

    APP_G = get_app_performance(Design)

    return APP_G

def make_default_HW_graph(PROC_G):
	
    index = 0
    HW_G = nx.Graph()
    
    HW_G.add_node("OPB0")
    HW_G.node["OPB0"]["type"] = "BUS"
    HW_G.node["OPB0"]["name"] = "OPB"

    HW_G.add_node("TX0")
    HW_G.node["TX0"]["type"] = "TX"
    HW_G.node["TX0"]["name"] = "ESETX"
    HW_G.add_edge("TX0", "OPB0")
        
    for proc_node in PROC_G:
        cpu_name = "CPU" + str(index)
        PROC_G.node[proc_node]['HW'] = cpu_name
        HW_G.add_node(cpu_name)
        HW_G.node[cpu_name]['type'] = 'PROCESSOR'
        HW_G.node[cpu_name]['name'] = 'MICROBLAZE'
        HW_G.node[cpu_name]['process'] = [proc_node]
        HW_G.add_edge(cpu_name, "OPB0")
        index += 1

    return HW_G

def get_app_performance(Design):

    shutil.copytree('func_model_srcs', '.temp/func_model_srcs')
    os.chdir('.temp')
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

#   APP_G = nx.DiGraph()
#   APP_G.add_nodes_from(Design['PROC'].nodes())
#   APP_G.add_edges_from(Design['PROC'].edges())
#   for edge in APP_G.edges():
#       APP_G[edge[0]][edge[1]]['name'] = Design['PROC'][edge[0]][edge[1]]['name']

##  extract bus cycle information ##    
    bus_file = open(Design['name'] + '.bus', 'r')
    bus_info = bus_file.readlines()
    bus_cycle = []
    for str in bus_info:
        bus_cycle.append(str.strip('\t\n').split('\t'))

    for edge in APP_G.edges():
        edge_name = APP_G[edge[0]][edge[1]]['name']
        
        for list in bus_cycle:
            if list[0] == edge_name:
                APP_G[edge[0]][edge[1]]['transfer'] = int(list[1])
    
    bus_file.close()

## extract computation cycle information ##

    com_file = open(Design['name'] + '.pe', 'r')
    com_info = com_file.readlines()
    com_cycle = []
    for str in com_info:
        com_cycle.append(str.strip('\t\n').split('\t'))

    for node_name in APP_G.nodes():
        tmp_list = []
        for list in com_cycle:
            if list[0] == node_name and 'computation' in tmp_list[0]:
                APP_G.node[node_name]['cycle'] = int(list[1])
            tmp_list = list
    
    os.chdir('..')
    shutil.rmtree('.temp')
    return APP_G




# test code
if __name__ == '__main__':
        
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

    APP_G = get_app_graph(PROC_G)
