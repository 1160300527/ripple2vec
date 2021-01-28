# -*- coding: utf-8 -*-

import numpy as np
import random,sys,logging
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import Manager
from time import time
from collections import deque

from utils import *
from algorithms import *
from algorithms_distances import *
import graph
from topk import findNeighborK,findNeighborK_2


class Graph():
	def __init__(self, g, is_directed, workers, untilLayer = None,method=0,ripple=True):

		logging.info(" - Converting graph to dict...")
		self.G = g.gToDict()
		self.weight = g.weighted
		logging.info("Graph converted.")

		self.num_vertices = g.number_of_nodes()
		self.num_edges = g.number_of_edges()
		self.is_directed = is_directed
		self.workers = workers
		self.calcUntilLayer = untilLayer
		self.iniLayerZero = True
		self.mDgree = self.max_degree()
		self.method = method
		self.ripple = ripple
		logging.info('Graph - Number of vertices: {}'.format(self.num_vertices))
		logging.info('Graph - Number of edges: {}'.format(self.num_edges))


	def max_degree(self):
		mDgree = 0
		for node in self.G.keys():
			if(len(self.G[node])>mDgree):
				mDgree = len(self.G[node])
		return mDgree


	def cal_layer(self):
		rippleList = restoreVariableFromDisk('RippleList')
		self.node_layer = {}
		for node in rippleList.keys():
			self.node_layer[node] = len(rippleList[node])

	def preprocess_neighbors_with_bfs(self):

		with ProcessPoolExecutor(max_workers=self.workers) as executor:
			job = executor.submit(exec_bfs,self.G,self.weight,self.workers,self.calcUntilLayer,self.mDgree,self.ripple)
			
			self.max_depth = job.result()
			if(self.method==2):
				if(self.max_depth<100):
					if(self.max_depth>1):
						self.method = 100/float(self.max_depth-1)
					else:
						self.method = 100

		return


	def preprocess_degree_lists(self):

		with ProcessPoolExecutor(max_workers=self.workers) as executor:
			job = executor.submit(preprocess_degreeLists)
			
			job.result()

		return

	def contexLayers(self):
		rippleList = restoreVariableFromDisk('RippleList')
		ripples = dict()
		hitting_k_list = list()
		vertices = rippleList.keys()
		parts = self.workers
		chunks = partition(vertices,parts)
		futures = {}
		
		t0 = time()
		with ProcessPoolExecutor(max_workers = self.workers) as executor:
			part = 1
			for c in chunks:
				ripple_part = {}
				for key in c:
					ripple_part[key] = rippleList[key]
				logging.info("Executing split the hitting time vector to different layers of part {}...".format(part))
				job = executor.submit(splitHittingTime,c,ripple_part)
				futures[job] = part
				part += 1


			logging.info("Receiving results of split the hitting time...")
			for job in as_completed(futures):
				k_hitting_list = job.result()
				for i in range(len(k_hitting_list)):
					if(i > len(hitting_k_list)-1):
						hitting_k_list.append(k_hitting_list[i])
					else:
						hitting_k_list[i].extend(k_hitting_list[i])
				r = futures[job]
				logging.info("Part {} Completed.".format(r))	
		
		if(self.workers>len(hitting_k_list)):
			w = len(hitting_k_list)
		else:
			w = self.workers
		chunks = partition(range(len(hitting_k_list)),w)
		futures = {}
		sorted_hitting_list = [0]*len(hitting_k_list)
		hitting_map_list = [0]*len(hitting_k_list)
		with ProcessPoolExecutor(max_workers = w) as executor:
			part = 1
			for c in chunks:
				logging.info("Executing sort hitting time of part {}...".format(part))
				job = executor.submit(sortHittingTime,hitting_k_list[c[0]:c[len(c)-1]+1],c)
				futures[job] = part
				part += 1


			logging.info("Receiving results of sort...")
			for job in as_completed(futures):
				sorted_hitting_k,map_k_hitting,c = job.result()
				sorted_hitting_list[c[0]:c[len(c)-1]+1] = sorted_hitting_k
				hitting_map_list[c[0]:c[len(c)-1]+1] = map_k_hitting
				r = futures[job]
				logging.info("Part {} Completed.".format(r))

		chunks = partition(vertices,parts)
		futures = {}
		t1 = time()
		logging.info('Splitting and sortting the hitting time cost. Time: {}s'.format((t1-t0)))
		with ProcessPoolExecutor(max_workers = self.workers) as executor:
			part = 1
			for c in chunks:
				logging.info("Executing find the top k nearest nodes of part {}...".format(part))
				job = executor.submit(findNeighborK,c,self.G,self.node_layer,sorted_hitting_list,hitting_map_list,part,self.max_depth,self.method)
				futures[job] = part
				part += 1


			logging.info("Receiving results of top k...")
			for job in as_completed(futures):
				job.result()
				r = futures[job]
				logging.info("Part {} Completed.".format(r))
		t2 = time()
		logging.info('Find top k nodes cost. Time: {}s'.format((t1-t2)))

	def calc_distances_all_vertices(self):
    
		if(self.calcUntilLayer):
			logging.info("Calculations until layer: {}".format(self.calcUntilLayer))

		futures = {}

		count_calc = 0

		vertices = list(reversed(sorted(self.G.keys())))

		logging.info("Recovering compactDegreeList from disk...")
		rippleList = restoreVariableFromDisk('RippleList')
		

		parts = self.workers
		chunks = partition(vertices,parts)

		t0 = time()
		
		with ProcessPoolExecutor(max_workers = self.workers) as executor:

			part = 1
			for c in chunks:
				logging.info("Executing part {}...".format(part))
				list_v = []
				for v in c:
					list_v.append([vd for vd in rippleList.keys() if vd > v])
				job = executor.submit(calc_distances_ripple, c, list_v, rippleList,part,self.max_depth,self.method)
				futures[job] = part
				part += 1


			logging.info("Receiving results...")

			for job in as_completed(futures):
				job.result()
				r = futures[job]
				logging.info("Part {} Completed.".format(r))
		
		logging.info('Distances calculated.')
		t1 = time()
		logging.info('Time : {}m'.format((t1-t0)/60))
		
		return




	def create_distances_network(self):

		with ProcessPoolExecutor(max_workers=1) as executor:
			job = executor.submit(generate_distances_network,self.workers)

			job.result()

		return

	def preprocess_parameters_random_walk(self):

		with ProcessPoolExecutor(max_workers=1) as executor:
			job = executor.submit(generate_parameters_random_walk,self.workers)

			job.result()

		return


	def simulate_walks(self,num_walks,walk_length):

		# for large graphs, it is serially executed, because of memory use.
		if(len(self.G) > 500000):

			with ProcessPoolExecutor(max_workers=1) as executor:
				job = executor.submit(generate_random_walks_large_graphs,num_walks,walk_length,self.workers,self.G.keys(),self.node_layer,self.iniLayerZero)

				job.result()

		else:
			
			with ProcessPoolExecutor(max_workers=1) as executor:
				job = executor.submit(generate_random_walks,num_walks,walk_length,self.workers,self.G.keys(),self.node_layer,self.iniLayerZero)

				job.result()


		return	

