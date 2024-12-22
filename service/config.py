import os
import json
import unicodedata
import re
import networkx as nx
import matplotlib.pyplot as plt
import tiktoken
from tqdm import tqdm
import time
from gradio_client import Client
import PyPDF2
import requests

client = Client("Qwen/Qwen2.5")
filepath = "Mephi_data.pdf"
MAX_TOKENS = 1000
ENCODING = tiktoken.encoding_for_model("gpt-3.5-turbo")