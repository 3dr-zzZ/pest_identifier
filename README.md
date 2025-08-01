# Pest Identification & Database Construction

[English](README.md) | [中文](README.zh-CN.md)

This project is oriented around personal learning and involves training image classification models and building a database system. It aims to automatically classify and retrieve information for 120 common vector species (rats, mosquitoes, cockroaches, and flies). The following documents the work completed and lessons learned at each stage of the project.

**Project Flowchart:**  
<img width="887" height="317" alt="image" src="https://github.com/user-attachments/assets/973c7f60-5c94-46b6-8ec8-4d28d0e8bf51" />

**Demo:**  

https://github.com/user-attachments/assets/20c77c18-41e5-46f8-9943-40b57d1db07b  

_(Note: The high-resolution demo image is available at the bottom of this document.)_

## Project File Structure
<pre>
.
├── database/                  # Database module
│   ├── data_csv/              # Raw CSV data and related scripts
│   ├── csv_to_db.py           # Script to import CSVs into the database
│   ├── queries.sql            # Sample SQL query statements
│   └── schema.sql             # Database schema definition

├── dataset/                   # Dataset processing
│   ├── classes.txt            # Class label names
│   ├── download_image.py      # Script to download images
│   ├── download_link.py       # Script to extract download links
│   ├── extract_label.py       # Script to extract labels
│   └── split.py               # Script to split train/val sets

├── predict/                   # Inference and lookup module
│   ├── look_up.py             # Query species info from database
│   ├── predict.py             # Main model inference script
│   └── workwork.py            # Combined "classify + lookup" script

├── train_model.ipynb          # Model training notebook using timm
├── train_torch.ipynb          # Custom model training notebook using PyTorch

├── README.md
├── LICENSE
└── .gitignore
</pre>

