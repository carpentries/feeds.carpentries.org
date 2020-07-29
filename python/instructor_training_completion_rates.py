import requests
import os
import pandas as pd

import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt

api_key = os.environ['REDASH_KEY_QUERY184']

url = "https://redash.carpentries.org/api/queries/184/results.json?api_key=" + api_key

# Read query results as json and extract just the actual data
training_progress = requests.get(url)
training_progress_json = training_progress.json()
training_progress_json_data = training_progress_json['query_result']['data']['rows']

# Convert json data to dataframe
training_progress_df = pd.DataFrame(training_progress_json_data)

# Select just the necessary columns
tp = training_progress_df[['person_name', 'badges', 'checkout_step', 'checkout_step_date', 'checkout_step_status']]
tp = tp.fillna("no badge")

# Get just the people who passed
tp_pass = tp[tp['checkout_step_status']=='p']

# Pivot checkout steps to one row
tp_pass = tp_pass.groupby(['person_name', 'badges'])['checkout_step'].apply(','.join).reset_index()

# Check whether Discussion, Homework, or Demo appear in the training progress and add to column
tp_pass['Discussion'] = tp_pass['checkout_step'].apply(lambda x: "Discussion" in x)
tp_pass['Homework'] = tp_pass['checkout_step'].apply(lambda x: "Homework" in x)
tp_pass['Demo'] = tp_pass['checkout_step'].apply(lambda x: "Demo" in x)

# Check whether person has a badge
tp_pass['Badged'] = tp_pass['badges'].apply(lambda x: "Instructor" in x)


# Count how many of the three steps (Discussion, Homework, or Demo) have been completed
tp_pass['steps_completed'] = (tp_pass[['Discussion', 'Homework', 'Demo']] == True).sum(axis=1)


# Group count by number of steps completed
completion_rates = tp_pass[['person_name', 'steps_completed']].groupby(['steps_completed']).agg(['count'])

# Rename index, remove unnecessary level
completion_rates.columns = completion_rates.columns.set_levels(['persons'], level=0)
completion_rates.columns = completion_rates.columns.droplevel()

# Replace count of 3 with count of badged and rename the column.  People sometimes get badged without having all three steps checked.
completion_rates.loc[3] = tp_pass['Badged'][tp_pass['Badged'] == True].count()
completion_rates.rename(index={3:'3 (badged)'}, inplace=True)

total_trainees = completion_rates['count'].sum()

plot_title = "Checkout Steps Completed, January 2018-present\nn=" + str(total_trainees)

# # Create bar plot of data and save to file
ax = completion_rates.plot(kind='bar', title =plot_title, figsize=(8,5), legend=False, fontsize=12)
ax.set_xlabel("Count Checkout Steps Completed", fontsize=12)
ax.set_ylabel("Count Persons", fontsize=12)

for p in ax.patches:
    percentage = int((p.get_height() / completion_rates['count'].sum()) * 100)
    annotation = str(int(p.get_height())) + " (" + str(percentage) + "%)"
    ax.annotate(annotation, (p.get_x(), p.get_height() + 15 ))

ax.set_ylim(0, completion_rates.loc['3 (badged)']['count'] + 100)

plt.xticks(rotation='horizontal')

# Save plot to image file
plt.savefig('plot_checkout_completion_rates.svg')

# Save dataframe to json
completion_rates.to_json('checkout_completion_rates.json')

crt = completion_rates.to_html()

with open('checkout_completion_rates.html', 'w') as f:
    f.write("Of all trainees who completed our two day Instructor Training course, the number of people ")
    f.write("who completed 0, 1, or 2 checkout steps, and who completed all three steps (and were badged as Instructors.)")
    f.write("<br>")
    f.write("<a href='checkout_completion_rates.json'>Raw JSON data</a>")
    f.write("<img src='plot_checkout_completion_rates.svg' />")

    f.write(crt)
