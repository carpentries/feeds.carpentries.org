# Import all the things

import requests
import os
import pandas as pd
import numpy as np
import plotly

import matplotlib
matplotlib.use('agg')  # Because of the tkinter error
import matplotlib.pyplot as plt

# Only for Jupyter notebook
# %matplotlib inline

import plotly.graph_objects as go

# Keeps long text in columns from getting truncated
pd.set_option('display.max_colwidth', -1)

api_key = os.environ['REDASH_KEY_QUERY187']

query_url = "https://redash.carpentries.org/api/queries/187/results.json?api_key=" + api_key

all_events = requests.get(query_url)
all_events_json = all_events.json()

all_events_json = all_events_json['query_result']['data']['rows']
all_events_df = pd.DataFrame(all_events_json)
all_2018 = all_events_df[all_events_df['YEAR']=='2018']
all_2019 = all_events_df[all_events_df['YEAR']=='2019']

# Set up plot formatting
title_text ="The Carpentries Instructor Training Events Seat Usage"

member_color = "#003f5c"  # dark blue
open_color = "#ffa600"    # orange


# Plot member and open seasts as bar and totals as scatter for ALL dates

trace_all_member = go.Bar(
                x=all_events_df['slug'], 
                y=all_events_df['member_seats'], 
                name="All Member",
                hoverinfo='y + x',
                marker_color = member_color)
    
trace_all_open = go.Bar(
                x=all_events_df['slug'], 
                y=all_events_df['open_seats'], 
                name="All Open",
                hoverinfo='y + x',
                marker_color = open_color)

trace_all = go.Scatter(
                x=all_events_df['slug'], 
                y=all_events_df['total_seats'], 
                name="All Events", 
                mode="text",
                text=all_events_df['total_seats'],
                textposition = "top center",
                showlegend=False,
                hoverinfo='none')


# Plot member and open seats as bar and totals as scatter for 2018 dates
trace_2018 = go.Scatter(
                x=all_2018['slug'], 
                y=all_2018['total_seats'], 
                name="2018 All", 
                mode="text",
                text=all_2018['total_seats'],
                textposition = "top center",
                visible=False, 
                showlegend=False, 
                hoverinfo='none')


trace_2018_open = go.Bar(
                x=all_2018['slug'], 
                y=all_2018['open_seats'], 
                name="2018 Open", 
                visible=False,
                hoverinfo='y + x',
                marker_color = open_color)


trace_2018_member = go.Bar(x=all_2018['slug'], 
                           y=all_2018['member_seats'], 
                           name="2018 Member", 
                           visible=False, 
                           hoverinfo='y + x',
                           marker_color = member_color)


# Plot member and open seats as bar and totals as scatter for 2019 dates

trace_2019 = go.Scatter(
                x=all_2019['slug'], 
                y=all_2019['total_seats'], 
                name="2019 All", 
                mode="text",
                text=all_2019['total_seats'],
                textposition = "top center",
                visible=False,
                showlegend=False,
                hoverinfo='none')


trace_2019_open = go.Bar(
                x=all_2019['slug'], 
                y=all_2019['open_seats'], 
                name="2019 Open", 
                visible=False, 
                hoverinfo='y + x',
                marker_color = open_color)


trace_2019_member = go.Bar(
                x=all_2019['slug'], 
                y=all_2019['member_seats'], 
                name="2019 Member", 
                visible=False,
                hoverinfo='y + x',
                marker_color = member_color)


data = [trace_2018, 
        trace_2018_open,
        trace_2018_member,
        trace_2019, 
        trace_2019_open,
        trace_2019_member,
        trace_all, 
        trace_all_member, 
        trace_all_open,
        ]


updatemenus = list([
    dict(active=-1,
         type = "buttons",  # Leaving this line off makes it look like a drop down
         buttons=list([   
            dict(label = '2018 Events',
                 method = 'update',
                 args = [{'visible': [x in (trace_2018_member, trace_2018_open, trace_2018) for x in data]},
                         {'title': title_text + ': 2018'}]),
             
  
             dict(label = '2019 Events',
                 method = 'update',
                 args = [{'visible': [x in (trace_2019_member, trace_2019_open, trace_2019) for x in data]},
                         {'title': title_text + ': 2019'}]),
             
             dict(label = "All Events",
                  method = 'update',
                   args = [{'visible':[x in (trace_all_member, trace_all_open, trace_all) for x in data]}, 
                           {'title': title_text + ': 2018-2019' },
                          ])

        ]),
    )
])



layout = dict(title= title_text + ': 2018-2019', showlegend=True,
              updatemenus=updatemenus, barmode='stack', width=1600, height=800)


fig = go.Figure(data=data, layout=layout)

# For Jupyter notebook
# fig.show()


all_events_df.to_csv('IT_seat_usage.csv')
plotly.offline.plot(fig, filename='IT_seat_usage.html', auto_open=False)
