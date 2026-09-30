# 1. Dataset Selection

**Name and Description**
Our project utilizes the TTC Bus, Streetcar, and Subway Delay Data, sourced from the City of Toronto Open Data Portal. The dataset provides historical logs of transit delay incidents to support our supervised regression task. The unit of analysis is a single logged delay incident, with the target variable being the continuous delay duration in minutes.

**Link to Original Dataset**
The datasets are sourced from the Toronto Transit Commission via the City of Toronto Open Data Portal -  TTC Bus / Streetcar / Subway Delay Data
The specific portal pages for each dataset are:
* [TTC Bus Delay Data](https://open.toronto.ca/dataset/ttc-bus-delay-data/)
* [TTC Streetcar Delay Data](https://open.toronto.ca/dataset/ttc-streetcar-delay-data/)
* [TTC Subway Delay Data](https://open.toronto.ca/dataset/ttc-subway-delay-data/)

**Dataset License**
The data is published under the **Open Government Licence – Toronto**
(https://open.toronto.ca/open-data-licence/)

**Dataset Construction and Organization**
We assembled our working dataset from publicly published TTC records spanning January 2014 to December 2024 (132 months with no gaps). The raw downloaded data consists of 270 CSV files, plus README and code-lookup files. 

The files were originally organized by the city in a mixed structure: records up through 2021 are grouped as monthly CSV files within yearly folders, while records from 2022 to 2024 are stored as single annual CSV files. To construct our dataset, we combined these files, which initially yielded 854,623 raw surface transit rows (707,398 bus rows and 147,225 streetcar rows) after identifying and removing a duplicated 2020 folder provided in the raw download.