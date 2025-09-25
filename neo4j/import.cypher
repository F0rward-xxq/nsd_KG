// Create constraints
CREATE CONSTRAINT disease_id_unique IF NOT EXISTS
FOR (d:Disease) REQUIRE d.id IS UNIQUE;

// Load nodes
USING PERIODIC COMMIT 1000
LOAD CSV WITH HEADERS FROM 'file:///nodes.csv' AS row
MERGE (d:Disease {id: row.`id:ID`})
SET d.name = row.name,
    d.entry_url = row.entry_url,
    d.overview = row.overview,
    d.cause = row.cause,
    d.prevent = row.prevent,
    d.symptom = row.symptom,
    d.inspect = row.inspect,
    d.diagnosis = row.diagnosis,
    d.treat = row.treat,
    d.nursing = row.nursing,
    d.food = row.food;

// Load relationships (comorbid diseases)
USING PERIODIC COMMIT 1000
LOAD CSV WITH HEADERS FROM 'file:///relations.csv' AS row
MATCH (s:Disease {id: row.`:START_ID`})
MATCH (t:Disease {id: row.`:END_ID`})
MERGE (s)-[r:COMORBID_WITH]->(t);
