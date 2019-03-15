import pandas as pd

def get_current_timestr(dt):
    return pd.to_datetime(dt).strftime('%Y-%m-%d %H:%M')


def get_arrow(a, b):
    if a < b:
        return ':decrease:'
    else:
        return ':increase:'