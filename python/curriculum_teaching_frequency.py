import requests
import os
import pandas as pd

import plotly
import plotly.graph_objects as go
import plotly.express as px

import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
# %matplotlib inline # only for Jupyter Notebook

# Keeps long text in columns from getting truncated
pd.set_option('display.max_colwidth', None)

import numpy as np

api_key = os.environ['REDASH_KEY_QUERY157']
query_url = "https://redash.carpentries.org/api/queries/157/results.json?api_key=" + api_key

all_events = requests.get(query_url)
all_events_json = all_events.json()
all_events_json = all_events_json['query_result']['data']['rows']
all_events_df = pd.DataFrame(all_events_json)
all_events_df.dropna(inplace=True)
all_events_df.event_start = pd.to_datetime(all_events_df['event_start'])
all_events_df['year'] = all_events_df['event_start'].dt.year
all_events_df['curriculum'] = all_events_df['curriculum'].str.replace('Data Carpentry', 'DC')
all_events_df['curriculum'] = all_events_df['curriculum'].str.replace('Library Carpentry', 'LC')
all_events_df['curriculum'] = all_events_df['curriculum'].str.replace('Software Carpentry', 'SWC')

curr_group = all_events_df[['slug', 'curriculum', 'how_organized','year']].groupby(['year', 'curriculum', 'how_organized',]).count().unstack(fill_value=0).stack()



curr_group.reset_index(inplace=True)

curr_group.sort_values(by=['year', 'curriculum', 'how_organized'], inplace=True)


trace2019_self = go.Bar(
                x = curr_group[(curr_group['year']==2019) & (curr_group['how_organized']=="Self-organized")]['curriculum'],
                y = curr_group[(curr_group['year']==2019) & (curr_group['how_organized']=="Self-organized")]['slug'],
                name="Self Organized"
    
                )

trace2019_cent = go.Bar(
                x = curr_group[(curr_group['year']==2019) & (curr_group['how_organized']=="Centrally organized")]['curriculum'],
                y = curr_group[(curr_group['year']==2019) & (curr_group['how_organized']=="Centrally organized")]['slug'],
                name="Centrally Organized"
                )

data = [trace2019_self, trace2019_cent]

title_text = "The Carpentries Workshops"

layout = dict(title= title_text + ': 2019', 
              showlegend=True,
              barmode='stack',
              xaxis={'showgrid':True}
              )


fig = go.Figure(data=data, layout=layout)

curr_group.to_csv('curriculum_teaching_frequency.csv')
plotly.offline.plot(fig, filename='curriculum_teaching_frequency.html', auto_open=False)


