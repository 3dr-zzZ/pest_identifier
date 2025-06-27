# 2025.06.23, 3dr
import requests # type: ignore
import os
from urllib.parse import quote
from urllib.request import urlretrieve
import time

#####配置#####
IMAGES_PER_SPECIES = 3  # 每个物种下载的观察记录数
output_dir = "dataset"
#############

os.makedirs(output_dir, exist_ok=True)  # 创建总文件夹

# 输入：抓取的物种学名
species_list = []
with open("species.txt", "r") as f:
    for line in f:
        species_list.append(line.strip())

def download_images_for_species(species_name):
    print(f"\nFetching: {species_name}")
    encoded_name = quote(species_name)
    url = f"https://api.inaturalist.org/v1/observations?taxon_name={encoded_name}&per_page={IMAGES_PER_SPECIES}&order=desc&order_by=created_at"

    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch data for {species_name}")
            return

        data = response.json()
        save_folder = os.path.join(output_dir, species_name.replace(" ", "_"))
        os.makedirs(save_folder, exist_ok=True)

        count = 0
        for i, result in enumerate(data.get("results", [])):
            for j, photo in enumerate(result.get("photos", [])):
                img_url = photo["url"].replace("square", "large")
                filename = os.path.join(save_folder, f"{species_name.replace(' ', '_')}_{i}_{j}.jpg")
                try:
                    urlretrieve(img_url, filename)
                    print(f"Saved: {filename}")
                    count += 1
                except Exception as e:
                    print(f"Error downloading {img_url}: {e}")
            time.sleep(0.1)  # 避免请求过快被限速

        print(f"📦 Done: {count} images saved for {species_name}")

    except Exception as e:
        print(f"Error fetching data for {species_name}: {e}")

# 逐个处理每个物种
for species in species_list:
    download_images_for_species(species)
