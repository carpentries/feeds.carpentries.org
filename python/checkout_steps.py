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

checkout_condensed = checkout_wide[['trainee_id','Training', 'Welcome Session', 'Get Involved', 'Demo']]

checkout_condensed.loc[checkout_condensed['Training'] == 1.0, 'Training'] = True
checkout_condensed.loc[checkout_condensed['Welcome Session'] == 1.0, 'Welcome Session'] = True
checkout_condensed.loc[checkout_condensed['Get Involved'] == 1.0, 'Get Involved'] = True
checkout_condensed.loc[checkout_condensed['Demo'] == 1.0, 'Demo'] = True

# Aggregate this to a table that has counts grouped by each combination of checkout steps
checkout_counts = checkout_condensed.groupby(['Training', 'Welcome Session', 'Get Involved', 'Demo']).size().reset_index()

checkout_counts.rename(columns={0:"count"}, inplace=True)

checkout_counts.to_json('_data/checkout_counts.json', orient='records')