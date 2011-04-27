import pyx
import random
from math import sqrt
from operator import itemgetter
import networkx as nx
import matplotlib.pyplot as plt

def main():
	# define map
	m = prm_map(20, 20, [map_elem(3,3,10,10),map_elem(7,7,8,9)])
	
	# define start and end of path
	start = pt(1,1)
	end = pt(19,19)
	m.nodes.append(start)
	m.nodes.append(end)
	
	#sample to select nodes in map
	num_nodes = 400
	node_cnt = 0
	
	
	while(node_cnt < num_nodes):
		pnt = pick_point(m)
		if not m.contains_point(pnt):
			m.nodes.append(pnt)
			node_cnt += 1
	
	# build prm graph
	for n in m.nodes:
		node_dists = []
		for n_prime in m.nodes:
			if not intersects_map(n, n_prime,m):
				node_dists.append( [dist(n, n_prime), n_prime])
		
		neighbors = []
		
		for n_p in sorted(node_dists, key = itemgetter(0)):
			if not in_edge_list(m.edges, line(n, n_p[1])):
				neighbors.append(n_p[1])
			if len(neighbors) == 4:
				break
				
		[m.edges.append(line(n, ne)) for ne in neighbors]
	
	# determine optimal path without probabilities
	Gs = nx.Graph()
	
	[Gs.add_node((n.x,n.y)) for n in m.nodes]
	[Gs.add_edge((e.pt1.x,e.pt1.y), (e.pt2.x,e.pt2.y), weight=dist(e.pt1, e.pt2)) for e in m.edges]
	
	m.s_path = nx.shortest_path(Gs, (start.x, start.y), (end.x,end.y), weighted=True)
	
	p_map = prm_map(20, 20, [map_elem(10,10,3,10)])
	
	Gp = nx.Graph()
	
	
	[Gp.add_node((n.x,n.y)) for n in m.nodes]
	
	for e in m.edges:
		if intersects_map(e.pt1, e.pt2, p_map) or p_map.contains_point(e.pt1) or p_map.contains_point(e.pt2):	
			Gp.add_edge((e.pt1.x,e.pt1.y), (e.pt2.x,e.pt2.y), weight=dist(e.pt1, e.pt2)*2)
		else:
			Gp.add_edge((e.pt1.x,e.pt1.y), (e.pt2.x,e.pt2.y), weight=dist(e.pt1, e.pt2))
	
	m.p_path = nx.shortest_path(Gp, (start.x, start.y), (end.x,end.y), weighted=True)
	
	m.draw("map_edges")

def in_edge_list(list, edge):
	for e in list:
		if e == edge:
			return True
	return False

def intersects_map(pt1, pt2, m):
	for e in m.elems:
		bl = pt(e.x,e.y)
		tl = pt(e.x,e.y+e.h)
		tr = pt(e.x+e.w,e.y+e.h)
		br = pt(e.x+e.w,e.y)
		
		if intersects(pt1, pt2, bl, tl) or intersects(pt1, pt2, tl, tr) or intersects(pt1, pt2, tr, br) or intersects(pt1, pt2, br, bl):
			 return True
		
	return False

	
def intersects(A,B,C,D):
	return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)

def ccw(A,B,C):
	return (C.y-A.y)*(B.x-A.x) > (B.y-A.y)*(C.x-A.x)

def dist(pt1,pt2):
	return sqrt((pt1.x-pt2.x)**2 + (pt1.y-pt2.y)**2)

class line():
	def __init__(self,pt1,pt2):
		self.pt1 = pt1
		self.pt2 = pt2
		
	def __eq__(self, other):
		return (self.pt1 == other.pt1 and self.pt2 == other.pt2) or (self.pt1 == other.pt2 and self.pt2 == other.pt1)

class pt():
	def __init__(self,x,y):
		self.x = x
		self.y = y
		
	def __eq__(self, other):
		return self.x == other.x and self.y == other.y

def pick_point(m):
	x = random.uniform(0,m.width)
	y = random.uniform(0,m.height)
	
	return pt(x,y)

class map_elem():
	def __init__(self, x,y,w,h):
		self.x = x;
		self.y = y;
		self.w = w;
		self.h = h;

class prm_map:
	def __init__(self, h=20, w=20, e=[]):
		self.height = h
		self.width = w
		self.elems = e
		self.nodes = []
		self.edges = []
		self.s_path = []
		self.p_path = []
	
	def contains_point(self,pnt):
		for e in self.elems:
			if (pnt.x >= e.x and pnt.x <= e.x + e.w) and (pnt.y >= e.y and pnt.y <= e.y + e.h):
				return True
		else:
			return False
	
	def add_elem(e, self):
		if (not(e.x+e.w > self.width or e.y+e.h > self.height)):
			self.elems.append(e)
		else:
			print "element out of bounds!"
	
	def draw(self, outfile):
		
		drawn_map = pyx.canvas.canvas()
		
		# draw bounds
		drawn_map.stroke(pyx.path.line(0,0,self.width,0))	
		drawn_map.stroke(pyx.path.line(self.width,0, self.width, self.height))
		drawn_map.stroke(pyx.path.line(self.width, self.height, 0, self.height))
		drawn_map.stroke(pyx.path.line(0,self.height,0,0))
		
		drawn_map.fill(pyx.path.rect(10,10,3,10),[pyx.color.grey(.5)])
		
		for box in self.elems:
			drawn_map.fill(pyx.path.rect(box.x,box.y,box.w,box.h))
			
		for n in self.nodes:
			drawn_map.fill(pyx.path.circle(n.x,n.y,0.1), [pyx.color.rgb.red])
		
		for e in self.edges:
			drawn_map.stroke(pyx.path.line(e.pt1.x,e.pt1.y,e.pt2.x,e.pt2.y))
			
		distance = 0
		for i in range(len(self.s_path)-1):
			drawn_map.stroke(pyx.path.line(self.s_path[i][0],self.s_path[i][1],self.s_path[i+1][0],self.s_path[i+1][1]), [pyx.color.rgb.green, pyx.style.linewidth(.1)])
			distance += dist(pt(self.s_path[i][0],self.s_path[i][1]), pt(self.s_path[i+1][0],self.s_path[i+1][1]))
			
		print "shortest path distance: " + str(distance)

		distance = 0
		for i in range(len(self.p_path)-1):
			drawn_map.stroke(pyx.path.line(self.p_path[i][0],self.p_path[i][1],self.p_path[i+1][0],self.p_path[i+1][1]), [pyx.color.rgb.blue, pyx.style.linewidth(.1)])
			distance += dist(pt(self.p_path[i][0],self.p_path[i][1]), pt(self.p_path[i+1][0],self.p_path[i+1][1]))
			
		print "probabilistic path distance: " + str(distance)
			
			
		drawn_map.fill(pyx.path.circle(1, 1,.15), [pyx.color.rgb.blue])
		drawn_map.fill(pyx.path.circle(19,19,.15), [pyx.color.rgb.blue])
			
		drawn_map.writePDFfile(outfile)
	

if __name__ == "__main__":
	main()