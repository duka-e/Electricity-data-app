import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title='Europe Electricity Data',
                  page_icon=':battery:',
                  layout='centered'
                  )

st.title("Exploring Europe's electricity data")
st.subheader("A snapshot of Europe's energy mix and CO2 intensity from 1990 to 2024")
st.subheader('Dataset')

url = 'https://ember-energy.org/data/yearly-electricity-data/'
st.markdown("This dashboard relies on the dataset found below. The data was obtained from [Ember](%s), specifically the dataset labelled as 'Yearly electricity data Europe.'" % url)

df = pd.read_csv("europe_yearly_full_release_long_format.csv")
df = df[['Area', 'Year', 'Category', 'Subcategory', 'Variable', 'Unit', 'Value']]
df = df[~(df['Area']=='EU')] # removing EU which is aggregates values for all countries.

st.write(df)

# Part 1: energy mix 
st.subheader('1. Visualising changes in the energy mix')
st.markdown("The energy mix is the combination of different energy sources, both renewable and non-renewable, that a country uses to meet its energy needs, such as electricity generation. Over the years, the energy mix has been undergoing tranformations following the phase out of coal and the growth of renewable energy, for example.")
st.markdown("The animated chart below plays out how sources of generation have varied over time for a given country.")

country_options = df['Area'].unique().tolist()
country = st.multiselect('Select countries to compare:', country_options, ['Germany', 'Spain'])

df1 = df[df['Area'].isin(country)]

#Filtering the data to only select rows reporting TWh values per each type of fuel/energy source:
df1 = df1[(df1['Subcategory']=='Fuel') & (df1['Unit']=='%')]

# Converting the df into wide format data because this will allow me to decide the order of the different energy sources on the stacked bar chart:
df1 = df1[['Area', 'Year', 'Variable', 'Value']]
df4 = df1.pivot(index=['Area', 'Year'], columns='Variable', values='Value').reset_index()

# Creating bar chart to demonstrate energy mix
custom_colors = colors = [
    "#0068c9",
    "#83c9ff",
    "#ff2b2b",
    "#ffabab",
    "#29b09d",
    "#7defa1",
    "#ff8700",
    "#ffd16a",
    "#6d3fc0",
    "#b51d80",
    "#bfc2c7"
]

fig = px.bar(df4, 
             x='Area', 
             y=['Hard coal', 'Lignite', 'Gas', 'Other fossil', 'Nuclear', 'Hydro', 'Bioenergy', 'Solar', 'Onshore wind', 'Offshore wind', 'Other renewables'], 
             color_discrete_sequence=custom_colors,
             title = "Chart", 
             animation_frame='Year')

fig.update_layout(
    title='The source of electricity generation over time',
    xaxis_title='Country',
    yaxis_title='Electricity Generated (%)',
    legend_title='Source of generation',
    width=100,
    height=500
)

fig.update_xaxes(showgrid=True)
st.write(fig)


# Part two of dashboard: CO2 intensity
st.subheader("2. Carbon dioxide intensity over the years")
st.markdown("Carbon dioxide intensity is a measure of the amount of grams of carbon dioxide (CO2) that are emitted to produce a kilowatt hour (kWh) of electricity. A shift toward more renewable energy sources over time contributes to the development of a negative trend for this measurement.")
st.markdown("The rate of change in CO2 intensity for any country can be calculated and presented in the table and graph below to describe the trajectory and pace of different countries in reducing their CO2 emissions.")

country_options2 = df['Area'].unique().tolist()
country2 = st.multiselect('Select countries to compare:', country_options2, ['Germany', 'Croatia', 'Denmark'])
df2 = df[(df['Area'].isin(country2)) & (df['Variable']=='CO2 intensity')]


# Table below to display the gradients of the lines of best fit for each country selected
slopes={}
for country in country2:
    temp = df2[df2['Area'] == country]
    if len(temp) > 1:
        m, b = np.polyfit(temp['Year'], temp['Value'], 1)
        slopes[country] = m

if slopes:
    results = pd.DataFrame({
        "Country": list(slopes.keys()),
        "Rate of change in CO2 intensity (gCO2e/kWh per year)": list(slopes.values())
    })

    st.dataframe(results.style.format({"Gradient": "{:.3f}"}))
else:
    st.info("Select at least 1 country to calculate rate of change.")

# Graph to visualise CO2 intensity vs time data based on user's selection:
fig2 =px.line(df2, x='Year', y='Value', color='Area', markers=True,
             labels={
                 'Value':'CO2 Intensity (gCO2e per kWh)'
             },
             title="CO2 intensity vs time")

fig2.update_layout(width=300, height=500)

fig2.update_layout(
    legend_title='Country',
    xaxis = dict(
        tickmode = 'linear',
        tick0 = 5,
        dtick = 5))
fig2.update_xaxes(showgrid=True)

st.write(fig2)
