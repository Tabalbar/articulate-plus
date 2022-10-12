from collections import defaultdict
from copy import copy
import json

from .sql_constructor import SQLConstructor
from dev.text_tokenizer_pipeline.temporal_utils import TemporalUtils


class VisualizationTask:
    def __init__(self):
        self.context_utterances = None

        self.action = None
        self.data_query = None
        self.horizontal_axis = set()
        self.horizontal_axis_grouping = set()
        self.vertical_axis = set()
        self.filters = defaultdict(set)
        self.aggregators = set()
        self.context_filters = defaultdict(set)
        self.context_aggregators = set()
        self.plot_type = None
        self.is_plot_type_specified = None
        self.manually_added_aggregator = None
        self.map_type = None
        self.summary = None
        self.sql = SQLConstructor()

    def add_horizontal_axis(self, horizontal_axis):
        # print("HORIZONTAL AXIS NOT NEW_CASES:" +horizontal_axis)
        self.horizontal_axis.add(horizontal_axis)
        self.sql.add_select(horizontal_axis)
        self.update_specification()

    def remove_horizontal_axis(self, horizontal_axis):
        self.horizontal_axis.remove(horizontal_axis)
        self.sql.remove_select(horizontal_axis)
        self.update_specification()

    def add_vertical_axis(self, vertical_axis):
        self.vertical_axis.add(vertical_axis)
        self.sql.add_select_count(vertical_axis)
        self.update_specification()

    def remove_vertical_axis(self, vertical_axis):
        self.vertical_axis.remove(vertical_axis)
        self.sql.remove_select_count(vertical_axis)
        self.update_specification()

    def add_vertical_axis_sum(self, vertical_axis):
        self.vertical_axis.add(vertical_axis)
        self.sql.add_select_sum(vertical_axis)
        self.update_specification()

    def remove_vertical_axis_sum(self, vertical_axis):
        self.vertical_axis.remove(vertical_axis)
        self.sql.remove_select_sum(vertical_axis)
        self.update_specification()

    def add_filter(self, attribute, value):
        self.filters[attribute].add(value)
        self.sql.add_where((attribute, value))

        self.update_specification()

    def add_context_filter(self, attribute, value):
        self.context_filters[attribute].add(value)

    def add_all_filters(self, filters):
        cpy_filters = copy(filters)
        for attribute, values in cpy_filters.items():
            for value in values:
                self.add_filter(attribute, value)

    def add_all_context_filters(self, filters):
        cpy_filters = copy(filters)
        for attribute, values in cpy_filters.items():
            for value in values:
                self.add_context_filter(attribute, value)

    def remove_filter(self, attribute):
        values = self.filters.pop(attribute, None)
        if not values:
            return

        for value in values:
            self.sql.remove_where((attribute, value))
            self.update_specification()

    def remove_context_filter(self, attribute):
        self.context_filters.pop(attribute, None)

    def remove_all_filters(self):
        cpy_filters = copy(self.filters)
        for attribute in cpy_filters.keys():
            self.remove_filter(attribute)

    def remove_all_context_filters(self, filters):
        cpy_filters = copy(filters)
        for attribute, value in cpy_filters.items():
            self.remove_context_filter(attribute)

    def remove_filter_value(self, attribute, value):
        if attribute not in self.filters:
            return

        values = self.filters[attribute]
        values.remove(attribute)

        if not values:
            self.filters.pop(attribute, None)

        self.sql.remove_where((attribute, value))
        self.update_specification()

    def remove_context_filter_value(self, attribute, value):
        if attribute not in self.context_filters:
            return

        values = self.context_filters[attribute]
        values.remove(attribute)

        if not values:
            self.context_filters.pop(attribute, None)

    def any_filter_geographically_relevant(self):
        if not self.filters:
            return False

        # if self.aggregators:
        #     return False

        for filter_attribute in self.filters.keys():
            if filter_attribute in ['county_type', 'region', 'state']:
                print("GEOGRAPHICAL aggregator")
                return True

        return False

    def any_aggregator_geographically_relevant(self):
        # if not self.filters:
        #     return False

        if not self.aggregators:
            return False
        else:
            for i in range(len((list(self.aggregators)))):
                if (list(self.aggregators)[i][0]) in ['county_type', 'region', 'state']:
                    print("GEOGRAPHICAL aggregator")
                    return True
        # return False



    def any_context_filter_geographically_relevant(self):
        if not self.context_filters:
            return False

        if self.aggregators:
            return False

        for filter_attribute in self.context_filters.keys():
            if filter_attribute in ['county_type', 'region', 'state']:
                print("GEOGRAPHICAL ATTRIBUTE")
                return True

        return False

    def get_summary(self):
        if not self.plot_type:
            return self.plot_type

        if "map" not in self.plot_type:
            self.summary = self.plot_type + ' chart '
        else:
            self.summary = self.plot_type + ' '

        if self.filters:
            self.summary += 'of '
            for attribute, values in self.filters.items():
                for value in values:
                    self.summary += attribute + '=' + value + ', '
            self.summary = self.summary[:-2] + ' '

        if self.aggregators:
            self.summary += 'by '
            for attribute, entity_children in self.aggregators:
                self.summary += attribute + ', '
            self.summary = self.summary[:-2] + ' '

        self.summary = self.summary.strip().lower()
        return self.summary

    def add_aggregator(self, attribute, entity_children):
        self.sql.add_group_by(attribute)
        self.sql.add_order_by(attribute, entity_children)
        self.add_horizontal_axis(attribute)
        self.aggregators.add((attribute, entity_children))
        self.update_specification()

    # def add_first_aggregator(self, attribute, entity_children):
    #     self.sql.add_group_by(attribute)
    #     self.sql.add_order_by(attribute, entity_children)
    #
    #     # self.add_horizontal_axis(attribute)
    #     self.aggregators.add((attribute, entity_children))
    #     self.update_specification()

    def add_aggregator_map(self, attribute):
        self.sql.add_group_by(attribute)
        self.sql.add_group_by("fips")
        # self.sql.add_group_by("longitude")
        # self.sql.add_order_by(attribute, entity_children)

        # self.add_horizontal_axis(attribute)
        # self.aggregators.add((attribute, entity_children))
        # self.update_specification()

    def add_context_aggregator(self, attribute, entity_children):
        self.context_aggregators.add((attribute, entity_children))

    def add_all_aggregators(self, aggregators):
        cpy_aggregators = copy(aggregators)
        for attribute, entity_children in cpy_aggregators:
            self.add_aggregator(attribute, entity_children)

    def add_all_context_aggregators(self, aggregators):
        cpy_aggregators = copy(aggregators)
        for attribute, entity_children in cpy_aggregators:
            self.add_context_aggregator(attribute, entity_children)

    def remove_aggregator(self, attribute):
        print("............In remove aggregator...........")
        cpy_aggregators = copy(self.aggregators)
        for candidate, entity_children in cpy_aggregators:
            if candidate == attribute:
                self.aggregators.discard((attribute, entity_children))
                self.sql.remove_group_by(attribute)
                self.sql.remove_order_by(attribute, entity_children)

                if attribute in self.horizontal_axis:
                    self.remove_horizontal_axis(attribute)
                elif attribute in self.horizontal_axis_grouping:
                    self.remove_horizontal_axis_grouping(attribute)
                self.update_specification()

    def remove_context_aggregator(self, attribute):
        cpy_context_aggregators = self.context_aggregators
        for candidate, entity_children in cpy_context_aggregators:
            if candidate == attribute:
                self.context_aggregators.discard(attribute)

    def remove_all_aggregators(self):
        cpy_aggregators = copy(self.aggregators)
        for attribute, entity_children in cpy_aggregators:
            self.remove_aggregator(attribute)

    def remove_all_context_aggregators(self):
        cpy_aggregators = copy(self.context_aggregators)
        for attribute, entity_children in cpy_aggregators:
            self.remove_context_aggregator(attribute)

    def add_horizontal_axis_grouping(self, attribute):
        if attribute in self.horizontal_axis:
            self.horizontal_axis_grouping.add(attribute)
            self.horizontal_axis.discard(attribute)
            return

        self.sql.add_select(attribute)
        self.horizontal_axis_grouping.add(attribute)
        self.update_specification()

    def remove_horizontal_axis_grouping(self, horizontal_axis_grouping):
        self.horizontal_axis_grouping.remove(horizontal_axis_grouping)
        self.sql.remove_select(horizontal_axis_grouping)
        self.update_specification()

    def update_specification(self):
        self.data_query = self.sql.construct()

    def redistribute_horizontal_axis_variables(self):
        if not self.horizontal_axis and not self.horizontal_axis_grouping:
            return

        if self.horizontal_axis and len(self.horizontal_axis_grouping) < 2:
            return

        itr = iter(self.horizontal_axis_grouping)
        axis = itr.__next__()
        self.horizontal_axis.add(axis)
        self.horizontal_axis_grouping.discard(axis)

    def get_json_obj(self):
        s = json.dumps(self, default=self._to_json, sort_keys=True, indent=4)
        obj = json.loads(s)
        return obj

    def get_json_str(self):
        return json.dumps(self, default=self._to_json, sort_keys=True, indent=4)

    def _to_json(self, o):
        if hasattr(o, '__dict__'):
            return o.__dict__
        elif isinstance(o, set):
            return list(o)
    def remove_sql(self):
        self.sql.remove()
        self.update_specification()
