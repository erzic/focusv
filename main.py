import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
from scraper_parts import get_links, check_proyecto_nuevo, scrape_proyecto_normal, scrape_proyecto_nuevo
from alive_progress import alive_bar

links=get_links()

df_master = pd.DataFrame()

links_shortened = links.copy()

with alive_bar(total=len(links_shortened), bar="bubbles") as bar:
    for casa in links_shortened:
        is_proyecto_nuevo, soup, r, saltarse_link = check_proyecto_nuevo(casa)

        if saltarse_link:
            continue
        
        if is_proyecto_nuevo:
            scrape_proyecto_nuevo()
            continue
        else:        
            df_tmp = scrape_proyecto_normal(soup=soup, r=r)

        df_master = pd.concat([df_master, df_tmp])
        
        bar()