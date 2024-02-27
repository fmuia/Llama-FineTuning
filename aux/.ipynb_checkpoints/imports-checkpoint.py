from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlparse, parse_qs, urlunparse

from bs4 import BeautifulSoup, NavigableString

import re
import csv
import time
import math
import pandas as pd
import unicodedata

import arxiv

import matplotlib.pyplot as plt
import seaborn as sns

pd.set_option('display.max_colwidth', None)
