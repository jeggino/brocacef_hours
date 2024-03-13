import streamlit as st

import pandas as pd

import datetime

from deta import Deta

# --- CONNECT TO DETA ---
deta = Deta(st.secrets["deta_key"])
db = deta.Base("df_brocacef")

# --- FUNCTIONS ---
def load_dataset():
  return db.fetch().items

def insert_input(date,start_hour,finish_hour,long_brake,short_brake,working_hours):

  return db.put({"date":date,"start_hour":start_hour,"finish_hour":finish_hour,"long_brake":long_brake,"short_brake":short_brake,"working_hours":working_hours})

# --- APP ---

with st.sidebar:
  date = st.date_input("Date", datetime.datetime.today())
  start_hour = str(st.time_input('Start time', datetime.time(14, 45)))
  finish_hour = str(st.time_input('Finish time', value=None))
 
  if finish_hour is None:

    st.info('insert a time', icon="ℹ️")
    st.stop()
  
  long_brake = st.number_input("Insert a long brake", value=0, placeholder="Type a number...",key="a")
  short_brake = st.number_input("Insert a short brake", value=0, placeholder="Type a number...",key="b")
  long_brake_values = 0.5
  short_brake_values = 0.25

  d1 = datetime.datetime.strptime(finish_hour, "%H:%M:%S")
  d2 = datetime.datetime.strptime(start_hour, "%H:%M:%S")
  d = d1-d2
  working_hours = (d.total_seconds()/60)/60 - long_brake * long_brake_values - short_brake * short_brake_values
  st.write(working_hours)
  
  submitted = st.button("Insert hours")
  
  if submitted:
    
    insert_input(date,start_hour,finish_hour,long_brake,short_brake,working_hours)
    st.write(f"You worked {working_hours} hours")
    
                
db_content = load_dataset()
df_point = pd.DataFrame(db_content)

df_point
