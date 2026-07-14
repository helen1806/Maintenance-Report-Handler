from dataclasses import dataclass, field
from typing import Dict, List

from app.models import MaintenanceExtraction


# ==========================
# Graph Domain Models
# ==========================

@dataclass
class Node:
    label: str
    properties: Dict


@dataclass
class Relationship:
    start_label: str
    relationship_type: str
    end_label: str


@dataclass
class Graph:
    nodes: List[Node] = field(default_factory=list)
    relationships: List[Relationship] = field(default_factory=list)


# ==========================
# Graph Builder
# ==========================

class GraphBuilder:

    def build_graph(self, extraction: MaintenanceExtraction) -> Graph:

        graph = Graph()

        # ---------- Nodes ----------

        graph.nodes.append(self._build_asset_type(extraction.asset_type))
        graph.nodes.append(self._build_component(extraction.component))
        graph.nodes.append(self._build_failure_mode(extraction.failure_mode))
        graph.nodes.append(self._build_root_cause(extraction.root_cause))
        graph.nodes.append(self._build_maintenance_action(extraction.maintenance_action))

        # These values will be populated later.
        graph.nodes.append(self._build_maintenance_report())
        graph.nodes.append(self._build_maintenance_case())

        # ---------- Relationships ----------

        graph.relationships.extend(self._build_relationships())

        return graph

    # ==========================
    # Node Builders
    # ==========================

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

    def _build_maintenance_report(self) -> Node:

        return Node(
            label="MaintenanceReport",
            properties={
                "report_id": None,
                "file_name": None,
                "file_url": None
            }
        )

    def _build_maintenance_case(self) -> Node:

        return Node(
            label="MaintenanceCase",
            properties={
                "case_id": None,
                "complaint_text": None
            }
        )

    # ==========================
    # Relationship Builder
    # ==========================

    def _build_relationships(self) -> List[Relationship]:

        return [

            Relationship(
                start_label="MaintenanceReport",
                relationship_type="DESCRIBES",
                end_label="MaintenanceCase"
            ),

            Relationship(
                start_label="MaintenanceCase",
                relationship_type="ABOUT",
                end_label="AssetType"
            ),

            Relationship(
                start_label="AssetType",
                relationship_type="HAS",
                end_label="Component"
            ),

            Relationship(
                start_label="Component",
                relationship_type="CAN_EXPERIENCE",
                end_label="FailureMode"
            ),

            Relationship(
                start_label="FailureMode",
                relationship_type="CAUSED_BY",
                end_label="RootCause"
            ),

            Relationship(
                start_label="FailureMode",
                relationship_type="RESOLVED_BY",
                end_label="MaintenanceAction"
            )
        ]