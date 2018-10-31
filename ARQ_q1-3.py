'''
1. clean drug names
2. create array of all drugs that will be supplied to ARQ and unit types
3. for each drug in list, find how many of each unit there is in CDSD
4. output csv file

'''
class Drug:
    def __init__(self,name,main_group,sub_group,cases,grams,millilitres,tablets,capsules,plants,patches,seeds,suppositories,milligrams,micrograms,kilograms,litres):
        self.name = name
        self.main_group = main_group
        self.sub_group = sub_group
        self.cases = cases
        self.grams = grams
        self.milligrams = milligrams
        self.micrograms = micrograms
        self.kilograms = kilograms
        self.millilitres = millilitres
        self.litres = litres
        self.tablets = tablets
        self.capsules = capsules
        self.plants = plants
        self.patches = patches
        self.seeds = seeds
        self.suppositories = suppositories

    
    def to_dict(self):
        return {
            'name':self.name,
            'main_group':self.main_group,
            'sub_group':self.sub_group,
            'cases':self.cases,
            "GRAM(S)":self.grams,
            "MILLILITRES":self.millilitres,
            "MILLIGRAM(S)":self.milligrams,
            "TABLET(S) MICRODOT(S)":self.tablets,
            "CAPSULE(S)":self.capsules,
            "MICROGRAM":self.micrograms,
            "PLANT(S)":self.plants,
            "KILOGRAM(S)":self.kilograms,
            "PATCH":self.patches,
            "SEED(S)":self.seeds,
            "LITRE(S)":self.litres,
            "SUPPOSITOR(IES)":self.suppositories
        }
#Clean drug names

import csv
import pandas as pd
import arq_dicts

df_cdsd = pd.read_csv("CDSD_2017.csv", sep=',', error_bad_lines=False, index_col=False, dtype='unicode')

drug_name_dict = arq_dicts.clean_drug_names

#exclude RCMP from CDSD_2017.csv
df_cdsd = df_cdsd[df_cdsd.CASE_POLICE_TYPE != "R.C.M.P."]
df_cdsd = df_cdsd.reset_index()

#change values in DRUG_NAME column according to dictionary

for i, row in df_cdsd.iterrows():
    if len(row['DRUG_NAME']) < 1:
        new_str = row['DRUG_NAME']
    try:
        new_str = drug_name_dict[row['DRUG_NAME'].lower()]
    except:
        #if the string isn't found in the dictionary, return the string.
        new_str = row['DRUG_NAME']
    df_cdsd.at[i,'DRUG_NAME'] = new_str

#Change cannabis name for plant and seed unit
for i, row in df_cdsd.iterrows():
    if row['DRUG_NAME'] == "Cannabis":
        if row['SEIZURE_UNIT'] == "PLANT(S)":
            df_cdsd.at[i,'DRUG_NAME'] = "Cannabis plant"
        elif row['SEIZURE_UNIT'] == "SEED(S)":
            df_cdsd.at[i,'DRUG_NAME'] = "Cannabis seed"
            
#create dataset
units = [ 
    "GRAM(S)",
    "MILLILITRES",
    "TABLET(S) MICRODOT(S)",
    "CAPSULE(S)",
    "PLANT(S)",
    "PATCH",
    "SEED(S)",
    "SUPPOSITOR(IES)",
    "MILLIGRAM(S)",
    "MICROGRAM",
    "KILOGRAM(S)",
    "LITRE(S)"
    ]

def sum_drug_quantity(drug):
    drug_qtys = {}
    drug_qtys['cases'] = len(df_cdsd[df_cdsd["DRUG_NAME"]==drug])
    
    for unit in units:
        drug_qtys[unit] = len(df_cdsd[(df_cdsd.DRUG_NAME == drug)])
        df_subset = df_cdsd[(df_cdsd.DRUG_NAME == drug) & (df_cdsd.SEIZURE_UNIT == unit)]
        df_subset['SEIZURE_QUANTITY']=df_subset['SEIZURE_QUANTITY'].astype(float)
        drug_qtys[unit] = df_subset['SEIZURE_QUANTITY'].sum()
    return drug_qtys
    
