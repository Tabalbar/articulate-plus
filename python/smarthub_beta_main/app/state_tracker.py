from collections import OrderedDict

import numpy as np
from sklearn.metrics import pairwise_distances_argmin_min

from .state_utils import StateUtils


class StateTracker:
    def __init__(self, search_window_size=-1):
        self.history = OrderedDict()
        self.history_state = OrderedDict()
        self.history_id = 0
        self.search_window_size = search_window_size

    def __str__(self):
        s = ''
        for history_id, spec in self.history.items():
            s += "History ID " + str(history_id) + '\n' + \
                 'Action ' + str(spec.visualization_task.action) + '\n' + \
                 'Context Utterances ' + str(spec.visualization_task.context_utterances) + '\n' + \
                 'Aggregators ' + str([a[0] for a in spec.visualization_task.aggregators]) + '\n' + \
                 'Filters ' + str(spec.visualization_task.filters) + '\n' + \
                 'Plot Type ' + str(spec.plot_headline.plot_type) + '\n' + \
                 'Dialogue Act ' + str(spec.dialogue_act) + '\n\n'
        s += '\n\n'
        return s

    def get_plot_headline_history(self, cosine_similarity, search_history_id_before=-1):
        if not self.history:
            return None

        history_specs = []
        if cosine_similarity:
            for cos_sim, (history_id, history_spec) in zip(cosine_similarity, self.history.items()):
                if search_history_id_before != -1 and history_id >= search_history_id_before:
                    break

                history_specs.append((cos_sim, history_spec.plot_headline))
        else:
            for history_id, history_spec in self.history.items():
                if search_history_id_before != -1 and history_id >= search_history_id_before:
                    break

                history_specs.append((0.0, history_spec.plot_headline))

        return history_specs

    def add_visualization_specification(self, visualization_specification):
        self.history[self.history_id] = visualization_specification
        self.history_state[self.history_id] = StateUtils.transform_to_feature_vector(visualization_specification)
        self.history_id += 1

    def remove_visualization_specification(self, visualization_specification):
        if not self.history:
            return

        del self.history[visualization_specification.plot_headline.id]
        del self.history_state[visualization_specification.plot_headline.id]

    '''
    - Suppose the history entries are as follows:
            history[0]: line chart
            history[1]: bar chart
            history[2]: heatmap
            history[3]: heatmap
            history[5]: heatmap
            history[8]: line chart
    
    - Suppose search_window_size = -1.
        - search_most_recent_visualization_specification_by_plot_type(plot_type='line chart') returns history[8].
        - search_most_recent_visualization_specification_by_plot_type(plot_type='bar chart') returns history[1].
    
    - Suppose search_window_size = 3. then, our search space is reduced:
            history[3]: heatmap
            history[5]: heatmap
            history[8]: line chart
            
        - search_most_recent_visualization_specification_by_plot_type(plot_type='bar chart') returns None.
    '''

    def search_most_recent_visualization_specification_by_plot_type(self, plot_type, search_history_id_before=-1):
        # if history is empty or search_window_size is 0, then end early.
        if not self.history or self.search_window_size == 0:
            distance_to_found_visualization_specification = -1
            return distance_to_found_visualization_specification, None

        # get the search space.
        visualization_specification_search_space = []
        for idx, (history_id, history_spec) in enumerate(self.history.items()):
            if search_history_id_before != -1 and history_id >= search_history_id_before:
                break

            visualization_specification_search_space.append((history_id, history_spec))

        if self.search_window_size != -1:
            # adjust search space based on search_window_size.
            visualization_specification_search_space = \
                visualization_specification_search_space[-1 * self.search_window_size:]

        # search the plot_type, starting from most recent history entry.
        # end early if search_window_size is exceeded.
        for idx, (history_id, visualization_specification) in enumerate(
                reversed(visualization_specification_search_space)):
            if visualization_specification.plot_headline.plot_type == plot_type:
                distance_to_found_visualization_specification = idx
                return distance_to_found_visualization_specification, visualization_specification

        # no plot_type matched in the history
        distance_to_found_visualization_specification = -1
        return distance_to_found_visualization_specification, None

    '''
    - Suppose the history entries are as follows:
            history[0]
            history[1]
            history[2]
            history[3]
            history[5]
            history[8]
    
    - search_visualization_specification_by_history_id(target_history_id=-1) will return history[8].
    - search_visualization_specification_by_history_id(target_history_id=7) will return None.
    - search_visualization_specification_by_history_id(target_history_id=3) will return history[3].
    - search_visualization_specification_by_history_id(target_history_id=2) will return history[2].
    
    - Suppose search_window_size = 3. then, our search space is reduced:
            history[3]
            history[5]
            history[8]

    - search_visualization_specification_by_history_id(target_history_id=-1) will return history[8].
    - search_visualization_specification_by_history_id(target_history_id=7) will return None.
    - search_visualization_specification_by_history_id(target_history_id=3) will return history[3].
    - search_visualization_specification_by_history_id(target_history_id=2) will return None.
    '''

    def search_visualization_specification_by_history_id(self, target_history_id, search_history_id_before=-1):
        if not self.history or self.search_window_size == 0:
            distance_to_found_visualization_specification = -1
            return distance_to_found_visualization_specification, None

        # get the search space.
        visualization_specification_search_space = []
        for idx, (history_id, history_spec) in enumerate(self.history.items()):
            if search_history_id_before != -1 and history_id >= search_history_id_before:
                break

            visualization_specification_search_space.append((history_id, history_spec))

        if self.search_window_size != -1:
            # adjust search space based on search_window_size.
            visualization_specification_search_space = \
                visualization_specification_search_space[-1 * self.search_window_size:]

        if target_history_id == -1:
            # when target_history_id is -1, need to get most recent entry in history.
            distance_to_found_visualization_specification = 0
            most_recent_history_id, most_recent_history_spec = visualization_specification_search_space[-1]
            return distance_to_found_visualization_specification, most_recent_history_spec

        # otherwise search for the target_history_id in the search space
        for idx, (history_id, history_spec) in enumerate(visualization_specification_search_space):
            if target_history_id == history_id:
                distance_to_found_visualization_specification = \
                    len(visualization_specification_search_space) - (idx + 1)
                return distance_to_found_visualization_specification, history_spec

        # no matching id in the history so return None.
        distance_to_found_visualization_specification = -1
        return distance_to_found_visualization_specification, None

    '''
    The purpose of this method is to search for a prev spec that is cosine similar to the vis spec.
    
    - minimum_similarity_cutoff: minimum cosine similarity value required to be considered a match.
    - search_state_id_before: only search for prev specs before this state id.
        - useful for evaluation: only search for earlier vis specs since the more recent vis specs 
          do not technically exist yet hence should not be matched against during search.
    - EPSILON_INIT: subtract this amount from each feature vector, this value decays during decay window time.
    - START_EPSILON_DECAYING: start decaying value at this index (i.e., start of decay window).
    - END_EPSILON_DECAYING: end decaying value at this index (i.e., end of decay window).
        - example:
            Suppose below are the 6 vis spec entries in history, i.e., history[8] is the most recent vis spec entry 
            in the history.
            
            Also parameters are set:
                EPSILON_INIT = 1.0,
                START_EPSILON_DECAYING = 3
                END_EPSILON_DECAYING = 6.
            
            Then, 
                EPSILON_DECAY_VALUE = 1.0 / (6-3) = 0.33
            
            history[0]: feature_vector(history[0]) - 1.0
            history[1]: feature_vector(history[1]) - 1.0
            history[2]: feature_vector(history[2]) - 1.0
            history[3]: feature_vector(history[3]) - 0.67   (start of decay window)
            history[5]: feature_vector(history[5]) - 0.34   (part of decay window)
            history[8]: feature_vector(history[8]) - 0.01   (end of decay window)
            
            hence, we can see that the most recent entry (i.e., history[8]) is essentially untouched, hence
            has much higher chance of being matched against then compared to history[0], which lost almost all of
            its value. this is consistent with idea that user will more likely refer to the recent past than to
            the distant past.
    - search_window_size: only consider the most recent window_search_size entries of history. if the
      window_search_size = 3, then in our running example this means consider only 3 most recent entries
      for the prev spec search:
            history[3]: feature_vector(history[3]) - 0.67   (start of decay window)
            history[5]: feature_vector(history[3]) - 0.34   (part of decay window)
            history[8]: feature_vector(history[4]) - 0.01   (end of decay window)       
    
    General algorithm flow:
        1. if no history exists or search_window_size is 0:
            end early.
        2. query = convert vis_spec to a numerical feature vector
        3. START_EPSILON_DECAYING: start decay window at half way of the history.
        4. END_EPSILON_DECAYING: end decay window at the end of the history.
        5. EPSILON_DECAY_VALUE: subtract this amount from EPSILON_INIT during decay window.
        6. search_space = []
           for each (history_id, feature vector) in the history:
               if history_id >= search_history_id_before:
                   break out of this loop
                    
               feature_vector = feature vector - EPSILON_INIT.
               add feature_vector to search_space. 
               if in the most recent half of history (i.e., decay window):
                   EPSILON_INIT = EPSILON_INIT - EPSILON_DECAY_VALUE
        7. search_space = 
            only consider the most recent search_window_size entries of search_space.
        8. search_space_vis_specs = []
           for each (history_id, vis spec) in the history:
            if history_id >= search_history_id_before:
                break out of this loop
            add vis_spec of search_space_vis_specs.
        9. search_space_vis_specs = 
            only consider the most recent search_window_size entries of search_space_vis_specs
        10. found_vis_spec, cos_sim = search the query in the search_space using cosine similarity measure.
        11. if vis_spec has no filters or attributes: 
            return most recent vis spec in history.
        12. if cos_sim >= minimum_similarity_cutoff:
                return found_vis_spec.
            otherwise
                return None
    '''

    def search_closest_cosine_similar_previous_visualization_specification(self, visualization_specification,
                                                                           minimum_similarity_cutoff=0.0,
                                                                           search_history_id_before=-1,
                                                                           EPSILON_INIT=1.0,
                                                                           START_EPSILON_DECAYING=-1,
                                                                           END_EPSILON_DECAYING=-1):
        # if no history exists or window size is 0, end early.
        if not self.history or self.search_window_size == 0:
            distance_to_found_visualization_specification = -1
            return distance_to_found_visualization_specification, None, None, None, None

        # transform vis spec to feature vector.
        query = StateUtils.transform_to_feature_vector(visualization_specification)

        # start decay window at half way of the history (i.e., start of decay window).
        if START_EPSILON_DECAYING == -1:
            START_EPSILON_DECAYING = len(self.history_state) // 2

        # end decaying value at this index (i.e., end of decay window).
        if END_EPSILON_DECAYING == -1:
            END_EPSILON_DECAYING = len(self.history_state)

        # the amount of value to subtract from EPSILON_INIT during decay window.
        EPSILON_DECAY_VALUE = EPSILON_INIT / (END_EPSILON_DECAYING - START_EPSILON_DECAYING)

        # build the feature vector search space.
        feature_vector_search_space = []
        for idx, (history_id, history_feature_vector) in enumerate(self.history_state.items()):
            if search_history_id_before != -1 and history_id >= search_history_id_before:
                break

            feature_vector_search_space.append((history_id, history_feature_vector * (1 - EPSILON_INIT)))

            if END_EPSILON_DECAYING >= idx + 1 > START_EPSILON_DECAYING:
                EPSILON_INIT -= EPSILON_DECAY_VALUE

        if not feature_vector_search_space:
            distance_to_found_visualization_specification = -1
            return distance_to_found_visualization_specification, None, None, None, None

        # adjust the feature vector search space for search_window_size most recent history.
        if self.search_window_size != -1:
            feature_vector_search_space = feature_vector_search_space[-1 * self.search_window_size:]

        # bulid the vis spec search space.
        visualization_specification_search_space = []
        for state_idx, (history_id, history_spec) in enumerate(self.history.items()):
            if search_history_id_before != -1 and history_id >= search_history_id_before:
                break
            visualization_specification_search_space.append(history_spec)

        if not visualization_specification_search_space:
            distance_to_found_visualization_specification = -1
            return distance_to_found_visualization_specification, None, None, None, None

        # adjust the vis spec search space for search_window_size most recent history.
        if self.search_window_size != -1:
            visualization_specification_search_space = visualization_specification_search_space[
                                                       -1 * self.search_window_size:]

        # transform feature vector search space into matrix representation.
        feature_vector_search_space_matrix = None
        for idx, (id, feature_vector) in enumerate(feature_vector_search_space):
            if idx == 0:
                feature_vector_search_space_matrix = feature_vector
            else:
                feature_vector_search_space_matrix = np.vstack([feature_vector_search_space_matrix, feature_vector])
        feature_vector_search_space_matrix = feature_vector_search_space_matrix.reshape(
            int(feature_vector_search_space_matrix.shape[0] / StateUtils.get_state_size()), -1)

        # transform query feature vector into matrix representation.
        query_matrix = query.reshape(1, -1)

        # search the feature vector search space for the query.
        _, closest = pairwise_distances_argmin_min(feature_vector_search_space_matrix, query_matrix, metric='cosine')

        # transform closest distances into cosine similarity values.
        cosine_similarity = [1 - dist for dist in closest]

        # if the vis_spec has no filters and no attributes, the query_matrix is all 0's, hence just return
        # the most recent vis spec from history.
        if not visualization_specification.visualization_task.filters and not \
                visualization_specification.visualization_task.aggregators:
            print(".........................In shared create vis from existing template discourse rules..............................")
            print(".........................No filters or aggregators..............................")
            distance_to_found_visualization_specification = 0
            return distance_to_found_visualization_specification, \
                   self.get_plot_headline_history(cosine_similarity, search_history_id_before), \
                   cosine_similarity, \
                   visualization_specification_search_space[-1], \
                   -1

        # this is the result of our search, i.e., found_vis_spec.
        idx = np.argmax(cosine_similarity)
        distance_to_found_visualization_specification = len(visualization_specification_search_space) - (idx + 1)

        # return found_vis_spec if cosine similarity exceeds minimum threshold, otherwise return None.
        if cosine_similarity[idx] >= minimum_similarity_cutoff:
            return distance_to_found_visualization_specification, \
                   self.get_plot_headline_history(cosine_similarity, search_history_id_before), \
                   cosine_similarity, \
                   visualization_specification_search_space[idx], \
                   idx
        else:
            return distance_to_found_visualization_specification, \
                self.get_plot_headline_history(cosine_similarity, search_history_id_before), \
                cosine_similarity, \
                None, \
                None
