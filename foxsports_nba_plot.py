import json
import requests
import sqlite3
import plotly.plotly as py
import plotly.graph_objs as go
import numpy as np

trace1= go.Scatter(x=[0,0.5,1,2,2.2],y=[1.23,2.5,0.42,3,1])
layout = go.Layout(images= [dict(
                  source= "https://userscontent2.emaze.com/images/0e8ac80a-9117-45a0-b503-41d01ee8ddfa/cefc4149-a2d4-4432-b328-e4c1b3fd0a7a.jpg",
                  xref= "x",
                  yref= "y",
                  x= 0,
                  y= 3,
                  sizex= 2,
                  sizey= 2,
                  sizing= "stretch",
                  opacity= 0.5,
                  layer= "below")])
fig=go.Figure(data=[trace1],layout=layout)
py.plot(fig, validate=False, filename="test")