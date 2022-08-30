from copy import deepcopy

from dev.text_tokenizer_pipeline import EntityPOSAndTemporalFilter, TemporalUtils
from .visualization_task import VisualizationTask


class VisualizationTaskConstructor:
    def __init__(self):
        pass

    '''
    The purpose of merge_construct is to inform the current task of the information known by
    a previous task, in particular the filters and aggregators.
    '''
    @staticmethod
    def merge_construct(previous_task, current_task):
        # get the previous filters and aggregators.
        previous_filters, previous_aggregators = \
            previous_task.filters, previous_task.aggregators
        print("Prev filter: "+str(previous_filters))
        print("Prev aggregator: "+ str(previous_aggregators))

        # get the current filters and aggregators.
        current_filters, current_aggregators = \
            current_task.filters, current_task.aggregators
        print("Current filter: "+str(current_filters))
        print("Current aggregator: "+ str(current_aggregators))

        # create merged task as a identical copy of prev task.
        merged_task = deepcopy(previous_task)

        # update merged task utterances to the current task utterances.
        merged_task.context_utterances = current_task.context_utterances

        # update merged task plot type with the current task plot type.
        merged_task.plot_type = current_task.plot_type

        # if plot type altered (map to another or another to map), accordingly update
        # sql query with removing latitude and longitude or adding latitude and longitude.
        if 'map' not in previous_task.plot_type and 'map' in current_task.plot_type:
            # print(" In if 'map' not in previous_task.plot_type and 'map' in current_task.plot_type:")
            if "NUM_COUNTIES" in merged_task.vertical_axis:
                # print("............in inner if.............")
                # "TOTAL CRIME" is not in the vertical axis always (i.e., only when dialogue act is create\modify vis).
                merged_task.remove_vertical_axis("NUM_COUNTIES")
            elif "NUM_CASES" in merged_task.vertical_axis:
                 merged_task.remove_vertical_axis("NUM_CASES")
                # merged_task.remove_aggregator(current_task.aggregators)
            # print("*****************"+ str(current_aggregators[0]))
            # merged_task.sql.add_select(current_aggregators[0])
            merged_task.sql.add_select('fips')
            # merged_task.sql.add_select('longitude')
            merged_task.update_specification()
        elif 'map' in previous_task.plot_type:
            if 'map' not in current_task.plot_type and merged_task.is_plot_type_specified:
                if 'bar' in current_task.plot_type:
                    if 'new_cases' in merged_task.aggregators:
                        merged_task.add_vertical_axis("NUM_CASES")
                        merged_task.sql.remove_group_by('fips')
                        merged_task.sql.remove_select('fips')
                        merged_task.update_specification()
                    else:
                        merged_task.add_vertical_axis("NUM_COUNTIES")
                        temp = next(iter(merged_task.aggregators))
                        merged_task.sql.add_select(temp[0])
                        merged_task.add_aggregator_map(temp[0])
                        merged_task.sql.remove_group_by('fips')
                        merged_task.sql.remove_select('fips')
                        # merged_task.sql.add_select
                        merged_task.update_specification()
            elif 'map' not in current_task.plot_type and not merged_task.is_plot_type_specified:
                merged_task.sql.add_select("fips")
                temp = next(iter(merged_task.aggregators))
                merged_task.sql.add_select(temp[0])
                merged_task.add_aggregator_map(temp[0])
                merged_task.plot_type = "heat map"
                merged_task.map_type = "geographical"

        if current_filters:
            # get curr task filter attributes.
            curr_attributes = set((current_filters.keys()))

            # get prev task filter attributes.
            prev_attributes = set((previous_filters.keys()))

            if not curr_attributes.intersection(prev_attributes):
                # curr and prev task do not share filters.
                # default to prev task filters from merged task.
                # e.g.,
                #   prev request = "Show me theft <filter> broken down by neighborhood <aggregator>?"
                #   curr request = "Can you show me this same graph but for schools <filter> this time?"
                # hence, prev filter = "crime=theft", curr filter = 'location=school'.
                pass
            else:
                # otherwise curr and prev task do share filters.
                # remove the shared filters from merged task.
                # e.g.,
                #   prev request = "Show me theft <filter> broken down by neighborhood <aggregator>?"
                #   curr request = "Can you show me this same graph but for assaults <filter> this time?"
                # hence, prev filter = "crime=theft", curr filter = 'crime=assault'.
                for attribute, values in current_filters.items():
                    if len(values) > 1:
                        continue

                    merged_task.remove_filter(attribute)

            # if curr and prev task do not share filters, remove all prev task filters
            # from merged task, retaining only the curr task filters.

            # if curr and prev task do share filters, remove all of these shared filters
            # from merged task, retaining only the non-shared prev + non-shared curr task filters.
            merged_task.add_all_filters(current_filters)

        if current_aggregators:
            # print("......................in current aggregators.........................")
            # get the curr task temporal aggregators.
            curr_temporal_attribute = TemporalUtils.get_first_temporal_attribute(current_aggregators)
            # print("get the curr task temporal aggregators. "+str(curr_temporal_attribute))

            # get the prev task temporal aggregators.
            prev_temporal_attribute = TemporalUtils.get_first_temporal_attribute(previous_aggregators)

            if curr_temporal_attribute and prev_temporal_attribute:
                # if both prev and curr tasks contain temporal aggregators, remove prev task one
                # from merged task.
                # e.g.,
                #   prev request = "Show me theft <filter> broken down by month <aggregator>?"
                #   curr request = "Can you show me this same graph but for years <aggregator> this time?"
                # hence, prev temporal aggregator = "month", curr temporal aggregator = 'year'.
                merged_task.remove_aggregator(prev_temporal_attribute)
            elif not current_aggregators.intersection(previous_aggregators):
                # otherwise if curr task and prev task do not share any aggregators, remove all prev task aggregators.
                # e.g.,
                #   prev request = "Show me theft <filter> broken down by year <aggregator>?"
                #   curr request = "Can you show me this same graph but for location <aggregator> this time?"
                # hence, prev aggregator = "year", curr aggregator = 'location'.
                merged_task.remove_all_aggregators()

            # if curr and prev task contain temporal aggregators, remove the prev task one
            # from merged task, replacing with curr task temporal aggregator + all other prev task aggregators
            # + all curr task aggregators.

            # if either curr and prev task do not contain temporal aggregators, then:
            #   if they do not share aggregators, then:
            #       remove all prev task aggregators from merged task, retaining only the curr task aggregators.
            #   otherwise if they do share some aggregators, then:
            #       retain the non-shared prev task aggregators + non-shared curr task aggregators +
            #       shared aggregators.
            merged_task.add_all_aggregators(current_aggregators)
        # else:
        #     merged_task.remove_all_aggregators()

        # update summary
        merged_task.get_summary()

        return merged_task

    @staticmethod
    def construct(setup_utterances, request_utterance, dialogue_act, referring_expression):
        # get the dialogue act and end early if it is not a request.
        top_dialogue_act_label, bottom_dialogue_act_label = dialogue_act
        if top_dialogue_act_label != 'merged':
            return None

        # plot type override through referring expression :Can I see the last graph as a map
        is_plot_type_override = False
        # if the utterance has explicit mention of plot type


        # create new task.
        visualization_task = VisualizationTask()

        # default plot type is bar chart.
        visualization_task.plot_type = 'bar chart'
        visualization_task.is_plot_type_specified = False

        # the y-axis is the total crime counts in all kinds of plots except maps.
        visualization_task.add_vertical_axis("NUM_COUNTIES")

        # sql queries will select from chicagocrime database.
        visualization_task.sql.add_from('counties_cdc_cases')

        # update context utterances with the setup and request utterances.
        visualization_task.context_utterances = {'setup': [utterance.text for utterance in setup_utterances],
                                                 'request': request_utterance.text}

        # search through the setup utterances for any filters and\or aggregators.
        for utterance in setup_utterances:
            # iterate through words of current setup utterance.
            for token in utterance:
                # if not a data attribute, then cannot be filter or aggregator so end early.
                if not token._.entity_data_attribute:
                    continue

                if bottom_dialogue_act_label == 'winmgmt':
                    if not visualization_task.action and token.pos_ == 'VERB':
                        # if it is win mgmt request, skip early for verbs since these words
                        # cannot be filters or aggregators.
                        continue

                # if it is a parent entity, then must be an aggregator, so add it to the new task.
                # e.g., add "neighborhood" from utterance "Show me theft <filter> by neighborhood <aggregator>"
                if token._.is_entity and token._.is_entity_name:
                    visualization_task.add_context_aggregator(token._.entity,
                                                              tuple([child for child in token._.entity_children if
                                                                     child is not None and '\\' not in child]))

                    visualization_task.add_aggregator(token._.entity,
                                                      tuple([child for child in token._.entity_children if
                                                             child is not None and '\\' not in child]))

                # otherwise it is a child entity, so add it as a filter to the new task.
                # e.g., add "theft" from utterance "Show me theft <filter> by neighborhood <aggregator>"
                elif token._.is_entity:
                    visualization_task.add_context_filter(token._.entity, token._.entity_value[0])
                    visualization_task.add_filter(token._.entity, token._.entity_value[0])

        # iterate through the words of the request utterance.
        for token in request_utterance:
            if bottom_dialogue_act_label == 'winmgmt':
                if token._.entity == 'winmgmt':
                    # if it is a win mgmt request and a win mgmt attribute, assign action to it.
                    # e.g., action="close" in utterance "Can you close <win mgmt attribute> the graph?"
                    visualization_task.action = token._.entity_value[0]
                    continue

            if not visualization_task.action and token.pos_ == 'VERB' and token.tag_ != 'MD':
                # update action with the current word if it is a non modal verb.
                # e.g., action="make" in "Can <modal verb> you make <non-modal verb> this graph bigger"
                visualization_task.action = token.text
                continue

            if token._.entity == 'winmgmt' and token.pos_ == 'ADJ':
                # if the current word is an adjective and a win mgmt attribute then update action to this word.
                # e.g., action="bigger" in "Can you make this graph bigger <adjective, win mgmt> please?"
                visualization_task.action = token.text
                continue

            if token._.entity == 'visualization':
                if referring_expression:
                    #for referring_expression in referring_expressions:
                    referring_expressions_range = range(referring_expression.get_start_char_idx(),
                                                        referring_expression.get_end_char_idx())
                    if not token.idx in referring_expressions_range:
                        # if the word is a visualization attribute and not part of referring expression
                        # then update plot type to corresponding attribute value.
                        # e.g., plot type="map" in "Can you show this graph <ref exp is "this graph",
                        # graph is vis attribute> as a map <plot type falls outside of "this graph" ref exp>.
                        if not token._.is_entity_name:
                            visualization_task.plot_type = token._.entity_value[0]
                            is_plot_tye_override = True
                else:
                    # if no ref exps exists, then just directly update plot type.
                    # e.g., plot type="map" in "Show me thefts for each neighborhood as a map <vis attribute>"
                    if not token._.is_entity_name:
                        # print("TOKEN entity visualization :"+str(token))
                        visualization_task.plot_type = token._.entity_value[0]
                        visualization_task.is_plot_type_specified = True

                continue
            if referring_expression:
                print("*******referring expression**********")


            # if the word is not a data attribute then cannot be a filter or aggregator.
            if not token._.entity_data_attribute:
                # print("Token not a data attribute: "+str(token))
                continue
            # If token is an entity ---> Filters and Aggregators
            # Check if token is an aggregator (slot)
            if token._.is_entity and token._.is_entity_name:

                # if word is a parent attribute, then add as aggregator to the new task.
                # e.g., add "neighborhood" from utterance "Show me theft <filter> by neighborhood <aggregator>"
                visualization_task.add_aggregator(token._.entity,
                                                  tuple([child for child in token._.entity_children if
                                                         child is not None and '\\' not in child]))
                if token._.is_continuous_temporal:
                    visualization_task.plot_type = "line chart"
                else:
                    visualization_task.add_horizontal_axis_grouping(token._.entity)
            # Check if token is a filter (Slot value)
            elif token._.is_entity:

                # otherwise if word is a child attribute, then add as filter to the new task.
                # add "theft" from utterance "Show me theft <filter> by neighborhood <aggregator>"
                    # sql.add_from('counties_cdc_cases')
                if type(token._.entity_value) == list:
                    visualization_task.add_filter(token._.entity, token._.entity_value[0])
                else:
                    visualization_task.add_filter(token._.entity, token._.entity_value)

        visualization_task.redistribute_horizontal_axis_variables()
        if bottom_dialogue_act_label in ['createvis', 'modifyvis']:
            #number of cases
            if 'new_cases' in visualization_task.filters or 'line' in visualization_task.plot_type :
                print("Number of cases")
                if visualization_task.aggregators:
                    print("Number of cases with aggregator")
                    visualization_task.remove_vertical_axis("NUM_COUNTIES")
                    visualization_task.add_vertical_axis_sum("NUM_CASES")
                    visualization_task.sql.add_select("date")
                    visualization_task.sql.add_group_by("date")
                    visualization_task.sql.add_select(list(visualization_task.aggregators)[0][0])
                    visualization_task.sql.add_group_by(list(visualization_task.aggregators)[0][0])
                    visualization_task.remove_filter('new_cases')
                    visualization_task.remove_filter('date')
                    visualization_task.plot_type = "line"
                else:
                    visualization_task.remove_vertical_axis("NUM_COUNTIES")
                    visualization_task.add_vertical_axis_sum("NUM_CASES")
                    visualization_task.sql.add_select("date")
                    visualization_task.sql.add_group_by("date")
                    visualization_task.add_horizontal_axis("date")
                    # visualization_task.add_aggregator("date")
                    visualization_task.remove_filter('new_cases')
                    visualization_task.remove_filter('date')
                    visualization_task.plot_type = "line"
            #Case 1a: ONLY one aggregators are there in the utterance and the plot will be map type
            #I want to see the rate of diabetes <aggregator> in the US. (general query, one aggregator)
            else:
                if 'map' not in visualization_task.plot_type and visualization_task.aggregators:
                    if not visualization_task.is_plot_type_specified and not is_plot_type_override:
                        if len(visualization_task.aggregators) == 1:
                            if visualization_task.any_aggregator_geographically_relevant():
                                print("one geographically relevant aggregator --> bar chart")
                                visualization_task.add_horizontal_axis(list(visualization_task.aggregators)[0][0])
                                visualization_task.sql.add_group_by(list(visualization_task.aggregators)[0][0])
                            else:
                                visualization_task.remove_vertical_axis("NUM_COUNTIES")
                                visualization_task.sql.add_select("fips")
                                temp = next(iter(visualization_task.aggregators))
                                visualization_task.sql.add_select(temp[0])
                                visualization_task.add_aggregator_map(temp[0])
                                visualization_task.plot_type = "heat map"
                                visualization_task.map_type = "geographical"
                        elif len(visualization_task.aggregators) == 2:
                            #Case 2:if there are two aggregators it will not be a map
                            if visualization_task.any_aggregator_geographically_relevant():
                                print("*****geographically relevant aggregator******")
                                visualization_task.sql.add_select(list(visualization_task.aggregators)[0][0])
                                visualization_task.sql.add_select(list(visualization_task.aggregators)[1][0])
                                visualization_task.add_horizontal_axis(list(visualization_task.aggregators)[1][0])
                                visualization_task.add_horizontal_axis(list(visualization_task.aggregators)[0][0])
                            else:
                                visualization_task.plot_type = "heat map"
                                visualization_task.map_type = "non_geographical" #non-geographical heat map
                                visualization_task.sql.add_select(list(visualization_task.aggregators)[0][0])
                                visualization_task.sql.add_select(list(visualization_task.aggregators)[1][0])
                                visualization_task.add_horizontal_axis(list(visualization_task.aggregators)[1][0])
                                visualization_task.add_horizontal_axis(list(visualization_task.aggregators)[0][0])
                            # visualization_task.add_first_aggregator(list(visualization_task.aggregators)[0][0])
                            # visualization_task.add_aggregator(list(visualization_task.aggregators)[1][0])

                    #Case 1b: user asks for a bar chart
                    elif visualization_task.is_plot_type_specified and visualization_task.plot_type == "bar chart":
                        temp = next(iter(visualization_task.aggregators))
                        visualization_task.sql.add_select(temp[0])
                        # visualization_task.add_aggregator(temp[0])
                #Case 1c: ONLY one aggregators are there in the utterance and map plot type specified by user
                elif 'map' in visualization_task.plot_type and visualization_task.aggregators and not visualization_task.filters\
                        and not is_plot_type_override and visualization_task.is_plot_type_specified:
                    visualization_task.remove_vertical_axis("NUM_COUNTIES")
                    visualization_task.sql.add_select("fips")
                    temp = next(iter(visualization_task.aggregators))
                    visualization_task.sql.add_select(temp[0])
                    visualization_task.add_aggregator_map(temp[0])
                #Utterances can have filters
                # elif 'map' not in visualization_task.plot_type and visualization_task.aggregators:
                #     if not is_plot_type_specified and not is_plot_type_override:
                #         #only one aggregator and any number of filters
                #         if visualization_task.filters and len(visualization_task.aggregators) == 1:
                #             # Case 2a: Check if the aggregator is geographically relevant
                #             if visualization_task.any_aggregator_geographically_relevant():
                #                 visualization_task.remove_vertical_axis("NUM_COUNTIES")
                #                 visualization_task.sql.add_select("fips")
                #                 visualization_task.sql.add_select(list(visualization_task.aggregators)[0][0])
                #

                elif 'bar' in visualization_task.plot_type:
                    # order by in sql can be removed for bar plots.
                    print("*****bar in vis plot type*****")
                    if visualization_task.aggregators:
                        temp = next(iter(visualization_task.aggregators))
                        visualization_task.sql.add_select(temp[0])
                        visualization_task.add_horizontal_axis(temp[0])
                    visualization_task.add_vertical_axis("NUM_COUNTIES")
                    visualization_task.sql.remove_all_order_bys()

            visualization_task.update_specification()

            visualization_task.get_summary()

        else:
            # for requests other than create vis or modify vis ones, i.e., win mgmt requests,
            # clear the sql query and remove total crime from y-axis.
            # visualization_task.data_query = None
            # visualization_task.summary = bottom_dialogue_act_label + ' operation on visualization'
            # visualization_task.remove_vertical_axis("ATTRIBUTE")

            visualization_task.remove_all_filters()
            visualization_task.remove_all_aggregators()
            visualization_task.remove_sql()
            visualization_task.sql.add_from('counties_cdc_cases')
            visualization_task.summary = bottom_dialogue_act_label + ' operation on visualization'
            visualization_task.remove_vertical_axis("NUM_COUNTIES")

        return visualization_task
