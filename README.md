# factory-analysis
This is a Python program for analyzing and visualising the modifications carried out
at a specific manufacturing plant. It cleans-up the data, does some analysis
and creates several plots for a presentation about the site.

The program "create_report.py", reads an input file named "dataset.csv" listing certain details 
about every modification that has been processed at a site over the past 18 years. 
- Each modification represents a risk-assessed change to one of the production plants
for the purpose of improving its safety and/or performance.
- Projects indicate significant plant upgrades which are subject to more rigorous
planning and execution procedures. These are denoted by a code, e.g. 5228285.
- The site is grouped into three production areas of interest: Cyanides, Methacrylates
and MM8. Each area consists of a number of production plants, e.g. the ACH8 plant is
located within the MM8 production area.
- Genuine modifications are numbered “YYYY-nnnn”, where “YYYY” is the year of
creation and “nnnn” is a unique identifier.

The data contains no sensitive information and I have been given permission to share it.
