from time import perf_counter

def find_core_points(points, epsilon, min_pts, query_object):
    core_points = []
    for point in points:
        nr_neighbors = query_object.count_range(point, epsilon)
        if nr_neighbors < min_pts:
            point.cluster_label = 0
        else:
            core_points.append(point)
    return core_points

def remove_noise_points(points, epsilon, min_pts, query_object):
    for point in points:
            if point.is_labeled():
                query_object.delete_point(point)


def create_clusters(points, epsilon, min_pts, query_object, core_points):
    cluster_counter = 1
    for point in core_points:

        # Skip points that are already labeled
        if point.is_labeled():
            continue

        # New cluster:
        stack = [point]
        query_object.delete_point(point)

        while stack:
            cluster_point = stack.pop()
            cluster_point.cluster_label = cluster_counter            

            # Add neighbors to stack
            neighbors = query_object.report_range(cluster_point, epsilon)
            stack += neighbors
            for neighbor in neighbors:
                query_object.delete_point(neighbor)

        cluster_counter += 1

    return cluster_counter - 1

def find_clustering(points, epsilon, min_pts, query_object, report):
    """
    For every point in our dataset we find the set of it's neighbors N
    A neighbor is a point with distance smaller than or equal to epsilon
    If | N | < minPts it is not a core point and we move to the next point

    :param points       array of all points
    :param epsilon      epsilon as specified in lecture notes
    :param min_pts      minPts as specified in lecture notes
    :param query_object RangeQuery object used to find neighbours
    :return             number of clusters found
    """

    # Step 1: find all core points
    s1 = perf_counter()
    core_points = find_core_points(points, epsilon, min_pts, query_object)
    s2 = perf_counter()
    report["find_core_points"] = s2 - s1

    # Step 2: remove all noise points from the quad tree
    s3 = perf_counter()
    remove_noise_points(points, epsilon, min_pts, query_object)
    s4 = perf_counter()
    report["remove_noise_points"] = s4 - s3
    
    # Step 3: create clusters
    
    s5 = perf_counter()
    n_clusters =  create_clusters(points, epsilon, min_pts, query_object, core_points) # disregard the noise points, which carry label 0
    s6 = perf_counter()
    report["create_clusters"] = s6 - s5

    return n_clusters