#manager()

import streamlit as st
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
import math

class Isotopes_in_Waste:
    def __init__(self, isotope, activity):
        self.isotope_name = isotope
        self.activity = activity

st.markdown("###### author: :blue[Andrzej Grzegrzłka]" )
st.markdown("###### contact: :blue[andrzej.grzegrzolka@zuop.gov.pl]" )

# title of the app
st.header('Radioactive waste classification')

# dataframe loading
df = pd.read_csv('Isotope.csv', sep = ";", index_col = 0, 
        names = ["Name", "ExemptionConcentr", "ExemptionActivity", "HalfLife"])
df.loc[df['HalfLife'] == "#N/D!", 'HalfLife'] = '0'
df['HalfLife'] = df['HalfLife'].str.replace(',', '.').astype(float)

# visualize dataframe
st.write(df)

# input dates
#start_date = st.date_input("Podaj datę początkową", min_value="1900-01-01", max_value="2300-01-01")
#end_date = st.date_input("Podaj datę końcową", min_value="1900-01-01", max_value="2300-01-01")
elapsed_years = st.number_input("Enter the number of years since the waste was generated: ", step=0.5, format="%0.1f")
#elapsed_years = (end_date - start_date).days/365
elapsed_months = int(elapsed_years*12)
mass = st.number_input("Enter the mass of the waste in kg: ", step=0.5, format="%0.1f")

st.divider()

isotopes_in_waste = {}

isotopes_names = df.index.to_list()
if 'isotopes' not in st.session_state:
    st.session_state['isotopes'] = []

def manager():  #function to manage adding and clearing isotopes
    isotope_name = st.selectbox(label="Select isotope: ", options = isotopes_names)
    activity = st.number_input("Enter isotope activity [MBq: ]")*1000
    add_button = st.button("Add isotope", key='add_button', type="primary")
    clear_button = st.button("Clear isotopes", key='clear', type="primary")
    selected_isotope_names = [isotope.isotope_name for isotope in st.session_state['isotopes']]
    if add_button:
        if activity > 0 and isotope_name not in selected_isotope_names:
            new_isotope = Isotopes_in_Waste(isotope_name, activity)
            isotopes_in_waste[isotope_name] = new_isotope
            st.session_state['isotopes'] += [new_isotope]
            selected_isotope_names.append(isotope_name)
        else:
            st.warning("You have already selected this isotope")
        
    if clear_button:
        st.session_state['isotopes'] = []
        selected_isotope_names = [isotope.isotope_name for isotope in st.session_state['isotopes']]
        plt.clf()


# This function is essential for managing the user interactions related to isotope selection and activity input,
# this will also add the selected isotopes to the session state
# and display the selected isotopes in the dataframe


manager() #call the function to execute the isotope selection and activity input management,

data = []

def Category(mass, isotopes_in_waste):
    sumIsotopeConcentrationToExemption = 0
    for my_isotope in isotopes_in_waste:
        sumIsotopeConcentrationToExemption += round(my_isotope.activity / mass / df.loc[my_isotope.isotope_name]["ExemptionConcentr"],2)
    if sumIsotopeConcentrationToExemption <= 1:
        return "Exempted"
    if sumIsotopeConcentrationToExemption > 1 and sumIsotopeConcentrationToExemption <= 10000:
        return "Low Level"
    if sumIsotopeConcentrationToExemption > 10000 and sumIsotopeConcentrationToExemption <= 10000000:
        return "Intermediate Level"
    else:
        return "High Level"

def Subcategory(mass, isotopes_in_waste):
    sumIsotopeConcentrationToExemption = 0
    after3YearsSumIsotopeConcentrationToExemption = 0
    for my_isotope in isotopes_in_waste:
        sumIsotopeConcentrationToExemption += round((my_isotope.activity / mass / df.loc[my_isotope.isotope_name]["ExemptionConcentr"]),2)
        halflife = float(df.loc[my_isotope.isotope_name]["HalfLife"])
        after3YearsSumIsotopeConcentrationToExemption += round((my_isotope.activity * pow(math.e, -(math.log(2) * (3 / halflife))) / mass / df.loc[my_isotope.isotope_name]["ExemptionConcentr"]),2)
    
    longLived = []
    longLivedSumIsotopeConcentration = 0
    longLivedSumIsotopeConcentrationToExemption = 0
    for my_isotope in isotopes_in_waste:
        if df.loc[my_isotope.isotope_name]["HalfLife"] > 30.2:
            print(f"LL_Isotopes: {my_isotope.isotope_name}")
            longLivedSumIsotopeConcentrationToExemption += round((my_isotope.activity / mass / df.loc[my_isotope.isotope_name]["ExemptionConcentr"]),2)
            longLivedSumIsotopeConcentration += round(my_isotope.activity / mass,2)
            longLived.append(my_isotope)

    
    #st.subheader("- sum isotope concentration to exemption:   {}".format(round(sumIsotopeConcentrationToExemption,2)))
    #st.write("- sum isotope concentration to exemption: ",(round(sumIsotopeConcentrationToExemption,2)))
    st.text("- sum isotope concentration to exemption:  {}".format(round(sumIsotopeConcentrationToExemption,2)))
    st.text("- after 3 years sum iotope concentration to exemption:  {}".format(round(after3YearsSumIsotopeConcentrationToExemption,2)))
    st.text("- sum long lived isotopes concentration:  {}".format(longLivedSumIsotopeConcentrationToExemption))   
    st.text("- sum long lived isotopes concentration to exemption:  {}".format(longLivedSumIsotopeConcentrationToExemption))   

    st.divider()

    if sumIsotopeConcentrationToExemption <= 1:
        return "Exempted"
    if after3YearsSumIsotopeConcentrationToExemption < 1:
        return "Transient"
    if longLivedSumIsotopeConcentrationToExemption > 1:
        if longLivedSumIsotopeConcentration > 400:
            return "Long lived"
        else:
            return "Short lived"
    return "Short lived"

