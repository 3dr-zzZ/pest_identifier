CREATE TABLE "species" (
    "id" INTEGER
    "english_name" TEXT  -- 物种英文学名
    "chinese_name"  TEXT  -- 物种中文学名
    "common_name"  TEXT  -- 物种中文俗名
    "distribution"  TEXT  -- 物种地理分布
    "hazards" TEXT  -- 物种可能导致的疾病/危害
    "traits" TEXT  -- 物种鉴别特征
    PRIMARY KEY("id")
)

CREATE TABLE "images" (
    "id" INTEGER
    "width" INTEGER -- 图片像素宽
    "height" INTEGER  -- 图片像素高
    "file_name" TEXT UNIQUE  -- 路径
    "date" NUMERIC  -- 拍摄日期
    "latitude" REAL  -- 纬度
    "longitude" REAL  -- 经度
    "location_uncertainty" INTEGER
    PRIMARY KEY("id")
)

CREATE TABLE "includes"(
    "species_id"
    "image_id"
    FOREIGN KEY("species_id") FROM "species"."id"
    FOREIGN KEY("image_id") FROM "images"."id"
)
