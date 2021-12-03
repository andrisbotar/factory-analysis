# -*- coding: utf-8 -*-
"""
This is a Python program for analyzing and visualising the modifications carried out
at a specific manufacturing plant. 

This is a program written in Python 3.7.9, using regex,
pandas 1.2.1, matplotlib 3.3.4 and numpy 1.19.2.

The data contains no sensitive information and I have been given permission to share it.


The program reads an input file named "dataset.csv" listing certain details 
about every modification that has been processed at a site over the past 18 years.
• Each modification represents a risk-assessed change to one of the production plants
for the purpose of improving its safety and/or performance.
• Projects indicate significant plant upgrades which are subject to more rigorous
planning and execution procedures. These are denoted by a code, e.g. 5228285.
• The site is grouped into three production areas of interest: Cyanides, Methacrylates
and MM8. Each area consists of a number of production plants, e.g. the ACH8 plant is
located within the MM8 production area.
• Genuine modifications are numbered “YYYY-nnnn”, where “YYYY” is the year of
creation and “nnnn” is a unique identifier.

The "dataset.csv" file contains 6 columns named 
Mod_No	Area	Plant	Temporary Mod	Status	and Project No
First the Mod_No colun is split into the Mod_Id and Mod_Yr columns

Then several "cleanup" steps are performed on the data:
Cancelled modifications are removed.
"Services" - 3rd Party Equipment" are categorised into the "Services" area.
Leading and trailing whitespaces in the project column are removed

In the project column, there are multiple ways "N/A" has been entered,
to make sure all are correctly categorised every entry in this column,
that matches the following 2 crteria is replaced with "N/A":
1.: It is shorter than 4 character
2.: it contains the letter n, followed by 0 or more other charaters, followed by the letter a
This is done using the na_regex, regular expression.
If there are 4character long project codes, containing the letters n and a,
this may lead to those being ignored.
Additionally all empty or "-" project entries are replaced with "N/A".

After this,the following plots and results are generated:
The number of modification carried out in each year are plotted.
The number of modification carried out in each area are also plotted.
The number of modifications in each plant within each are are plotted on 3 separate graphs
The number of mods per project are plotted.
The name of the project with the most mods is printed.


Assumptions:
- Each PLant only belongs to one area (except perhaps services)
- There are only the specified 3 areas + services
- Mod_No is composed of Mod_Id and Mod_Yr

@author: Andras Botar
Feb 14 2021

TODO:
temporary vs permanent mods
read multiple files
fit Zipf or power law to distribution of mods
"""

#import libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

#settings
DISPLAY_PLOTS= True #a debug boolean to change wether plots are displayed by the plot_function
PLOT_SERVICES = False #a boolean to set wether the "services" area is plotted in the yearly breakdown barcharts
PROJECT_THRESHOLD = 5 #how the minimum number of mods a project must have to be displayed

#prepare useful constants and lists
FILE = "dataset.csv" #location of the input file
column_names = ['Mod_Yr','Mod_Id', 'Area', 'Plant', 'Temporary Mod', 'Status', 'Project'] #the expected column names for the dataframe
pd.set_option('max_colwidth', 8) #debug settings to view raw data
pd.set_option('display.max_rows', 50)

#define functions
def plot_function(dataframe,title, x_name, stacking=False, plot_kind='bar'):
    """If the DISPLAY_PLOTS boolean is True,
    this function makes box plots of a column (given by column_name) of
    a pandas dataframe (given by dataframe).
    This plot is then titled, its axes named and then displayed"""
    if DISPLAY_PLOTS:
        if plot_kind == 'bar':
            plot = dataframe.sort_index().plot(kind=plot_kind, stacked=stacking)
        if plot_kind == 'pie':
            plot = dataframe.sort_index().plot(kind=plot_kind, stacked=stacking, autopct='%1.0f%%')
        plot.set_title(title)
        plot.set_xlabel(x_name)
        plot.set_ylabel('Number of modifications')
        plt.savefig(f'Plots/{title}')
        plt.show()


def project_cleanup(dataframe):
    """This function replaces invalid or uninteligable
    entries in the project column with N/A.

    It replaces:
    Other versions of N/A e.g.: NA, na, N.a,...
    "TBC", "various", "TBA", "Multiple"
    entries made up entirely of:
    -whitespaces
    -zeros
    -dashes
    -non alphanumeric characters
    entries where the Project_No is the same as the Mod_Id

    Regex replacements are made separately for readability and ease of modifcation.
    """
    na_regex=r'(?=((n|N).*(a|A)))(?=^[a-zA-Z\W]{0,4}$)'  #replaces N/A entries in the project column, as detailed in the program header

    df2 = dataframe.replace(na_regex, np.nan, regex=True)\
        .replace(['TBC','various','TBA','Multiple'], np.nan)\
        .replace(r'(^\s*$)', np.nan, regex=True)\
        .replace(r'(^0*$)', np.nan, regex=True)\
        .replace(r'(^-*$)', np.nan, regex=True)\
        .replace(r'(^\W$)', np.nan, regex=True)\

    df2 = df2[df2.Project != df2.Mod_No] #remove all entries where the project name is just the Mod_No
    return df2

