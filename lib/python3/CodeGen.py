import networkx as nx
import os

def CodeGenerator(Design):
    
    # python code generator
    file_name = Design['name'] + '.py'
    file = open(file_name, 'w')

    ############## str_start #################
    str_start = """#!/usr/bin/python
import sys, os
pathname = os.path.dirname(sys.argv[0])
cpath = os.path.abspath(pathname)
sys.path.append(os.environ['ESE_PROJECT_ROOT']+"/lib/python2.3/site-packages")

import esexml

d = esexml.design()
"""
    str_start += "d.set_design_name(\"" + Design['name'] + "\")\n"
    ############## str_start end ##################

    ############## HW start #####################
    str_HW = ''
    HW_G = Design['HW']
    PROC_G = Design['PROC']
    Node_name = HW_G.nodes()

    for IP in Node_name:
        if HW_G.node[IP]['type'] == 'PROCESSOR':
            str_HW += "d.addPE(\"" + IP + "\",\"PROCESSOR\",\"" + HW_G.node[IP]['name'] + "\",0)\n"
        elif HW_G.node[IP]['type'] == 'BUS':
            str_HW += "d.addBus(\"" + IP + "\",\"BUS\",\"" + HW_G.node[IP]['name'] + "\")\n"
        elif HW_G.node[IP]['type'] == 'TX':
            str_HW += "d.addTX(\"" + IP + "\")\n"

    str_HW += "\n\n"

    for IP in Node_name:
        if HW_G.node[IP]['type'] == 'PROCESSOR':
            str_HW += "p = d.getPE(\"" + IP + "\")\n"

            index = 0
            for bus in HW_G.neighbors(IP):
                port_name = IP + "_PORT" + str(index)
                str_HW += "p.addPort(\"" + port_name + "\")\n"
                str_HW += "d.addConn(\"" + IP + "\",\"" + port_name + "\",\"M\",\"" + bus + "\")\n\n"
                index += 1
	
            if len(HW_G.node[IP]['process']) > 1:
                str_HW += "p.set_rtos(1)\n"
                str_HW += "p.setRtosType(\"xilkernel\")\n\n"	

            for p in HW_G.node[IP]['process']:
                str_HW += "p.addProc(\"" + PROC_G.node[p]['info'].name + "\")\n"
                str_HW += "proc = p.getProc(\"" + PROC_G.node[p]['info'].name + "\")\n"
                str_HW += "clist = esexml.eseCharList()\n"
                for i in PROC_G.node[p]['info'].c_file :
                    str_HW += "cname = cpath+\"" + i + "\"\n"
                    str_HW += "clist.append(cname)\n"
                str_HW += "proc.add_cfiles(clist)\n"
                str_HW += "hlist = esexml.eseCharList()\n"
                for i in PROC_G.node[p]['info'].h_file :
                    str_HW += "hname = cpath+\"" + i + "\"\n"
                    str_HW += "hlist.append(hname)\n"
                str_HW += "proc.add_hfiles(hlist)\n"
                for i in PROC_G.node[p]['info'].port :
                    str_HW += "proc.addInterface(\"" + i[0] + "\",esexml.ESE_" + i[1] + ")\n"
                    str_HW += "intf = proc.getInterface(\"" + i[0] + "\")\n"
                    str_HW += "intf.setTypeValue(esexml.ESE_" + i[1] + ",\"" + i[2] + "\")\n"
                str_HW += "\n\n"

        elif HW_G.node[IP]['type'] == 'TX':
            str_HW += "p = d.getTX(\"" + IP + "\")\n"

            index = 0
            for bus in HW_G.neighbors(IP):
                port_name = IP + "_PORT" + str(index)
                str_HW += "p.addPort(\"" + port_name + "\")\n"
                str_HW += "p.set_fifo_size(1024)\n"
                str_HW += "d.addConn(\"" + IP + "\",\"" + port_name + "\",\"S\",\"" + bus + "\")\n"
                str_HW += "bus = d.getBus(\"" + bus + "\")\n"
                str_HW += "bus.setTxLowAddr(\"" + IP + "\",\"" + '{0:#x}'.format(0x00200000 * (index+1)) + "\")\n\n"
                index += 1
    ############## HW end #######################

    ############## CH Start ################
    str_CH = ''

    for edge in  PROC_G.edges():
        ch_name = PROC_G.edge[edge[0]][edge[1]]['name']
        ch_writer_if = PROC_G.edge[edge[0]][edge[1]]['writer_if']
        ch_reader_if = PROC_G.edge[edge[0]][edge[1]]['reader_if']
        ch_size = PROC_G.edge[edge[0]][edge[1]]['size']

        str_CH += "l = d.display_chfifo_mapping_types(\"" + edge[0] + "\",\"" + edge[1] + "\")\n"
        str_CH += "i = l.first()\n"
        str_CH += "d.add_chfifo(\"" + ch_name + "\",\"" + PROC_G.node[edge[0]]['HW'] + "\",\"" +  edge[0] + "\",\"" + PROC_G.node[edge[1]]['HW'] + "\",\"" + edge[1] + "\")\n"
        str_CH += "ch = d.get_chfifo(\"" + ch_name + "\")\n"
        str_CH += "ch.set_writer_interface(\"" + ch_writer_if + "\")\n"
        str_CH += "ch.set_reader_interface(\"" + ch_reader_if + "\")\n"
        str_CH += "ch.set_size(\"" + str(ch_size) + "\")\n"
        str_CH += "rt = d.find_routes_chfifo(\"" + edge[0] + "\",\"" + edge[1] + "\",i)\n"
        str_CH += "d.set_chfifo_route(\"" + ch_name + "\",rt,i)\n\n"
        list1 = HW_G.neighbors(PROC_G.node[edge[0]]['HW'])
        list2 = HW_G.neighbors(PROC_G.node[edge[1]]['HW'])
        for target in list1:
            if target in list2:
                bus = target
        str_CH += "bus = d.getBus(\"" + target + "\")\n"
        str_CH += "bus.setSyncType(\"" + ch_name + "\",\"INTERRUPT\")\n"
    ############## CH End ##################

    ############## BUS Start ###################



    ############## Dump Start ##################
    str_Dump = ''
    str_Dump += "d.dump_everything()\n"

    eds_name = "/" + Design['name'] + '.eds'


    str_Dump += "name = cpath+\"" + eds_name + "\"\n"
    str_Dump += "print d.saveToDisk(cpath+\"" + eds_name + "\")\n"




    file.write(str_start)
    file.write(str_HW)
    file.write(str_CH)
    file.write(str_Dump)

    os.chmod(file_name, 0o744)
    file.close()
