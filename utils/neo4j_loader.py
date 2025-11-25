#!/usr/bin/env python3
"""
Neo4j Graph Loader
Loads knowledge graphs from output/graphs/{dataset_name}_new.json into Neo4j database
"""
import json
import os
from typing import Dict, List, Optional
from neo4j import GraphDatabase
from utils.logger import logger


class Neo4jLoader:
    """Load knowledge graphs into Neo4j database"""
    
    def __init__(self, uri: str, user: str, password: str, database: str = "neo4j"):
        """
        Initialize Neo4j connection
        
        Args:
            uri: Neo4j connection URI (e.g., bolt://localhost:7687)
            user: Neo4j username
            password: Neo4j password
            database: Neo4j database name (default: neo4j)
        """
        self.uri = uri
        self.user = user
        self.password = password
        self.database = database
        self.driver = None
        
    def connect(self):
        """Establish connection to Neo4j"""
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            # Test connection
            with self.driver.session(database=self.database) as session:
                session.run("RETURN 1")
            logger.info(f"✅ Connected to Neo4j at {self.uri}, database: {self.database}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to Neo4j: {e}")
            return False
    
    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")
    
    def clear_graph(self, dataset_name: str):
        """Clear existing graph data for a dataset"""
        if not self.driver:
            raise RuntimeError("Neo4j driver not initialized. Call connect() first.")
        
        try:
            with self.driver.session(database=self.database) as session:
                # Delete all nodes and relationships with dataset label
                session.run(
                    "MATCH (n {dataset: $dataset}) DETACH DELETE n",
                    dataset=dataset_name
                )
            logger.info(f"Cleared existing graph data for dataset: {dataset_name}")
        except Exception as e:
            logger.error(f"Error clearing graph: {e}")
            raise
    
    def load_graph_from_json(self, graph_path: str, dataset_name: str, clear_existing: bool = True) -> Dict:
        """
        Load graph from JSON file into Neo4j
        
        Args:
            graph_path: Path to the graph JSON file
            dataset_name: Name of the dataset
            clear_existing: Whether to clear existing data for this dataset
            
        Returns:
            Dict with stats: nodes_created, relationships_created
        """
        if not self.driver:
            raise RuntimeError("Neo4j driver not initialized. Call connect() first.")
        
        if not os.path.exists(graph_path):
            raise FileNotFoundError(f"Graph file not found: {graph_path}")
        
        # Load JSON
        with open(graph_path, 'r', encoding='utf-8') as f:
            graph_data = json.load(f)
        
        # Clear existing data if requested
        if clear_existing:
            self.clear_graph(dataset_name)
        
        # Detect format and load
        if isinstance(graph_data, list):
            return self._load_relationship_list_format(graph_data, dataset_name)
        elif isinstance(graph_data, dict) and "nodes" in graph_data:
            return self._load_standard_format(graph_data, dataset_name)
        else:
            raise ValueError(f"Unknown graph format in {graph_path}")
    
    def _load_relationship_list_format(self, graph_data: List[Dict], dataset_name: str) -> Dict:
        """
        Load GraphRAG format: list of relationships with start_node/end_node/relation
        
        Format:
        [
          {
            "start_node": {"label": "entity", "properties": {"name": "A", "schema_type": "person"}},
            "end_node": {"label": "entity", "properties": {"name": "B", "schema_type": "location"}},
            "relation": "located_in"
          },
          ...
        ]
        """
        nodes_created = 0
        relationships_created = 0
        
        logger.info(f"Loading {len(graph_data)} relationships from GraphRAG format...")
        
        with self.driver.session(database=self.database) as session:
            for item in graph_data:
                if not isinstance(item, dict):
                    continue
                
                start_node = item.get("start_node", {})
                end_node = item.get("end_node", {})
                relation = item.get("relation", "RELATED_TO")
                
                # Extract node info
                start_props = start_node.get("properties", {})
                end_props = end_node.get("properties", {})
                
                start_name = start_props.get("name", "")
                end_name = end_props.get("name", "")
                
                if not start_name or not end_name:
                    continue
                
                # Get node types
                start_type = start_props.get("schema_type", start_node.get("label", "Entity"))
                end_type = end_props.get("schema_type", end_node.get("label", "Entity"))
                
                # Create nodes and relationship
                try:
                    result = session.run(
                        """
                        MERGE (a:Entity {name: $start_name, dataset: $dataset})
                        ON CREATE SET a.type = $start_type, a += $start_props
                        ON MATCH SET a += $start_props
                        MERGE (b:Entity {name: $end_name, dataset: $dataset})
                        ON CREATE SET b.type = $end_type, b += $end_props
                        ON MATCH SET b += $end_props
                        MERGE (a)-[r:RELATES {type: $relation, dataset: $dataset}]->(b)
                        RETURN a, b, r
                        """,
                        start_name=start_name,
                        end_name=end_name,
                        dataset=dataset_name,
                        start_type=start_type,
                        end_type=end_type,
                        start_props=start_props,
                        end_props=end_props,
                        relation=relation
                    )
                    
                    if result.peek():
                        nodes_created += 2  # approximation (may be merged)
                        relationships_created += 1
                        
                except Exception as e:
                    logger.warning(f"Error creating relationship: {e}")
                    continue
        
        logger.info(f"✅ Loaded graph: ~{nodes_created} nodes, {relationships_created} relationships")
        return {
            "nodes_created": nodes_created,
            "relationships_created": relationships_created,
            "format": "relationship_list"
        }
    
    def _load_standard_format(self, graph_data: Dict, dataset_name: str) -> Dict:
        """
        Load standard format: {nodes: [...], edges: [...]}
        
        Format:
        {
          "nodes": [
            {"id": "1", "name": "Alice", "type": "person", "attributes": [...]},
            ...
          ],
          "edges": [
            {"source": "1", "target": "2", "relation": "knows", "weight": 1.0},
            ...
          ]
        }
        """
        nodes = graph_data.get("nodes", [])
        edges = graph_data.get("edges", [])
        
        logger.info(f"Loading {len(nodes)} nodes and {len(edges)} edges from standard format...")
        
        nodes_created = 0
        relationships_created = 0
        
        with self.driver.session(database=self.database) as session:
            # Create nodes
            for node in nodes:
                node_id = node.get("id", "")
                name = node.get("name", node_id)
                node_type = node.get("type", "Entity")
                attributes = node.get("attributes", [])
                
                if not node_id:
                    continue
                
                try:
                    session.run(
                        """
                        MERGE (n:Entity {id: $id, dataset: $dataset})
                        SET n.name = $name, n.type = $type, n.attributes = $attributes
                        """,
                        id=node_id,
                        name=name,
                        type=node_type,
                        attributes=attributes,
                        dataset=dataset_name
                    )
                    nodes_created += 1
                except Exception as e:
                    logger.warning(f"Error creating node {node_id}: {e}")
                    continue
            
            # Create relationships
            for edge in edges:
                source = edge.get("source", "")
                target = edge.get("target", "")
                relation = edge.get("relation", "RELATED_TO")
                weight = edge.get("weight", 1.0)
                
                if not source or not target:
                    continue
                
                try:
                    session.run(
                        """
                        MATCH (a:Entity {id: $source, dataset: $dataset})
                        MATCH (b:Entity {id: $target, dataset: $dataset})
                        MERGE (a)-[r:RELATES {type: $relation, dataset: $dataset}]->(b)
                        SET r.weight = $weight
                        """,
                        source=source,
                        target=target,
                        relation=relation,
                        weight=weight,
                        dataset=dataset_name
                    )
                    relationships_created += 1
                except Exception as e:
                    logger.warning(f"Error creating relationship {source}->{target}: {e}")
                    continue
        
        logger.info(f"✅ Loaded graph: {nodes_created} nodes, {relationships_created} relationships")
        return {
            "nodes_created": nodes_created,
            "relationships_created": relationships_created,
            "format": "standard"
        }


