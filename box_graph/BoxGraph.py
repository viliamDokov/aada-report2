import sys
import os
import time
from time import perf_counter
try:
    from point import ClusterPoint as CP
    from box_graph import BoxGraph
    from box import Box
except:
    from box_graph.point import ClusterPoint as CP
    from box_graph.box_graph import BoxGraph
    from box_graph.box import Box

assignment_nr = 2

def find_core_points(bg):
    """
    Step 2: find the core points
    """
#// BEGIN_TODO [FIND-CORE-POINTS]

    boxes = bg.boxes

    for box in boxes:
        if len(box.points) >= bg.min_pts:
            box.func = Box.Func.PARTIAL
            for p in box.points: p.func = CP.Func.CORE
        else: 
            for p in box.points:
                count = len(box.points)
                for neighbour_box in box.neighbours:
                    for u in neighbour_box.points:
                        if p.sq_distance_to(u) <= bg.eps_sqr:
                            count += 1
                if count >= bg.min_pts:
                    box.func = Box.Func.PARTIAL
                    p.func = CP.Func.CORE

#// END_TODO [FIND-CORE-POINTS]              


def compute_cluster_cores(bg):
    """
    Step 3: compute the cluster cores    
    """
    nr_clusters = -1
#// BEGIN_TODO [COMPUTE-CLUSTER-CORES]
    for box in bg.boxes:
        if not box.is_labeled() and box.func == Box.Func.PARTIAL:
            nr_clusters += 1
            Q = [box]
            while len(Q) > 0:
                front_box = Q.pop()
                front_box.label = nr_clusters
                for point in front_box.points:
                    if point.func == CP.Func.CORE:
                        point.cluster_label = front_box.label
                for neighbour_box in front_box.neighbours:
                    if not neighbour_box.is_labeled() and neighbour_box.func == Box.Func.PARTIAL:
                        if front_box.is_core_neighbour(neighbour_box, bg.eps):
                            front_box.label = nr_clusters
                            Q.append(neighbour_box)

    # assert nr_clusters == 2

#// END_TODO [COMPUTE-CLUSTER-CORES]
    return nr_clusters + 1


def assign_border_points(bg):
    """
    Step 4: assign border points to clusters
    """
#// BEGIN_TODO [ASSIGNING-BORDER-POINTS]

# ===== =====> Replace this line by your code. <===== ===== #

    for box in bg.boxes:
        for point in box.points:
            if point.cluster_label == CP.DEFAULT_LABEL:
                nearest_point = None
                nearest_dist = 999999999999999999
                for neighbour_point in box.points:
                    if neighbour_point.cluster_label != CP.DEFAULT_LABEL and point.sq_distance_to(neighbour_point) < nearest_dist:
                        nearest_point = neighbour_point
                        nearest_dist = point.sq_distance_to(neighbour_point)
                for neighbour_box in box.neighbours:
                    for neighbour_point in neighbour_box.points:
                        if neighbour_point.cluster_label != CP.DEFAULT_LABEL and point.sq_distance_to(neighbour_point) < nearest_dist:
                            nearest_point = neighbour_point
                            nearest_dist = point.sq_distance_to(neighbour_point)

                if nearest_dist < bg.eps_sqr:
                    point.cluster_label = nearest_point.cluster_label
                    point.func = CP.Func.BORDER

#// END_TODO [ASSIGNING-BORDER-POINTS]
def box_run(path_in, path_out):
    """
    Reads the input set, clusters the points and writes to output

    :param path_in:     location of the input set
    :param path_out:    location to print the output
    """
    # Step 1: read file and create box graph
    report = {}
    try:
        with open(path_in, "r") as f:
            s = perf_counter()
            bg = BoxGraph.read_input(f)
            report["init"] = perf_counter() - s    
    except IOError as e:
        print(e)
        print("could not read input file:", path_in, file=sys.stderr)
        return


    s1 = perf_counter()
    # Step 2: Compute the core points
    find_core_points(bg)
    s2 = perf_counter()
    report["find_core_points"] = s2 - s1

    # Step 3: cluster the core points
    s3 = perf_counter()
    nr_clusters = compute_cluster_cores(bg)
    s4 = perf_counter()
    report["compute_cluster_cores"] = s4 - s3

    # Step 4: assign border points to clusters
    s5 = perf_counter()
    assign_border_points(bg)
    s6 = perf_counter()
    report["assign_border_points"] = s6 - s5
    
    try:
        bg.write_output(nr_clusters, path_out, assignment_nr)
    except IOError:
        print("could not write output to file:", path_out, file=sys.stderr)
    print("Cluster counter:", nr_clusters, file=sys.stderr)

    return report