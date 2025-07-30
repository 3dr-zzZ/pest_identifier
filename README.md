# 病媒生物识别与数据库搭建

本项目旨在训练能够识别4类病媒（老鼠、蚊子、蟑螂、苍蝇）每类30种共120种生物的图像分类模型，并构建相应的信息数据库以查询物种信息。

## 目录
  1. 数据库的构建
  2. 模型训练
  3. 项目收获

## 项目文件结构

## 1. 数据库的构建
数据库使用SQLite语言搭建，相关文件均在/database 目录下。
### 1.1 结构介绍：
分为四张表以及将其连接的桥表。ER图如下：

<img width="500" height="500" alt="image" src="https://github.com/user-attachments/assets/9fe896ca-8e33-415f-a758-5b25ddfd0299" />

其中，每张表分别存储这些信息：
  - species: id, 物种学名, 物种中文名, 物种俗名, 物种鉴别特征
  - taxonomies: id, 名称, 中文名, 层级（门、纲、目、科、属）
  - diseases: id, 名称, 症状
  - locations: id, 名称, 类别（省份、国家、区域）

分多个表格的好处：
  - 提升一致性：多个物种共用地理位置、分类学、疾病，避免可能的错误拼写问题，节省少量空间（数据量大时更明显）。
  - 提升查询速度：在进行诸如“某地区分布有哪些物种”的查询时，无需全文检索，加快查询。
  - 便于存储信息：分表格存储便于存储诸如分类学层级、疾病症状等细分信息。

### 1.2 创建数据库：
**初始化数据库：**
<br>数据库纲要已编辑好并储存在/database/schema.sql，运行：
```bash
sqlite3 pests.db
.read schema.sql
```
即可初始化数据库。

**填充数据：**
<br>由于使用常规查询语句手动填充数据对于本项目的较大数据量较为困难，因此写了一个脚本/database/csv_to_db.py 简化数据填充流程:
  1. 在/database/data_csv 中相应名称的csv文件中填写内容。
  2. csv_to_db.py 上方配置好路径、表格和模式（replace: 替换, append: 添加）。
  3. 运行脚本即可完成数据填充。

## 2. 模型训练
本节介绍了从训练数据搜集到模型训练的整个过程，也涉及部分数据可靠性检验的内容。
### 2.1 训练数据集
*---所有训练数据集相关代码均在/dataset目录下---*<br><br>
训练数据集由两部分组成：1）由公开数据集iNaturalist Dataset 2021挑选的20种，2）iNaturalist网站上Research Level的图片补全其余种类。

**<br>开源数据集**
<br>选择iNaturalist Dataset作为训练数据集，其优势有：
 - 数据量大：物种分类具体到种，包括10,000种物种，2.7M+张图片。
 - 数据质量高：由各地公民科学家拍摄和标注，经过专家审核，且带有全面细致的遵循COCO数据集的标注格式 (Van Horn et al.)。
 - 图片信息多：自然条件下观测，背景信息复杂，物种状态各异，符合本项目模型可能的应用场景。
 - 下载便利：GitHub上开源、且PyTorch内置。
<br>对比但并未选择的数据集： 
 - ImageNet虽然十分经典、包含动物图片，但包含过多不相干类别（汽车、飞机等），且其中动物种类并不按照生物学分类区分。
 - IP102虽然同以农业害虫识别为目的，但其中存在标签不严谨（拼写错误、分类层级混乱）问题、且对本项目四类病媒支持较少。
<br>在iNaturalist Dataset 2021中提取到20种本项目关注的生物：5种蚊子、3种老鼠、4种苍蝇和8种蟑螂，在train_mini中每种有50张图片。

**<br>动物数据库网站**
<br>在从公开数据集获取了部分数据后，可以通过动物数据网站补全其余物种。对比后依然选择iNaturalist网站作为数据来源，优势有：
 - 与iNaturalist Dataset同源，保障数据一致性。
 - iNaturalist Dataset优势大部分均有。
 - 下载便利：提供API服务、GBIF有存储支持。
<br>对比但未选择的动物数据库网站：
 - Encyclopedia of Life(EOL):汇总全球多来源的生物信息，包括照片、声音、视频；或许适用于多模态场景，但物种照片较少，不适合单一场景下的图像识别任务。
 - 中国动物主题数据库：由中国科学院动物研究所和中国科学院昆明动物研究所主持，包含全面的国内动物数据；但网站缺乏维护，访问较为困难。

**<br>数据下载**
<br>*开源数据集*
<br>下载iNaturalist Dataset 2021有两种方式：
  1. 通过其GitHub repo(https://github.com/visipedia/inat_comp/tree/master/2021 )下载。
  2. 使用pytorch内置函数下载，详见：https://docs.pytorch.org/vision/stable/generated/torchvision.datasets.INaturalist.html#torchvision.datasets.INaturalist

<br>*动物数据库*
<br>从动物数据库iNaturalist上下载数据也有两种方式：
  1. 通过iNaturalist API请求：使用classes.txt和download_image.py
     <br>a. 在classes.txt中输入所要下载物种的学名，例如：Culex pipiens。
     <br>b. 在download_image.py中配置每种物种下载数量和保存路径。
     <br>c. 运行download_image.py进行下载。
  2. 通过GBIF保存的物种信息，提取图片链接下载：
     <br><img width="500" height="500" alt="image" src="https://github.com/user-attachments/assets/359d0209-f5f8-49c8-86e8-e11b4f9b517f" />
     <br>a. 在GBIF上筛选iNaturalist Research-grade Observations和相应物种，下载Darwin Core Archive (含有multimedia)。
     <br>b. 在download_link.py中配置路径和下载数量。
     <br>c. 运行download_link.py，脚本自动提取文档中的图片链接下载。

**<br>数据处理**
<br>
  1. **清洗：** 手动去除数据集中模糊图片和其它不相关图片（老鼠脚印、孑孓、头骨等）。
  2. **划分：** 使用split.py划分为train和val数据集。
