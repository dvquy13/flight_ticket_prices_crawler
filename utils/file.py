import os
import pandas as pd


def save_or_append(df: pd.DataFrame, path: str):
    if not os.path.exists(path):
        df.to_csv(path, index=False)
    else:
        with open(path, 'a', encoding='utf-8') as f:
            df.to_csv(f, header=False, index=False)