#UUI Solar Data

This project will enable data collection, aggregation, reporting & alerting, 
and visualization for the energy output of all solar arrays installed on
the UUI campus.

There are 3 separate operational systems, each with their own developer API:
1. SolarEdge
2. Enphase
3. Sunnyboy

A kiosk system, consisting of a Raspberry Pi 3 and HDMI wall-mounted monitor,
will display real-time updates and historical performance data for comparisons.
The visualization formats to be shown are TBD.

The Raspi 3 will be running a python process that collects data from the arrays in 15-minute ticks.
This data will be fed into a local instance of [Dash by Plotly](https://plot.ly/) for display and visualization. 


 