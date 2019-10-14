import requests
import os
import pandas as pd
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt


API_KEY = os.environ['REDASH_KEY_QUERY165']

# Redash query that returns each training checkout step completed for each trainee
training_progress_url = 'http://redash.carpentries.org/api/queries/165/results.json?api_key=' + API_KEY

# Read query results as json and extract just the actual data
training_progress = requests.get(training_progress_url)
training_progress_json = training_progress.json()
training_progress_json_data = training_progress_json['query_result']['data']['rows']

# Convert json data to dataframe
training_progress_df = pd.DataFrame(training_progress_json_data)

# Check whether Discussion, Homework, or Demo appear in the training progress and add to column
training_progress_df['Discussion'] = training_progress_df['progress'].apply(lambda x: "Discussion" in x)
training_progress_df['Homework'] = training_progress_df['progress'].apply(lambda x: "Homework" in x)
training_progress_df['Demo'] = training_progress_df['progress'].apply(lambda x: "Demo" in x)

# Check whether person has a badge
training_progress_df['Badged'] = training_progress_df['title'].apply(lambda x: pd.notnull(x))


# Count how many of the three steps (Discussion, Homework, or Demo) have been completed
training_progress_df['steps_completed'] = (training_progress_df[['Discussion', 'Homework', 'Demo']] == True).sum(axis=1)

# Group count by number of steps completed
completion_rates = training_progress_df[['trainee_person_name', 'steps_completed']].groupby(['steps_completed']).agg(['count'])

# Rename index, remove unnecessary level
completion_rates.columns = completion_rates.columns.set_levels(['persons'], level=0)
completion_rates.columns = completion_rates.columns.droplevel()

# Replace count of 3 with count of badged and rename the column.  People sometimes get badged without having all three steps checked.
completion_rates.loc[3] = training_progress_df['Badged'][training_progress_df['Badged'] == True].count()
completion_rates.rename(index={3:'3 (badged)'}, inplace=True)

# Send output to csv
completion_rates.to_json('completion_rates.json')

total_trainees = str(completion_rates['count'].sum())

plot_title = "Checkout Steps Completed, January 2018-present\nn=" + total_trainees

# Create bar plot of data and save to file
ax = completion_rates.plot(kind='bar', title =plot_title, figsize=(8,5), legend=False, fontsize=12)
ax.set_xlabel("Count Checkout Steps Completed", fontsize=12)
ax.set_ylabel("Count Persons", fontsize=12)

for p in ax.patches:
    ax.annotate(int(p.get_height()), (p.get_x() + 0.15, p.get_height() + 5 ))

ax.set_ylim(0, completion_rates.loc['3 (badged)']['count'] + 100)

plt.xticks(rotation='horizontal')
plt.savefig('checkout.png')