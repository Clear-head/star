import numpy as np
import ForExcel as fe
import ForWeather as fw
import pandas as pd
from sklearn.linear_model import LinearRegression

weekday = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
weekend = ['Saturday', 'Sunday']


lr = LinearRegression()
