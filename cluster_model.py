CENTROIDS = [
    [2.923076923076923, 3.076923076923077, 2.8461538461538463, 4.0],
    [3.0, 3.6, 1.4, 1.6],
    [4.2, 4.6, 4.0, 4.6],
]


def predict_cluster(skills):
    best_cluster = 0
    best_distance = None
    for cluster, centroid in enumerate(CENTROIDS):
        distance = 0
        for value, center in zip(skills, centroid):
            diff = value - center
            distance += diff * diff
        if best_distance is None or distance < best_distance:
            best_distance = distance
            best_cluster = cluster
    return best_cluster
