import pandas as pd
import re
#from flask import flask

def mark_empty_columns(df):
    #create a list of tuples (colname: empty True/False)
    col_list = []
    for (colname, colval) in df.iteritems():
        is_null = colval.isnull().values.all()
        col_dict = {}
        col_dict['name'] = colname
        col_dict['is_null'] = is_null
        col_list.append(col_dict)
    return col_list

def get_column_name_patterns(columns):
    regex_pattern = r'[0-9]+'
    for column in columns:
        if 'tlfb' in column['name']:
            column['pattern'] = 'tlfb'
        else:
            column['pattern'] = re.sub(regex_pattern, '#',column['name'])
    return columns


#main function
def remove_empty_columns(df):
    column_list = mark_empty_columns(df)
    column_list = get_column_name_patterns(column_list)
    columns_to_delete = []
    for column in column_list:
        if column['is_null']:
            pattern = column['pattern']
            group = [col['is_null'] for col in column_list if col['pattern']==pattern]
            if all(group):
                columns_to_delete.append(column['name'])
    df = df.drop(columns_to_delete, axis=1)
    removed_columns_message=''
    for column in columns_to_delete:
        removed_columns_message+=(column+', ')
    return df, removed_columns_message
