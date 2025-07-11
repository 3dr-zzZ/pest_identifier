CREATE TABLE "species" (
    "id"                INTEGER,
    "scientific_name"   TEXT,  -- 物种学名
    "chinese_name"      TEXT,  -- 物种中文学名
    "other_name"        TEXT,  -- 物种中文俗名
    "traits"            TEXT,  -- 物种鉴别特征
    PRIMARY KEY("id")
);

CREATE TABLE "taxonomies" (
    "id"            INTEGER,
    "name"          TEXT UNIQUE,
    "chinese_name"  TEXT UNIQUE,
    "type"          NOT NULL CHECK("type" IN ('phylum', 'class', 'order', 'family', 'genus')),
    PRIMARY KEY("id")
);

CREATE TABLE "diseases" (
    "id"        INTEGER,
    "name"      TEXT UNIQUE,
    "symptoms"  TEXT,  -- 疾病症状
    PRIMARY KEY("id")
);

CREATE TABLE "locations" (
    "id"       INTEGER,
    "name"     TEXT UNIQUE,
    "type"     TEXT NOT NULL CHECK("type" IN ('province', 'country', 'region')),
    PRIMARY KEY("id")
);

CREATE TABLE "references" (
    "id"        INTEGER PRIMARY KEY,
    "citation"  TEXT,
    "url"       TEXT,
    "year"      INTEGER
);

CREATE TABLE "medias" (
    "id"          INTEGER PRIMARY KEY,
    "species_id"  INTEGER NOT NULL,
    "media_path"  TEXT NOT NULL UNIQUE,
    "media_type"  TEXT NOT NULL CHECK ("media_type" IN ('image','audio','video')),
    "license"     TEXT,
    "source"      TEXT,
    FOREIGN KEY (species_id) REFERENCES species(id) ON DELETE CASCADE
);


-- Joint tables
CREATE TABLE "belongs"(
    "species_id"  INTEGER,
    "taxonomy_id" INTEGER,
    PRIMARY KEY("species_id", "taxonomy_id"),
    FOREIGN KEY("species_id") REFERENCES "species"("id") ON DELETE CASCADE,
    FOREIGN KEY("taxonomy_id") REFERENCES "taxonomies"("id") ON DELETE CASCADE
);

CREATE TABLE "distributed"(
    "species_id"  INTEGER,
    "location_id" INTEGER,
    PRIMARY KEY("species_id", "location_id"),
    FOREIGN KEY("species_id") REFERENCES "species"("id") ON DELETE CASCADE,
    FOREIGN KEY("location_id") REFERENCES "locations"("id") ON DELETE CASCADE
);

CREATE TABLE "carries"(
    "species_id" INTEGER,
    "disease_id" INTEGER,
    PRIMARY KEY("species_id", "disease_id"),
    FOREIGN KEY("species_id") REFERENCES "species"("id") ON DELETE CASCADE,
    FOREIGN KEY("disease_id") REFERENCES "diseases"("id")ON DELETE CASCADE
);


CREATE TABLE "species_reference" (
    "species_id"    INTEGER,
    "reference_id"  INTEGER,
    "note"          TEXT,
    PRIMARY KEY ("species_id", "reference_id"),
    FOREIGN KEY ("species_id") REFERENCES "species"("id") ON DELETE CASCADE,
    FOREIGN KEY ("reference_id") REFERENCES "references"("id") ON DELETE CASCADE
);
