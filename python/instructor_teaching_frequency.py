
import pandas as pd
import requests
import matplotlib.pyplot as plt
import os

api_key33 = os.environ['REDASH_KEY_QUERY33']
api_key39 = os.environ['REDASH_KEY_QUERY39']

# Count Instructor and their teaching frequency
url = "http://redash.carpentries.org/api/queries/33/results.json?api_key=" +  api_key33
# Read query results as json and extract just the actual data
teaching_frequency = requests.get(url)
teaching_frequency_json = teaching_frequency.json()
teaching_frequency_json_data = teaching_frequency_json['query_result']['data']['rows']

# Get count of instructors who have never taught and add it to the above json data
url_never = "http://redash.carpentries.org/api/queries/39/results.json?api_key=" + api_key39
never_taught = requests.get(url_never)
never_taught_count = len(never_taught.json()['query_result']['data']['rows'])
teaching_frequency_json_data.append({'num_wkshps': 0, 'num_instructors': never_taught_count})

# Convert json data to dataframe
teaching_frequency_df = pd.DataFrame(teaching_frequency_json_data)
teaching_frequency_df.sort_values(by=['num_wkshps'], inplace=True)

total_instructors=teaching_frequency_df['num_instructors'].sum()

# Create bins to store teaching frequencies.
bins = [float("-inf"), 0, 5, 10, 25, float("inf")]
labels = ['Never', '1-5\nworkshops', '6-10\nworkshops', '11-25\nworkshops', '26 or more\nworkshops']
teaching_frequency_df['interval_bins'] = pd.cut(x=teaching_frequency_df['num_wkshps'], bins=bins, labels=labels)
teaching_frequency_binned = teaching_frequency_df.groupby(['interval_bins'])[['num_instructors']].sum().reset_index()
binned_max = teaching_frequency_binned['num_instructors'].max()

# Plot binned teaching frequency
fig, ax = plt.subplots()
teaching_frequency_binned.plot(kind='bar', x='interval_bins', ax=ax, zorder=3, )
ax.grid(zorder=0, color="lightgray")
ax.legend(['Count Instructors'], )
ax.set_ylim([0, binned_max * 1.15])
plt.xticks(rotation=0)
plt.xlabel("Workshop Count")
plt.ylabel("Instructor Count")
plt.title("The Carpentries Instructor Teaching Frequency \n(n=" + str(total_instructors) + ")")

# Add annotations to bars
for p in ax.patches:
    count = int((p.get_height()))
    pct = int(p.get_height() / total_instructors * 100)
    bar_top_label = str(count) + "\n(" + str(pct) + "%)"
    ax.annotate(bar_top_label, (p.get_x() * 1.05, p.get_height() + 15 ),)
plt.tight_layout()  # Keeps labels on edges from getting cut off

# Save outputs as png image and json data
plt.savefig('./instructor_teaching_frequency.png')
teaching_frequency_df.to_json('./instructor_teaching_frequency.json')
