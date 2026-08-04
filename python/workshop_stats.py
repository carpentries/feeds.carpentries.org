# Import all the things

import os
import requests
import pandas as pd

import pycountry

WORKSHOP_TYPES = {
    "SWC": "Software Carpentry",
    "DC": "Data Carpentry",
    "LC": "Library Carpentry",
    "TTT": "Instructor Training",
    "HPCC": "HPC Carpentry",
    "AIC": "AI Carpentry",
    "Circuits": "Mix & Match"
}

# Write some functions

def get_country_name(char2):
    """Converts two character country code into country name"""

    try:
        return pycountry.countries.get(alpha_2=char2).name
    except:
        return "Unknown"

get_country_name("US")


def get_lesson_program(tag_name):
    tags = [tag.strip() for tag in str(tag_name).split(",")]
    for tag in tags:
        if tag in WORKSHOP_TYPES:
            return WORKSHOP_TYPES[tag]
    return None


def admin_name(row):
    """Sets administrator as self organized, centrally organized, instructor training"""
    if row['administrator_id'] in ("302", "642", "173"):
        return 'CO'
    elif row['administrator_id'] == "717":
        return 'IT'
    else:
        return 'SO'

# Read data from redash query for workshops with administrator
api_key168 = os.environ['REDASH_KEY_QUERY168']
data = pd.read_csv("http://redash.carpentries.org/api/queries/168/results.csv?api_key=" + api_key168, keep_default_na=False)

# Set full country name
data['country_name'] = data['country'].apply(lambda x: get_country_name(x))

# Set lesson program name
data['lesson_program'] = data['tag_name'].apply(lambda x: get_lesson_program(x))

# Set self/centrally organized
data['administrator'] = data.apply(lambda x: admin_name(x), axis = 1)

# Convert dates to date types
data['start_date'] = pd.to_datetime(data['start_date'])
data['end_date'] = pd.to_datetime(data['end_date'])
data['year'] = data['start_date'].dt.year

# Get just workshops, drop instructor training
workshops = data[data['administrator'] != 'IT']

# Drop lesson onboardings (hacky way to do this)
workshops = workshops[workshops['country'] != 'W3']

# Get workshops by country and year
by_country_year =  workshops.groupby(['country_name', 'year'])['slug'].count().reset_index()
by_country_year = by_country_year.pivot_table(index = 'country_name', columns='year', values='slug')
by_country_year.fillna(0, inplace=True)
by_country_year = by_country_year.astype(int)
by_country_year.to_json('_data/workshops_country_year.json')

# Get workshops by country and administrator
by_country_admin = workshops.groupby(['country_name', 'administrator'])['slug'].count().reset_index()
by_country_admin = by_country_admin.pivot_table(index = 'country_name', columns='administrator', values='slug')
by_country_admin.fillna(0, inplace=True)
by_country_admin = by_country_admin.astype(int)
by_country_admin.to_json('_data/workshops_country_administrator.json')

# Get workshops by country and lesson program
by_country_lessonprogram = workshops.groupby(['country_name', 'lesson_program'])['slug'].count().reset_index()
by_country_lessonprogram = by_country_lessonprogram.pivot_table(index = 'country_name', columns='lesson_program', values='slug')
by_country_lessonprogram.fillna(0, inplace=True)
by_country_lessonprogram = by_country_lessonprogram.astype(int)
by_country_lessonprogram.to_json('_data/workshops_country_lessonprogram.json')


