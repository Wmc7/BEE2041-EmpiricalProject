# %% [markdown]
# # Data Science Blog 

# %% [markdown]
# ## Scrape Data

# %%
from urllib import request, error
from bs4 import BeautifulSoup
import pandas as pd
import re

# %% [markdown]
# ### Adult Lifetime Cannabis Use By Country

# %%
target1 = 'https://en.wikipedia.org/wiki/Adult_lifetime_cannabis_use_by_country'

response = BeautifulSoup(request.urlopen(target1),'html.parser')
TAB = response.find('table', class_='wikitable sortable mw-datatable sort-under sticky-header static-row-numbers col2left col8center')

rows = TAB.find_all('tr')

data = []
for row in rows:
    row_data = []
    for cell in row.find_all('td'):
        row_data.append(cell.text)
    data.append(row_data)

columnNames = ['Location', 'Geographical Area', 'Year', 'Age Range', 'Males', 'Females', 'Total', 'Ref']

AdultUseByCountry = pd.DataFrame(data, columns = columnNames)

# %% [markdown]
# ### Annual Cannabis Use

# %%
target2 = 'https://en.wikipedia.org/wiki/List_of_countries_by_annual_cannabis_use'

response = BeautifulSoup(request.urlopen(target2),'html.parser')
TAB = response.find('table', class_='wikitable sortable mw-datatable static-row-numbers sticky-header sort-under col1left col5left')

# print(response)

rows = TAB.find_all('tr')

data = []
for row in rows:
    row_data = []
    for cell in row.find_all('td'):
        row_data.append(cell.text)
    data.append(row_data)

columnNames = ['Location', 'Annual Prevalence', 'Year', 'Age Group', 'Source Notes']

AnnualUseByCountry = pd.DataFrame(data, columns = columnNames)

AnnualUseByCountry = AnnualUseByCountry.drop(0)
AnnualUseByCountry = AnnualUseByCountry.drop(columns = ['Source Notes', 'Age Group', 'Year'])

# %%
data = []
for row in rows:
    row_data = []
    for cell in row.find_all('td'):
        row_data.append(cell.text)
    data.append(row_data)

columnNames = ['Location', 'Annual Prevalence', 'Year', 'Age Group', 'Source Notes']

AnnualUseByCountry = pd.DataFrame(data, columns = columnNames)

AnnualUseByCountry = AnnualUseByCountry.drop(0)
AnnualUseByCountry = AnnualUseByCountry.drop(columns = ['Source Notes', 'Age Group', 'Year'])

# Sample list of country names with additional unwanted characters
countries = AnnualUseByCountry['Location']

# Function to clean country names
def clean_country_name(name):
    # Use regex to remove any characters that are not letters or spaces
    cleaned_name = re.sub(r'[^a-zA-Z\s]', '', name)
    # Strip leading and trailing whitespace
    cleaned_name = cleaned_name.strip()
    return cleaned_name

# Clean all country names in the list
cleaned_countries = [clean_country_name(country) for country in countries]

AnnualUseByCountry['Location'] = cleaned_countries

selected_countries = ['United Kingdom', 'Netherlands', 'Canada', 'Australia', 'Uruguay']
filteredAnnualUseByCountry = AnnualUseByCountry[AnnualUseByCountry['Location'].isin(selected_countries)]
filteredAnnualUseByCountry['Annual Prevalence'] = filteredAnnualUseByCountry['Annual Prevalence'].str.replace(r'[^\d.]', '', regex=True)
filteredAnnualUseByCountry = filteredAnnualUseByCountry.reset_index().drop(columns='index')

# %% [markdown]
# ### Set Market Values

# %%
marketValue = {
    "Australia":1700000000,
    "Canada":3900000000,
    "Netherlands": 120000000,
    "United Kingdom":2860000000,
    "Uruguay": 55600000
}

# %%
marketValueDf = pd.DataFrame({'Country': list(marketValue.keys()), 'Value (USD)': list(marketValue.values())})

# %% [markdown]
# ### Scrape Population

# %%
target3 = 'https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_population'

response = BeautifulSoup(request.urlopen(target3),'html.parser')
TAB = response.find('table', class_='wikitable sortable sticky-header sort-under mw-datatable col2left col6left')

# print(response)

rows = TAB.find_all('tr')

data = []
for row in rows:
    row_data = []
    for cell in row.find_all('td'):
        row_data.append(cell.text)
    data.append(row_data)

columnNames = ['Index Store','Country', 'Population', '% of World', 'Date', 'Source', 'Source Notes']

PopByCountry = pd.DataFrame(data, columns = columnNames)

PopByCountry = PopByCountry.drop(0)
PopByCountry = PopByCountry.drop(columns = ['Index Store','Source Notes', 'Source', 'Date', '% of World'])



# %%
# Sample list of country names with additional unwanted characters
countries = PopByCountry['Country']

# Clean all country names in the list
cleaned_countries = [clean_country_name(country) for country in countries]

PopByCountry['Country'] = cleaned_countries

filterPopByCountry = PopByCountry[PopByCountry['Country'].isin(selected_countries)]
filterPopByCountry['Population'] = filterPopByCountry['Population'].str.replace(r'[^\d.]', '', regex=True)
filterPopByCountry = filterPopByCountry.reset_index().drop(columns = ['index'])

filterPopByCountry

# %% [markdown]
# NEED TO FIX POPULATION LINKS