CategoryOfWaste = Category(mass, st.session_state['isotopes'])
SubcategoryOfWaste = Subcategory(mass, st.session_state['isotopes'])

#st.text("Category of Waste: {}".format(CategoryOfWaste))
#st.text("Subcategory of Waste: {}".format(SubcategoryOfWaste))
#st.write("Category of Waste: ", CategoryOfWaste)
#st.write("Subcategory of Waste: ", SubcategoryOfWaste)



# Another cool feature is that `st.write()` can also handle Markdown text.
# But if you want more control over the formatting, you can use `st.markdown()`.

# write markdown


# markdown_txt = (
#     "#### Subcategory of Waste: \n"
#     "#### :red[Subcategory of Waste: ],st.write(, CategoryOfWaste)\n"
#     "This is a Markdown paragraph.\n"
# )
# st.markdown(markdown_txt)




st.markdown("###### :blue[Category of Waste:]  {}".format(CategoryOfWaste))
st.markdown("###### :blue[Subcategory of Waste:]  {}".format(SubcategoryOfWaste))

st.divider()







#plotting the activity of isotopes over time

x = range(elapsed_months)
activity_units_factor = 1000
for isotope in st.session_state['isotopes']:
    #calculate activity
    halflife = float(df.loc[isotope.isotope_name]["HalfLife"])
    calc_activity = round(isotope.activity/activity_units_factor * pow(math.e, -(math.log(2) * (elapsed_years / halflife))),2)
    calc_3_year_activity = round(isotope.activity/activity_units_factor * pow(math.e, -(math.log(2) * (3 / halflife))),2)

    IsotopeConcentrationToExemption = round(isotope.activity / mass / df.loc[isotope.isotope_name]["ExemptionConcentr"],2)
    after3YearsSumIsotopeConcentrationToExemption = round(isotope.activity * pow(math.e, -(math.log(2) * (3 / halflife))) / mass / df.loc[isotope.isotope_name]["ExemptionConcentr"],2)

    data.append([isotope.isotope_name, halflife, isotope.activity/activity_units_factor, IsotopeConcentrationToExemption, calc_3_year_activity, after3YearsSumIsotopeConcentrationToExemption, calc_activity,])
    
    #create plot
    activities_by_month = []
    for month in range(elapsed_months):
        time = month / 12 
        activities_by_month.append(round(isotope.activity/activity_units_factor * pow(math.e, - (math.log(2) * (time / halflife) )),2))
    
    plt.plot(x, activities_by_month, label = isotope.isotope_name)

# 
plt.ticklabel_format(style='plain')
#plt.ticklabel_format(style="plain", axis="y")
plt.xlabel("Time (months)")
plt.ylabel("Activity [MBq]")
plt.title("Activity of isotope after: " + str(elapsed_years) + " years")
plt.legend()  #add a legend
plt.show()
#plt.savefig('chart.png') #/Users/andy/Desktop/Programming/Python/JacekIsot/chart.png
st.pyplot(plt)

#print dataframe
#st.write("Data początkowa", start_date )
#st.write("Data końcowa", end_date )
st.divider()

# st.text: The st.text() function is used for displaying plain text.
# It's basic and doesn't include any styling, making it useful for simple text elements.

# st.write("Liczba lat od wytworzenia odpadu: ", elapsed_years) # style="font-size: 50px;"
st.text("Number of years since waste generation:   {}".format(elapsed_years))
st.text("Number of months since waste generation: {}".format(elapsed_months))
st.text("Waste weight in kg: {}".format(mass))




selected_isotopes_df = pd.DataFrame(data, columns=['Isotope', 'Halflife', 'Beg Act', 'IsotConcToExempt', 'Act after 3 years', '3IsotConcToExempt', 'Act after...'])


selected_isotopes_df.loc['Total']=selected_isotopes_df.sum(numeric_only=True)   # add 'total' row at the bottom 
selected_isotopes_df.loc[selected_isotopes_df.index[-1], 'Halflife'] = ''  # not sum the total value in 'Halflife', column blank
selected_isotopes_df.loc[selected_isotopes_df.index[-1], 'Isotope'] = ''  # column blank



st.write(selected_isotopes_df )



# Custom button example

#st.markdown("""
#<style>
#.custom-button {
#  background-color: green;
#   color: white;
#   padding: 14px 20px;
#   margin: 8px 0;
#   border: none;
#   cursor: pointer;
#   width: 100%;
#}
#.custom-button:hover {
#   opacity: 0.8;
#}
#</style>
#<button class="custom-button">Add isotope</button>
#""", unsafe_allow_html=True)##
#
