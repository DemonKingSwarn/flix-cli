import httpx
from bs4 import BeautifulSoup

import re
import sys

from colorama import Fore, Style

client = httpx.Client()

cyan = lambda a: f"{Fore.CYAN}{a}{Style.RESET_ALL}"

def get_id(query):
    query = query.replace(" ","_")
    
    url = f"https://v2.sg.media-imdb.com/suggestion/{query[0]}/{query}.json"
    
    r=client.get(url)
    
    get_id.imdb_ids = [i["id"] for i in r.json().get("d")]
    names = [i["l"] for i in r.json().get("d")]
    
    print(cyan("[*]Results: "))
    print("\n")
    for i in range(len(names)):
        print(cyan(f"{i+1}. {names[i]}"))
    
    print("\n")    
    get_id.c = int(input(cyan("[*]Enter number: ")))
    
    return get_id.imdb_ids[get_id.c-1]

query = input("Search: ")
get_id(query)

GDRIVE_API = "https://api.gdriveplayer.us/v2/series/imdb"

url = f"{GDRIVE_API}/{get_id.imdb_ids[get_id.c-1]}"

fetch = client.get(url).text

print(fetch)