def load_graph_to_neo4j(
    graph_path: str,
    dataset_name: str,
    uri: str,
    user: str,
    password: str,
    database: str = "neo4j",
    clear_existing: bool = True
) -> Optional[Dict]:
    """
    Convenience function to load a graph into Neo4j
    
    Args:
        graph_path: Path to graph JSON file
        dataset_name: Dataset name
        uri: Neo4j URI
        user: Neo4j username
        password: Neo4j password
        database: Neo4j database name
        clear_existing: Whether to clear existing data
        
    Returns:
        Dict with load stats or None on failure
    """
    loader = Neo4jLoader(uri, user, password, database)
    
    try:
        if not loader.connect():
            return None
        
        stats = loader.load_graph_from_json(graph_path, dataset_name, clear_existing)
        return stats
    except Exception as e:
        logger.error(f"Failed to load graph to Neo4j: {e}", exc_info=True)
        return None
    finally:
        loader.close()


if __name__ == "__main__":
    # Test loading demo graph
    import sys
    from dotenv import load_dotenv
    
    load_dotenv()
    
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password")
    database = os.getenv("NEO4J_DATABASE", "neo4j")
    
    graph_path = "output/graphs/demo_new.json"
    
    if not os.path.exists(graph_path):
        print(f"Graph file not found: {graph_path}")
        sys.exit(1)
    
    print(f"Loading {graph_path} into Neo4j...")
    stats = load_graph_to_neo4j(graph_path, "demo", uri, user, password, database)
    
    if stats:
        print(f"✅ Success: {stats}")
    else:
        print("❌ Failed to load graph")
        sys.exit(1)