#Create a "Plots" directory, if it doesn't already exists and plotting is enabled.
if DISPLAY_PLOTS: 
    Path("Plots").mkdir(parents=True, exist_ok=True)

#begin data formatting
df = pd.read_csv(FILE) #read data from file into pandas dataframe
df.columns = [i.replace('Project No','Project') for i in df.columns] #replace "Project No" with just "Project" since it has no whitespace in it and is easier to handle

df = project_cleanup(df) #cleanup project numbers
df = df[df.Status != 'Cancelled'] #remove cancelled projects
df = df.replace(to_replace=r'Services*(.+)', value="Services",regex=True)  #replace any Area name starting with "Sevices..." with simply the string "services"
df['Project'] = df['Project'].str.strip() #remove leading and trailing whitespaces from project column

#split Mod_No into year and in-year number of mod
new = df["Mod_No"].str.split("-", expand = True)
df.insert(0,'Mod_Yr','')
df.insert(0,'Mod_Id','')
df['Mod_Yr'] = new[0]
df['Mod_Id'] = new[1]
df.drop(columns =["Mod_No"], inplace = True)


#begin data analysis
#Plot the number of modifications each year in a bar chart
plot_function(df.value_counts('Mod_Yr'),'Modifications over years', 'Year', 'Mod_Yr')

#Plot the number of modifications each area in a bar or pie chart
counts = df.value_counts('Area') #count the number of mods in each area
#plot_function(df.value_counts('Area'),'Modifications in each area (Bar chart)', 'Area', 'Area')
plot_function(df.value_counts('Area'),'Modifications in each area (Pie chart)', 'Area', 'Area', plot_kind='pie')


cdf = pd.DataFrame((df.value_counts('Mod_Yr').index)) #a new counting dataframe containing not the details of the mods, just the count of how many mods were carried out in each year, with each column representing a different area
for item in counts.index:
    if ((item != 'Services') and not PLOT_SERVICES) or PLOT_SERVICES:
        dfl = df[df.Area == item] #select a specific area to handle
        cdf[item] = dfl.value_counts('Mod_Yr').sort_index().tolist()
        plot_function(dfl.value_counts('Plant'),'Modifications in each {} plant'\
                      .format(item), 'Plant') #Plot the modifications per plant in each area
        plot_function(dfl.value_counts('Mod_Yr'),'Modifications in {} area each year '\
                      .format(item), 'Year') #Plot the modifications per plant in each year

#print(cdf)
column_titles=["Methacrylates","Cyanides","MM8"]
cdf = cdf.reindex(columns=column_titles)



#Plot stacked barchart of projects in each area over years
plot_function(cdf, 'Mods in each are over the year', 'Year', stacking=True)

#Plot stacked barchart of each area over years, but normalised as a percentage of all the projects in that year
totals = [i+j+k for i,j,k in zip(cdf['MM8'], cdf['Methacrylates'], cdf['Cyanides'])]
for item in counts.index:
    if item != 'Services':
        cdf[item] = [i / j * 100 for i,j in zip(cdf[item], totals)]
plot_function(cdf, 'Mods in each area over the years, normalised', 'Year', stacking=True)



#HCN6 plant had disproportionately many modifications, let us examine when these occurred
dfs = df[df.Plant == 'HCN6']
plot_function(dfs.value_counts('Mod_Yr'),'Modifications of HCN6 plant over the years', 'Year')
#spike in 2005
#plot_function(dfs.value_counts('Status'),'Status of HCN6 plant modifications', 'Year')

#display how many modifications were in each project
dfp = df.value_counts('Project')
print('There were a total of {} modifications related to {} projects out of the {} total.'.format(dfp.sum(), len(dfp.index), len(df.index)))
dfp = dfp[dfp > PROJECT_THRESHOLD] #only display projects with more modifications than a given threshold
dfp.plot(kind='bar')
#plot_function(dfp.sort_index(),'Modifications related to projects', 'Project')
#dfp = dfp[dfp > 0] #illustrate how most projects only included a few modifications
#dfp.plot()

#Print the project with the most mods
print("The {} project included {} modifications, the most out of all the projects!"\
      .format(dfp.idxmax(),dfp.max()))

#view the modifications from 2021
"""df21 = df[df.Mod_Yr == '2021']
print(df21)"""


#debug commands to view raw data
#print(df)

#end
