# 病媒生物识别与数据库搭建

本项目旨在训练能够识别4类病媒（老鼠、蚊子、蟑螂、苍蝇）每类30种共120种生物的图像分类模型，并构建相应的信息数据库以查询物种信息。

## 目录
  1. 数据库的构建
  2. 模型训练
  3. 识别——查询流程
  4. 项目收获

## 项目文件结构
项目地址: [GitHub](https://github.com/3dr-zzZ/pest_identifier/tree/main)

## 1. 数据库的构建
*---此部分相关代码在/database目录下---*<br><br>
数据库使用SQLite语言搭建。
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
<br>数据库纲要已编辑好并储存在schema.sql，运行：
```bash
sqlite3 pests.db
.read schema.sql
```
即可初始化数据库。

**填充数据：**
<br>由于使用常规查询语句手动填充数据对于本项目的较大数据量较为困难，因此写了一个脚本csv_to_db.py 简化数据填充流程:
  1. 在data_csv 中相应名称的csv文件中填写内容。
  2. csv_to_db.py 上方配置好路径、表格和模式（replace: 替换, append: 添加）。
  3. 运行脚本即可完成数据填充。

## 2. 模型训练
本节介绍了从训练数据搜集到模型训练的整个过程，也涉及部分数据可靠性检验的内容。
### 2.1 训练数据集
*---此部分相关代码在/dataset目录下---*<br><br>
训练数据集由两部分组成：1）由公开数据集iNaturalist Dataset 2021挑选的20种，2）iNaturalist网站上Research Level的图片补全其余种类。

**<br>开源数据集**
<br>选择iNaturalist Dataset作为训练数据集，其优势有：
 - 数据量大：物种分类具体到种，包括10,000种物种，2.7M+张图片。
 - 数据质量高：由各地公民科学家拍摄和标注，经过专家审核，且带有全面细致的遵循COCO数据集的标注格式 (Van Horn et al.)。
 - 图片信息多：自然条件下观测，背景信息复杂，物种状态各异，符合本项目模型可能的应用场景。
 - 下载便利：GitHub上开源、且PyTorch内置。

对比但并未选择的数据集： 
 - ImageNet虽然十分经典、包含动物图片，但包含过多不相干类别（汽车、飞机等），且其中动物种类并不按照生物学分类区分。
 - IP102虽然同以农业害虫识别为目的，但其中存在标签不严谨（拼写错误、分类层级混乱）问题、且对本项目四类病媒支持较少。
<br>在iNaturalist Dataset 2021中提取到20种本项目关注的生物：5种蚊子、3种老鼠、4种苍蝇和8种蟑螂，在train_mini中每种有50张图片。

**<br>动物数据库网站**
<br>在从公开数据集获取了部分数据后，可以通过动物数据网站补全其余物种。对比后依然选择iNaturalist网站作为数据来源，优势有：
 - 与iNaturalist Dataset同源，保障数据一致性。
 - iNaturalist Dataset优势大部分均有。
 - 下载便利：提供API服务、GBIF有存储支持。

对比但未选择的动物数据库网站：
 - Encyclopedia of Life(EOL):汇总全球多来源的生物信息，包括照片、声音、视频；或许适用于多模态场景，但物种照片较少，不适合单一场景下的图像识别任务。
 - 中国动物主题数据库：由中国科学院动物研究所和中国科学院昆明动物研究所主持，包含全面的国内动物数据；但网站缺乏维护，访问较为困难。

**<br>数据下载**
<br>*开源数据集*
<br>下载iNaturalist Dataset 2021有两种方式：
  1. 通过其[GitHub repo](https://github.com/visipedia/inat_comp/tree/master/2021 )下载。
  2. 使用[torchvision内置函数下载](https://docs.pytorch.org/vision/stable/generated/torchvision.datasets.INaturalist.html#torchvision.datasets.INaturalist
)

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

### 2.2 模型训练
本项目采用基于ImageNet预训练的ConvNeXt-tiny进行微调，选择的主要原因是其参数量小、相似参数量模型中表现均衡；试验目的较强，主要为了验证代码运行，并不必须该模型。

模型训练分别使用两种代码：train_model.py和train_torch.py。
 - train_model.py：使用PyTorch以及timm库，在Chat-GPT o3的协助下编写。
 - train_torch.py：仅使用PyTorch，以学习为目的自己编写。

**train_model.py**
整体的训练速度和效果都更优，并且使用了诸如：冻结骨干网络数轮次以训练新的线性层、CutMix/MixUp、label smoothing等技巧。
以下是在小规模数据（iNaturalist Dataset 2021中20种物种）上训练的记录：
| 次数   | 训练集准确率 | 验证集准确率 | 关键调整 |
|-------|-------|-------|-------|
| 第一次 | 99.9%  | 67%    | 默认设置，初始训练 |
| 第二次 | 97.4%  | 70.5%  | 学习率 3e-4 → 1e-4 |
| 第三次 | 98.02% | 73.23% | 清洗训练集，移除孑孓、脚印图片等；验证集去除小鼠头骨和高糊图 |
| 第四次 | 96.25% | 67.68% | 冻结轮数 1 → 3，第 6 轮出现峰值，存在过拟合 |
| 第五次 | 88.44% | 73.23% | 冻结轮数 3 → 5；添加 label smoothing、CutMix 和 MixUp |
| 第六次 | 79.69% | 69.19% | 训练轮数 12 → 15，出现提升-平稳-下降趋势；单纯增加训练轮数无明显作用 |
| 第七次 | 83.44% | 70.2%  | 训练轮数 15 → 12, MixUp alpha 0.2 → 0.1, CutMix alpha 1.0 → 0.5 |

## 3. 分类—查询流程
*---此部分相关代码在/predict目录下---*<br><br>
为了实现从输入病媒图片到直接输出前几个识别结果的信息，编写了执行数据库相关操作的API、执行图像分类相关操作的API、以及将其整合的脚本。
### 查询数据库
查询数据库的相关代码在**look_up.py**中。其中的函数/API包括：
 - load_database(): 加载数据库，返回cursor。
 - look_up(): 通过cursor查询物种，返回相关信息。
 - format_db_output(): 整理look_up()返回的信息，返回字符串。
 - main(): 包含了一个样例。

### 进行分类
分类相关代码在**predict.py**中。其中的函数/API包括：
 - load_model(): 加载模型并返回。
 - get_transforms(): 获取transform并返回。
 - predict_one(): 对图片进行预测，返回topk预测。
 - main(): 命令行运行相关代码。

### 整合流程
通过调用前面封装好的API，**workwork.py**可以实现对于给定图片，输入路径后返回识别结果及物种相关信息的操作。

使用：
```bash
python workwork.py <image_path>
```

示例：

<img width="648" height="405" alt="image" src="https://github.com/user-attachments/assets/0001cac1-f56a-4bd7-be26-b167b483d11c" />


## 4. 学习收获
在本项目的推进过程中，我收获了丰富的知识与技能，并在多个方面得到了实质性的成长。

刚开始接触项目时，我通过询问AI、查阅百科资料了解了分类对象为“病媒生物”，明确了任务在机器学习和深度学习范畴中属于计算机视觉领域的图像分类问题。随后，我以“病媒（vector）”、“害虫（pest）”、“机器学习（machine learning）”以及“图像分类（image classification）”为关键词进行文献检索与阅读，梳理了当前领域的技术路线，并撰写了简单的综述。

在技术实现方面，我学习并掌握了使用 PyTorch 进行模型训练的基本方法，最初尝试复现 iNaturalist Competition 2021 冠军团队的方案，但因硬件资源有限，转而选择微调一个预训练的小模型。考虑到模型输出可能存在误差，以及真实应用中用户对物种背景信息的需求，我设计并搭建了一个基于 SQLite 的数据库系统，用于存储物种相关信息，并与分类模型模块衔接，构建了一个“识别—查询”一体化的工作流程。在此过程中，我掌握了 SQL 和 Python 在实际任务中的基本应用能力，并通过编写用于数据收集与处理和后续整合流程的脚本，进一步提升了解决实际问题的编程能力。

此外，在模型训练中我也意识到了数据对于模型质量至关重要的影响。为了对训练数据的质量和可信度进行评估，我还探索了“数据血缘”和“图像可信度”等相关知识，整理成了以下笔记：
 - [数据血缘](https://www.notion.so/Data-Lineage-2347b3784acb8049ba75f0b5319e3cb2?source=copy_link)
 - [图像可信度](https://www.notion.so/2377b3784acb80ac8c77c66c79ede424?source=copy_link)

值得一提的是，在项目推进过程中，我也逐步发掘了自己对某些研究方向的兴趣。例如在阅读 Mora, Camilo 等人关于《How many species are there on Earth and in the ocean?》的论文时，我对其通过回归建模“以已知推未知”的思维方式产生了浓厚兴趣。同时，在学习 SQL 和深度学习的过程中，我对课内所学知识有了更深刻的理解——无论是 SQL 查询优化背后的计算机原理，还是深度学习中所涉及的微积分、统计和线性代数。尤其是在深度学习方面，我逐渐意识到模型的可解释性不仅是一个技术挑战，也是一个极具潜力的研究方向，它可能为我们理解模型决策机制、提高模型透明度、学习新知识带来重要突破。

综上，我在本项目中主要收获了以下三方面能力：
  1. **文献检索与阅读能力**：能够独立开展关键词搜索、阅读文献并整理综述；
  2. **跨学科学习能力**：深入了解了计算机视觉（图像分类）、图像篡改检测、数据血缘、深度学习可解释性等前沿领域；
  3. **技术实践能力提升**：掌握了 SQL、PyTorch 的基本应用，具备了独立完成数据处理、模型训练、数据库搭建和系统整合等工作的能力。
