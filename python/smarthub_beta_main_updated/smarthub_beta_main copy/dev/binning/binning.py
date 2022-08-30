import numpy as np
from nltk.cluster import KMeansClusterer
from nltk.cluster.util import cosine_distance
from sklearn.metrics import pairwise_distances_argmin_min

'''
This is the binning algorithm.

sample config: {'cos_sim_threshold':0.55,\
    'max_bins_threshold':-1,\
    'min_bin_size_threshold':3,\
    'sample_size':1_000,\
	'dims':100,\
    'cross_validate':True}

The COS_SIM_THRESHOLD=0.55 means that only words that are added to that bin are the ones for which
cosine(word,centroid) >= 0.55.

The MAX_BINS_THRESHOLD=50 means that we do not want the algorithm to create more than 50. By
default the value is -1 which means that there are no max limits on the total number of bins.

The MIN_BIN_SIZE_THRESHOLD=-1 means that even a bin containing only a single feature vector is valid. But if
for example MIN_BIN_SIZE_THRESHOLD=10, that means any bin containing less than 10 feature vectors will
have its corresponding binning_labels value assigned to -1. Hence can then be found with the code below:
for bin in binning_labels:
	if bin==-1:
		print(bin)

FEATURE_VECTOR_DIMS=100 means that each feature vector has 100 dimensions. By default the algorithm assumes
the consumer is using 100-dimensional feature vectors.
'''


class Bin:
    def __init__(self, FEATURE_VECTOR_DIMS=100):
        self._FEATURE_VECTOR_DIMS = FEATURE_VECTOR_DIMS
        self.centroid = np.zeros((self._FEATURE_VECTOR_DIMS,))
        self.size = 0

    def add(self, feature_vector):
        self.centroid += feature_vector
        self.size += 1

    def get_centroid(self):
        return self.centroid / self.size

    def get_size(self):
        return self.size


