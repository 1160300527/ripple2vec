from heapq import *
from utils import *
import math
from algorithms_distances import algorithms_ripple
from time import time

def findNeighborK(vertices,G,node_layer,sorted_hitting_time,hitting_map_list,part,max_layer,method):
    distances =  dict()
    d = int(2 * math.log(len(G),2))+1
    for v in vertices:
        t0 = time()
        D = dict()
        #d = len(G[v])
        k = node_layer[v]
        heap = []
        heapify(heap)
        sum_count = 0
        for i in range(k):
            nbs_i = dict()
            pos_v = hitting_map_list[i][v]
            hitting_time_pos = float(sorted_hitting_time[i][pos_v][1])
            len_i = len(sorted_hitting_time[i])
            if(pos_v>0):
                heappush(heap,(algorithms_ripple(0,1-sorted_hitting_time[i][pos_v-1][1]/hitting_time_pos,i,max_layer,method),-1,i,pos_v-1,sorted_hitting_time[i][pos_v-1][0]))
            if(pos_v<len_i-1):
                heappush(heap,(algorithms_ripple(0,1-hitting_time_pos/sorted_hitting_time[i][pos_v+1][1],i,max_layer,method),1,i,pos_v+1,sorted_hitting_time[i][pos_v+1][0]))
            flag = False
            count = 0
            while(len(nbs_i)<d and len(heap)>0 and len(D.keys())<(i+1)*d):
                (distance1,dir1,dim1,p1,u) = heappop(heap)
                pos = p1
                distance = distance1
                #if change to  len(D.keys())<(i+1)*d,will lead the case distances=null(maybe nbs_i>d and len(D.keys())>=(i+1)*d,some data has the same distance)
                while(len(D.keys())<(i+1)*d):
                    count+=1
                    if(u in D.keys()):
                        D[u] = (D[u][0]+distance,D[u][1]+1)
                    else:
                        D[u] = (distance,0)
                    if(D[u][1]==i and u>v):
                        nbs_i[u] = D[u][0]
                        if(method>1 and method!=3):
                            nbs_i[u] = method*nbs_i[u]

                        # if((v,u) in distances):
                        #     distances[v,u][i] = distance
                        # else:
                        #     distances[v,u] = {i:distance}
                    pos = pos+dir1
                    if(pos>=0 and pos<len(sorted_hitting_time[dim1])):
                        u,hitting_time = sorted_hitting_time[dim1][pos]
                        pos_v = hitting_map_list[dim1][v]
                        hitting_time_v = float(sorted_hitting_time[dim1][pos_v][1])
                        if(pos<pos_v):
                            distance = algorithms_ripple(0,1-hitting_time/hitting_time_v,dim1,max_layer,method)
                        else:
                            distance = algorithms_ripple(0,1-hitting_time_v/hitting_time,dim1,max_layer,method)
                    elif(len(nbs_i)<d):
                        break
                    if(len(nbs_i)>=d):
                        H = []
                        for node in D.keys():
                            if(node<=v):
                                continue
                            dis = 0
                            if(D[node][1]==i):
                                dis = D[node][0]
                            else:
                                for j in range(i+1):
                                    hitting_time_v1 = sorted_hitting_time[j][hitting_map_list[j][v]][1]
                                    if(node_layer[node]<=j):
                                        hitting_time_v2 = 0
                                    else:
                                        hitting_time_v2 = sorted_hitting_time[j][hitting_map_list[j][node]][1]
                                    if(hitting_time_v1 > hitting_time_v2):
                                        Max = hitting_time_v1
                                        Min = hitting_time_v2
                                    else:
                                        Max = hitting_time_v2
                                        Min = hitting_time_v1
                                    if(Max>0):
                                        #distance = distance+(float(Max)/Min)-1
                                        dis = algorithms_ripple(dis,(1-float(Min)/Max),j,max_layer,method)
                            if(method>1 and method!=3):
                                dis = dis*method
                            heappush(H,(dis,node))
                        for j in range(d):
                            if(len(H)<0):
                                flag = True
                            item = heappop(H)
                            if((v,item[1]) in distances):
                                distances[v,item[1]][i] = item[0]
                            else:
                                distances[v,item[1]] = {i:item[0]}
                        break
                    if(len(heap)>0):

                        (distance2,dir2,dim2,p2,u_2) = heap[0]
                        if(distance2<distance):
                            break
                if(pos>=0 and pos<len(sorted_hitting_time[dim1])):
                    heappush(heap,(distance,dir1,dim1,pos,sorted_hitting_time[dim1][pos][0]))
            sum_count+=count
            if(len(D.keys())>=(i+1)*d or flag):
                H = []
                for node in D.keys():
                    dis = 0
                    if(D[node][1]==i):
                        dis = D[node][0]
                    else:
                        for j in range(i+1):
                            hitting_time_v1 = sorted_hitting_time[j][hitting_map_list[j][v]][1]
                            if(node_layer[node]<=j):
                                hitting_time_v2 = 0
                            else:
                                hitting_time_v2 = sorted_hitting_time[j][hitting_map_list[j][node]][1]
                            if(hitting_time_v1 > hitting_time_v2):
                                Max = hitting_time_v1
                                Min = hitting_time_v2
                            else:
                                Max = hitting_time_v2
                                Min = hitting_time_v1
                            if(Max>0):
                                #distance = distance+(float(Max)/Min)-1
                                dis = algorithms_ripple(dis,(1-float(Min)/Max),j,max_layer,method)
                    if(method>1 and method!=3):
                        dis = dis*method
                    heappush(H,(dis,node))
                for j in range(d):
                    if(len(H)<1):
                        break
                    item = heappop(H)
                    if((v,item[1]) in distances):
                        distances[v,item[1]][i] = item[0]
                    else:
                        distances[v,item[1]] = {i:item[0]}
            if(len(nbs_i)<d):
                for u in nbs_i.keys():
                    distance = nbs_i[u]
                    if((v,u) in distances):
                        distances[v,u][i] = distance
                    else:
                        distances[v,u] = {i:distance}
        t1 = time()
        logging.info('Distances list vertex {}. Time: {}s'.format(v,(t1-t0)))
    saveVariableOnDisk(distances,"distances-"+str(part))


