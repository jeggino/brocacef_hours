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
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
    
)

# --- CONNECT TO DETA ---
deta = Deta(st.secrets["deta_key"])
db = deta.Base("df_brocacef")

# --- FUNCTIONS ---
def load_dataset():
  return db.fetch().items

def insert_input(date,start_hour,finish_hour,long_brake,short_brake,working_hours):

  return db.put({"date":str(date),"start_hour":start_hour,"finish_hour":finish_hour,"long_brake":long_brake,"short_brake":short_brake,"working_hours":working_hours})

def stream_data():
    for word in _LOREM_IPSUM.split(" "):
        yield word + " "
        time.sleep(0.02)
        
# --- APP ---
# horizontal menu
selected = option_menu(None, ['✍️','📊'], 
                       icons=None,
                       default_index=0,
                       orientation="horizontal",
                       )

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

    average_week = round(data_df["working_hours"][:-1].mean(),2)
    average_day = round(df["working_hours"].mean(),2)
    max_day = data_df_day.loc[data_df_day['working_hours']==data_df_day['working_hours'].max(), 'day_of_the_week'].squeeze()
    less_day = data_df_day.loc[data_df_day['working_hours']==data_df_day['working_hours'].min(), 'day_of_the_week'].squeeze()
    max_day_hours = round(data_df_day["working_hours"].max(),2)
    min_day_hours = round(data_df_day["working_hours"].min(),2)
    max_day_hours_2 = round(df["working_hours"].max(),2)
    max_day_2 = df.loc[df['working_hours']==df['working_hours'].max(), ["day_of_the_week",'date']].squeeze()
    less_day_hours_2 = round(df["working_hours"].min(),2)
    less_day_2 = df.loc[df['working_hours']==df['working_hours'].min(),["day_of_the_week",'date'] ].squeeze()

    # REPORT
    with st.popover("Report"):
        st.markdown(f"""
        On average, you work **{average_week}** hours per week, which is equivalent to a daily average of **{average_day}** hours. 
        **{max_day}** is the day when you usually work the most, with a total of **{max_day_hours}** hours. In contrast, **{less_day}** is the day when you work the least, with only **{min_day_hours}** hours worked. 
        **{max_day_2['day_of_the_week']}**, on the date of **{max_day_2['date']}**, was the day when you worked the most hours in absolute terms. On the other hand, **{less_day}**, on the date of **{less_day_2['date']}**, was the day when you worked the fewest hours in absolute terms.
        """)