# The binning algorithm maintains the set of bins, and each bin contains the words that belong to that bin.
class Binning:
    def __init__(self, cos_sim_threshold=0.55, max_bins_threshold=-1, min_bin_size_threshold=-1,
                 feature_vector_dims=100, apply_as_prior_to_kmeans=False, verbose=0):
        self.binning_labels = []
        self.centroids = []
        self.bins = []

        self._COS_SIM_THRESHOLD = cos_sim_threshold
        self._MAX_BINS_THRESHOLD = max_bins_threshold
        self._MIN_BIN_SIZE_THRESHOLD = min_bin_size_threshold
        self._FEATURE_VECTOR_DIMS = feature_vector_dims
        self._APPLY_AS_PRIOR_TO_KMEANS = apply_as_prior_to_kmeans
        self._verbose = verbose

    # update the bin to bin_idx corresponding to the idx-th row in the input data
    def _update(self, bin_idx, feature_vector):
        bin = self.bins[bin_idx]
        bin.add(feature_vector)
        self.centroids[bin_idx] = bin.get_centroid()

    def _create(self, bin_idx, feature_vector):
        bin = Bin(self._FEATURE_VECTOR_DIMS)
        bin.add(feature_vector)

        if bin_idx < len(self.bins):
            print("bin_idx is less", bin_idx, "so create new")
            self.centroids[bin_idx] = bin.get_centroid()
            self.bins[bin_idx] = bin
        else:
            print("bin_idx already exists", bin_idx, "so add to existing")
            self.centroids.append(bin.get_centroid())
            self.bins.append(bin)

    def add_to_bin(self, bin_idx, feature_vector):
        if bin_idx < len(self.bins):
            bin = self.bins[bin_idx]
            bin.add(feature_vector)
            self.centroids[bin_idx] = bin.get_centroid()
        else:
            bin = Bin(self._FEATURE_VECTOR_DIMS)
            bin.add(feature_vector)
            self.centroids.append(bin.get_centroid())
            self.bins.append(bin)

    def _add(self, feature_vector):
        '''
        If this is first bin, we add it simply as the first bin
        '''
        if len(self.bins) == 0:
            bin_idx = 0
            self._create(bin_idx=bin_idx, feature_vector=feature_vector)
            self.binning_labels.append(bin_idx)
            return

        # compare the cosine distance between the word vector and each of the centroids.
        _, closest = pairwise_distances_argmin_min(self.centroids,
                                                   feature_vector.reshape(-1).reshape(-1, self._FEATURE_VECTOR_DIMS),
                                                   metric='cosine')

        # get the index of the bin corresponding to the closest distance and furthest distance
        min_bin_idx = np.argmin(closest)
        max_bin_idx = np.argmax(closest)

        '''
        If the distance is close enough to our COS_SIM_THRESHOLD, then add to the corresponding cluster and update its centroid.
        Otherwise, we need to create a new bin to hold the word. But only do that if we have not exceeded the MAX_BINS_THRESHOLD.
        If we have exceeded the MAX_BINS_THRESHOLD, then evict the bin with the largest centroid value (since on average the words
        in that bin are furthest away from the center).
        '''
        if 1 - closest[min_bin_idx] >= self._COS_SIM_THRESHOLD:
            bin_idx = min_bin_idx
            self._update(bin_idx=bin_idx, feature_vector=feature_vector)
            self.binning_labels.append(min_bin_idx)

        elif self._MAX_BINS_THRESHOLD == -1:
            bin_idx = len(self.bins)
            self._create(bin_idx=bin_idx, feature_vector=feature_vector)
            self.binning_labels.append(bin_idx)

        elif len(self.bins) < self._MAX_BINS_THRESHOLD:
            bin_idx = len(self.bins)
            self._create(bin_idx=bin_idx, feature_vector=feature_vector)
            self.binning_labels.append(bin_idx)

        else:
            bin_idx = max_bin_idx
            self._create(bin_idx=bin_idx, feature_vector=feature_vector)
            self.binning_labels.append(bin_idx)

    def get_size(self):
        return len(self.bins)

    def fit(self, X):
        total_data = len(X)
        if self._verbose:
            print("Verbose: Started binning on", total_data, "total feature vectors")
        for idx, feature_vector in enumerate(X):
            if idx % 1000 == 0:
                print("Verbose: Binned", idx, "feature vectors out of", total_data, "feature vectors")
            self._add(feature_vector)

        if self._verbose:
            print("Verbose: Completed binning with a total of", self.get_size(), "bins")

        if self._MIN_BIN_SIZE_THRESHOLD != -1:
            if self._verbose:
                print("Verbose: Started assigning bins with less than", self._MIN_BIN_SIZE_THRESHOLD,
                      "bin size to bin number -1")
            # if bin size is less then the minimum threshold
            ignore_bins = dict()
            for bin_idx, bin in enumerate(self.bins):
                if bin.size <= self._MIN_BIN_SIZE_THRESHOLD:
                    ignore_bins[bin_idx] = True

            for idx, bin_idx in enumerate(self.binning_labels):
                if bin_idx in ignore_bins:
                    self.binning_labels[idx] = -1

            copy_centroids = []
            copy_bins = []
            for bin_idx, (centroid, bin) in enumerate(zip(self.centroids, self.bins)):
                if bin_idx in ignore_bins:
                    continue
                copy_centroids.append(centroid)
                copy_bins.append(bin)
            del self.centroids
            self.centroids = copy_centroids
            del self.bins
            self.bins = copy_bins

            if self._verbose:
                print("Verbose: Completed assigning bins with less than", self._MIN_BIN_SIZE_THRESHOLD,
                      "bin size to -1, finding a total of", len(ignore_bins), "bins removed")

        if self._APPLY_AS_PRIOR_TO_KMEANS:
            if self._verbose:
                print("Verbose: Started running kmeans on", self.get_size(), "total bins and", len(self.centroids),
                      "total centroids with", total_data, "total data points")
            # kmeans=KMeans(n_clusters=self.get_size(),init=np.asarray(self.centroids),n_init=1,verbose=1)
            # kmeans=KMeans(n_clusters=self.get_size(),verbose=1)
            # kmeans.fit(X)
            # self.centroids=kmeans.cluster_centers_
            # for bin_idx,centroid in enumerate(self.centroids):
            #    self.bins[bin_idx].centroid=centroid
            # self.binning_labels=kmeans.labels_
            kmeans = KMeansClusterer(num_means=self.get_size(), distance=cosine_distance, initial_means=self.centroids,
                                     avoid_empty_clusters=True, repeats=1)
            self.binning_labels = kmeans.cluster(X, assign_clusters=True)
            self.centroids = kmeans.means()
            for bin_idx, centroid in enumerate(self.centroids):
                self.bins[bin_idx].centroid = centroid

            if self._verbose:
                print("Verbose: Completed running kmeans on", self.get_size(), "total bins and", len(self.centroids),
                      "total centroids with", len(self.binning_labels), "total data points")
