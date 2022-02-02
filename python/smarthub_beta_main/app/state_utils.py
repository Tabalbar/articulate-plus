import numpy as np

from dev.corpus_feature_extractor import CorpusFeatureExtractorUtils

'''
The big picture problem we are solving is:                                            
Given the history of dialogue states up until now (i.e, s1, ..., sN), what is the best
action to take?
                                                                       
Dialogue State Tracking helps address this problem:
- Consider N dialogue states: S = [s1, s2, s3, ..., sN]
s1: vis spec corresponding to the first request made by the user,
.
.
.
sN: vis spec corresponding to the latest request made by the user.
- also consider, a*, the best action, is the system response, i.e., new vis spec. 
- Example:
Suppose user has so far made N-1 requests, and the Jth request = 'Show me a map of thefts in the neighborhoods'. 

Then, the dialogue state history is as follows:
S = [..., sJ = (map, thefts, neighborhood),...sN-1].

- if the new, Nth user request = "Can you do the same map graph but for assaults this time?".
- then,  a* = sN = (map, assault, neighborhood) = copying vis spec of sJ and changing "thefts" to "assaults".

In this class, we define the vector representation of a dialogue state as a 10 X 100 dimensional vector:
10 aggregate attributes (year, interval, neighborhood, location, month, crime, day, season, time, plot type)
X
100 dimensional embedding vector.

Example:
sJ = (map, thefts, neighborhood):
10 X 100  dim: (year    interval    neighborhood            location    month       crime               day     season      time    plot type)
                 0         0       embedding(neighborhood)    0           0         avg(                0        0          0    embedding(map)
                                                                                        embedding(crime),
                                                                                        embedding(thefts)
                                                                                    )     
'''


class StateUtils:
    entity_lookup = CorpusFeatureExtractorUtils.get_context_based_corpus_entity_extractor().entity_lookup
    embedding_model = entity_lookup.get_embeddings()
    aggregate_vocab = entity_lookup.get_all_names_embeddings()
    filter_vocab = entity_lookup.get_all_values_embeddings()

    AGGREGATE_FILTER_IDX = 0
    # FILTER_IDX=AGGREGATE_IDX+len(aggregate_vocab)
    # FILTER_IDX=0
    # CONTEXT_AGGREGATE_IDX=FILTER_IDX+len(filter_vocab)
    # CONTEXT_FILTER_IDX=CONTEXT_AGGREGATE_IDX+len(aggregate_vocab)
    # PLOT_TYPE_IDX=CONTEXT_FILTER_IDX+len(filter_vocab)
    # PLOT_TYPE_IDX=FILTER_IDX+len(filter_vocab)
    PLOT_TYPE_IDX = AGGREGATE_FILTER_IDX + len(aggregate_vocab)

    # HORIZONTAL_AXIS_IDX=PLOT_TYPE_IDX+1
    # HORIZONTAL_GROUP_AXIS_IDX=HORIZONTAL_AXIS_IDX+3
    # VERTICAL_AXIS_IDX=HORIZONTAL_GROUP_AXIS_IDX+3

    @staticmethod
    def _average_feature_vectors(feature_vector1, feature_vector2):
        for idx, (feature1, feature2) in enumerate(zip(feature_vector1, feature_vector2)):
            if np.any(feature1 == np.zeros(feature1.shape)):
                feature_vector1[idx] += feature2
                continue

            if np.any(feature2 == np.zeros(feature2.shape)):
                continue

            feature_vector1[idx] = (feature1 + feature2) / 2

        return feature_vector1

    @staticmethod
    def transform_to_feature_vector(visualization_specification):
        feature_vector = np.zeros((StateUtils.get_state_size(), StateUtils.embedding_model._dims))

        if visualization_specification.visualization_task.aggregators:
            aggregators = [attribute for attribute, entity_children in
                           visualization_specification.visualization_task.aggregators]
            aggregate_vector = np.zeros((len(StateUtils.aggregate_vocab), StateUtils.embedding_model._dims))
            for aggregate in aggregators:
                idx, embedding = StateUtils.aggregate_vocab[aggregate.lower()]
                aggregate_vector[idx] = embedding
            feature_vector[StateUtils.AGGREGATE_FILTER_IDX:StateUtils.PLOT_TYPE_IDX] = \
                StateUtils._average_feature_vectors(
                    feature_vector[StateUtils.AGGREGATE_FILTER_IDX:StateUtils.PLOT_TYPE_IDX], aggregate_vector)

        if visualization_specification.visualization_task.filters:
            filter_vector = np.zeros((len(StateUtils.aggregate_vocab), StateUtils.embedding_model._dims))
            for filter_aggregate, filter_values in visualization_specification.visualization_task.filters.items():
                idx, parent_embedding = StateUtils.aggregate_vocab[filter_aggregate.lower()]
                for filter_value in filter_values:
                    _, child_embedding = StateUtils.filter_vocab[filter_value.lower()]
                    filter_vector[idx] += child_embedding
                filter_vector[idx] += parent_embedding
                filter_vector[idx] /= len(filter_values) + 1
            feature_vector[StateUtils.AGGREGATE_FILTER_IDX:StateUtils.PLOT_TYPE_IDX] = \
                StateUtils._average_feature_vectors(
                    feature_vector[StateUtils.AGGREGATE_FILTER_IDX:StateUtils.PLOT_TYPE_IDX], filter_vector)

        if visualization_specification.plot_headline.plot_type:
            plot_type_vector = StateUtils.embedding_model.get_token_embedding(
                None, visualization_specification.plot_headline.plot_type.lower())
            feature_vector[StateUtils.PLOT_TYPE_IDX] = plot_type_vector

        return feature_vector

    @staticmethod
    def get_state_size():
        return StateUtils.PLOT_TYPE_IDX + 1
