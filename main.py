import requests
from bs4 import BeautifulSoup
import pandas as pd
from progress.bar import Bar
from scraper_parts import get_links, check_proyecto_nuevo, scrape_proyecto_normal, scrape_proyecto_nuevo

links=get_links()
df_master = pd.DataFrame()
links_shortened = links[:5].copy()

print(f"Response: {len(links)} items")

with Bar("Processing %(remaining)d out of %(max)d:", fill="#", max=(len(links)), suffix="%(percent).1f%% - eta: %(eta)ds - elapsed: %(elapsed)ds") as bar:
    for casa in links:
        soup_tmp = BeautifulSoup(requests.get(casa).text, "html.parser")

        if not soup_tmp.find(name="img", attrs={"class":"image404"})==None:
            print(f"Link {casa} saltado, no es valido")
            continue

        is_proyecto_nuevo, soup, r, saltarse_link = check_proyecto_nuevo(casa)

        if is_proyecto_nuevo:
            scrape_proyecto_nuevo()
            continue
        else:        
            df_tmp = scrape_proyecto_normal(soup=soup, r=r)

        df_master = pd.concat([df_master, df_tmp])
        bar.next()

df_master.to_excel("resultado.xlsx", index=False)