UPDATE core_article SET introduction = '' WHERE id = 141;

create sequence core_reference_tags_id_seq;
SELECT setval('core_reference_tags_id_seq', (SELECT MAX(id) FROM core_reference_tags)+1);

ALTER TABLE "core_reference_tags"
ALTER "id" TYPE integer,
ALTER "id" SET DEFAULT nextval('public.core_reference_tags_id_seq'),
ALTER "id" SET NOT NULL;

SELECT setval('core_tag_id_seq', (SELECT MAX(id) FROM core_tag)+1);

delete from multiplicity_graphtype where id = 1;

UPDATE staf_material SET parent_id = 970921 WHERE id = 971057;

SELECT setval('core_organization_id_seq', (SELECT MAX(id) FROM core_organization)+1);
SELECT setval('multiplicity_datasettypestructure_id_seq', (SELECT MAX(id) FROM multiplicity_datasettypestructure)+1);
SELECT setval('multiplicity_datasettype_id_seq', (SELECT MAX(id) FROM multiplicity_datasettype)+1);

INSERT INTO "core_useraction" ("id", "name") VALUES ('5', 'Data imported');

UPDATE staf_material SET code = CONCAT('HS',code) WHERE catalog_id = 1 AND parent_id != 970753;
