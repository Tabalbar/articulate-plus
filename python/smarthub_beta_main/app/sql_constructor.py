from collections import OrderedDict

'''
Input: "Show me thefts by months of the year"
Output: "SELECT COUNT(*) FROM CHICAGOCRIME WHERE crime='thefts' GROUP BY months

 SELECT counties_cdc_cases.date, SUM(new_cases) As Total_Cases FROM counties_cdc_cases 
 WHERE( region = 'southeast' ANDcounty_type = 'rural') GROUP BY counties_cdc_cases.date;
'''


class SQLConstructor:
    def __init__(self):
        self._SELECT = OrderedDict()
        self._SELECT_COUNT = OrderedDict()
        self._SELECT_SUM = OrderedDict() #->for sum(new_cases)
        self._FROM = OrderedDict()
        self._WHERE = OrderedDict()
        self._GROUP_BY = OrderedDict()
        self._ORDER_BY = OrderedDict()

    def get_select(self):
        return self._SELECT

    def set_select(self, SELECT):
        self._SELECT = SELECT

    def add_select(self, select_attribute):
        self._SELECT[select_attribute] = select_attribute

    def remove_select(self, select_attribute):
        self._SELECT.pop(select_attribute, None)

    def get_select_count(self):
        return self._SELECT_COUNT

    def set_select_count(self, SELECT_COUNT):
        self._SELECT_COUNT = SELECT_COUNT

    def add_select_count(self, select_count_attribute):
        self._SELECT_COUNT[select_count_attribute] = select_count_attribute

    def remove_select_count(self, select_count_attribute):
        self._SELECT_COUNT.pop(select_count_attribute, None)
   #SELECT_SUM crud

    def add_select_sum(self, select_sum_attribute):
        self._SELECT_SUM[select_sum_attribute] = select_sum_attribute

    def remove_select_sum(self, select_sum_attribute):
        self._SELECT_SUM.pop(select_sum_attribute, None)

    def get_from(self, FROM):
        return self._FROM

    def set_from(self, FROM):
        self._FROM = FROM

    def add_from(self, from_attribute):
        self._FROM[from_attribute] = from_attribute

    def remove_from(self, from_attribute):
        self._FROM.pop(from_attribute, None)

    def get_where(self):
        return self._WHERE

    def set_where(self, WHERE):
        self._WHERE = WHERE

    def add_where(self, where_attribute_value):
        attribute, value = where_attribute_value[0], where_attribute_value[1]
        if attribute not in self._WHERE:
            self._WHERE[attribute] = set()

        formatted = attribute + "='" + value + "'"
        self._WHERE[attribute].add(formatted)

    def remove_where(self, where_attribute_value):
        attribute, value = where_attribute_value[0], where_attribute_value[1]
        for attribute_value in self._WHERE[attribute]:
            if value in attribute_value:
                self._WHERE[attribute].remove(attribute_value)
                if not self._WHERE[attribute]:
                    self._WHERE.pop(attribute, None)
                break

    def get_group_by(self):
        return self._GROUP_BY

    def set_group_by(self, GROUP_BY):
        self._GROUP_BY = GROUP_BY

    def add_group_by(self, group_by_attribute):
        self._GROUP_BY[group_by_attribute] = group_by_attribute

    def remove_group_by(self, group_by_attribute):
        self._GROUP_BY.pop(group_by_attribute, None)

    def get_order_by(self):
        return self._ORDER_BY

    def set_order_by(self, ORDER_BY):
        self._ORDER_BY = ORDER_BY

    def add_order_by(self, order_by_attribute, entity_children):
        if not entity_children:
            return

        special_case = 'CASE '
        for i in range(1, len(entity_children)):
            child_data_attribute = entity_children[i]
            special_case += 'WHEN counties_cdc_cases.' + order_by_attribute + "= '" + child_data_attribute + "' THEN " + str(
                i) + ' '

        special_case += 'END ASC'
        self._ORDER_BY[order_by_attribute] = special_case

    def remove_order_by(self, order_by_attribute, entity_children):
        if order_by_attribute in self._ORDER_BY:
            self._ORDER_BY.pop(order_by_attribute, None)
            return

        special_case = 'CASE '
        for i in range(1, len(entity_children)):
            child_data_attribute = entity_children[i]
            special_case += 'WHEN counties_cdc_cases.' + order_by_attribute + "= '" + child_data_attribute + "' THEN " + str(
                i) + ' '
        special_case += 'END ASC'
        self._ORDER_BY.pop(special_case, None)

    def remove_all_order_bys(self):
        self._ORDER_BY.clear()

    def _join_attribute_value_pairs(self, clause):
        if not clause:
            return ''

        formatted = ''
        for key in clause.keys():
            attributes = ['counties_cdc_cases.' + attribute for attribute in clause[key]]
            formatted += '('
            formatted += ' OR '.join(attributes)
            formatted += ') AND '
        return formatted[:-1 * len(' AND ')]

    def remove(self):
        self._SELECT.clear()
        self._SELECT_COUNT.clear()
        self._SELECT_SUM.clear()
        self._FROM.clear()
        self._WHERE.clear()
        self._GROUP_BY.clear()
        self._ORDER_BY.clear()

    def construct(self):
        selects = ','.join(['counties_cdc_cases.' + attribute for attribute in self._SELECT.values()])
        select_counts = ','.join([v for v in self._SELECT_COUNT.values() if v != None])
        select_sums = ','.join([v for v in self._SELECT_SUM.values() if v != None])
        froms = ','.join(self._FROM.values())
        order_bys = ','.join(self._ORDER_BY.values())
        group_bys = ','.join(['counties_cdc_cases.' + attribute for attribute in self._GROUP_BY.values()])
        wheres = self._join_attribute_value_pairs(self._WHERE)
        wheres = wheres.replace('\\', '')

        sql = 'SELECT '
        # if (group_bys):
        #     sql += ''
        # else:
        #     # print("In ELSE")
        #     sql += 'DISTINCT 'x


        if selects:
            sql += selects + ','
        if select_counts:
            sql += 'count(DISTINCT counties_cdc_cases.fips) as ' + select_counts
        elif select_sums:
            sql += 'sum(new_cases) as ' + select_sums
        else:
            sql = sql[:-1]
        sql += ' FROM ' + froms
        # if select_sums:
        #     sql += 'sum(new_cases) as' + select_sums
        if wheres:
            sql += ' WHERE ' + wheres
        if group_bys:
            sql += ' GROUP BY ' + group_bys
        if order_bys:
            sql += ' ORDER BY ' + order_bys
            if 'NUM_COUNTIES' in select_counts:
                sql += ', NUM_COUNTIES'
        # elif select_counts:
        #     sql += ' ORDER BY xribute'

        # print("SQL = " +str(sql))

        return sql
