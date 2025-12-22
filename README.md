# Stock Market Database and Reporting Suite
___
## Overview
Leveraging **Python** and **[Massive's RESTful API](https://massive.com/)** service (formerly Polygon.io), I've created the following:
1. **SQLite** Database Creation Pipeline
2. Stored Procedures to perform DB updates/maintence 
3. Charting utilities to visualize data from our newfound DB with **matplotlib**

These modules are fully operational as I depend on them for my day-to-day market analysis/backtesting. Let's unpack each of these in a little more detail.

## [SQLite Database Creation Pipeline](Database)
___
Using a 3P API/Data Service is an inherently IO-bound task, which is why [polygon_api.py](Database/polygon_api.py) makes use of the **AIOHTTP** library. This provides an HTTP client that support asynchronous requests to Massive, significantly improving DB build times. Asynchronous calls are made in strategically sized batches to respect Massive's 100 request per second [rate limit](https://massive.com/knowledge-base/article/what-is-the-request-limit-for-massives-restful-apis).

The DB table structures are stored in [table_maps.py](Database/table_maps.py). They are expressed in  a JSON style to make configuration updates (column renames, change in data types) simple. The database structure is outlined in the diagram below:

![Stock_DB Diagram](Database/docs/diagram.PNG)

### Table Summary
___
**Daily** - The daily price action of over 5,000 stock market symbols, enriched with popularly used indicators (MACD, EMA's).

**Weekly** - The weekly price action of those same symbols, enriched with the same indicators (minus SMA_50).

**Symbol** - Metadata about the underlying companies (website, logo url, list date)

**Calendar** - A standard DB date table to facilitate time intelligence queries (built using the **Pandas** and **Holidays** libraries).

## Database Stored Procedures
___
What good is a database if it doesn't update and stay relevant? These [**stored procedures**](Database/stored_procedures.py) are scheduled to run after each market day with the intended goals in mind:
1. Retrieve the latest price action from **[Massive's RESTful API](https://massive.com/)**
2. Calculate the latest indicator derivatives
3. Boot inactive stocks from the database
4. Recruit symbols recently listed on the market

The database creation script and update procedures are kept in the same module, as a lot of the same code can be reused.