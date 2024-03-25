import streamlit as st
from streamlit_option_menu import option_menu

import pandas as pd

import datetime

from deta import Deta

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Brocacef",
    page_icon="💪",
    layout="wide",
    
)

# --- CONNECT TO DETA ---
deta = Deta(st.secrets["deta_key"])
db = deta.Base("df_brocacef")

# --- FUNCTIONS ---
def load_dataset():
  return db.fetch().items

def insert_input(date,start_hour,finish_hour,long_brake,short_brake,working_hours):

  return db.put({"date":str(date),"start_hour":start_hour,"finish_hour":finish_hour,"long_brake":long_brake,"short_brake":short_brake,"working_hours":working_hours})

# --- APP ---
# horizontal menu
selected = option_menu(None, ['✍️','📊'], 
                       icons=None,
                       default_index=0,
                       orientation="horizontal")

if selected == '✍️':
  date = st.date_input("Date", datetime.datetime.today())
  start_hour = str(st.time_input('Start time', datetime.time(14, 45),step=300))
  finish_hour = str(st.time_input('Finish time', datetime.time(22, 00),step=300))

  if finish_hour is None:

    st.info('insert a time', icon="ℹ️")
    st.stop()
  
  long_brake = st.number_input("Insert a long brake", value=1, placeholder="Type a number...",key="a")
  short_brake = st.number_input("Insert a short brake", value=1, placeholder="Type a number...",key="b")
  long_brake_values = 0.5
  short_brake_values = 0.25

  d1 = datetime.datetime.strptime(finish_hour, "%H:%M:%S")
  d2 = datetime.datetime.strptime(start_hour, "%H:%M:%S")
  d = d1-d2
  working_hours = round((d.total_seconds()/60)/60 - long_brake * long_brake_values - short_brake * short_brake_values,2)
  
  submitted = st.button("Insert hours")
  
  if submitted:
    
    insert_input(date,start_hour,finish_hour,long_brake,short_brake,working_hours)
    st.write(f"You worked {working_hours} hours")
    
if selected == '📊':
  
    db_content = load_dataset()
    df = pd.DataFrame(db_content)
    df['date'] = pd.to_datetime(df['date'])
    df['week_of_year'] = df['date'].dt.isocalendar().week
    df['day_of_the_week'] = df['date'].dt.day_name() 
    
    data_df = df.groupby("week_of_year",as_index=False)["working_hours"].sum()
    data_df_day = df.groupby("day_of_the_week",as_index=False)["working_hours"].mean()

    st.data_editor(
    data_df,
    column_config={
        "week_of_the_year": "Week",
        "working_hours": st.column_config.ProgressColumn(
            "Hours",
            help="Number of hours per week",
            format='%.4g',
            min_value=0,
            max_value=data_df.working_hours.max(),
        ),
    },
    hide_index=True,
        use_container_width = True
)

    average_week = round(data_df["working_hours"].mean(),2)
    average_day = round(df["working_hours"].mean(),2)
    max_day = data_df_day.loc[data_df_day['working_hours']==data_df_day['working_hours'].max(), 'day_of_the_week'].squeeze()
    less_day = data_df_day.loc[data_df_day['working_hours']==data_df_day['working_hours'].min(), 'day_of_the_week'].squeeze()
    max_day_hours = round(data_df_day["working_hours"].max(),2)
    min_day_hours = round(data_df_day["working_hours"].min(),2)
    max_day_hours_2 = round(df["working_hours"].max(),2)
    max_day_2 = df.loc[df['working_hours']==df['working_hours'].max(), ["day_of_the_week",'date'].squeeze()
    less_day_hours_2 = round(df["working_hours"].min(),2)
    less_day_2 = df.loc[df['working_hours']==df['working_hours'].min(), 'date'].squeeze()
    st.markdown(f"**Average hours per week**: {average_week}")
    st.markdown(f"**Average hours per day**: {average_day}")
    st.markdown(f"**{max_day}** ({max_day_hours}) is the day when you work more, and **{less_day}** ({min_day_hours}) is the day when you work less")
    st.markdown(f"**{max_day_2}** ({max_day_hours_2}) is the day when you work more, and **{less_day_2}** ({less_day_hours_2}) is the day when you work less")


