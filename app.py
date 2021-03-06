import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

import streamlit.components.v1 as components

import ssl


import streamlit as st

st.markdown(
        f"""
<style>
    .reportview-container .main .block-container{{
        max-width: {1000}px;
        
    }}
    
</style>
""",
        unsafe_allow_html=True,
    )



ssl._create_default_https_context = ssl._create_unverified_context

DATE_TIME = "date/time"
Data_URL = ("motor2.csv")
st.title("Motor vehicle collision in new york city")
st.markdown("## Dashboard to visualise motor vehicle crash statistics in New York city ")


@st.cache
def load_data():
	datafr = pd.read_csv(Data_URL, parse_dates=[['CRASH DATE', 'CRASH TIME']])
	#datafr = datafr[datafr['LATITUDE'] <=72]
	datafr = datafr[datafr['LONGITUDE'] <=-70 ]
	datafr = datafr[datafr['LONGITUDE'] >=-180 ]
	datafr.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True)
	lower_case = lambda x: str(x).lower()
	datafr.rename(lower_case, axis='columns', inplace=True)
	datafr.rename(columns={'crash date_crash time': 'date/time'}, inplace=True)
	return datafr


data = load_data()


st.header("Number of Injuries in NYC")
injured = st.slider("Minimum Number of people injured", 0, 19,value=2)

x = data.query('`number of persons injured` >= @injured')[['latitude', 'longitude']].dropna()
st.map(x,9)




st.header("How many collisions occur during a given time of day?")
hour = st.slider("Hour to look at", 0, 23)

data = data[data[DATE_TIME].dt.hour == hour]
st.markdown("Vehicle collisions between %i:00 and %i:00" % (hour, (hour + 1) % 24))

midpoint = (np.average(data["latitude"]), np.average(data["longitude"]))


st.write(pdk.Deck(
map_style="mapbox://styles/mapbox/light-v9",
initial_view_state={
  "latitude": midpoint[0],
  "longitude": midpoint[1],
  "zoom": 11,
  "pitch": 50,
},
layers=[
  pdk.Layer(
  "HexagonLayer",
  data=data[['date/time', 'latitude', 'longitude']],
  get_position=["longitude", "latitude"],
  auto_highlight=True,
  radius=100,
  extruded=True,
  pickable=False,
  
  elevation_range=[0, 1000],
  ),
],
)

)

st.subheader("Breakdown by minute between %i:00 and %i:00" % (hour, (hour + 1) % 24))
filtered = data[(data[DATE_TIME].dt.hour >= hour) & (data[DATE_TIME].dt.hour < (hour + 1))]
hist = np.histogram(filtered[DATE_TIME].dt.minute, bins=60, range=(0, 60))[0]
chart_data = pd.DataFrame({"minute": range(60), "crashes": hist})

fig = px.bar(chart_data, x='minute', y='crashes', hover_data=['minute', 'crashes'], height=400)
st.write(fig)

st.header("Top 5 dangerous streets by affected class")
select = st.selectbox('Affected class', ['Pedestrians', 'Cyclists', 'Motorists'])

if select == 'Pedestrians':
	st.write(data.query("`number of pedestrians injured` >= 1")[["on street name", "number of pedestrians injured"]].sort_values(by=['number of pedestrians injured'], ascending=False).dropna(how="any")[:5])

elif select == 'Cyclists':
	st.write(data.query("`number of cyclist injured` >= 1")[["on street name", "number of cyclist injured"]].sort_values(by=['number of cyclist injured'], ascending=False).dropna(how="any")[:5])

else:
	st.write(data.query("`number of motorist injured` >= 1")[["on street name", "number of motorist injured"]].sort_values(by=['number of motorist injured'], ascending=False).dropna(how="any")[:5])