# %%
filteredAnnualUseByCountry = pd.merge(filteredAnnualUseByCountry, marketValueDf, left_on = 'Location', right_on = 'Country').drop(columns= 'Country')
filteredAnnualUseByCountry = pd.merge(filteredAnnualUseByCountry, filterPopByCountry, left_on = 'Location', right_on = 'Country').drop(columns= 'Country')
filteredAnnualUseByCountry = filteredAnnualUseByCountry.sort_values(by = ['Annual Prevalence'])
filteredAnnualUseByCountry['Annual Prevalence'] = pd.to_numeric(filteredAnnualUseByCountry['Annual Prevalence'])
filteredAnnualUseByCountry['Population'] = pd.to_numeric(filteredAnnualUseByCountry['Population'])
filteredAnnualUseByCountry['Annual Users'] = filteredAnnualUseByCountry['Population'] * filteredAnnualUseByCountry['Annual Prevalence']/100
filteredAnnualUseByCountry['Value Per User'] = filteredAnnualUseByCountry['Value (USD)']/filteredAnnualUseByCountry['Annual Users']

# %%
filteredAnnualUseByCountry

# %% [markdown]
# ## Model future growth for UK Market

# %%
import matplotlib.pyplot as plt

fig, ax = plt.subplots()

ax.bar(filteredAnnualUseByCountry['Location'], filteredAnnualUseByCountry['Annual Prevalence'])

ax.set_ylabel('Cannabis Use (% of populations)')
ax.set_title('Annual Cannabis Use by Population')

plt.show()

# %%
fig, ax = plt.subplots()

ax.bar(filteredAnnualUseByCountry['Location'], filteredAnnualUseByCountry['Value Per User'])

ax.set_ylabel('Annual Cannabis Spend per User (USD)')
ax.set_title('Annual Cannabis Spend by Country')

plt.show()

# %%
fig, ax = plt.subplots()

ax.bar(filteredAnnualUseByCountry['Location'], filteredAnnualUseByCountry['Value (USD)'])

ax.set_ylabel('Market Value (Billion USD)')
ax.set_title('Annual Cannabis Market Value by Country')

plt.show()

# %% [markdown]
# ## Model Future Growth

# %%
filteredAnnualUseByCountry.iloc[4]

# %%
# Scenario 1 & 2

NewPrevalence = (filteredAnnualUseByCountry['Annual Prevalence'].iloc[4] + 5, filteredAnnualUseByCountry['Annual Prevalence'].iloc[4] * 2)
ModelDataFrame = pd.DataFrame(NewPrevalence, columns = ['New Prevalence'])

ModelDataFrame['New Annual Users'] = ModelDataFrame['New Prevalence']/100 * filteredAnnualUseByCountry['Population'].iloc[4]
ModelDataFrame['New Value'] = ModelDataFrame['New Annual Users'] * filteredAnnualUseByCountry['Value Per User'].iloc[4]

ModelDataFrame['Scenario'] = ['Scenario 1', 'Scenario 2']

# Scenario 3 & 4

scenario3and4 = pd.DataFrame(NewPrevalence, columns = ['New Prevalence'])
scenario3and4['New Annual Users'] = scenario3and4['New Prevalence']/100 * filteredAnnualUseByCountry['Population'].iloc[4]
scenario3and4['New Value'] = scenario3and4['New Annual Users'] * filteredAnnualUseByCountry['Value Per User'].iloc[4] * 0.9
scenario3and4['Scenario'] = ['Scenario 3', 'Scenario 4']

# Scenario 5 & 6

scenario5and6 = pd.DataFrame(NewPrevalence, columns = ['New Prevalence'])
scenario5and6['New Annual Users'] = scenario5and6['New Prevalence']/100 * filteredAnnualUseByCountry['Population'].iloc[4]
scenario5and6['New Value'] = scenario5and6['New Annual Users'] * filteredAnnualUseByCountry['Value Per User'].iloc[4] * 0.8
scenario5and6['Scenario'] = ['Scenario 5', 'Scenario 6']

# Join all data 

ModelDataFrame = pd.concat([ModelDataFrame, scenario3and4, scenario5and6])

ModelDataFrame

# %%
fig, ax = plt.subplots()

ax.bar(ModelDataFrame['Scenario'], ModelDataFrame['New Value']/1e9)

ax.set_ylabel('Market Value (Billion USD)')
ax.set_title('Projected Market Value after Legalisation')

plt.show()

# %%
ModelDataFrame['Tax Raised'] = 0.3 * ModelDataFrame['New Value']

# %%
(filteredAnnualUseByCountry['Value Per User'].iloc[4] / filteredAnnualUseByCountry['Value Per User'].iloc[3] - 1) * 100

# %%
ModelDataFrame["Total Tax Potential"] = ModelDataFrame['Tax Raised'] / 0.06

# %%
ModelDataFrame

# %%
fig, ax = plt.subplots()

ax.bar(ModelDataFrame['Scenario'], ModelDataFrame['Total Tax Potential']/1e9)
ax.bar(ModelDataFrame['Scenario'], ModelDataFrame['Tax Raised']/1e9, bottom = ModelDataFrame['Tax Raised']/1e9, color = 'r')

ax.set_ylabel('Tax Raised (Billion USD)')
ax.set_title('Projected Tax Profits after Legalisation')

plt.show()

# %%



