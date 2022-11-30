from collections import defaultdict
from decimal import Decimal

import mysql.connector as mc

from .visualization_specification import VisualizationSpecification


class VisualizationSpecificationConstructor:
    db = mc.connect(host='localhost', user='root', password='admin', database='covid',
                    auth_plugin='mysql_native_password')
    db_executor = db.cursor()

    @staticmethod
    def construct(visualization_task, dialogue_act):
        visualization_specification = VisualizationSpecification()

        top_dialogue_act_label, bottom_dialogue_act_label = dialogue_act
        if bottom_dialogue_act_label in ['createvis', 'modifyvis']:
            visualization_specification.horizontal_axis = visualization_task.horizontal_axis
            visualization_specification.horizontal_axis_grouping = visualization_task.horizontal_axis_grouping
            visualization_specification.vertical_axis = visualization_task.vertical_axis
            visualization_specification.data_query = visualization_task.data_query

        visualization_specification.plot_headline.plot_type = visualization_task.plot_type
        visualization_specification.plot_headline.map_type = visualization_task.map_type
        visualization_specification.plot_headline.action = visualization_task.action
        visualization_specification.plot_headline.summary = visualization_task.summary

        visualization_specification.visualization_task = visualization_task
        visualization_specification.dialogue_act = dialogue_act
        VisualizationSpecificationConstructor._update_from_data_query(visualization_specification)

        return visualization_specification

    @staticmethod
    def _update_from_data_query(visualization_specification):
        if not visualization_specification.data_query:
            return None

        try:

            print(visualization_specification.data_query)
            VisualizationSpecificationConstructor.db_executor.execute(visualization_specification.data_query)
        except IndexError:
            VisualizationSpecificationConstructor.db_executor.close()
            VisualizationSpecificationConstructor.db = mc.connect(host='localhost', user='root', password='admin',
                                                                  database='covid')
            VisualizationSpecificationConstructor.db_executor = VisualizationSpecificationConstructor.db.cursor()
            VisualizationSpecificationConstructor.db_executor.execute(visualization_specification.data_query)

        rows = VisualizationSpecificationConstructor.db_executor.fetchall()
        #for now

        for row in rows:
                visualization_specification.data_query_results.append(str(row))
        VisualizationSpecificationConstructor.convert_data_query_results_to_vega_lite_data_spec(visualization_specification,rows)


    @staticmethod
    def convert_data_query_results_to_vega_lite_data_spec(visualization_specification,rows):

        if visualization_specification.plot_headline.plot_type == 'line':
            print("line chart")
            # temporal chart with "date" as horizontal axis and "new_cases" on vertical axis
            if not visualization_specification.visualization_task.aggregators:
                print("no aggregator")
                # dates = VisualizationSpecificationConstructor.convert_date()
                horizontal_axis = next(iter(visualization_specification.horizontal_axis))
                vertical_axis = next(iter(visualization_specification.vertical_axis))
                for i in range(len(rows)):
                    spec = dict({horizontal_axis: VisualizationSpecificationConstructor.convert_date(rows[i][0]), vertical_axis: rows[i][1]})
                    visualization_specification.data_vega_lite_spec.append(spec)
            else:
                print("line chart with aggregator")
                # dates = VisualizationSpecificationConstructor.convert_date()
                key = next(iter(visualization_specification.horizontal_axis))
                print("key: "+ key)
                if key in 'region':
                    vertical_axis = next(iter(visualization_specification.vertical_axis))
                    for i in range(len(rows)):
                        if rows[i][0] in ['northeast','southeast','southwest','midwest','rockies','pacific','noncontiguous']:
                            value = rows[i][0]
                            if str(type(rows[i][1])) == "<class 'float'>" :
                                vertical_axis_value = rows[i][1]
                                date_value = rows[i][2]
                                spec = dict({"date": VisualizationSpecificationConstructor.convert_date(date_value), key:value, vertical_axis: vertical_axis_value})
                                visualization_specification.data_vega_lite_spec.append(spec)
                            else:
                                vertical_axis_value = rows[i][2]
                                date_value = rows[i][1]
                                spec = dict({"date": VisualizationSpecificationConstructor.convert_date(date_value), key:value, vertical_axis: vertical_axis_value})
                                visualization_specification.data_vega_lite_spec.append(spec)
                        elif rows[i][1] in ['northeast','southeast','southwest','midwest','rockies','pacific','noncontiguous']:
                            value = rows[i][1]
                            if str(type(rows[i][0])) == "<class 'float'>" :
                                vertical_axis_value = rows[i][0]
                                date_value = rows[i][2]
                                spec = dict({"date": VisualizationSpecificationConstructor.convert_date(date_value), key:value, vertical_axis: vertical_axis_value})
                                visualization_specification.data_vega_lite_spec.append(spec)
                            else:
                                vertical_axis_value = rows[i][2]
                                date_value = rows[i][0]
                                spec = dict({"date": VisualizationSpecificationConstructor.convert_date(date_value), key:value, vertical_axis: vertical_axis_value})
                                visualization_specification.data_vega_lite_spec.append(spec)
                        else:
                            value = rows[i][2]
                            if str(type(rows[i][0])) == "<class 'float'>" :
                                vertical_axis_value = rows[i][0]
                                date_value = rows[i][1]
                                spec = dict({"date": VisualizationSpecificationConstructor.convert_date(date_value), key:value, vertical_axis: vertical_axis_value})
                                visualization_specification.data_vega_lite_spec.append(spec)
                            else:
                                vertical_axis_value = rows[i][1]
                                date_value = rows[i][0]
                                spec = dict({"date": VisualizationSpecificationConstructor.convert_date(date_value), key:value, vertical_axis: vertical_axis_value})
                                visualization_specification.data_vega_lite_spec.append(spec)
                elif key in 'county_type':
                    vertical_axis = next(iter(visualization_specification.vertical_axis))
                    for i in range(len(rows)):
                        if rows[i][0] in ["rural","urban","suburban","small-city","OTHER"]:
                            value = rows[i][0]
                            if str(type(rows[i][1])) == "<class 'float'>" :
                                vertical_axis_value = rows[i][1]
                                date_value = rows[i][2]
                                spec = dict({"date": VisualizationSpecificationConstructor.convert_date(date_value), key:value, vertical_axis: vertical_axis_value})
                                visualization_specification.data_vega_lite_spec.append(spec)
                            else:
                                vertical_axis_value = rows[i][2]
                                date_value = rows[i][1]
                                spec = dict({"date": VisualizationSpecificationConstructor.convert_date(date_value), key:value, vertical_axis: vertical_axis_value})
                                visualization_specification.data_vega_lite_spec.append(spec)
                        elif rows[i][1] in ['northeast','southeast','southwest','midwest','rockies','pacific','noncontiguous-']:
                            value = rows[i][1]
                            if str(type(rows[i][0])) == "<class 'float'>" :
                                vertical_axis_value = rows[i][0]
                                date_value = rows[i][2]
                                spec = dict({"date": VisualizationSpecificationConstructor.convert_date(date_value), key:value, vertical_axis: vertical_axis_value})
                                visualization_specification.data_vega_lite_spec.append(spec)
                            else:
                                vertical_axis_value = rows[i][2]
                                date_value = rows[i][0]
                                spec = dict({"date": VisualizationSpecificationConstructor.convert_date(date_value), key:value, vertical_axis: vertical_axis_value})
                                visualization_specification.data_vega_lite_spec.append(spec)
                        else:
                            value = rows[i][2]
                            if str(type(rows[i][0])) == "<class 'float'>" :
                                vertical_axis_value = rows[i][0]
                                date_value = rows[i][1]
                                spec = dict({"date": VisualizationSpecificationConstructor.convert_date(date_value), key:value, vertical_axis: vertical_axis_value})
                                visualization_specification.data_vega_lite_spec.append(spec)
                            else:
                                vertical_axis_value = rows[i][1]
                                date_value = rows[i][0]
                                spec = dict({"date": VisualizationSpecificationConstructor.convert_date(date_value), key:value, vertical_axis: vertical_axis_value})
                                visualization_specification.data_vega_lite_spec.append(spec)
                        


                else:
                    key_text = key.split("_")[-2]
                    vertical_axis = next(iter(visualization_specification.vertical_axis))
                # print(rows)
                    for i in range(len(rows)):
                        if rows[i][0] == "not-available" or rows[i][1] == "not-available" or rows[i][2] == "not-available":
                            continue
                        if key_text in rows[i][0].split("-"):
                            value = rows[i][0]
                            if str(type(rows[i][1])) == "<class 'float'>" :
                                vertical_axis_value = rows[i][1]
                                date_value = rows[i][2]
                                spec = dict({"date": VisualizationSpecificationConstructor.convert_date(date_value), key:value, vertical_axis: vertical_axis_value})
                                visualization_specification.data_vega_lite_spec.append(spec)
                            else:
                                vertical_axis_value = rows[i][2]
                                date_value = rows[i][1]
                                spec = dict({"date": VisualizationSpecificationConstructor.convert_date(date_value), key:value, vertical_axis: vertical_axis_value})
                                visualization_specification.data_vega_lite_spec.append(spec)
                        elif key_text in rows[i][1].split("-"):
                            value = rows[i][1]
                            if str(type(rows[i][0])) == "<class 'float'>" :
                                vertical_axis_value = rows[i][0]
                                date_value = rows[i][2]
                                spec = dict({"date": VisualizationSpecificationConstructor.convert_date(date_value), key:value, vertical_axis: vertical_axis_value})
                                visualization_specification.data_vega_lite_spec.append(spec)
                            else:
                                vertical_axis_value = rows[i][2]
                                date_value = rows[i][0]
                                spec = dict({"date": VisualizationSpecificationConstructor.convert_date(date_value), key:value, vertical_axis: vertical_axis_value})
                                visualization_specification.data_vega_lite_spec.append(spec)
                        else:
                            value = rows[i][2]
                            if str(type(rows[i][0])) == "<class 'float'>" :
                                vertical_axis_value = rows[i][0]
                                date_value = rows[i][1]
                                spec = dict({"date": VisualizationSpecificationConstructor.convert_date(date_value), key:value, vertical_axis: vertical_axis_value})
                                visualization_specification.data_vega_lite_spec.append(spec)
                            else:
                                vertical_axis_value = rows[i][1]
                                date_value = rows[i][0]
                                spec = dict({"date": VisualizationSpecificationConstructor.convert_date(date_value), key:value, vertical_axis: vertical_axis_value})
                                visualization_specification.data_vega_lite_spec.append(spec)

        elif visualization_specification.plot_headline.plot_type == 'bar chart':
            print("bar chart")
            if len(visualization_specification.horizontal_axis) == 2:
                print("********grouped bar chart***************")
                county_type_list = ["rural","urban","suburban","small-city","OTHER"]
                region_list = ['northeast','southeast','southwest','midwest','rockies','pacific','noncontiguous']
                     
                if list(visualization_specification.horizontal_axis)[0] == "county_type" or list(visualization_specification.horizontal_axis)[0] == "region":
                    print("group in horizontal axis[0]")
                    group = list(visualization_specification.horizontal_axis)[0]
                    horizontal_axis = list(visualization_specification.horizontal_axis)[1]
                    vertical_axis = list(visualization_specification.vertical_axis)[0]
                else:
                    print("group in horizontal axis[1]")
                    group = list(visualization_specification.horizontal_axis)[1]
                    horizontal_axis = list(visualization_specification.horizontal_axis)[0]
                    vertical_axis = list(visualization_specification.vertical_axis)[0]
           
                for i in range(len(rows)):

                    if rows[i][0] == "not-available" and rows[i][0] == "not-available":
                        continue
                    elif rows[i][0] != "not-available" and rows[i][1] == "not-available":
                        if horizontal_axis in rows[i][0].split("-"):
                            horizontal_axis_val = rows[i][0]
                            group_val = rows[i][1]
                            spec = dict({horizontal_axis: horizontal_axis_val, group: group_val, vertical_axis: rows[i][2]})
                            visualization_specification.data_vega_lite_spec.append(spec)
                        else:
                            horizontal_axis_val = rows[i][1]
                            group_val = rows[i][0]
                            spec = dict({horizontal_axis: horizontal_axis_val, group: group_val, vertical_axis: rows[i][2]})
                            visualization_specification.data_vega_lite_spec.append(spec)
                    elif rows[i][0] == "not-available" and rows[i][1] != "not-available":
                        if horizontal_axis in rows[i][1].split("-"):
                            horizontal_axis_val = rows[i][1]
                            group_val = rows[i][0]
                            spec = dict({horizontal_axis: horizontal_axis_val, group: group_val, vertical_axis: rows[i][2]})
                            visualization_specification.data_vega_lite_spec.append(spec) 
                        else:
                            horizontal_axis_val = rows[i][0]
                            group_val = rows[i][1]
                            spec = dict({horizontal_axis: horizontal_axis_val, group: group_val, vertical_axis: rows[i][2]})
                            visualization_specification.data_vega_lite_spec.append(spec)
                    else:
                        if rows[i][0] in county_type_list and rows[i][1] in region_list:
                            horizontal_axis_val = rows[i][0]
                            group_val = rows[i][1]
                            spec = dict({"county_type": horizontal_axis_val, "region": group_val, vertical_axis: rows[i][2]})
                            visualization_specification.data_vega_lite_spec.append(spec)
                        elif rows[i][1] in county_type_list and rows[i][0] in region_list:
                            horizontal_axis_val = rows[i][1]
                            group_val = rows[i][0]
                            spec = dict({"county_type": horizontal_axis_val, "region": group_val, vertical_axis: rows[i][2]})
                            visualization_specification.data_vega_lite_spec.append(spec)

                        elif rows[i][1] in county_type_list or rows[i][1] in region_list:
                            print("rows[i][1] in county type list/region list")
                            # if horizontal_axis in rows[i][0].split("-"):
                            horizontal_axis_val = rows[i][0]
                            print("horizontal_axis_val: "+horizontal_axis_val)
                            group_val = rows[i][1]
                            print("group_val: "+group_val)
                            spec = dict({horizontal_axis: horizontal_axis_val, group: group_val, vertical_axis: rows[i][2]})
                            visualization_specification.data_vega_lite_spec.append(spec)
                        else:
                            print("rows[i][1] in county type list/region list")
                            horizontal_axis_val = rows[i][1]
                            print("horizontal_axis_val: "+horizontal_axis_val)
                            group_val = rows[i][0]
                            print("group_val: "+group_val)
                            spec = dict({horizontal_axis: horizontal_axis_val, group: group_val, vertical_axis: rows[i][2]})
                            visualization_specification.data_vega_lite_spec.append(spec)
                # for i in range(len(rows)):
                #     spec = dict({horizontal_axis: rows[i][1], group: rows[i][0], vertical_axis: rows[i][2]})
                #     visualization_specification.data_vega_lite_spec.append(spec)
            elif len(visualization_specification.horizontal_axis) == 1:
                horizontal_axis = list(visualization_specification.horizontal_axis)[0]
                vertical_axis = list(visualization_specification.vertical_axis)[0]
                group = "date"
                if vertical_axis == 'NUM_CASES':
                    return
                else:
                    for i in range(len(rows)):
                        spec = dict({horizontal_axis: rows[i][0], vertical_axis: rows[i][1]})
                        visualization_specification.data_vega_lite_spec.append(spec)
            else:
                print("****no horizontal axis or more than two horizontal axes***")
                # visualization_specification.data_vega_lite_spec.append
        elif visualization_specification.plot_headline.plot_type == 'heat map':
            print("heat map")
            if visualization_specification.plot_headline.map_type == "geographical":
                print("in geographical map")
                if not visualization_specification.horizontal_axis:
                    print("no horizontal axis")
                    for i in range(len(rows)):
                        if str(type(rows[i][1])) == "<class 'int'>" :
                            spec = dict({"fips": rows[i][1], "num_cases": rows[i][0]})
                            visualization_specification.data_vega_lite_spec.append(spec)
                        else:
                            spec = dict({"fips": rows[i][0], "num_cases": rows[i][1]})
                            visualization_specification.data_vega_lite_spec.append(spec)
                else:
                    aggregator = list(visualization_specification.horizontal_axis)[0]
                    for i in range(len(rows)):
                        if str(type(rows[i][1])) == "<class 'int'>" :
                            spec = dict({"fips": rows[i][1], aggregator: rows[i][0]})
                            visualization_specification.data_vega_lite_spec.append(spec)
                        else:
                            spec = dict({"fips": rows[i][0], aggregator: rows[i][1]})
                            visualization_specification.data_vega_lite_spec.append(spec)
            elif len(visualization_specification.horizontal_axis) == 2:
                print("non-geographical heat map")
                aggregator_1 = list(visualization_specification.horizontal_axis)[0]
                aggregator_2 = list(visualization_specification.horizontal_axis)[1]
                vertical_axis = list(visualization_specification.vertical_axis)[0]
                if aggregator_1 in ['region', 'county_type']:
                    #check for any one of these two geographcal attributes
                    agg_1_text = list(visualization_specification.horizontal_axis)[0]
                else:
                    agg_1_text = aggregator_1.split("_")[-2]
                if agg_1_text == "vulnerability":
                    agg_1_text = aggregator_1.split("_")[-3]
                print("****aggregator 1 text: "+str(agg_1_text))
                # agg_2_text = aggregator_2.split("_")[0]
                for i in range(len(rows)):
                    if rows[i][0] == "not-available" and rows[i][0] == "not-available":
                        continue
                    elif rows[i][0] != "not-available" and rows[i][1] == "not-available":
                        if agg_1_text in rows[i][0].split("-"):
                            aggregator_1_value = rows[i][0]
                            aggregator_2_value = rows[i][1]
                            spec = dict({vertical_axis: rows[i][2], aggregator_1: aggregator_1_value, aggregator_2: aggregator_2_value})
                            visualization_specification.data_vega_lite_spec.append(spec)
                        else:
                            aggregator_1_value = rows[i][1]
                            aggregator_2_value = rows[i][0]
                            spec = dict({vertical_axis: rows[i][2], aggregator_1: aggregator_1_value, aggregator_2: aggregator_2_value})
                            visualization_specification.data_vega_lite_spec.append(spec)
                    elif rows[i][0] == "not-available" and rows[i][1] != "not-available":
                        if agg_1_text in rows[i][1].split("-"):
                            aggregator_1_value = rows[i][1]
                            aggregator_2_value = rows[i][0]
                            spec = dict({vertical_axis: rows[i][2], aggregator_1: aggregator_1_value, aggregator_2: aggregator_2_value})
                            visualization_specification.data_vega_lite_spec.append(spec) 
                        else:
                            aggregator_1_value = rows[i][0]
                            aggregator_2_value = rows[i][1]
                            spec = dict({vertical_axis: rows[i][2], aggregator_1: aggregator_1_value, aggregator_2: aggregator_2_value})
                            visualization_specification.data_vega_lite_spec.append(spec)
                    else:
                        if agg_1_text in rows[i][0].split("-"):
                            aggregator_1_value = rows[i][0]
                            aggregator_2_value = rows[i][1]
                            spec = dict({vertical_axis: rows[i][2], aggregator_1: aggregator_1_value, aggregator_2: aggregator_2_value})
                            visualization_specification.data_vega_lite_spec.append(spec)
                        else:
                            aggregator_1_value = rows[i][1]
                            aggregator_2_value = rows[i][0]
                            spec = dict({vertical_axis: rows[i][2], aggregator_1: aggregator_1_value, aggregator_2: aggregator_2_value})
                            visualization_specification.data_vega_lite_spec.append(spec)
                           

                    
            elif len(visualization_specification.horizontal_axis) >= 2:
                print("In vega-lite spec creation and horizontal axis length >=3")
            # if agg_1_text in rows[i][0].split("-"):
                    #     # print("in if----")
                    #     # print(aggregator_1)
                    #     aggregator_1_value = rows[i][0]
                    #     print(aggregator_1_value)
                    #     aggregator_2_value = rows[i][1]
                    #     spec = dict({vertical_axis: rows[i][2], aggregator_1: aggregator_1_value, aggregator_2: aggregator_2_value})
                    # else:
                    #     # print("in else----")
                    #     # print(aggregator_2)
                    #     aggregator_1_value = rows[i][1]
                    #     aggregator_2_value = rows[i][0]
                    #     print(aggregator_2_value)
                    #     spec = dict({vertical_axis: rows[i][2], aggregator_1: aggregator_1_value, aggregator_2: aggregator_2_value})
                    

        else:
            print("not one of the above three plot types")




        #will come to this later
        # if 'map' in visualization_specification.plot_headline.plot_type:
        #     latbin = 0.0
        #     longbin = 0.0
        #
        #     bin_counts = defaultdict(int)
        #     bins = []
        #     for row in rows:
        #         lat_long_data = []
        #         for r in row:
        #             if type(r) == Decimal:
        #                 lat_long_data.append(float(r))
        #
        #         latitude, longitude = lat_long_data[0], lat_long_data[1]
        #         latbin = int(latitude / 0.001) * 0.001
        #         longbin = int(longitude / 0.001) * 0.001
        #
        #         bin = (latbin, longbin)
        #         bins.append(bin)
        #         bin_counts[bin] += 1
        #
        #     for idx, bin in enumerate(bin_counts.keys()):
        #         data_query_result = str(bin) + ";" + str(bin_counts[bin])
        #         visualization_specification.data_query_results.append(data_query_result)
        # else:
        #     for row in rows:
        #         visualization_specification.data_query_results.append(str(row))

    @staticmethod
    def convert_date(date):

        if date == "10/30/20":
            date_val = "2020-10-30"
        elif date == "11/30/20":
            date_val = "2020-11-30"
        elif date == "12/30/20":
            date_val = "2020-12-30"
        elif date == "1/30/21":
            date_val = "2021-01-30"
        elif date == "4/30/20":
            date_val = "2020-04-30"
        elif date == "5/30/20":
            date_val = "2020-05-30"
        elif date == "6/30/20":
            date_val = "2020-06-30"
        elif date == "7/30/20":
            date_val = "2020-07-30"
        elif date == "8/30/20":
            date_val = "2020-08-30"
        elif date == "9/30/20":
            date_val = "2020-09-30"
        else:
            print("In convert_date else")
            print(str(date))

        return date_val


