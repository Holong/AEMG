import networkx as nx
import CodeGen

def get_app_graph(PROC_G):
	
	index = 0
	HW_G = nx.Graph()

	for proc_node in PROC_G:
		cpu_name = "CPU" + str(index)
		proc_node['HW'] = cpu_name
		HW_G.add_node(cpu_name)
		HW_G.node[cpu_name]['type'] = 'PROCESSOR'
		HW_G.node[cpu_name]['name'] = 'MICROBLAZE'
		HW_G.node[cpu_name]['process'] = [proc_node]
		

		
