from sql_constructor import SQLConstructor


sql = SQLConstructor()
sql.add_select('date')
sql.add_select_sum('new_cases')
sql.add_from('counties_cdc_cases')
sql_query = sql.construct()
print(sql_query)
