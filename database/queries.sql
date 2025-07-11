-- to see what species are included in the database, use:
SELECT scientific_name FROM species;

-- to access a species' information, use:
SELECT chinese_name, other_name, traits FROM species
WHERE scientific_name = 'Aedes albopictus';

-- to access a species' distributed locations, use:
SELECT locations.name, locations.type FROM species
JOIN distributed ON species.id = distributed.species_id
JOIN locations ON distributed.location_id = locations.id
WHERE scientific_name = 'Aedes albopictus';

-- to access a species' taxonomy, use:
SELECT taxonomies.name, taxonomies.chinese_name, taxonomies.type FROM species
JOIN belongs ON species.id = belongs.species_id
JOIN taxonomies ON belongs.taxonomy_id = taxonomies.id
WHERE scientific_name = 'Aedes albopictus';

-- to access a species' diseases carried, use:
SELECT diseases.name FROM species
JOIN carries ON species.id = carries.species_id
JOIN diseases ON carries.disease_id = diseases.id
WHERE scientific_name = 'Aedes albopictus';
