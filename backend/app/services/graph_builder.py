from dataclasses import dataclass, field
from typing import Dict, List

from app.models.maintenance_schema import MaintenanceExtraction
import uuid


# ==========================
# Graph Domain Models
# ==========================

@dataclass
class Node:
    label: str
    properties: Dict


@dataclass
class Relationship:
    start_node: Node
    relationship_type: str
    end_node: Node


@dataclass
class Graph:
    nodes: List[Node] = field(default_factory=list)
    relationships: List[Relationship] = field(default_factory=list)



class GraphBuilder:

    def build_graph(self, extraction: MaintenanceExtraction, filename: str, file_hash: str) -> Graph:

        graph = Graph()
        report_id = str(uuid.uuid4())
        case_id = str(uuid.uuid4())
      
        # Core Nodes (Always created per file)
        report_node = self._build_maintenance_report(report_id, filename, file_hash)
        case_node = self._build_maintenance_case(case_id)
        graph.nodes.extend([report_node, case_node])

        # Core Relationship
        graph.relationships.append(Relationship(
            start_node=report_node,
            relationship_type="DESCRIBES",
            end_node=case_node
        ))

        # Optional Domain Nodes
        asset_type_node = self._build_asset_type(extraction.asset_type) if extraction.asset_type else None
        component_node = self._build_component(extraction.component) if extraction.component else None
        failure_mode_node = self._build_failure_mode(extraction.failure_mode) if extraction.failure_mode else None
        root_cause_node = self._build_root_cause(extraction.root_cause) if extraction.root_cause else None
        maintenance_action_node = self._build_maintenance_action(extraction.maintenance_action) if extraction.maintenance_action else None

        # Add nodes if they exist
        for node in [asset_type_node, component_node, failure_mode_node, root_cause_node, maintenance_action_node]:
            if node:
                graph.nodes.append(node)

        # Build relationships conditionally
        if case_node and asset_type_node:
            graph.relationships.append(Relationship(case_node, "ABOUT", asset_type_node))
        
        if asset_type_node and component_node:
            graph.relationships.append(Relationship(asset_type_node, "HAS", component_node))

        if component_node and failure_mode_node:
            graph.relationships.append(Relationship(component_node, "CAN_EXPERIENCE", failure_mode_node))

        if failure_mode_node and root_cause_node:
            graph.relationships.append(Relationship(failure_mode_node, "CAUSED_BY", root_cause_node))

        if failure_mode_node and maintenance_action_node:
            graph.relationships.append(Relationship(failure_mode_node, "RESOLVED_BY", maintenance_action_node))

        return graph

    def _build_asset_type(self, asset_type: str) -> Node:

        return Node(
            label="AssetType",
            properties={
                "name": asset_type
            }
        )

    def _build_component(self, component: str) -> Node:

        return Node(
            label="Component",
            properties={
                "name": component
            }
        )

    def _build_failure_mode(self, failure_mode: str) -> Node:

        return Node(
            label="FailureMode",
            properties={
                "name": failure_mode
            }
        )

    def _build_root_cause(self, root_cause: str) -> Node:

        return Node(
            label="RootCause",
            properties={
                "name": root_cause
            }
        )

    def _build_maintenance_action(self, action: str) -> Node:

        return Node(
            label="MaintenanceAction",
            properties={
                "name": action
            }
        )

    def _build_maintenance_report(self, report_id: str, filename: str, file_hash: str) -> Node:

        return Node(
            label="MaintenanceReport",
            properties={
                "report_id": report_id,
                "file_name": filename,
                "file_hash": file_hash,
                "file_url": "UNKNOWN_URL"
            }
        )

    def _build_maintenance_case(self, case_id: str) -> Node:

        return Node(
            label="MaintenanceCase",
            properties={
                "case_id": case_id,
                "complaint_text": "UNKNOWN_TEXT"
            }
        )