import time
import sys

try:
    from point import Point, ClusterPoint
    from square import Square
    from node import Node
    from db_scan import *
    from dataset import *
    from range_query import RangeQuery, LinearQuery
except Exception: 
    from quadtree_and_linear.point import Point, ClusterPoint
    from quadtree_and_linear.square import Square
    from quadtree_and_linear.node import Node
    from quadtree_and_linear.db_scan import *
    from quadtree_and_linear.dataset import *
    from quadtree_and_linear.range_query import RangeQuery, LinearQuery


assignment_nr = 2

class QuadTree(RangeQuery):

    """
    Implementation of RangeQuery using a QuadTree
    """

    def __init__(self, points):
        self.points = points
        stack = []
        initial_square = Square.get_bounding_square(points)
        stack.insert(0, (points,initial_square,None))

        while len(stack) > 0:
            ps, sq, parent = stack.pop()
            node = Node(parent=parent, size=len(ps),square=sq, children=[])
            if parent is not None:
                parent.add_child(node)
            else:
                root_node = node
            if len(ps) == 1:
                node.set_point(ps[0])
            if len(ps) > 1:
                sub_squares = sq.splice_square()
                sub_ps = [[] for _ in range(4)]
                for p in ps:
                    for i, sub_sq in enumerate(sub_squares):
                        if sub_sq.contains_point(p):
                            sub_ps[i].append(p)
                            break
                for i in range(4):
                     stack.insert(0, (sub_ps[i],sub_squares[i],node))

        self.root_node = root_node


        self.root_node = root_node

    def report_range(self, p, epsilon):
        """
        Returns the points that lie within range epsilon from p
        """
        neighbors = []
#// BEGIN_TODO [IMPLEMENT-FIND-NEIGHBORS]      

        queue = [self.root_node]
        while len(queue) > 0:
            node = queue.pop()
            if len(node.children) == 0 and node.point is not None:
                if node.point.sq_distance_to(p) <= epsilon ** 2:
                    neighbors.append(node.point)
            for child in node.children:
                if child.square.overlaps_with_circle(p, epsilon):
                    queue.append(child)
#// END_TODO [IMPLEMENT-FIND-NEIGHBORS]
        return neighbors

    def count_range(self, p, epsilon):
        """
        Returns the number of points that lie within range epsilon from p
        """

        count = 0

        queue = [self.root_node]
        while len(queue) > 0:
            node = queue.pop()
            if len(node.children) == 0 and node.point is not None:
                if node.point.sq_distance_to(p) <= epsilon ** 2:
                    count += 1
            for child in node.children:
                if child.square.is_contained_in_circle(p, epsilon):
                    count += child.size
                elif child.square.overlaps_with_circle(p, epsilon):
                    queue.append(child)

        return count


    def delete_point(self, point):
        """
        Deletes point from this quad tree
        """
        node = self.root_node
        while len(node.children) > 0:
            for child in node.children:
                if child.square.contains_point(point):
                    node = child
                
        if node.point == point:
            node.point = None
            if node.parent is None: 
                node.size = 0
                return
            if node.parent.size == 2:
                other_node = None
                for child in node.parent.children:
                    if child.point is not None and child.point != point:
                        other_node = child
                assert other_node is not None
                
                while node.parent is not None and node.parent.size == 2:
                    node = node.parent
                
                node.children = []
                node.point = other_node.point
            
            while node is not None:
                node.size -= 1
                node = node.parent

def linear_run(path_in, path_out):
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
    
    report = {}
    # Initialize the quad tree
    query_obj = LinearQuery(ds.cluster_points, report)
    
    # Use the quad tree to create a clustering
    nr_clusters = find_clustering(ds.cluster_points, ds.epsilon, ds.min_pts, query_obj, report)
    
    try:
        ds.write_output(nr_clusters, path_out, assignment_nr)
    except IOError:
        print("could not write output to file:", path_out, file=sys.stderr)
    print("Cluster counter:", nr_clusters, file=sys.stderr)

    return report