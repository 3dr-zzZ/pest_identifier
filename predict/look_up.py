"""A library including functions to load pests database and look up species by the scientific name.

Functions:
    load_database(): load the database.
    look_up(): look up species with scientific name in database.
    format_db_output(): format output from look_up() to make it more readable.

Example usage in other files:
    >>> PROJECT_ROOT = Path(__file__).resolve().parents[1]
    >>> DB_PATH = PROJECT_ROOT/"database"/"pests.db"
    >>> scientific_name = "Aedes albopictus"
    >>> con = load_database(path = DB_PATH)  # establish a sqlite3 connection
    >>> cur = con.cursor()
    >>> format_db_output(look_up(scientific_name = scientific_name, cur = cur))
    # result will display here

Author: 3dr-zzZ
"""

import sqlite3
from pathlib import Path
from sys import argv


# ------ configuration ------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT/"database"/"pests.db"
scientific_name = "Aedes albopictus"

# ------ load database ------
def load_database(path: str|Path) -> sqlite3.Cursor:
    con = sqlite3.connect(path)
    return con.cursor()


# ------ look up in db ------
def look_up(scientific_name: str, cur: sqlite3.Cursor) -> dict|None:
    """Look up species w/ scientific_name in the database.
    
    Note: the scientific name has to be the binomial name (e.g. Culex pipiens), 
    instead of the complete scientific name (e.g. Culex (Culex) pipiens Linnaeus, 1758)
    """
    # first check if the species is in the database
    species_list = cur.execute("SELECT scientific_name FROM species;")
    species_list = species_list.fetchall()
    if (scientific_name,) not in species_list:
        print("数据库尚未收录该物种")
        return

    # look for information about the species
    rslt_dict = {}
    basics_rslt = cur.execute(f"SELECT chinese_name, other_name, traits FROM species\
                            WHERE scientific_name = '{scientific_name}';")
    basics_rslt = basics_rslt.fetchall()[0]  # index = 0 because there's only one row per species
    rslt_dict["物种中文名"] = basics_rslt[0]
    rslt_dict["物种别名"] = basics_rslt[1]
    rslt_dict["鉴别特征"] = basics_rslt[2]

    tax_rslt = cur.execute(f"SELECT taxonomies.name, taxonomies.chinese_name, taxonomies.type FROM species\
                            JOIN belongs ON species.id = belongs.species_id\
                            JOIN taxonomies ON belongs.taxonomy_id = taxonomies.id\
                            WHERE scientific_name = '{scientific_name}';")
    tax_rslt = tax_rslt.fetchall()
    tax_list = []
    for i in range(5):
        tax_list.append(f"{tax_rslt[i][0]} ({tax_rslt[i][1]})")
        tax_organized = " - ".join(tax_list)
    rslt_dict["生物学分类"] = tax_organized

    loc_rslt = cur.execute(f"SELECT locations.name, locations.type FROM species\
                            JOIN distributed ON species.id = distributed.species_id\
                            JOIN locations ON distributed.location_id = locations.id\
                            WHERE scientific_name = '{scientific_name}';")
    loc_rslt = loc_rslt.fetchall()
    province_list = []
    country_list = []
    region_list = []
    for i in range(len(loc_rslt)):
        place = loc_rslt[i]
        if place[1] == 'province':
            province_list.append(place[0])
        elif place[1] == 'country':
            country_list.append(place[0])
        else:
            region_list.append(place[0])
    province_organized = "、".join(province_list)
    country_organized = "、".join(country_list)
    region_organized = "、".join(region_list)
    rslt_dict["国内分布"] = province_organized
    rslt_dict["国际分布"] = country_organized
    rslt_dict["区域分布"] = region_organized

    dis_rslt = cur.execute(f"SELECT diseases.name FROM species\
                            JOIN carries ON species.id = carries.species_id\
                            JOIN diseases ON carries.disease_id = diseases.id\
                            WHERE scientific_name = '{scientific_name}';")
    dis_rslt = dis_rslt.fetchall()
    diseases_list = []
    for disease in dis_rslt:
        diseases_list.append(disease[0])
    disease_organized = "、".join(diseases_list)
    rslt_dict["携带疾病/病毒"] = disease_organized
    return rslt_dict
    

# ------ format result ------
def format_db_output(db_output: dict|None) -> None:
    """Format the output from db for better readability."""
    if db_output is None:
        return
    for key in db_output.keys():
        content = db_output[key]
        if content == '':
            content = f"暂未收录{key}"
        print(key + ":", content)
    return
    
    

def main():
    cur = load_database(DB_PATH)

    print(f"looking for the species: {scientific_name}")
    rslt = look_up(scientific_name, cur)

    print(f"formatting the results: {scientific_name}")
    format_db_output(rslt)

    
if __name__ == "__main__":
        main()
