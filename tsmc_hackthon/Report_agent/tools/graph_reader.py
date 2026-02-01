"""
Supply Chain Graph Reader Tool

This module provides functions to read and query the supply chain graph
from supply_chain_graph.json.
"""

import json
from typing import Dict, List, Optional
from pathlib import Path


# Load the supply chain graph at module level
_GRAPH_PATH = Path(__file__).parent.parent / "supply_chain_graph.json"
_graph_data: Optional[Dict] = None


def _load_graph() -> Dict:
    """Load the supply chain graph from JSON file."""
    global _graph_data
    if _graph_data is None:
        with open(_GRAPH_PATH, "r", encoding="utf-8") as f:
            _graph_data = json.load(f)
    return _graph_data


def get_node_by_id(node_id: str) -> Optional[Dict]:
    """
    Get a node (company) by its ID.
    
    Args:
        node_id: The company ID (e.g., "2330", "AAPL")
    
    Returns:
        Node dict with id, name, country, category, role, tags, or None if not found.
    """
    graph = _load_graph()
    for node in graph.get("nodes", []):
        if node.get("id") == node_id:
            return node
    return None


def get_node_by_name(name: str) -> Optional[Dict]:
    """
    Get a node (company) by its name (case-insensitive).
    
    Args:
        name: The company name (e.g., "TSMC", "Apple")
    
    Returns:
        Node dict or None if not found.
    """
    graph = _load_graph()
    name_lower = name.lower()
    for node in graph.get("nodes", []):
        if node.get("name", "").lower() == name_lower:
            return node
    return None


def get_related_companies(company_id: str) -> Dict[str, List[Dict]]:
    """
    Get all companies related to the target company.
    
    Args:
        company_id: The target company ID
    
    Returns:
        Dict with 'customers', 'suppliers', 'partners' lists, each containing
        company info and relationship details.
    """
    graph = _load_graph()
    edges = graph.get("edges", [])
    nodes = {node["id"]: node for node in graph.get("nodes", [])}
    
    result = {
        "customers": [],
        "suppliers": [],
        "partners": [],
        "competitors": []
    }
    
    for edge in edges:
        source_id = edge.get("source")
        target_id = edge.get("target")
        relation = edge.get("relation", "")
        description = edge.get("description", "")
        
        # Check if target company is involved in this edge
        if target_id == company_id:
            # Source is connected TO target
            source_node = nodes.get(source_id, {})
            if relation == "Client":
                result["customers"].append({
                    **source_node,
                    "relationship_description": description
                })
            elif relation == "Supplier":
                result["suppliers"].append({
                    **source_node,
                    "relationship_description": description
                })
            elif relation == "Partner":
                result["partners"].append({
                    **source_node,
                    "relationship_description": description
                })
        
        elif source_id == company_id:
            # Target is connected FROM source
            target_node = nodes.get(target_id, {})
            if relation == "Partner":
                result["partners"].append({
                    **target_node,
                    "relationship_description": description
                })
    
    # Get competitors from nodes with role="Competitor" in same category
    target_node = nodes.get(company_id, {})
    target_category = target_node.get("category", "")
    
    for node in graph.get("nodes", []):
        if node.get("id") != company_id and node.get("role") == "Competitor":
            if node.get("category") == target_category:
                result["competitors"].append(node)
    
    return result


def get_nodes_by_role(role: str) -> List[Dict]:
    """
    Get all nodes with a specific role.
    
    Args:
        role: One of "Customer", "Supplier", "Partner", "Competitor", "Self"
    
    Returns:
        List of node dicts matching the role.
    """
    graph = _load_graph()
    return [node for node in graph.get("nodes", []) if node.get("role") == role]


def get_all_customers() -> List[Dict]:
    """Get all customer nodes."""
    return get_nodes_by_role("Customer")


def get_all_suppliers() -> List[Dict]:
    """Get all supplier nodes."""
    return get_nodes_by_role("Supplier")
