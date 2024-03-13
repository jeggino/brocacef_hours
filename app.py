import streamlit as st

import pandas as pd

from datetime import datetime

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
  today = datetime.today()
  st.write(today)
  date = st.date_input("Date", datetime.today())
  start_hour = st.time_input('Start time', datetime.time(14, 45))
  finish_hour = st.time_input('Finish time', value=None)
  
  if finish_hour is None:
    
    st.write("insert a time")
    st.stop()
  
  long_brake = st.number_input("Insert a number", value=0, placeholder="Type a number...")
  short_brake = st.number_input("Insert a number", value=0, placeholder="Type a number...")
  
  
  long_brake_values = 0.5
  short_brake_values = 0.25
  
  d = finish_hour-start_hour
  working_hours = (d.total_seconds()/60)/60 - long_brake * long_brake_values - short_brake * short_brake_values

  
  submitted = st.button("Insert hours")
  
  if submitted:
    
    insert_input(date,start_hour,finish_hour,long_brake,short_brake,working_hours)
    st.write(f"You worked {working_hours} hours")
    
                
db_content = load_dataset()
df_point = pd.DataFrame(db_content)

df_point
