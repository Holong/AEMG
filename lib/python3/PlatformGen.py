import networkx as nx
import CodeGen
import proc
import os, shutil
import xml.etree.ElementTree as ET

def get_app_graph(PROC_G):

    HW_G = make_default_HW_graph(PROC_G)
    Design = {'name':'getPerf', 'HW' : HW_G, 'PROC' : PROC_G}

    PROC_G = get_app_performance(Design)

    return PROC_G

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

##  extract bus cycle information ##    

    PROC_G = Design['PROC']

    bus_file = open(Design['name'] + '.bus', 'r')
    bus_info = bus_file.readlines()
    bus_cycle = []
    for str in bus_info:
        bus_cycle.append(str.strip('\t\n').split('\t'))

    for edge in PROC_G.edges():
        edge_name = PROC_G[edge[0]][edge[1]]['name']
        
        for list in bus_cycle:
            if list[0] == edge_name:
                PROC_G[edge[0]][edge[1]]['transfer'] = int(list[1])
    
    bus_file.close()

## extract computation cycle information ##

    com_file = open(Design['name'] + '.pe', 'r')
    com_info = com_file.readlines()
    com_cycle = []
    for str in com_info:
        com_cycle.append(str.strip('\t\n').split('\t'))

    for node_name in PROC_G.nodes():
        tmp_list = []
        for list in com_cycle:
            if list[0] == node_name and 'computation' in tmp_list[0]:
                PROC_G.node[node_name]['cycle'] = int(list[1])
            tmp_list = list
    
    os.chdir('..')
    shutil.rmtree('.temp')
    return PROC_G

def parse_xml(xml_file_name):
    tree = ET.parse(xml_file_name)
    root = tree.getroot()

    PROC_G = nx.DiGraph()

    for process in root:

        if process.tag == 'constraint':
            PROC_G.graph['time'] = process.attrib['msec']
            PROC_G.graph['num_pe'] = process.attrib['PE']
            PROC_G.graph['pe_clk'] = process.attrib['PE_CLK_MHZ']
            continue

        proc_name = process.attrib['name']
        PROC_G.add_node(proc_name)
        proc_info = proc.Process()
        proc_info.set_name(proc_name)
        
        for info in process:
            if info.tag == 'cfile':
                proc_info.set_cfile(info.text)
            elif info.tag == 'hfile':
                proc_info.set_hfile(info.text)
            elif info.tag == 'port':
                port_name = info.attrib['name']
                port_type = info.attrib['type']
                if port_type == 'write':
                    port_type = 'FIFO_CH_BW'
                else :
                    port_type = 'FIFO_CH_BR'
                port_func = info.attrib['function']

                proc_info.set_process_port(port_name, port_type, port_func)
        
        PROC_G.node[proc_name]['info'] = proc_info

    port_list = []
    for port in root.iter('port'):
        port_list.append(port)

    for port in port_list:
        if port.attrib['type'] == 'read':
            continue
        for dest_port in port_list:
            if port.attrib['name'] == dest_port.attrib['name'] and dest_port.attrib['type'] == 'read':
                break
        ch_name = port.attrib['name'][:port.attrib['name'].find('_if')]
        PROC_G.add_edge(port.attrib['proc'], dest_port.attrib['proc'], name = ch_name, writer_if = port.attrib['name'], reader_if = port.attrib['name'], size = 256)

    return PROC_G

def make_map(num_of_pe, PROC_G):
    
    map = {'total_cost':0, 'num_of_pe':0, 'num_of_cycle':0, 'map_info':{}}
    pe_speed = int(PROC_G.graph['pe_clk'])

    pe_load = []
    for i in range(0, num_of_pe):
        pe_load.append(["CPU" + str(i), 0])

    proc_cycle = []
    for proc_name in PROC_G.nodes():
        proc_cycle.append((proc_name, PROC_G.node[proc_name]['cycle']))

    proc_cycle.sort(key = lambda x: x[1])

    for proc_name, cycle in proc_cycle:
        load = cycle / pe_speed
        pe_load[0][1] += load
        map['map_info'][proc_name] = pe_load[0][0]
        pe_load.sort(key = lambda x:x[1])

    map['num_of_pe'] = num_of_pe
    map['num_of_cycle'] = pe_load[num_of_pe-1][1]
    map['total_cost'] = map['num_of_cycle']

# return {'total_cost':0, 'num_of_pe':0, 'num_of_cycle':0, 'map_info':{'readbmp':'CPU0', 'chendct':'CPU1', 'quantize':'CPU0', 'zigzag':'CPU1', 'huffencode':'CPU1'}}
    return map


def make_HW_graph(PROC_G, map):

    HW_G = nx.Graph()

    HW_G.add_node("OPB0")
    HW_G.node["OPB0"]["type"] = "BUS"
    HW_G.node["OPB0"]["name"] = "OPB"

    HW_G.add_node("TX0")
    HW_G.node["TX0"]["type"] = "TX"
    HW_G.node["TX0"]["name"] = "ESETX"
    HW_G.add_edge("TX0", "OPB0")

    print(HW_G.nodes())
    print(map['map_info'])

    for proc, cpu_name in map['map_info'].items():
        PROC_G.node[proc]['HW'] = cpu_name
        if cpu_name in HW_G.nodes():
            HW_G.node[cpu_name]['process'].append(proc)
        else :
            HW_G.add_node(cpu_name)
            HW_G.node[cpu_name]['type'] = 'PROCESSOR'
            HW_G.node[cpu_name]['name'] = 'MICROBLAZE'
            HW_G.node[cpu_name]['process'] = [proc]
            HW_G.add_edge(cpu_name, 'OPB0')
     
    return HW_G


def get_platform_graph(PROC_G):
## HW Graph Generation Code

    num_of_max_pe = int(PROC_G.graph['num_pe'])
    if num_of_max_pe > PROC_G.number_of_nodes():
        num_of_max_pe = PROC_G.number_of_nodes()

    optimized_map = {'total_cost':0, 'num_of_pe':0, 'num_of_cycle':0, 'map_info':{}}
    candidate_map = {'total_cost':0, 'num_of_pe':0, 'num_of_cycle':0, 'map_info':{}}

    for num_of_pe in range(num_of_max_pe, 1, -1):
        candidate_map = make_map(num_of_pe, PROC_G)

        if num_of_pe == num_of_max_pe:
            optimized_map = candidate_map
            continue

        if optimized_map['total_cost'] > candidate_map['total_cost']:
            optimized_map = candidate_map

    HW_G = make_HW_graph(PROC_G, optimized_map)

    return HW_G, PROC_G

def print_graph_info(Print_G):
    for node_name in Print_G.nodes():
        print("{0} : {1}".format(node_name, Print_G.node[node_name]))

    for edge_name in Print_G.edges():
        print("{0} - {1} : {2}".format(edge_name[0], edge_name[1], Print_G.edge[edge_name[0]][edge_name[1]]))

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

    for node_name in APP_G.nodes():
        print("{0} : {1}".format(node_name, APP_G.node[node_name]))

    for edge_name in APP_G.edges():
        print("{0} - {1} : {2}".format(edge_name[0], edge_name[1], APP_G.edge[edge_name[0]][edge_name[1]]))
