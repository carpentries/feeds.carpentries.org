# Import all the things
import pandas as pd
import requests
import os 

# Retreive data from Redash - checkout steps completed by each trainee
# Remove trainees who had anything happen before 2019-01-01 as we were not 
# systematically tracking this back then

api_key295 = os.environ['REDASH_KEY_QUERY295']

checkout_progress_url = "http://redash.carpentries.org/api/queries/295/results.json?api_key=" + api_key295

r = requests.get(checkout_progress_url)
checkout = r.json()['query_result']['data']['rows']
checkout = pd.DataFrame(checkout)
checkout['completed'] = True
checkout_old = checkout[checkout['date'] < "2019-01-01"]['trainee_id']
checkout = checkout[checkout['date'] > "2019-01-01"]
checkout=checkout[~checkout['trainee_id'].isin(checkout_old)]

# "Widen" the checkout progress table
# This creates one row for each trainee.
checkout_wide = checkout.pivot_table(index='trainee_id', columns = 'requirement', values="completed").reset_index()
checkout_wide.fillna(False, inplace=True)

# Drop rows where `Training == False`. These are likely cases where data was incorrectly entered or carryovers from old systems.

checkout_wide = checkout_wide[checkout_wide['Training'] == True]

# Combine the demo and homework columns as lesson program doesn't matter
# This "adds" the true/false values, to return a 1 (true value)

checkout_wide["Demo"] =  checkout_wide[['SWC Demo', 'DC Demo', 'LC Demo']].any(axis = "columns")
checkout_wide["Homework"] = checkout_wide[['SWC Homework', 'DC Homework', 'LC Homework']].any(axis = "columns")

## Re-order the columns so the necessary ones are at the end.

checkout_wide = checkout_wide[[  'DC Demo',
                                 'DC Homework',
                                 'LC Demo',
                                 'LC Homework',
                                 'SWC Demo',
                                 'SWC Homework',
                                 'trainee_id',
                                 'Training',
                                 'Discussion',
                                 'Homework',
                                 'Demo']]

# Get just the last columns (`'trainee_id','Training', 'Discussion', 'Homework', 'Demo'`). Save this to a new dataframe
checkout_condensed = checkout_wide[['trainee_id','Training', 'Discussion', 'Homework', 'Demo']]

# Aggregate this to a table that has counts grouped by each combination of checkout steps
checkout_counts = checkout_condensed.groupby(['Training', 'Discussion', 'Homework', 'Demo']).size().reset_index()
checkout_counts.rename(columns={0:"count"}, inplace=True)

checkout_counts.to_json('_data/checkout_counts.json', orient='records')