with open("drug_classifications.csv" ,"r") as csvfile:
    r = csv.DictReader(csvfile)
    drugs = []
    for row in r:
        drug_qtys = sum_drug_quantity(row['name'])
        new_drug = Drug(row['name'], row['main_group'], row['sub_group'], drug_qtys['cases'],drug_qtys['GRAM(S)'],
                       drug_qtys['MILLILITRES'],drug_qtys['TABLET(S) MICRODOT(S)'],drug_qtys['CAPSULE(S)'],
                       drug_qtys['PLANT(S)'],drug_qtys['PATCH'],drug_qtys['SEED(S)'],drug_qtys['SUPPOSITOR(IES)'],
                       drug_qtys['MILLIGRAM(S)'], drug_qtys['MICROGRAM'], drug_qtys['KILOGRAM(S)'], drug_qtys['LITRE(S)'])
        drugs.append(new_drug)
    df_drugs_categorized = pd.DataFrame.from_records([d.to_dict() for d in drugs])
    
    #combine kilograms, grams, milligrams, and micrograms
    df_drugs_categorized['GRAM(S)'] = df_drugs_categorized['KILOGRAM(S)']*1000 + df_drugs_categorized['GRAM(S)'] + df_drugs_categorized['MILLIGRAM(S)']/1000 + df_drugs_categorized['MICROGRAM']/1000000

    #combine millilitres and litres
    df_drugs_categorized['MILLILITRE(S)'] = df_drugs_categorized['MILLILITRES'] + df_drugs_categorized['LITRE(S)']*1000

drug_table = df_drugs_categorized.groupby(['main_group', 'sub_group','name'])['cases','GRAM(S)','MILLILITRES','TABLET(S) MICRODOT(S)','CAPSULE(S)','PLANT(S)','PATCH','SEED(S)','SUPPOSITOR(IES)'].apply(lambda x : x.astype(int).sum())


###CLEAN RCMP DATA AND APPEND###
rcmp_dict = arq_dicts.RCMP_names

df_rcmp = pd.read_csv("seizures_rcmp.csv")
df_rcmp_bc = pd.read_csv("seizures_rcmp_bc.csv")

for i, row in df_rcmp.iterrows():
    df_rcmp.at[i,'Property Type'] = rcmp_dict[row['Property Type'].lower()]
for i, row in df_rcmp_bc.iterrows():
    df_rcmp_bc.at[i,'Property Type'] = rcmp_dict[row['Property Type'].lower()]

df_rcmp=df_rcmp.groupby('Property Type').sum()
df_rcmp_bc=df_rcmp_bc.groupby('Property Type').sum()

df_rcmp["GRAM(S)"] = df_rcmp["kg"]*1000
df_rcmp["MILLILITRES"] = df_rcmp["L"]*1000
df_rcmp.rename(columns={"plants":"PLANT(S)"},inplace=True)
df_rcmp.drop(columns=['kg','L'],inplace=True)

df_rcmp_bc["GRAM(S)"] = df_rcmp_bc["kg"]*1000
df_rcmp_bc["MILLILITRES"] = df_rcmp_bc["L"]*1000
df_rcmp_bc.rename(columns={"plants":"PLANT(S)"},inplace=True)
df_rcmp_bc.drop(columns=['kg','L'],inplace=True)

drug_table=drug_table.reset_index()
drug_table["quantity"] = drug_table["TABLET(S) MICRODOT(S)"]+drug_table["CAPSULE(S)"]+drug_table["PATCH"]+drug_table["SUPPOSITOR(IES)"]
drug_table.drop(columns=["TABLET(S) MICRODOT(S)","CAPSULE(S)","PATCH","SUPPOSITOR(IES)"],inplace=True)                                                       

drug_table.rename(columns={"name":"Property Type"},inplace=True)
df_drug_cats=drug_table[['Property Type','main_group','sub_group']]
drug_table = drug_table.append(df_rcmp.reset_index(),sort=True)
drug_table = drug_table.append(df_rcmp_bc.reset_index(),sort=True)
drug_table = drug_table.groupby('Property Type').sum()

drug_table = pd.merge(drug_table,df_drug_cats,on='Property Type',how='left')

#save to csv
drug_table.to_csv('sorted_drugs.csv')