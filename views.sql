-- Convenience views for db/project-phaistos.sqlite (applied by build/build.sh)

DROP VIEW IF EXISTS forms_readable;
CREATE VIEW forms_readable AS
SELECT f.cldf_id AS form_id,
       l.cldf_id AS language_id,
       l.cldf_name AS language,
       l.Role AS role,
       p.cldf_id AS concept_id,
       p.cldf_name AS concept,
       f.cldf_value AS original,
       f.cldf_form AS form,
       f.cldf_segments AS segments,
       f.Muskogean_Residue AS muskogean_residue,
       f.Strict_Residue AS strict_residue,
       f.Loose_Mapping AS loose_mapping,
       f.cldf_comment AS comment,
       (SELECT group_concat(fs.SourceTable_id || CASE WHEN fs.context <> '' THEN '[' || fs.context || ']' ELSE '' END, '; ')
          FROM FormTable_SourceTable fs WHERE fs.FormTable_cldf_id = f.cldf_id) AS source
FROM FormTable f
JOIN LanguageTable l ON l.cldf_id = f.cldf_languageReference
JOIN ParameterTable p ON p.cldf_id = f.cldf_parameterReference;

-- Timucua plus the Southeastern lists, one row per form
DROP VIEW IF EXISTS southeast_forms;
CREATE VIEW southeast_forms AS
SELECT * FROM forms_readable
WHERE language_id IN ('TIMUCUA', 'MIKASUKI', 'HITCHITI_1884', 'HITCHITI_1937', 'CREEK', 'ALABAMA', 'KOASATI',
                      'APALACHEE', 'CHOCTAW', 'CHICKASAW', 'PROTO_MUSKOGEAN');

-- Per-concept similarity of each Southeastern list to Timucua
DROP VIEW IF EXISTS timucua_vs_southeast;
CREATE VIEW timucua_vs_southeast AS
SELECT p.cldf_name AS concept,
       l.cldf_name AS language,
       c.Form AS form,
       c.Timucua_Form AS timucua_form,
       c.SCA AS sca, c.NED AS ned, c.TPG AS tpg,
       c.Rank_SCA AS rank_among_timucua_concepts,
       c.N_Timucua_Concepts AS n_timucua_concepts,
       c.P_Candidate AS p_candidate,
       f.Muskogean_Residue AS form_is_muskogean_residue,
       c.Analysis_Status AS analysis_status
FROM "comparisons.csv" c
JOIN LanguageTable l ON l.cldf_id = c.cldf_languageReference
JOIN ParameterTable p ON p.cldf_id = c.cldf_parameterReference
JOIN FormTable f ON f.cldf_id = c.cldf_formReference;

-- Cognate sets from the frozen Stage 2 run and the Hitchiti addendum run
DROP VIEW IF EXISTS cognate_sets;
CREATE VIEW cognate_sets AS
SELECT ct.cldf_cognatesetReference AS cognateset_id,
       ct.Method AS method,
       ct.Run AS run,
       p.cldf_name AS concept,
       count(*) AS n_forms,
       group_concat(f.cldf_languageReference || ':' || f.cldf_form, ', ') AS members
FROM CognateTable ct
JOIN FormTable f ON f.cldf_id = ct.cldf_formReference
JOIN ParameterTable p ON p.cldf_id = f.cldf_parameterReference
GROUP BY ct.cldf_cognatesetReference, ct.Method, ct.Run, p.cldf_name;

-- Every aggregate test, calibration run and verdict
DROP VIEW IF EXISTS test_results;
CREATE VIEW test_results AS
SELECT cldf_id AS test, Hypothesis AS hypothesis, Recipient AS recipient, Donor AS donor,
       Concept_Set AS concept_set, Measure AS measure, N_Items AS n_items,
       Delta_S AS delta_s, Z AS z, P_Perm AS p_perm, P_Max AS p_max, Verdict AS verdict, Status AS status
FROM "tests.csv";
