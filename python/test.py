
import pandas as pd

data = {'county': ['Ali', 'Bob', 'Cam', 'Des', 'Eli'], 
        'year': [2016, 2017, 2013, 2019, 2019], 
        'reports': [14, 4, 81, 29, 39]}

outfile = "./test.csv"

df = pd.DataFrame(data)
df.to_csv(outfile)
