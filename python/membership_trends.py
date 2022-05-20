# Import all the things
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import timedelta
from datetime import datetime
import requests
import json


# Set values for today and 1st of next month
today = datetime.today()
next_month = (today.replace(day=1) + timedelta(days=32)).replace(day=1)

# Get data from Redash. Create dataframe of all memberships
api_key = os.environ['REDASH_KEY_QUERY298']
redash = "http://redash.carpentries.org/api/queries/298/results.json?api_key={}".format(api_key)
data = requests.get(url=redash)

all_members = data.json()['query_result']['data']['rows']
all_members = pd.DataFrame(all_members)

all_members[["agreement_start", "agreement_end"]] = all_members[["agreement_start", "agreement_end"]].apply(pd.to_datetime, format="%Y-%m-%d")

c = ['name',  'consortium',  'agreement_start',  'agreement_end',  'variant', 'country',  'total_workshops_allowed' 'total_seats_allowed',]

all_members = all_members.reindex(columns = c)

# Create an array of the first day of every month from  2018-01-01 to next calendar month from now.
dates = pd.date_range('2018-01-01', next_month, freq='1M')-pd.offsets.MonthBegin(1)

# member_count_by_month will be a list of lists
# each sub list will have two items - date and member count
# list of lists will be made into a dataframe

member_count_by_month = []

for d in dates: 
    m = all_members[(all_members['agreement_start'] <= d) & (all_members['agreement_end'] > d)]
    member_count = len(pd.unique(m['name']))
    x = [d, member_count]
    member_count_by_month.append(x)
    
member_count_by_month_df = pd.DataFrame(columns=['start_month', 'member_count'], data=member_count_by_month)

# Add a column to the data frame to get a simple moving average over 6 months
member_count_by_month_df['sma_six_month'] = member_count_by_month_df['member_count'].rolling(6).mean()
member_count_by_month_df['sma_six_month'] = member_count_by_month_df['sma_six_month'].round(2)

# Build the line plot
plt.style.use('bmh')
plot_title = "Carpentries Memberships with 6 Month Moving Average"
ax = member_count_by_month_df.plot(x='start_month', figsize = (16, 8), grid=True,)

# ax.grid('off', which='minor', axis='x')

ax.set_title(plot_title, fontsize=24)
ax.tick_params(direction='inout', length=6,  grid_alpha=0.5)
positions = [p for p in member_count_by_month_df.start_month]
labels = member_count_by_month_df.start_month
eol = [labels[i].strftime("%b %Y") if i % 2 == 0 else ""  for i in range(len(labels))]

plt.ylabel('Member count', fontsize = 14)
plt.xlabel('Month', fontsize = 14)
plt.yticks(fontsize=16)

ax.set_xticks(positions, )


ax.set_xticklabels(eol, ha="right", fontsize = 14, rotation=45, rotation_mode='anchor', )


ax.legend(['Member count', '6 Month Moving Average'], fontsize = 16)

# Save plot image and json
plt.savefig('./plot_membership_trends.png')
member_count_by_month_df['start_month'] = member_count_by_month_df['start_month'].dt.strftime('%Y-%m-%d')
member_count_by_month_df.to_json('membership_trends.json')


