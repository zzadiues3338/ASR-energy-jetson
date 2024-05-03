#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 11:29:09 2024

@author: chakz
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 11:29:09 2024

@author: chakz
"""

import os
import sys
import pandas as pd
import numpy as np

filename = sys.argv[1]

# Change directory to the script's directory dynamically
os.chdir(os.path.dirname(os.path.abspath(__file__)))

mem_baseline = 1650  # MB this is the resting memory consumption when no other application is running
thresh = 40  # % GPU utilization - when running typical CV/NLP application its almost always 99 .......
baseline_power = 515  # mW value this is the resting CPU+GPU consumption when no other application is running

print('reading in the power report')
#filename = 'output_2024-04-18_23-22-58.csv'
df = pd.read_csv(filename, header=None)

print(f'processing power report with threshold equal to {thresh}')

filtered_df = df[df.iloc[:, 27] > thresh]  # this is the column number for GPU load %

# Extract the first number before 'mW' from column 40, remove baseline power consumption value and sum them
total_mw = (filtered_df.iloc[:, 55].str.extract(r'(\d+)mW').astype(float).values - baseline_power).sum()  # GPU inst power

# Convert to watts
total_energy_joule = total_mw / 1000  # only if the time interval is in seconds

values_int = filtered_df.iloc[:, 3].str[:4].astype(int).values - mem_baseline  # time varying mem consumption for application

mean_value = np.mean(values_int)
median_value = np.median(values_int)
max_value = np.max(values_int)

print(f"TOTAL_ENERGY_JOULE={total_energy_joule}")
print(f"MEAN_VALUE={mean_value}")
print(f"MEDIAN_VALUE={median_value}")
print(f"MAX_VALUE={max_value}")
