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
            VisualizationSpecificationConstructor.db_executor.execute(visualization_specification.data_query)
        except IndexError:
            VisualizationSpecificationConstructor.db_executor.close()
            VisualizationSpecificationConstructor.db = mc.connect(host='localhost', user='root', password='admin',
                                                                  database='covid')
            VisualizationSpecificationConstructor.db_executor = VisualizationSpecificationConstructor.db.cursor()
            VisualizationSpecificationConstructor.db_executor.execute(visualization_specification.data_query)

        rows = VisualizationSpecificationConstructor.db_executor.fetchall()
        if 'map' in visualization_specification.plot_headline.plot_type:
            latbin = 0.0
            longbin = 0.0

            bin_counts = defaultdict(int)
            bins = []
            for row in rows:
                lat_long_data = []
                for r in row:
                    if type(r) == Decimal:
                        lat_long_data.append(float(r))

                latitude, longitude = lat_long_data[0], lat_long_data[1]
                latbin = int(latitude / 0.001) * 0.001
                longbin = int(longitude / 0.001) * 0.001

                bin = (latbin, longbin)
                bins.append(bin)
                bin_counts[bin] += 1

            for idx, bin in enumerate(bin_counts.keys()):
                data_query_result = str(bin) + ";" + str(bin_counts[bin])
                visualization_specification.data_query_results.append(data_query_result)
        else:
            for row in rows:
                visualization_specification.data_query_results.append(str(row))