Project repository: [GitHub](https://github.com/3dr-zzZ/pest_identifier/tree/main)

## Table of Contents
1. Learning Outcomes  
2. Database Construction  
3. Model Training  
4. Classification–Query Workflow  

## 1. Learning Outcomes

Throughout this project, I gained substantial technical skills and knowledge, and achieved meaningful growth across multiple areas.

When I first began, I consulted AI and online encyclopedias to understand what “vector organisms” are. I then clarified that the task falls under computer vision, specifically image classification within the fields of machine learning and deep learning. I searched and reviewed literature using keywords like "vector", "pest", "machine learning", and "image classification", and compiled a simple review of technical approaches in this domain.

As the project progressed, I continued exploring relevant literature to deepen my understanding. To better grasp the development of deep learning architectures, I studied classic papers including AlexNet, Transformer, and Swin Transformer. For data lineage, I referred to IBM’s technical webpages and papers on integrating lineage with machine learning, exploring how such techniques could help assess the trustworthiness of training data. I also studied survey and technical papers on image tampering detection to learn about detection techniques and their underlying algorithms.

On the implementation side, I learned the fundamentals of model training using PyTorch. I initially attempted to replicate the winning solution of the iNaturalist Competition 2021 but later switched to fine-tuning a smaller pretrained model due to limited hardware. To address potential prediction errors and fulfill users’ need for background information on species, I designed a SQLite-based database system to store species information and linked it to the classification module—creating a full “classify–query” pipeline.

In doing so, I became proficient in using SQL and Python in practical tasks. I also improved my ability to solve real-world problems by writing scripts for data collection, preprocessing, and system integration.

Additionally, I realized how crucial data quality is for model performance. I explored concepts like "data lineage" and "image credibility" to evaluate the reliability of training data, and compiled these notes:

- [Data Lineage](https://www.notion.so/Data-Lineage-2347b3784acb8049ba75f0b5319e3cb2?source=copy_link)
- [Image Credibility](https://www.notion.so/2377b3784acb80ac8c77c66c79ede424?source=copy_link)

I also discovered personal research interests along the way. For instance, while reading Mora, Camilo et al.’s *"How many species are there on Earth and in the ocean?"*, I became deeply interested in their regression-based methodology of “inferring the unknown from the known.” Meanwhile, studying SQL and deep learning gave me a more grounded understanding of my coursework—be it the computational foundations of SQL query optimization, or the calculus, statistics, and linear algebra behind deep learning models.

In particular, I came to appreciate how model interpretability is not only a technical challenge, but also a promising research direction. It could significantly enhance transparency, help explain model decisions, and even uncover new knowledge.

In summary, I developed the following core capabilities through this project:
1. **Literature review and research skills**: Independently searching, reading, and summarizing technical papers  
2. **Interdisciplinary learning**: Gaining insights into computer vision, image forensics, data lineage, and model interpretability  
3. **Technical proficiency**: Practical experience with SQL, PyTorch, data processing, model training, database design, and system integration

## 2. Database Construction

*—Related code located in the `/database` directory—*

The database is built using SQLite.

### 2.1 Structure Overview

The schema consists of four core tables and several bridge tables. The ER diagram is shown below:

<img width="500" height="500" alt="image" src="https://github.com/user-attachments/assets/9fe896ca-8e33-415f-a758-5b25ddfd0299" />

Each table stores the following information:
- `species`: id, scientific name, Chinese name, common name, distinguishing features
- `taxonomies`: id, name, Chinese name, rank (phylum, class, order, family, genus)
- `diseases`: id, name, symptoms
- `locations`: id, name, category (province, country, region)

**Advantages of using multiple tables:**
- **Improved consistency**: Reusable entities (e.g., taxonomy, diseases, geographic locations) reduce typos and redundancy
- **Faster queries**: E.g., to find "species distributed in a given area," the query avoids expensive full-text search
- **Better structure**: Easier to store nested or hierarchical attributes like taxonomy levels and disease symptoms

### 2.2 Creating the Database

**To initialize the database:**  
The schema is already defined in `schema.sql`. Run:

```bash
sqlite3 pests.db
.read schema.sql
```

**To populate data:**  
Manually entering records via SQL is time-consuming for larger datasets, so a script `csv_to_db.py` is provided to automate the process:
1. Fill in the corresponding CSV files in the `data_csv/` folder
2. Configure the path, table name, and mode (`replace` or `append`) at the top of `csv_to_db.py`
3. Run the script to import data into the database

## 3. Model Training

This section introduces the entire workflow from data collection to model training, including some steps for evaluating data quality and reliability.

### 3.1 Training Dataset

*—Related code located in the `/dataset` directory—*

The training dataset consists of two parts:  
1. 20 species selected from the open-source iNaturalist 2021 Dataset  
2. Images of additional species collected from the iNaturalist website (Research Grade)

**Open-source dataset:**  
The iNaturalist Dataset was chosen due to the following advantages:
- **Large scale**: Over 10,000 species and 2.7M+ labeled images at the species level
- **High quality**: Labeled by citizen scientists and verified by experts; adheres to COCO-format standards (Van Horn et al.)
- **Realistic settings**: Images captured in natural conditions with diverse backgrounds — suitable for real-world application scenarios
- **Easy access**: Publicly available on GitHub and supported by PyTorch built-ins

**Alternative datasets considered but not chosen:**
- *ImageNet*: Although classic, it contains many irrelevant categories (e.g., vehicles) and lacks strict biological taxonomy
- *IP102*: Focuses on agricultural pests but suffers from inconsistent labels (misspellings, mixed taxonomic ranks) and limited coverage of the 4 vector types targeted in this project

From the iNaturalist 2021 Dataset, 20 relevant species were selected:
- 5 mosquitoes  
- 3 rodents  
- 4 flies  
- 8 cockroaches
 
Each species has 50 images in the `train_mini` subset.

**Online image sources:**  
After extracting partial data from open datasets, the remaining species were supplemented using animal information platforms. iNaturalist was selected again for consistency and convenience:
- **Same source** as iNaturalist Dataset ensures label and style consistency
- Inherits all other advantages mentioned above
- **Convenient API and GBIF support** for retrieval

**Other platforms considered but not used:**
- *Encyclopedia of Life (EOL)*: Offers multimodal content (photos, audio, video), but has limited image data — not ideal for image classification alone
- *Chinese Animal Thematic Database*: Hosted by the Institute of Zoology, Chinese Academy of Sciences; comprehensive domestic records but outdated and difficult to access

**Image download options:**

*For iNaturalist Dataset 2021*:
1. Download from [official GitHub repo](https://github.com/visipedia/inat_comp/tree/master/2021)
2. Use [PyTorch's built-in dataset loader](https://pytorch.org/vision/stable/generated/torchvision.datasets.INaturalist.html)

*For iNaturalist Website data*:
1. Use iNaturalist API  
   - a. List scientific names in `classes.txt` (e.g., *Culex pipiens*)  
   - b. Configure download settings in `download_image.py`  
   - c. Run `download_image.py`  
2. Use GBIF archive  
   <img width="500" height="500" alt="image" src="https://github.com/user-attachments/assets/359d0209-f5f8-49c8-86e8-e11b4f9b517f" />  
   - a. Filter Research-grade observations on GBIF and download the Darwin Core Archive  
   - b. Set paths and limits in `download_link.py`  
   - c. Run `download_link.py` to extract and download image URLs from the archive

**Data processing:**
1. **Cleaning**: Manually remove blurry or irrelevant images (e.g., rat tracks, larvae, skulls)
2. **Splitting**: Use `split.py` to divide into training and validation sets

### 3.2 Model Training

This project uses a fine-tuned ConvNeXt-Tiny model pretrained on ImageNet. This model was chosen for its small size and balanced performance among lightweight architectures. The primary goal here is experimental — to validate functionality rather than optimize performance.

Two versions of training code are used:
- `train_model.py`: Written with PyTorch and `timm` library, developed with assistance from ChatGPT (GPT-4 o3)
- `train_torch.py`: A minimal version built using only PyTorch, written independently for learning purposes

**train_model.py**  
This script offers better training speed and results. It incorporates techniques such as:
- Freezing the backbone for a few epochs to train a new linear head
- Using CutMix and MixUp
- Label smoothing

Below are training results on the small-scale dataset (20 species from iNaturalist 2021):

| Attempt | Train Accuracy | Val Accuracy | Key Adjustments |
|---------|----------------|--------------|------------------|
| 1st     | 99.9%          | 67%          | Default settings, initial training |
| 2nd     | 97.4%          | 70.5%        | Learning rate changed from 3e-4 to 1e-4 |
| 3rd     | 98.02%         | 73.23%       | Cleaned dataset (removed blurry, irrelevant images) |
| 4th     | 96.25%         | 67.68%       | Freeze epochs increased from 1 to 3; overfitting occurred around epoch 6 |
| 5th     | 88.44%         | 73.23%       | Freeze epochs to 5; added label smoothing, CutMix, and MixUp |
| 6th     | 79.69%         | 69.19%       | Epochs increased from 12 to 15; plateaued with eventual decline |
| 7th     | 83.44%         | 70.2%        | Epochs reset to 12; MixUp alpha 0.2 → 0.1; CutMix alpha 1.0 → 0.5 |

## 4. Classification–Query Workflow

*—Related code located in the `/predict` directory—*

To enable end-to-end inference from image input to species information output, I implemented APIs for database querying and image classification, as well as an integrated script that combines both.

### Database Query

Relevant code is in `look_up.py`. Main functions/APIs include:
- `load_database()`: Loads the database and returns a cursor
- `look_up()`: Queries the database for species info based on the classification result
- `format_db_output()`: Formats the returned info as a printable string
- `main()`: A usage example

### Classification

Relevant code is in `predict.py`. Main functions/APIs include:
- `load_model()`: Loads the trained model
- `get_transforms()`: Returns the preprocessing transforms
- `predict_one()`: Predicts the image label and returns the top-k results
- `main()`: Command-line entry point

### Integrated Workflow

Using the wrapped APIs, the script `workwork.py` allows you to input an image path and receive both the classification result and associated species information.

**Usage:**
```bash
python workwork.py <image_path>
```

**Example Output:**

<img width="648" height="405" alt="image" src="https://github.com/user-attachments/assets/0001cac1-f56a-4bd7-be26-b167b483d11c" />

## License

This project is intended for personal learning and exploration. It is licensed under the MIT License.  
You are welcome to reference, reuse, suggest improvements, or share ideas!
