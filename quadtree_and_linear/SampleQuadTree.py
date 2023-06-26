import time
import sys

try:
    from point import Point, ClusterPoint
    from square import Square
    from node import Node
    from db_scan import *
    from dataset import *
    from range_query import RangeQuery  
except Exception: 
    from quadtree_and_linear.point import Point, ClusterPoint
    from quadtree_and_linear.square import Square
    from quadtree_and_linear.node import Node
    from quadtree_and_linear.db_scan import *
    from quadtree_and_linear.dataset import *
    from quadtree_and_linear.range_query import RangeQuery  


assignment_nr = 2


import sys

def quad_build(P, S):
    u = Node(None, len(P), S, [])
    
    if len(P) == 1:
        u.set_point(P[0])
        
    if len(P) > 1:
        sub_squares = S.splice_square()
        for square in sub_squares:
            v = quad_build([point for point in P if square.contains_point(point)], square)
            v.parent = u
            u.add_child(v)
    return u


class QuadTree(RangeQuery):

    """
    Implementation of RangeQuery using a QuadTree
    """

    def __init__(self, points):
        self.points = points

#// BEGIN_TODO [CREATE-QUAD-TREE]
        square = Square.get_bounding_square(points)
        root_node = quad_build(points, square) 
        
#// END_TODO [CREATE-QUAD-TREE]    
        self.root_node = root_node

    def report_range(self, p, epsilon):
        """
        Returns the points that lie within range epsilon from p
        """

        neighbors = []
#// BEGIN_TODO [IMPLEMENT-FIND-NEIGHBORS]      
        Q = [self.root_node]
        
        while len(Q) != 0:
            u = Q.pop()
            
            if u.point is not None:
                if u.point.sq_distance_to(p) <= (epsilon**u.point.dimension):
                    neighbors.append(u.point)

            for v in u.children:
                if v.square.overlaps_with_circle(center=p, radius=epsilon):
                    Q.append(v)

#// END_TODO [IMPLEMENT-FIND-NEIGHBORS]
        return neighbors

    def count_range(self, p, epsilon):
        """
        Returns the number of points that lie within range epsilon from p
        """

        count = 0
#// BEGIN_TODO [IMPLEMENT-COUNT-RANGE]

        Q = [self.root_node]
        
        while len(Q) > 0:
            u = Q.pop()

            if u.point is not None:
                if u.point.sq_distance_to(p) <= (epsilon**u.point.dimension):
                    count += 1
                    
            for v in u.children:
                if v.square.is_contained_in_circle(center=p, radius=epsilon):
                    count += v.size

                elif v.square.overlaps_with_circle(center=p, radius=epsilon):
                    Q.append(v)

#// END_TODO [IMPLEMENT-COUNT-RANGE]
        return count


    def delete_point(self, point):
        """
        Deletes point from this quad tree
        """
#// BEGIN_TODO [IMPLEMENT-DELETE-POINT]

        p = point
        u = self.root_node
        while len(u.children) > 0:
            for child in u.children:
                if child.square.contains_point(p):
                    u = child
                    break
                    
        if u.point is not None and u.point == p:
            u.set_point(None)
            if u.parent is None:
                u.size = 0
                return u
            
            if u.parent.size == 2:
                for child in u.parent.children:
                    if child.point is not None and child.point is not p:
                        q = child.point

                while u.parent.size == 2:
                    u = u.parent
                    if u.parent is None:
                        break
            
            u.children = []
            if u.size == 2:
                u.point = q
            
            while u is not None:
                u.size = u.size - 1
                u = u.parent    

#// END_TODO [IMPLEMENT-DELETE-POINT]

def sample_qt_run(path_in, path_out):
    """
    Reads the input set, clusters the points and writes to output\\
    path_in     location of the input set\\
    path_out    location to print the output
    """

    # Read input from file
    try:
        with open(path_in, "r") as f:
            ds = Dataset.read_input(f)    
    except IOError:
        print("could not read input file:", path_in, file=sys.stderr)
        return
    
    # Initialize the quad tree
    query_obj = QuadTree(ds.cluster_points)
    
    # Initialize linear range query
    #query_obj = LinearQuery(ds.cluster_points)

    # Use the quad tree to create a clustering
    nr_clusters = find_clustering(ds.cluster_points, ds.epsilon, ds.min_pts, query_obj)
    
    try:
        ds.write_output(nr_clusters, path_out, assignment_nr)
    except IOError:
        print("could not write output to file:", path_out, file=sys.stderr)
    print("Cluster counter:", nr_clusters, file=sys.stderr)