import pandas as pd
import numpy as np
import os

K = 90

counter = 0
for file in os.listdir('PAGASA/'):
    if not file.endswith('.csv'):
        continue

    df = pd.read_csv('PAGASA/' + file)
    df = df[df.isin([-999]).any(axis=1)]

    if len(df) >= K:
        print(file)
        counter += 1

print(counter)

