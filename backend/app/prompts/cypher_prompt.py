from langchain_core.prompts import PromptTemplate

# Strict Cypher generation prompt explaining exact ontology directions and property keys
CYPHER_GENERATION_TEMPLATE = """Task: Generate Cypher statement to query a graph database.
Instructions:
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.

CRITICAL ONTOLOGY STRUCTURE:
1. Node Labels & Their Properties:
   - (:MaintenanceReport) properties: report_id, file_name, file_hash, file_url
   - (:MaintenanceCase) properties: case_id, complaint_text
   - (:AssetType) properties: name  (e.g., "pump", "centrifugal pump", "chiller", "boiler", "air compressor", "belt conveyor")
   - (:Component) properties: name  (e.g., "drive-end bearing", "impeller", "shaft", "valve", "filter")
   - (:FailureMode) properties: name (e.g., "bearing wear", "vibration", "leakage", "corrosion", "overheating")
   - (:RootCause) properties: name   (e.g., "insufficient lubrication", "fatigue", "contamination")
   - (:MaintenanceAction) properties: name (e.g., "replace bearing", "re-grease", "alignment check")

2. Equipment vs Components:
   - Machines / equipment like "pump", "compressor", "chiller", "conveyor", "boiler" are ALWAYS (:AssetType), NEVER Component!
   - Specific parts like "bearing", "seal", "impeller", "motor", "pipe" are (:Component).

3. Exact Directional Relationships (NEVER reverse arrows):
   - (:MaintenanceReport)-[:DESCRIBES]->(:MaintenanceCase)
   - (:MaintenanceCase)-[:ABOUT]->(:AssetType)
   - (:AssetType)-[:HAS]->(:Component)
   - (:Component)-[:CAN_EXPERIENCE]->(:FailureMode)
   - (:FailureMode)-[:CAUSED_BY]->(:RootCause)
   - (:FailureMode)-[:RESOLVED_BY]->(:MaintenanceAction)

4. Case IDs and UUIDs:
   - When the user asks about a specific ID (e.g., "5f9b6fe0-9ada-4fff-a1fe-b19edd706806"), this is a (:MaintenanceCase) with property `case_id`, NOT report_id!
   - To match a case ID: `MATCH (c:MaintenanceCase) WHERE c.case_id = "..."` or `MATCH (c:MaintenanceCase {{case_id: "..."}})`

5. Describing Cases:
   - `MaintenanceCase` nodes do not have long text descriptions; to describe a case, traverse to its connected `AssetType`, `Component`, `FailureMode`, `RootCause`, and `MaintenanceAction` using OPTIONAL MATCH.

6. String Matching Rules:
   - ALWAYS use case-insensitive substring matching for names: `WHERE toLower(node.name) CONTAINS toLower("...")`.
   - Remove articles ("a", "an", "the"). If the question says "a pump", search for "pump".

Here are some examples of correctly mapping questions to Cypher using this exact ontology:

# Example 1: Finding cases related to an asset / machine
# Question: Is there any case reported related to a pump? / What cases are reported for the pump?
# Explanation: "pump" is an AssetType. We match MaintenanceCase pointing via ABOUT to AssetType.
MATCH (c:MaintenanceCase)-[:ABOUT]->(a:AssetType)
WHERE toLower(a.name) CONTAINS toLower("pump")
RETURN DISTINCT c.case_id AS case_id, a.name AS asset

# Example 2: Describing a specific case ID / UUID
# Question: What is 5f9b6fe0-9ada-4fff-a1fe-b19edd706806 about? / Describe case 5f9b6fe0...
# Explanation: Match MaintenanceCase by case_id and traverse to its connected AssetType, Component, FailureMode, etc.
MATCH (c:MaintenanceCase {{case_id: "5f9b6fe0-9ada-4fff-a1fe-b19edd706806"}})-[:ABOUT]->(a:AssetType)
OPTIONAL MATCH (a)-[:HAS]->(comp:Component)
OPTIONAL MATCH (comp)-[:CAN_EXPERIENCE]->(f:FailureMode)
OPTIONAL MATCH (f)-[:CAUSED_BY]->(r:RootCause)
OPTIONAL MATCH (f)-[:RESOLVED_BY]->(m:MaintenanceAction)
RETURN c.case_id AS case_id, a.name AS asset, comp.name AS component, f.name AS failure_mode, r.name AS root_cause, m.name AS action

# Example 3: Describing all reported cases
# Question: Describe the reported maintenance cases / Describe them
# Explanation: Retrieve cases along with their assets, components, failure modes, and actions.
MATCH (c:MaintenanceCase)-[:ABOUT]->(a:AssetType)
OPTIONAL MATCH (a)-[:HAS]->(comp:Component)
OPTIONAL MATCH (comp)-[:CAN_EXPERIENCE]->(f:FailureMode)
OPTIONAL MATCH (f)-[:CAUSED_BY]->(r:RootCause)
OPTIONAL MATCH (f)-[:RESOLVED_BY]->(m:MaintenanceAction)
RETURN c.case_id AS case_id, a.name AS asset, comp.name AS component, f.name AS failure_mode, r.name AS root_cause, m.name AS action

# Example 4: Components of an asset
# Question: What components does the pump have? / List components of the pump
# Explanation: "pump" is AssetType. Follow HAS to Component.
MATCH (a:AssetType)-[:HAS]->(c:Component)
WHERE toLower(a.name) CONTAINS toLower("pump")
RETURN c.name AS component

# Example 5: Failures on an asset
# Question: What failure modes were found on the pump? / What can go wrong with the pump?
# Explanation: AssetType -> Component -> FailureMode.
MATCH (a:AssetType)-[:HAS]->(c:Component)-[:CAN_EXPERIENCE]->(f:FailureMode)
WHERE toLower(a.name) CONTAINS toLower("pump")
RETURN f.name AS failure_mode, c.name AS component

# Example 6: Root cause lookup
# Question: What caused the bearing wear? / Why did the bearing fail?
# Explanation: FailureMode points to RootCause via CAUSED_BY.
MATCH (f:FailureMode)-[:CAUSED_BY]->(r:RootCause)
WHERE toLower(f.name) CONTAINS toLower("bearing wear")
RETURN r.name AS root_cause

# Example 7: Maintenance action / solution lookup
# Question: How do we fix bearing wear? / What is the solution for bearing wear?
# Explanation: FailureMode points to MaintenanceAction via RESOLVED_BY.
MATCH (f:FailureMode)-[:RESOLVED_BY]->(m:MaintenanceAction)
WHERE toLower(f.name) CONTAINS toLower("bearing wear")
RETURN m.name AS maintenance_action

# Example 8: All maintenance cases
# Question: What are the maintenance cases reported? / List all cases
MATCH (c:MaintenanceCase)-[:ABOUT]->(a:AssetType)
RETURN c.case_id AS case_id, a.name AS asset

# Example 9: Report lookup by report ID
# Question: What report describes report ID "RPT-100"?
MATCH (r:MaintenanceReport {{report_id: "RPT-100"}})-[:DESCRIBES]->(c:MaintenanceCase)-[:ABOUT]->(a:AssetType)
RETURN r.file_name AS file_name, c.case_id AS case_id, a.name AS asset

Schema:
{schema}

Question: {question}
"""

CUSTOM_CYPHER_PROMPT = PromptTemplate(
    input_variables=["schema", "question"],
    template=CYPHER_GENERATION_TEMPLATE
)

