from copy import deepcopy
from macpath import split

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
        print("Prev plot type: "+ str(previous_task.plot_type))
        with open('python_log.txt', 'a', encoding='utf-8') as log_file:
            log_file.write("\nPrev filter: "+str(previous_filters))
            log_file.write("\nPrev aggregator: "+ str(previous_aggregators))
            log_file.write("\nPrev plot type: "+ str(previous_task.plot_type))
            log_file.write("\n")

        # get the current filters and aggregators.
        current_filters, current_aggregators = \
            current_task.filters, current_task.aggregators
        print("Current filter: "+str(current_filters))
        print("Current aggregator: "+ str(current_aggregators))
        print("current task plot type: "+str(current_task.plot_type))
        with open('python_log.txt', 'a', encoding='utf-8') as log_file:
            log_file.write("\nCurrent filter: "+str(current_filters))
            log_file.write("\nCurrent aggregator: "+ str(current_aggregators))
            log_file.write("\ncurrent task plot type: "+str(current_task.plot_type))

        # create merged task as a identical copy of prev task.
        merged_task = deepcopy(previous_task)

        # update merged task utterances to the current task utterances.
        merged_task.context_utterances = current_task.context_utterances

        # update merged task plot type with the current task plot type if the current task plot type was specified. (Can I see this as a bar chart)
        if current_task.is_plot_type_specified:
            merged_task.plot_type = current_task.plot_type
        

        # if plot type altered (map to another or another to map), accordingly update
        # sql query with removing latitude and longitude or adding latitude and longitude.
        if 'map' not in previous_task.plot_type and 'map' in current_task.plot_type:
            print(" In if 'map' not in previous_task.plot_type and 'map' in current_task.plot_type:")
            if "NUM_COUNTIES" in merged_task.vertical_axis:
                # print("............in inner if.............")
                # "TOTAL CRIME" is not in the vertical axis always (i.e., only when dialogue act is create\modify vis).
                merged_task.remove_vertical_axis("NUM_COUNTIES")
            # elif "NUM_CASES" in merged_task.vertical_axis:
                #  merged_task.remove_vertical_axis("NUM_CASES")
                # merged_task.remove_aggregator(current_task.aggregators)
            # print("*****************"+ str(current_aggregators[0]))
            # merged_task.sql.add_select(current_aggregators[0])
            merged_task.sql.add_select('fips')
            # merged_task.sql.add_select('longitude')
            merged_task.update_specification()
        elif 'map' in previous_task.plot_type:
            if 'map' not in current_task.plot_type:
                if 'bar' in current_task.plot_type and current_task.is_plot_type_specified:
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
                else :
                    temp = next(iter(merged_task.aggregators))
                    merged_task.sql.add_select(temp[0])
                    merged_task.add_aggregator_map(temp[0])
                    merged_task.sql.add_select("fips")
                    merged_task.plot_type = "heat map"
                    merged_task.map_type = "geographical"
            elif 'map' in current_task.plot_type:
                print("map in current task plot type and previous task plot type")
                # temp = next(iter(merged_task.aggregators))
                # merged_task.sql.add_select(temp[0])
                # merged_task.add_aggregator_map(temp[0])
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
            # merged_task.add_all_aggregators(current_aggregators)

            if curr_temporal_attribute and prev_temporal_attribute:
                # if both prev and curr tasks contain temporal aggregators, remove prev task one
                # from merged task.
                # e.g.,
                #   prev request = "Show me theft <filter> broken down by month <aggregator>?"
                #   curr request = "Can you show me this same graph but for years <aggregator> this time?"
                # hence, prev temporal aggregator = "month", curr temporal aggregator = 'year'.
                merged_task.remove_aggregator(prev_temporal_attribute)
                merged_task.add_all_aggregators(current_aggregators)
            if not current_aggregators.intersection(previous_aggregators):
                # otherwise if curr task and prev task do not share any aggregators, remove all prev task aggregators.
                # e.g.,
                #   prev request = "Show me theft <filter> broken down by year <aggregator>?"
                #   curr request = "Can you show me this same graph but for location <aggregator> this time?"
                # hence, prev aggregator = "year", curr aggregator = 'location'.
                print("line 150")
                merged_task.remove_all_aggregators()
                merged_task.add_all_aggregators(current_aggregators)
                curr_agg = next(iter(current_task.aggregators))
                print("Current aggregator: "+str(current_task.aggregators))
                if len(current_aggregators) == 1:
                    print("one aggregator")
                    merged_task.sql.add_select("fips")
                    merged_task.sql.add_select(curr_agg[0])
                    merged_task.add_aggregator_map(curr_agg[0])
                    merged_task.sql.add_select("fips")
                    if merged_task.vertical_axis:
                        print("Removed vertical axis")
                        merged_task.remove_vertical_axis("NUM_COUNTIES")
                    merged_task.plot_type = "heat map"
                    merged_task.map_type = "geographical"
                else:
                    print("two aggregators")
                    merged_task.plot_type = "heat map"
                    merged_task.map_type = "non_geographical" #non-geographical heat map
                    merged_task.sql.add_select(list(merged_task.aggregators)[0][0])
                    merged_task.sql.add_select(list(merged_task.aggregators)[0][0])
                    merged_task.add_horizontal_axis(list(merged_task.aggregators)[0][0])
                    merged_task.add_horizontal_axis(list(merged_task.aggregators)[0][0])
                    merged_task.sql.remove_group_by('fips')
                    merged_task.sql.remove_select('fips')
                    merged_task.add_vertical_axis("NUM_COUNTIES")


                

            # if curr and prev task contain temporal aggregators, remove the prev task one
            # from merged task, replacing with curr task temporal aggregator + all other prev task aggregators
            # + all curr task aggregators.

            # if either curr and prev task do not contain temporal aggregators, then:
            #   if they do not share aggregators, then:
            #       remove all prev task aggregators from merged task, retaining only the curr task aggregators.
            #   otherwise if they do share some aggregators, then:
            #       retain the non-shared prev task aggregators + non-shared curr task aggregators +
            #       shared aggregators.
            # merged_task.add_all_aggregators(current_aggregators)
        # else:
        #     merged_task.remove_all_aggregators()

        # update summary
        merged_task.get_summary()

        return merged_task

    @staticmethod
    def construct(setup_utterances, request_utterance, dialogue_act, referring_expression):
        # get the dialogue act and end early if it is not a request.
        top_dialogue_act_label, bottom_dialogue_act_label = dialogue_act
        # if top_dialogue_act_label != 'merged':
        #     return None

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
                    print("line 248")
                    #for referring_expression in referring_expressions:
                    referring_expressions_range = range(referring_expression.get_start_char_idx(),
                                                        referring_expression.get_end_char_idx())
                    if not token.idx in referring_expressions_range:
                        print("line 253")
                        # if the word is a visualization attribute and not part of referring expression
                        # then update plot type to corresponding attribute value.
                        # e.g., plot type="map" in "Can you show this graph <ref exp is "this graph",
                        # graph is vis attribute> as a map <plot type falls outside of "this graph" ref exp>.
                        if not token._.is_entity_name:
                            print("line 257")
                            visualization_task.plot_type = token._.entity_value[0]
                            print(visualization_task.plot_type)
                            is_plot_type_override = True
                            visualization_task.is_plot_type_specified = True
                            
                else:
                    print("line 264")
                    # if no ref exps exists, then just directly update plot type.
                    # e.g., plot type="map" in "Show me thefts for each neighborhood as a map <vis attribute>"
                    if not token._.is_entity_name:
                        print("TOKEN entity visualization :"+str(token))
                        split_tokens = str(token).split(" ")
                        if len(split_tokens) >= 2:
                            for i in range(len(split_tokens)):
                                if split_tokens[i] == 'map':
                                    print("271")
                                    visualization_task.plot_type = token._.entity_value[0]
                                    visualization_task.is_plot_type_specified = True
                                elif 'region' in split_tokens[i]:
                                    visualization_task.add_aggregator("region",
                                                  tuple(["pacific","rockies","northeast","southeast","midwest","southwest","noncontiguous"]))
                                    visualization_task.add_aggregator_map("region")
                                    visualization_task.manually_added_aggregator = 'region'

                                elif 'cardio' in split_tokens[i] or 'heart' in split_tokens[i]:
                                    print("in cardio")
                                    visualization_task.add_aggregator("cardiovascular_disease_rate",
                                                  tuple(["very-high-cardiovascular-disease-rate","high-cardiovascular-disease-rate","moderate-cardiovascular-disease-rate","low-cardiovascular-disease-rate","very-low-cardiovascular-disease-rate","not-available"]))
                                    visualization_task.add_aggregator_map("cardiovascular_disease_rate")
                                    visualization_task.manually_added_aggregator = 'cardiovascular_disease_rate'

                                elif 'elderly' in split_tokens[i] or 'old' in split_tokens[i]:
                                    visualization_task.add_aggregator("elderly_percentage",
                                                  tuple(["very-high-elderly-percentage","high-elderly-percentage","moderate-elderly-percentage","low-elderly-percentage","very-low-elderly-percentage"]))
                                    visualization_task.add_aggregator_map("elderly_percentage")
                                    visualization_task.manually_added_aggregator = 'elderly_percentage'

                                elif 'county' in split_tokens[i] or 'counties' in split_tokens[i]:
                                    visualization_task.add_aggregator("county_type",
                                                  tuple(["rural","urban","suburban","small-city"]))
                                    visualization_task.add_aggregator_map("county_type")
                                    visualization_task.manually_added_aggregator = 'county_type'

                                elif 'doctor' in split_tokens[i] or 'physician' in split_tokens[i]:
                                    visualization_task.add_aggregator("access_to_doctor",
                                                  tuple(["very-high-access-to-doctors","high-access-to-doctors","moderate-access-to-doctors","low-access-to-doctors","very-low-access-to-doctors","not-available"]))
                                    visualization_task.add_aggregator_map("access_to_doctor")
                                    visualization_task.manually_added_aggregator = 'access_to_doctor'

                                elif 'uninsured' in split_tokens[i]:
                                    visualization_task.add_aggregator("uninsured_rate",
                                                  tuple(["very-high-uninsured-rate","high-uninsured-rate","moderate-uninsured-rate","low-uninsured-rate","very-low-uninsured-rate","not-available"]))
                                    visualization_task.add_aggregator_map("uninsured_rate")
                                    visualization_task.manually_added_aggregator = 'uninsured_rate'

                                elif 'diabetes' in split_tokens[i]:
                                    print("in diabetes")
                                    visualization_task.add_aggregator("diabetes_rate",
                                                  tuple(["very-high-diabetes-rate","high-diabetes-rate","moderate-diabetes-rate","low-diabetes-rate","very-low-diabetes-rate"]))
                                    visualization_task.add_aggregator_map("diabetes_rate")
                                    visualization_task.manually_added_aggregator = 'diabetes_rate'

                                elif 'poverty' in split_tokens[i]:
                                    visualization_task.add_aggregator("poverty_rate",
                                                  tuple(["very-high-poverty-rate","high-poverty-rate","moderate-poverty-rate","low-poverty-rate","very-low-poverty-rate"]))
                                    visualization_task.add_aggregator_map("poverty_rate")
                                    visualization_task.manually_added_aggregator = 'poverty_rate'

                                elif 'african' in split_tokens[i]:
                                    visualization_task.add_aggregator("african_american_population",
                                                  tuple(["very-high-african-american-population","high-african-american-population","moderate-african-american-population","low-african-american-population","very-low-african-american-population","not-available"]))
                                    visualization_task.add_aggregator_map("african_american_population")
                                    visualization_task.manually_added_aggregator = 'african_american_population'

                                elif 'hispanic' in split_tokens[i]:
                                    visualization_task.add_aggregator("hispanic_population",
                                                  tuple(["medium-hispanic-population","medium-hispanic-population","medium-hispanic-population","medium-hispanic-population","midwest","southwest","noncontiguous"]))
                                    visualization_task.add_aggregator_map("hispanic_population")
                                    visualization_task.manually_added_aggregator = 'hispanic_population'

                                elif 'covid' in split_tokens[i]:
                                    visualization_task.add_aggregator("covid_vulnerability_rank",
                                                  tuple(["very-high-covid-vulnerability-rank","high-covid-vulnerability-rank","moderate-covid-vulnerability-rank","low-covid-vulnerability-rank","very-low-covid-vulnerability-rank"]))
                                    visualization_task.add_aggregator_map("covid_vulnerability_rank")
                                    visualization_task.manually_added_aggregator = 'covid_vulnerability_rank'

                                elif 'social' in split_tokens[i]:
                                    visualization_task.add_aggregator("social_vulnerability_rank",
                                                  tuple(["very-high-social-vulnerability-rank","high-social-vulnerability-rank","moderate-social-vulnerability-rank","low-social-vulnerability-rank","high-low-social-vulnerability-rank"]))
                                    visualization_task.add_aggregator_map("social_vulnerability_rank")
                                    visualization_task.manually_added_aggregator = 'social_vulnerability_rank'
                        else:
                            visualization_task.plot_type = token._.entity_value[0]
                            visualization_task.is_plot_type_specified = True
                                                     
                continue
            # if referring_expression:
            #     print("*******referring expression**********")


            # if the word is not a data attribute then cannot be a filter or aggregator.
            if not token._.entity_data_attribute:
                # print("Token not a data attribute: "+str(token))
                continue
            # If token is an entity ---> Filters and Aggregators
            # Check if token is an aggregator (slot)
            if token._.is_entity and token._.is_entity_name:
                # print("***********************token**********************")
                # print(token)

                # if word is a parent attribute, then add as aggregator to the new task.
                # e.g., add "neighborhood" from utterance "Show me theft <filter> by neighborhood <aggregator>"
                visualization_task.add_aggregator(token._.entity,
                                                  tuple([child for child in token._.entity_children if
                                                         child is not None and '\\' not in child]))
                if token._.is_continuous_temporal:
                    print("line 335")
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
            if 'new_cases' in visualization_task.filters and 'map' not in visualization_task.plot_type: #or 'line' in visualization_task.plot_type 
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
            elif 'new_cases' in visualization_task.filters and 'map' in visualization_task.plot_type:
                visualization_task.remove_vertical_axis("NUM_COUNTIES")
                visualization_task.sql.add_select_sum("NUM_CASES")
                visualization_task.sql.add_select("fips")
                visualization_task.sql.add_group_by("fips")
                visualization_task.remove_filter('new_cases')
                visualization_task.plot_type = "heat map"
                visualization_task.map_type = "geographical"
            #Case 1a: ONLY one aggregators are there in the utterance and the plot will be map type
            #I want to see the rate of diabetes <aggregator> in the US. (general query, one aggregator)
            else:
                if 'map' not in visualization_task.plot_type and visualization_task.aggregators:
                    if not visualization_task.is_plot_type_specified and not is_plot_type_override:
                        if len(visualization_task.aggregators) == 1:
                            # if visualization_task.any_aggregator_geographically_relevant():
                            #     print("one geographically relevant aggregator")
                            #     visualization_task.add_horizontal_axis(list(visualization_task.aggregators)[0][0])
                            #     visualization_task.sql.add_group_by(list(visualization_task.aggregators)[0][0])
                            # else:
                            visualization_task.remove_vertical_axis("NUM_COUNTIES")
                            temp = next(iter(visualization_task.aggregators))
                            visualization_task.sql.add_select(temp[0])
                            visualization_task.add_aggregator_map(temp[0])
                            visualization_task.sql.add_select("fips")
                            visualization_task.plot_type = "heat map"
                            visualization_task.map_type = "geographical"
                        elif len(visualization_task.aggregators) == 2:
                            #Case 2a:if there are two aggregators and one of them is geographically relevant --> grouped bar chart
                            if visualization_task.any_aggregator_geographically_relevant():
                                print("*****geographically relevant aggregator******")
                                visualization_task.sql.add_select(list(visualization_task.aggregators)[0][0])
                                visualization_task.sql.add_select(list(visualization_task.aggregators)[1][0])
                                visualization_task.add_horizontal_axis(list(visualization_task.aggregators)[1][0])
                                visualization_task.add_horizontal_axis(list(visualization_task.aggregators)[0][0])
                            #Case 2b:if there are two aggregators and none of them is geographically relevant --> non-geographical heat map
                            else:
                                visualization_task.plot_type = "heat map"
                                visualization_task.map_type = "non_geographical" #non-geographical heat map
                                visualization_task.sql.add_select(list(visualization_task.aggregators)[0][0])
                                visualization_task.sql.add_select(list(visualization_task.aggregators)[1][0])
                                visualization_task.add_horizontal_axis(list(visualization_task.aggregators)[1][0])
                                visualization_task.add_horizontal_axis(list(visualization_task.aggregators)[0][0])
                            # visualization_task.add_first_aggregator(list(visualization_task.aggregators)[0][0])
                            # visualization_task.add_aggregator(list(visualization_task.aggregators)[1][0]
                        elif len(visualization_task.aggregators) > 2:
                            visualization_task.remove_all_aggregators()
                            visualization_task.remove_all_filters()
                            with open('python_log.txt', 'a', encoding='utf-8') as log_file:
                                log_file.write("\nMore than 2 aggregators in request : dropped")

                           
                            
                            # print("more than two aggregators :"+ str(len(list(visualization_task.aggregators))))
                            # print(str(list(visualization_task.aggregators)))                   
                            # count = 0
                            # for j in (list(visualization_task.aggregators)):
                            #     print(list(visualization_task.aggregators)[count][0])
                            #     if count > 1:
                                    
                            #         visualization_task.remove_aggregator(j[0])
                            #         count +=1
                            #     else:
                            #         visualization_task.plot_type = "heat map"
                            #         visualization_task.map_type = "non_geographical" #non-geographical heat map
                            #         visualization_task.sql.add_select(list(visualization_task.aggregators)[count][0])
                            #         visualization_task.add_horizontal_axis(list(visualization_task.aggregators)[count][0])
                            #         count +=1
                                   
                    #Case 1b: user asks for a bar chart
                    elif visualization_task.is_plot_type_specified and visualization_task.plot_type == "bar chart":
                        print("line 372")
                        temp = next(iter(visualization_task.aggregators))
                        visualization_task.sql.add_select(temp[0])
                        # visualization_task.add_aggregator(temp[0])
                #Case 1c: ONLY one aggregators are there in the utterance and map plot type specified by user
                elif 'map' in visualization_task.plot_type:
                    print("**map in vis plot type**")
                    if visualization_task.aggregators and not visualization_task.manually_added_aggregator:
                        print("in vis aggregators")
                        if len(visualization_task.aggregators) == 1:

                            # if visualization_task.any_aggregator_geographically_relevant():
                            #     print("one geographically relevant aggregator")
                            #     visualization_task.add_horizontal_axis(list(visualization_task.aggregators)[0][0])
                            #     visualization_task.sql.add_group_by(list(visualization_task.aggregators)[0][0])
                            # else:
                            visualization_task.remove_vertical_axis("NUM_COUNTIES")
                            temp = next(iter(visualization_task.aggregators))
                            visualization_task.sql.add_select(temp[0])
                            visualization_task.add_aggregator_map(temp[0])
                            visualization_task.sql.add_select("fips")
                            # visualization_task.plot_type = "heat map"
                            visualization_task.map_type = "geographical"
                        elif len(visualization_task.aggregators) == 2:
                            visualization_task.plot_type = "heat map"
                            visualization_task.map_type = "non_geographical" #non-geographical heat map
                            visualization_task.sql.add_select(list(visualization_task.aggregators)[0][0])
                            visualization_task.sql.add_select(list(visualization_task.aggregators)[1][0])
                            visualization_task.add_horizontal_axis(list(visualization_task.aggregators)[1][0])
                            visualization_task.add_horizontal_axis(list(visualization_task.aggregators)[0][0])
                            
                        else:
                            print("more than two aggregators")
                            visualization_task.remove_all_aggregators()
                            visualization_task.remove_all_filters()
                            with open('python_log.txt', 'a', encoding='utf-8') as log_file:
                                log_file.write("\nIn map and plot type specified, more than 2 aggregators in request : dropped")

                        # visualization_task.map_type = "geographical"
                        # visualization_task.remove_vertical_axis("NUM_COUNTIES")
                        # visualization_task.sql.add_select("fips")
                        # temp = next(iter(visualization_task.aggregators))
                        # visualization_task.sql.add_select(temp[0])
                        # visualization_task.add_aggregator_map(temp[0])
                    elif visualization_task.manually_added_aggregator:
                        print("in manual vis aggregators")
                        # visualization_task.remove_all_aggregators()
                        if len(visualization_task.aggregators) == 1:
                            visualization_task.map_type = "geographical"
                            visualization_task.remove_vertical_axis("NUM_COUNTIES")
                            visualization_task.sql.add_select("fips")
                            visualization_task.sql.add_select(visualization_task.manually_added_aggregator)
                            visualization_task.add_horizontal_axis(visualization_task.manually_added_aggregator)
                        elif len(visualization_task.aggregators) == 2:
                            if visualization_task.any_aggregator_geographically_relevant():
                                print("*****geographically relevant aggregator in manually added aggregators******")
                                visualization_task.plot_type = 'bar chart'
                                visualization_task.sql.add_select(list(visualization_task.aggregators)[0][0])
                                visualization_task.sql.add_select(list(visualization_task.aggregators)[1][0])
                                visualization_task.add_horizontal_axis(list(visualization_task.aggregators)[1][0])
                                visualization_task.add_horizontal_axis(list(visualization_task.aggregators)[0][0])
                            else:
                                visualization_task.plot_type = "heat map"
                                visualization_task.map_type = "non_geographical" #non-geographical heat map
                                visualization_task.sql.remove_group_by('fips')
                                visualization_task.sql.remove_select('fips')
                                visualization_task.sql.add_select(list(visualization_task.aggregators)[0][0])
                                visualization_task.sql.add_select(list(visualization_task.aggregators)[1][0])
                                visualization_task.add_horizontal_axis(list(visualization_task.aggregators)[1][0])
                                visualization_task.add_horizontal_axis(list(visualization_task.aggregators)[0][0])
                        else:
                            print("more than two manual aggregators")
                            visualization_task.remove_all_aggregators()
                            visualization_task.remove_all_filters()
                            
                            with open('python_log.txt', 'a', encoding='utf-8') as log_file:
                                log_file.write("\nIn map and plot type specified, more than 2 manual aggregators in request : dropped")



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
                    elif visualization_task.is_plot_type_specified:
                        print("***in line 459***")
                        visualization_task.add_vertical_axis("NUM_COUNTIES")
                        visualization_task.sql.remove_all_order_bys()
                    # else:
                    #     visualization_task.remove_vertical_axis("NUM_COUNTIES")
                    #     visualization_task.add_vertical_axis_sum("NUM_CASES")
                    #     visualization_task.sql.add_select("date")
                    #     visualization_task.sql.add_group_by("date")
                    #     visualization_task.add_horizontal_axis("date")
                    #     # visualization_task.add_aggregator("date")
                    #     visualization_task.remove_filter('new_cases')
                    #     visualization_task.remove_filter('date')
                    #     visualization_task.plot_type = "line"


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
            # visualization_task.sql.add_from('counties_cdc_cases')
            visualization_task.summary = bottom_dialogue_act_label + ' operation on visualization'
            visualization_task.remove_vertical_axis("NUM_COUNTIES")

        return visualization_task