def next(L,hitting_time):
    direct = 0
    u = -1
    if(L.up!=None):
        if(L.down!=None):
            if(L.up[0]<=L.down[0]):
                u = L.up[3]
                distance = L.up[0]
                direct = -1
            else:
                u = L.down[3]
                distance = L.down[0]
                direct = 1
        else:
            u = L.up[3]
            distance = L.up[0]
            direct = -1
    elif(L.down!=None):
        u = L.down[3]
        distance = L.down[0]
        direct = 1
    else:
        return None
    if(direct==-1):
        if(L.up[1]>0):
            pos = L.up[1]-1
            L.up = (1-hitting_time[pos][1]/L.rVal,pos,-1,hitting_time[pos][0])
        else:
            L.up = None
    else:
        if(L.down[1]<L.length-1):
            pos = L.down[1]+1
            L.down = (1-L.rVal/hitting_time[pos][1],pos,-1,hitting_time[pos][0])
        else:
            L.down = None
    return u,distance

def initScan(L,count_scanned,D,hitting_time,limit_count,max_layer,method):
    nbs = dict()
    if(L.start>0):
        pos = L.start-1
        L.up = (1-hitting_time[pos][1]/L.rVal,pos,-1,hitting_time[pos][0])
    if(L.start<L.length-1):
        pos = L.start+1
        L.down = (1-L.rVal/hitting_time[pos][1],pos,1,hitting_time[pos][0])
    for i in range(count_scanned):
        n = next(L,hitting_time)
        if(n!=None):
            u,distance = n
            if(u in D):
                D[u] = (algorithms_ripple(D[u][0],distance,L.layer,max_layer,method),D[u][1]+1)
            else:
                D[u] = (algorithms_ripple(0,distance,L.layer,max_layer,method),0)
            if(D[u][1]==L.layer and u>hitting_time[L.start][0]):
                nbs[u] = D[u][0]
        else:
            break
    return nbs
    

def initLayer(layer,v,length,position):
    L = dict()
    L['count'] = 0
    L.length = length
    L.layer = layer
    L.start = position
    return L




def ThresholdTopk(vertices,G,node_layer,sorted_hitting_time,hitting_map_list,part,max_layer,method):
    distances =  dict()
    d = int(2 * math.log(len(G.keys()),2))+1
    for v in vertices:

        D = dict()
        L = list()
        k = node_layer[v]
        count_scanned = 0
        #d = len(G[v])
        for i in range(k):
            pos = hitting_map_list[i][v]
            rVal = sorted_hitting_time[i][pos][1]
            layer = Layer(i,v,len(sorted_hitting_time[i]),pos,rVal)
            nbs_i = initScan(layer,count_scanned,D,sorted_hitting_time[i],d,max_layer,method)
            L.append(layer)
            while(len(nbs_i.keys())<d and  len(D.keys())<(i+1)*d):
                flag = False
                for j in range(len(L)):
                    l = L[j]
                    record = next(l,sorted_hitting_time[l.layer])
                    if(record==None):
                        continue
                    else:
                        flag = True
                        u,distance = record
                        if(u in D):
                            D[u] = (algorithms_ripple(D[u][0],distance,j,max_layer,method),D[u][1]+1)
                        else:
                            D[u] = (algorithms_ripple(0,distance,j,max_layer,method),0)
                        if(D[u][1]==i):
                            nbs_i[u] = D[u][0]
                            if(len(nbs_i)>=d):
                                break
                if(len(nbs_i)>=d):
                    break
                if not(flag):
                    break
                else:
                    count_scanned+=1
            
            # if(len(nbs_i)>=d):
            H = []
            for node in D.keys():
    
                dis = 0
                if(D[node][1]==i):
                    dis = D[node][0]
                else:
                    for j in range(i+1):
                        hitting_time_v1 = sorted_hitting_time[j][hitting_map_list[j][v]][1]
                        if(node_layer[node]<=j):
                            hitting_time_v2 = 0
                        else:
                            hitting_time_v2 = sorted_hitting_time[j][hitting_map_list[j][node]][1]
                        if(hitting_time_v1 > hitting_time_v2):
                            Max = hitting_time_v1
                            Min = hitting_time_v2
                        else:
                            Max = hitting_time_v2
                            Min = hitting_time_v1
                        if(Max>0):
                            #distance = distance+(float(Max)/Min)-1
                            dis = algorithms_ripple(dis,(1-float(Min)/Max),j,max_layer,method)
                heappush(H,(dis,node))
            for j in range(d):
                if(len(H)<1):
                    break
                item = heappop(H)
                if((v,item[1]) in distances):
                    distances[v,item[1]][i] = item[0]
                else:
                    distances[v,item[1]] = {i:item[0]}
            # else:
            #     for u in nbs_i.keys():
            #         distance = nbs_i[u]
            #         if((v,u) in distances):
            #             distances[v,u][i] = distance
            #         else:
            #             distances[v,u] = {i:distance}
    saveVariableOnDisk(distances,"distances-"+str(part))

                        
class Layer(object):
    def __init__(self,layer,v,length,position,rVal):
        self.count = 0
        self.length = length
        self.layer = layer
        self.start = position
        self.rVal = float(rVal)
        self.up = None
        self.down = None
