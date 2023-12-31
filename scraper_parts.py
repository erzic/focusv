def get_links(limit = None):
    import requests
    from bs4 import BeautifulSoup

    #
    #link_venta_casas = "https://www.encuentra24.com/el-salvador-es/bienes-raices-venta-de-propiedades-casas"
    # payload = {
    #     "q":"number.50", # para tener 50 resultados por cada pagina, disminuye el bucle
    # }
    # r = requests.get(link_venta_casas, params=payload)

    # soup = BeautifulSoup(r.text, 'html.parser')

    # links = ["".join([link_inicial, link.attrs["href"].split("?")[0]]) for link in soup.find_all(name="div", attrs={"class":"ann-ad-tile__cover"})]
    
    links = []
    contador = 1
    payload = {"q":"number.50"} # para tener 50 resultados por cada pagina, disminuye el bucle
    link_inicial="https://www.encuentra24.com"

    while True: # obtiene todos los links de cada pagina
        link_temp = f"https://www.encuentra24.com/el-salvador-es/bienes-raices-venta-de-propiedades-casas.{contador}"

        r = requests.get(link_temp, params=payload)
        soup = BeautifulSoup(r.text, 'html.parser')

        links_temp = [l for l in soup.find_all(name="a", attrs={"class":"ann-ad-tile__title"}) if l.text!=None or l.text.strip()!=""]
        links_temp = ["".join([link_inicial, link.attrs["href"].split("?")[0]]) for link in links_temp]
        link_temp = []
        if len(links_temp)==0:
            break
        links.extend(links_temp)

        if contador==limit:
            break

        contador+=1
    
    return links

def generate_links_log(links, filename="links_log.parquet"):

    import pandas as pd
    import datetime

    timestamp = datetime.datetime.today()
    year = timestamp.year
    month = timestamp.month
    day = timestamp.day

    try:
        df=pd.read_parquet(f"data/{filename}")
        df_tmp=pd.DataFrame()
        df_tmp["links"] = links
        df_tmp["fecha"] = pd.to_datetime([f"{year}/{month}/{day}"]*len(links), format="%Y/%m/%d")

        df = pd.concat([df, df_tmp], axis=1)
        df.to_parquet(f"data/{filename}")
    except:
        df = pd.DataFrame()
        df["links"] = links
        df["fecha"] = pd.to_datetime([f"{year}/{month}/{day}"]*len(links), format="%Y/%m/%d")
        df.to_parquet(f"data/{filename}")
    
    return None

def check_proyecto_nuevo(link):

    import requests
    from bs4 import BeautifulSoup

    r = requests.get(link)
    soup = BeautifulSoup(r.text, "html.parser")

    # try:
    #     breadcrumb = soup.find(name="div", attrs={"class":"d3-container adaptor-breadcrumb-detailpager"}).text
    #     breadcrumb_encontrado = True
        
    # except AttributeError:
    #     breadcrumb = ""
    #     breadcrumb_encontrado = False
        
    if link.lower().find("bienes-raices-proyectos-nuevos")!=-1:
        saltarse_link=True #esto se borra cuando tengamos el scraper de proyectos nuevos
        is_proyecto_nuevo=True
    else:
        saltarse_link=False
        is_proyecto_nuevo=False
    
    return is_proyecto_nuevo, soup, r, saltarse_link

    # if breadcrumb.find("Proyectos nuevos")!=-1:
    #     saltarse_link=True
    #     is_proyecto_nuevo=True
    #     return is_proyecto_nuevo, soup, r, saltarse_link
    
    # elif breadcrumb=="":
    #     saltarse_link=True
    #     is_proyecto_nuevo=True
    #     return is_proyecto_nuevo, soup, r, saltarse_link
    
    # else:
    #     saltarse_link=False
    #     is_proyecto_nuevo=False
    #     return is_proyecto_nuevo, soup, r, saltarse_link

def scrape_proyecto_normal(soup, r):
    import pandas as pd
    ad_info = soup.find(name="div", attrs={"class":"ad-info"})
    ad_info_parts = ad_info.find_all(name="li")

    info_dict = {}

    for part in ad_info_parts:
        info_name = part.find(name="span", attrs={"class":"info-name"}).text
        info_value = part.find(name="span", attrs={"class":"info-value"}).text
        info_dict[info_name] = [info_value]


    ad_details = soup.find(name="div", attrs={"class":"ad-details"})
    ad_details_part = ad_details.find_all(name="li")
    for part in ad_details_part:
        info_name = part.find(name="span", attrs={"class":"info-name"}).text
        info_value = part.find(name="span", attrs={"class":"info-value"}).text

        info_dict[info_name] = [info_value]


    section_box = soup.find_all(name="div", attrs={"class":"section-box"})
    section_box = [i for i in section_box if i.text.find("Detalles")!=-1][0]

    section_box_id = section_box.find(name="span", attrs={"class":"ad-id"}).text
    section_box_content_b = section_box.find(name=["b"]).text
    section_box_content_p = section_box.find(name=["p"]).text
    info_dict["Detalles"] = ["\n".join([section_box_content_b, section_box_content_p])]
    info_dict["id"] = [section_box_id]
    info_dict["link"] = [r.request.url]

    return pd.DataFrame(info_dict)

def scrape_proyecto_nuevo():
    pass