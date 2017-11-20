import os
import sys

import pickle
import zipfile
import re
import datetime

import urllib3
import http.client, urllib.request, urllib.parse, urllib.error, base64
import requests
import json


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations

#Analytical
import networkx as nx
import community

#Other
import ratelim
from bs4 import BeautifulSoup


#Paths
top = os.path.dirname(os.getcwd())

#External data
ext_data = os.path.join(top,'data/external')

#Interim data (to place seed etc)
int_data = os.path.join(top,'data/interim')

#Figures
fig_path = os.path.join(top,'reports/figures')

#Get date for saving files
today = datetime.datetime.today()

today_str = "_".join([str(x) for x in [today.day,today.month,today.year]])