import pandas as pd
import re

lt = pd.read_csv("L&T 2016-2017 (csps + cannabis).csv", encoding = "ISO-8859-1")

#deal with CSPS french translation format (given in the form "English | French")
vars_with_fr_translation = ['Province/Territory (Location)','Location Type (Location)','Dosage Unit (Submission Item)','Incident Type (Submission Item)','Incident Sub-Type (Submission Item)']
for var in vars_with_fr_translation:
    lt[var] = lt[var].str.replace(r"[|].+","")
    lt[var] = lt[var].str.lower()
lt['new_loc'] = lt['Incident Sub-Type (Submission Item)'] + " from " + lt['Location Type (Location)']
from lt_dict import location_dict
lt = lt.replace({"new_loc":location_dict})
from lt_dict import drug_dict
lt['drug_category'] = lt['Substance Name']
lt['drug_category'] = lt['drug_category'].str.strip()
lt['drug_category'] = lt['drug_category'].str.lower()
lt = lt.replace({"drug_category":drug_dict})

import numpy as np
lt['new_unit'] = np.where(lt['Total Substance in unit of MG'].isnull(),lt['Dosage Unit (Submission Item)'],"mg")#IF NULL, GET UNIT FROM OTHER COL, OTHERWISE mg
lt['new_qty']  = np.where(lt['Total Substance in unit of MG'].isnull(),lt['Quantity Lost or Stolen (Submission Item)'],lt['Total Substance in unit of MG'])

lt["new_qty"] = lt["new_qty"].str.replace(',', '').astype(float) # convert str to float
for i,row in lt.iterrows():
    if row['new_unit'] == "gram(s)":
        lt.at[i,"new_qty"] = lt.at[i,"new_qty"] * 1000
        lt.at[i,"new_unit"] = "mg"
    elif row['new_unit'] == "milligram(s)":
        lt.at[i,"new_unit"] = "mg"
        
lt16 = lt.loc[lt['year']==2016]
lt17 = lt.loc[lt['year']==2017]

lt = lt16

table_drug_amounts = lt.pivot_table(values="new_qty",index="drug_category",columns = "new_unit",aggfunc='sum')

table_drug_amounts.to_csv("lt_quantities16")
lt.to_csv("lt_cases16")

#rank locations using only mg
ltmg = lt[lt["new_unit"] == "mg"]

table_drug_by_location = ltmg.pivot_table(values="new_qty",index="new_loc",columns = "drug_category",aggfunc='sum')
table_drug_by_location

def notnull(drug_tuple):
    if drug_tuple[0] <= 0:
        return ""
    else:
        return drug_tuple[1]

drug_list = table_drug_by_location.index.values.tolist()
table_drug_by_location.fillna(-1,inplace=True) # sort breaks with NaN values, so replace them with -1

drugs_top_locations = {}
for col in table_drug_by_location:
    top3 = sorted(zip(table_drug_by_location[col],drug_list),reverse=True)[:3]
    drugs_top_locations[col] = [notnull(drug_tuple) for drug_tuple in top3] 

print(drugs_top_locations) # consider exporting to txt