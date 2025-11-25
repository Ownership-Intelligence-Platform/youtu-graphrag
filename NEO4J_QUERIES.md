# Neo4j Query Examples for GraphRAG

This guide provides Cypher queries to explore and analyze knowledge graphs imported into Neo4j.

## Basic Queries

### 1. Check if data was imported successfully
```cypher
// Count total nodes
MATCH (n) RETURN count(n) as total_nodes

// Count nodes by dataset
MATCH (n)
WHERE n.dataset IS NOT NULL
RETURN n.dataset, count(n) as node_count
ORDER BY node_count DESC
```

### 2. View sample nodes from a specific dataset
```cypher

// Check your data loaded
MATCH (n {dataset: 'test1'}) RETURN count(n)

// Replace 'test1' with your dataset name
MATCH (n {dataset: 'test1'})
RETURN n
LIMIT 25
```

### 3. Count relationships
```cypher
// Total relationships
MATCH ()-[r]->()
RETURN count(r) as total_relationships

// Relationships by dataset
MATCH ()-[r]->()
WHERE r.dataset IS NOT NULL
RETURN r.dataset, count(r) as rel_count
ORDER BY rel_count DESC
```

## Entity Exploration

### 4. Find all entity types in your graph
```cypher
MATCH (n {dataset: 'test1'})
RETURN DISTINCT n.type as entity_type, count(*) as count
ORDER BY count DESC
```

### 5. Find entities by name (search)
```cypher
// Search for entities containing specific text
MATCH (n {dataset: 'test1'})
WHERE n.name CONTAINS '张伟'
RETURN n.name, n.type, n
LIMIT 20
```

### 6. Get all properties of a specific entity
```cypher
MATCH (n {dataset: 'test1', name: '张伟'})
RETURN properties(n)
```

## Relationship Analysis

### 7. Find all relationship types
```cypher
MATCH ()-[r {dataset: 'test1'}]->()
RETURN DISTINCT r.type as relationship_type, count(*) as count
ORDER BY count DESC
```

### 8. Find entities with the most connections
```cypher
// Most connected nodes (high degree centrality)
MATCH (n {dataset: 'test1'})-[r]-()
RETURN n.name, n.type, count(r) as connections
ORDER BY connections DESC
LIMIT 20
```

### 9. Show direct relationships between two entities
```cypher
MATCH (a {dataset: 'test1', name: '张伟'})-[r]-(b {dataset: 'test1', name: '李芳'})
RETURN a.name, type(r), r.type, b.name
```

## Path Finding

### 10. Find shortest path between two entities
```cypher
MATCH path = shortestPath(
  (a {dataset: 'test1', name: '张伟'})-[*..5]-(b {dataset: 'test1', name: '李芳'})
)
RETURN path
```

### 11. Find all paths up to 3 hops
```cypher
MATCH path = (a {dataset: 'test1', name: '张伟'})-[*1..3]-(b {dataset: 'test1'})
RETURN path
LIMIT 50
```

### 12. Find entities within 2 degrees of separation
```cypher
MATCH (start {dataset: 'test1', name: '张伟'})-[*1..2]-(related)
RETURN DISTINCT related.name, related.type, labels(related)
LIMIT 30
```

## Pattern Matching

### 13. Find triangles (3-node cycles)
```cypher
MATCH (a {dataset: 'test1'})-[r1]-(b {dataset: 'test1'})-[r2]-(c {dataset: 'test1'})-[r3]-(a)
WHERE id(a) < id(b) AND id(b) < id(c)
RETURN a.name, b.name, c.name
LIMIT 20
```

### 14. Find entities of specific type with specific relationships
```cypher
// Example: Find all persons who work_at organizations
MATCH (p {dataset: 'test1', type: 'person'})-[r {type: 'work_at'}]->(o {type: 'organization'})
RETURN p.name as person, o.name as organization
```

### 15. Find hub nodes (entities connected to many different types)
```cypher
MATCH (hub {dataset: 'test1'})-[r]-(connected)
WITH hub, count(DISTINCT connected.type) as type_diversity, count(r) as total_connections
WHERE type_diversity > 3
RETURN hub.name, hub.type, type_diversity, total_connections
ORDER BY type_diversity DESC, total_connections DESC
LIMIT 20
```

## Subgraph Extraction

### 16. Get complete neighborhood of an entity
```cypher
// Get entity and all its direct connections
MATCH (center {dataset: 'test1', name: '张伟'})-[r]-(neighbor)
RETURN center, r, neighbor
```

### 17. Extract subgraph by entity type
```cypher
// Get all persons and their relationships
MATCH (a {dataset: 'test1', type: 'person'})-[r]-(b {dataset: 'test1'})
RETURN a, r, b
LIMIT 100
```

