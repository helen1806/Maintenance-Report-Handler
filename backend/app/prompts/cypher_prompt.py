from langchain_core.prompts import PromptTemplate

# Strict Cypher generation prompt explaining exact ontology directions
CYPHER_GENERATION_TEMPLATE = """Task: Generate Cypher statement to query a graph database.
Instructions:
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.

IMPORTANT ONTOLOGY SEMANTICS:
You MUST follow these exact directional relationships:
- (:MaintenanceReport)-[:DESCRIBES]->(:MaintenanceCase)
  (A MaintenanceReport points TO a MaintenanceCase)
- (:MaintenanceCase)-[:ABOUT]->(:AssetType)
  (A MaintenanceCase points TO an AssetType)
- (:AssetType)-[:HAS]->(:Component)
  (An AssetType points TO a Component)
- (:Component)-[:CAN_EXPERIENCE]->(:FailureMode)
  (A Component points TO a FailureMode)
- (:FailureMode)-[:CAUSED_BY]->(:RootCause)
  (A FailureMode points TO its RootCause. NOT RootCause to FailureMode)
- (:FailureMode)-[:RESOLVED_BY]->(:MaintenanceAction)
  (A FailureMode points TO a MaintenanceAction. NOT MaintenanceAction to FailureMode)

Do NOT reverse these arrows. For example, NEVER do (:RootCause)-[:CAUSED_BY]->(:FailureMode).

Here are some examples of correctly mapping questions to Cypher using this exact ontology:

# 1. Single-hop traversal
# Question: What is the maintenance case described by report ID "RPT-100"?
# Explanation: We start at MaintenanceReport with the given ID and follow DESCRIBES to MaintenanceCase.
# Cypher:
MATCH (r:MaintenanceReport {{report_id: "RPT-100"}})-[:DESCRIBES]->(c:MaintenanceCase)
RETURN c

# 2. Multi-hop traversal
# Question: What failure modes were found on the Air Handling Unit?
# Explanation: We start at AssetType, follow HAS to Component, and CAN_EXPERIENCE to FailureMode.
# Cypher:
MATCH (a:AssetType {{name: "Air Handling Unit"}})-[:HAS]->(c:Component)-[:CAN_EXPERIENCE]->(f:FailureMode)
RETURN f.name

# 3. Reverse relationship traversal
# Question: Which components can experience a "Bearing Failure"?
# Explanation: We start at FailureMode and traverse backward along CAN_EXPERIENCE to find the Component.
# Cypher:
MATCH (c:Component)-[:CAN_EXPERIENCE]->(f:FailureMode {{name: "Bearing Failure"}})
RETURN c.name

# 4. Root cause lookup
# Question: What caused the "Vibration" failure mode?
# Explanation: We match the FailureMode and follow the PROVIDED direction of CAUSED_BY to the RootCause.
# Cypher:
MATCH (f:FailureMode {{name: "Vibration"}})-[:CAUSED_BY]->(r:RootCause)
RETURN r.name

# 5. Maintenance action lookup
# Question: How do we fix a "Refrigerant Leak"?
# Explanation: We match the FailureMode and follow RESOLVED_BY to the MaintenanceAction.
# Cypher:
MATCH (f:FailureMode {{name: "Refrigerant Leak"}})-[:RESOLVED_BY]->(m:MaintenanceAction)
RETURN m.name

# 6. Component lookup
# Question: List all components of a Chiller.
# Explanation: We match AssetType "Chiller" and follow HAS to Component.
# Cypher:
MATCH (a:AssetType {{name: "Chiller"}})-[:HAS]->(c:Component)
RETURN c.name

# 7. Asset type lookup
# Question: Which assets have a "Compressor" component?
# Explanation: We traverse backward from Component "Compressor" via HAS to AssetType.
# Cypher:
MATCH (a:AssetType)-[:HAS]->(c:Component {{name: "Compressor"}})
RETURN a.name

# 8. Maintenance report summarization
# Question: Summarize the complaints found in report "RPT-100".
# Explanation: We match the MaintenanceReport by ID, traverse to MaintenanceCase, and return the complaint_text.
# Cypher:
MATCH (r:MaintenanceReport {{report_id: "RPT-100"}})-[:DESCRIBES]->(c:MaintenanceCase)
RETURN c.complaint_text

# 9. Ambiguous natural-language questions
# Question: Show me the problems with the boiler.
# Explanation: "Problems" maps to FailureMode, and "boiler" maps to AssetType. We must traverse AssetType -> Component -> FailureMode.
# Cypher:
MATCH (a:AssetType {{name: "Boiler"}})-[:HAS]->(c:Component)-[:CAN_EXPERIENCE]->(f:FailureMode)
RETURN f.name

# 10. Synonym-based questions
# Question: What is the solution for "Sensor Malfunction"?
# Explanation: "Solution" maps to MaintenanceAction, which is RESOLVED_BY from FailureMode.
# Cypher:
MATCH (f:FailureMode {{name: "Sensor Malfunction"}})-[:RESOLVED_BY]->(m:MaintenanceAction)
RETURN m.name

Schema:
{schema}

Question: {question}
"""

CUSTOM_CYPHER_PROMPT = PromptTemplate(
    input_variables=["schema", "question"],
    template=CYPHER_GENERATION_TEMPLATE
)
