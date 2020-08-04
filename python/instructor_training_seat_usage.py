import requests
import os
import pandas as pd
import plotly

# Only for Jupyter notebook
# %matplotlib inline

import plotly.graph_objects as go

# Keeps long text in columns from getting truncated
pd.set_option('display.max_colwidth', None)

api_key = os.environ['REDASH_KEY_QUERY187']

query_url = "https://redash.carpentries.org/api/queries/187/results.json?api_key=" + api_key

all_events = requests.get(query_url)
all_events_json = all_events.json()

all_events_json = all_events_json['query_result']['data']['rows']
all_events_df = pd.DataFrame(all_events_json)
all_2018 = all_events_df[all_events_df['YEAR'] == '2018']
all_2019 = all_events_df[all_events_df['YEAR'] == '2019']
all_2020 = all_events_df[all_events_df['YEAR'] == '2020']
# Set up plot formatting
title_text = "The Carpentries Instructor Training Events Seat Usage"

member_color = "#003f5c"  # dark blue
open_color = "#ffa600"  # orange


def create_bar_trace(df, title, member_open_all, bar_color):
    """
    Takes a dataframe with counts of trainees from open and member seats.  Returns trace
    for a bar chart plotting this data.
    """
    new_bar_trace = go.Bar(
        x=df['slug'],
        y=df[member_open_all],
        name = title,
        marker_color = bar_color,
        hoverinfo='y + x',
        )
    return new_bar_trace

def create_scatter_trace(df, title, visibility):
    """
    Takes a dataframe with counts of trainees from open and member seats.  Returns trace for scatter plot
    of this data.  Used to label bar charts.
    """
    new_scatter_trace = go.Scatter(
        x=df['slug'],
        y=df['total_seats'],
        name= title,
        mode="text",
        text=df['total_seats'],
        textposition="top center",
        visible=visibility,
        showlegend=False,
        hoverinfo='none')
    return new_scatter_trace

trace_all_open = create_bar_trace(df=all_events_df, title="All Open", member_open_all="open_seats", bar_color=open_color)
trace_all_member = create_bar_trace(df=all_events_df, title="All Member", member_open_all="member_seats", bar_color=member_color)
trace_2018_open = create_bar_trace(df=all_2018, title="2018 Open", member_open_all="open_seats", bar_color=open_color)
trace_2018_member = create_bar_trace(df=all_2018, title="2018 Member", member_open_all="member_seats", bar_color=member_color)
trace_2019_open = create_bar_trace(df=all_2019, title="2019 Open", member_open_all="open_seats", bar_color=open_color)
trace_2019_member = create_bar_trace(df=all_2019, title="2019 Member", member_open_all="member_seats", bar_color=member_color)
trace_2020_open = create_bar_trace(df=all_2020, title="2020 Open", member_open_all="open_seats", bar_color=open_color)
trace_2020_member = create_bar_trace(df=all_2020, title="2020 Member", member_open_all="member_seats", bar_color=member_color)
trace_2018_all = create_scatter_trace(df=all_2018, title="2019 all", visibility=True)
trace_2019_all = create_scatter_trace(df=all_2019, title="2019 all", visibility=True)
trace_2020_all = create_scatter_trace(df=all_2020, title="2019 all", visibility=True)
trace_all = create_scatter_trace(df=all_events_df, title="All Events", visibility=False)


data = [
        trace_2018_all,
        trace_2019_all,
        trace_2020_all,
        trace_2018_open,
        trace_2018_member,
        trace_2019_open,
        trace_2019_member,
        trace_2020_open,
        trace_2020_member,
        trace_all_open,
        trace_all_member
        ]

updatemenus = list([
    dict(active=-1,
         type="buttons",  # Leaving this line off makes it look like a drop down
         buttons=list([
             dict(label='2018 Events',
                  method='update',
                  args=[{'visible': [x in (trace_2018_member, trace_2018_open, trace_2018_all) for x in data]},
                        {'title': title_text + ': 2018'}]),

             dict(label='2019 Events',
                  method='update',
                  args=[{'visible': [x in (trace_2019_member, trace_2019_open, trace_2019_all) for x in data]},
                        {'title': title_text + ': 2019'}]),

             dict(label='2020 Events',
                  method='update',
                  args=[{'visible': [x in (trace_2020_member, trace_2020_open, trace_2020_all) for x in data]},
                        {'title': title_text + ': 2020'}]),

             dict(label="All Events",
                  method='update',
                  args=[{'visible': [x in (trace_all_member, trace_all_open, trace_all) for x in data]},
                        {'title': title_text + ': 2018-present'},
                        ])

         ]),
         )
])

layout = dict(title=title_text + " 2018-present", showlegend=True, updatemenus = updatemenus,
              barmode='stack', )

fig = go.Figure(data=data, layout=layout)

# For Jupyter notebook
# fig.show()


all_events_df.to_csv('IT_seat_usage.csv')
plotly.offline.plot(fig, filename='plot_IT_seat_usage.html', auto_open=False)