### 18. Get subgraph by relationship type
```cypher
// Show only 'located_in' relationships
MATCH (a {dataset: 'test1'})-[r {type: 'located_in'}]->(b {dataset: 'test1'})
RETURN a, r, b
```

## Advanced Analytics

### 19. Calculate degree centrality
```cypher
MATCH (n {dataset: 'test1'})
OPTIONAL MATCH (n)-[r]-()
WITH n, count(r) as degree
RETURN n.name, n.type, degree
ORDER BY degree DESC
LIMIT 20
```

### 20. Find isolated components
```cypher
// Entities with no connections
MATCH (n {dataset: 'test1'})
WHERE NOT (n)-[]-()
RETURN n.name, n.type
```

### 21. Relationship weight analysis
```cypher
// If your relationships have weights
MATCH ()-[r {dataset: 'test1'}]->()
WHERE r.weight IS NOT NULL
RETURN r.type, 
       avg(r.weight) as avg_weight,
       min(r.weight) as min_weight,
       max(r.weight) as max_weight,
       count(*) as count
```

## Data Management

### 22. Delete specific dataset
```cypher
// WARNING: This deletes all data for the dataset
MATCH (n {dataset: 'test1'})
DETACH DELETE n
```

### 23. Update entity properties
```cypher
// Add or update properties
MATCH (n {dataset: 'test1', name: '张伟'})
SET n.verified = true, n.updated_at = datetime()
RETURN n
```

### 24. Count entities by schema type
```cypher
MATCH (n {dataset: 'test1'})
WHERE n.schema_type IS NOT NULL
RETURN n.schema_type, count(*) as count
ORDER BY count DESC
```

## Visualization Queries

### 25. Get small connected component for visualization
```cypher
// Get a specific entity and its 2-hop neighborhood
MATCH path = (center {dataset: 'test1', name: '张伟'})-[*1..2]-(neighbor)
RETURN path
LIMIT 50
```

### 26. Sample random subgraph
```cypher
// Get random sample for overview
MATCH (n {dataset: 'test1'})
WITH n, rand() as r
ORDER BY r
LIMIT 30
OPTIONAL MATCH (n)-[rel]-(connected)
WHERE connected.dataset = 'test1'
RETURN n, rel, connected
```

## Quality Checks

### 27. Find entities with missing names
```cypher
MATCH (n {dataset: 'test1'})
WHERE n.name IS NULL OR n.name = ''
RETURN n
LIMIT 20
```

### 28. Find duplicate entities
```cypher
// Entities with same name but different IDs
MATCH (n {dataset: 'test1'})
WITH n.name as name, collect(n) as nodes
WHERE size(nodes) > 1
RETURN name, size(nodes) as duplicate_count, nodes
LIMIT 20
```

### 29. Relationship type coverage
```cypher
// See which entity type pairs are connected
MATCH (a {dataset: 'test1'})-[r]-(b {dataset: 'test1'})
RETURN DISTINCT a.type as from_type, r.type as relation, b.type as to_type, count(*) as count
ORDER BY count DESC
```

## Export Queries

### 30. Export to CSV format (in Neo4j Browser)
```cypher
// Export entity list
MATCH (n {dataset: 'test1'})
RETURN n.name as name, n.type as type, n.schema_type as schema_type

// Export relationships
MATCH (a {dataset: 'test1'})-[r]->(b {dataset: 'test1'})
RETURN a.name as source, r.type as relation, b.name as target
```

## Tips

1. **Use LIMIT**: Always add `LIMIT` to prevent overwhelming results
2. **Index your data**: Create indexes for faster queries:
   ```cypher
   CREATE INDEX entity_dataset FOR (n:Entity) ON (n.dataset)
   CREATE INDEX entity_name FOR (n:Entity) ON (n.name)
   ```
3. **Use EXPLAIN/PROFILE**: Optimize slow queries:
   ```cypher
   PROFILE MATCH (n {dataset: 'test1'}) RETURN count(n)
   ```
4. **Dataset isolation**: Always filter by `dataset` to avoid mixing graphs
5. **Browser visualization**: Use Neo4j Browser for visual exploration of paths

## Common Patterns in GraphRAG

```cypher
// Question decomposition pattern
MATCH (q:Question {dataset: 'test1'})-[:DECOMPOSED_TO]->(sq:SubQuestion)
RETURN q, sq

// Evidence chain pattern
MATCH path = (q:Question)-[:SUPPORTED_BY*1..3]->(evidence)
RETURN path

// Community detection (if imported)
MATCH (n {dataset: 'test1'})
WHERE n.community_id IS NOT NULL
RETURN n.community_id, collect(n.name) as members, count(*) as size
ORDER BY size DESC
```
