def createAgregates(df, agg_function, table_name):
    agg_column = df.columns[1]
    if agg_function == 'sum':
        return df.groupby(['Latitude', 'Longitude'])[agg_column].sum()
    elif agg_function == 'max':
        return df.groupby(['Latitude', 'Longitude'])[agg_column].max()
    elif agg_function == 'min':
        return df.groupby(['Latitude', 'Longitude'])[agg_column].min()


def convert_data(df, table_name, parameter):
    if "wind" in parameter and "icond2" in parameter:
        df[table_name] = df[table_name].apply(convert_ms_to_kmh)
    elif "snow" in parameter and "icond2" in parameter:
        df[table_name] = df[table_name].apply(convert_m_to_cm)

    return df


def convert_ms_to_kmh(ms):
    return ms * 3.6


def convert_m_to_cm(value):
    return value * 100;
