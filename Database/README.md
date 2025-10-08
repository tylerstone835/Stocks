# Financial Data Pipeline


This project is a fully functional Python pipeline that builds and maintains a financial market database using data from the [Polygon.io](https://polygon.io) RESTful API.  

The **create_database.py** script asynchronously retrieves five years of OHLC (Open, High, Low, Close) price data for daily and weekly timeframes, calculates technical market indicators, and stores the results in a local **SQLite** database. Utilizing asynchronous API calls and symbol batching, the entire database builds in approximately 25 minutes, all while respecting 3P rate limits. To provide time intelligence and stock symbol dimensionality, this script will also create a **stock** **overview** and **calendar/date** table.

The **update_database.py** contains the stored procedures to keep the database relevant and well-maintained after creation. Utilizing strategic SQL queries (**queries.py**), the stored procedures can efficiently locate new OHLC records with missing indicator data, and retrieve the **necessary** historic aggregates when calculating the new indicator values. This script is intended to be scheduled as an update task at the end of each market day. 

# Relational Diagram

All table configurations are stored in **table_maps.py**.
![Price Action Datbabase | Relationship Model](readme_assets/diagram.png)