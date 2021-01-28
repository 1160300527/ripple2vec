# ripple2vec
This repository provides a reference implementation of *struc2vec* as described in the paper:
> 𝑟𝑖𝑝𝑝𝑙𝑒2𝑣𝑒𝑐: Node Embedding with RippleDistance of Structures.<br>
> Jizhou Luo,Song Xiao,Shouxu Jiang,Hong Gao.<br>

The *ripple2vec* algorithm learns continuous representations for nodes in any graph by capturing structural similarities between nodes.

Before to execute *ripple2vec*, it is necessary to install the following packages:
<br/>
``pip install numpy``
<br/>
``pip install futures``
<br/>
``pip install fastdtw``
<br/>
``pip install gensim``

### Basic Usage

#### Example
To run *ripple2vec* on Mirrored Zachary's karate club network, execute the following command from the project home directory:<br/>
	``python2 src/main.py --input graph/karate-mirrored.edgelist --output emb/karate-mirrored.emb``

#### Options

You can check out the other options available to use with *ripple2vec* using:<br>
``python2 src/main.py --help``

To run *ripple2vec* on brazil airports network, using all optimizations, execute the following command from the project home directory:
<br/>
``python2 src/main.py --input graph/brazil-airports.edgelist --output emb/brazil-ripple.emb --num-walks 5 --walk-length 15 --window-size 10 --dimensions 32 --OPT1 True --OPT2 True --OPT3 True --OPT4 True --until-layer 4``

#### Input
The supported input format is an edgelist:

	node1_id_int node2_id_int <weight_float>
		
The graph is assumed to be undirected and unweighted by default. These options can be changed by setting the appropriate flags.

#### Output
The output file has *n+1* lines for a graph with *n* vertices. 
The first line has the following format:

    num_of_nodes dim_of_representation
The next *n* lines are as follows:
	
	node_id dim1 dim2 ... dimd

where dim1, ... , dimd is the *d*-dimensional representation learned by *ripple2vec*.

### Miscellaneous

Please send any questions you might have about the code and/or the algorithm to <luojizhou@hit.edu.cn>.

*Note:* This is only a reference implementation of the *ripple2vec* algorithm.
