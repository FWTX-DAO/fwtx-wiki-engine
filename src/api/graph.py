"""
Graph API endpoints for direct graph queries and visualization.
"""

from fastapi import APIRouter, HTTPException, Depends
import logging

from src.db.falkor import falkor_driver
from src.middleware.auth import get_api_key
from src.models.graph import GraphQueryRequest, GraphQueryResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/graph", tags=["graph"])

@router.post("/query", response_model=GraphQueryResponse)
async def execute_graph_query(
    request: GraphQueryRequest,
    api_key: str = Depends(get_api_key)
) -> GraphQueryResponse:
    """
    Execute a raw Cypher query on the graph database.
    
    Returns nodes and edges formatted for visualization.
    """
    try:
        logger.info(f"Executing graph query: {request.query}")
        
        # Execute the query
        results, summary, keys = await falkor_driver.execute_query(
            request.query,
            **request.params
        )
        
        # Check if results is None or empty
        if results is None:
            logger.warning("Query returned None")
            return GraphQueryResponse(nodes=[], edges=[], raw_results=[])
            
        logger.info(f"Query returned {len(results) if hasattr(results, '__len__') else 'unknown'} results")
        logger.info(f"Keys: {keys}")
        
        # Process results to extract nodes and edges
        nodes = []
        edges = []
        node_ids = set()
        edge_ids = set()
        
        # Convert results to list if needed
        try:
            results_list = list(results) if results else []
        except Exception as e:
            logger.error(f"Error converting results to list: {e}")
            results_list = []
        
        for i, record in enumerate(results_list):
            if record is None:
                continue
                
            # Debug logging for first few records
            if i < 3:
                logger.info(f"Record {i}: type={type(record)}, attributes={dir(record)}")
                
            # Get all values from the record directly (keys might be None)
            values = []
            if hasattr(record, 'values'):
                values = record.values()
            elif hasattr(record, '__iter__'):
                values = record
            elif hasattr(record, 'get'):
                # If we have keys, use them
                if keys:
                    values = [record.get(k) for k in keys]
                else:
                    # Try to get values directly
                    values = record.values() if hasattr(record, 'values') else []
            
            for j, value in enumerate(values):
                if i < 3:
                    logger.info(f"  Value {j}: type={type(value)}, hasattr_properties={hasattr(value, 'properties')}, hasattr_type={hasattr(value, 'type')}")
                
                # Handle nodes (FalkorDB returns Node objects)
                if value is not None and hasattr(value, 'properties'):
                    # This is a node
                    try:
                        props = value.properties if hasattr(value, 'properties') else {}
                        node_id = str(props.get('uuid', f"node_{id(value)}"))
                        
                        if node_id not in node_ids:
                            node_ids.add(node_id)
                            
                            # Get node labels
                            labels = []
                            if hasattr(value, 'labels'):
                                labels = list(value.labels)
                            elif hasattr(value, 'label'):
                                labels = [value.label]
                            
                            nodes.append({
                                'id': node_id,
                                'label': props.get('name', props.get('title', 'Unknown')),
                                'type': labels[0] if labels else 'Entity',
                                'properties': props
                            })
                    except Exception as e:
                        logger.warning(f"Error processing node: {e}")
                
                # Handle relationships (FalkorDB Edge objects)
                elif value is not None and hasattr(value, 'type') and not hasattr(value, 'properties'):
                    # This is likely a relationship/edge
                    try:
                        edge_id = f"edge_{id(value)}"
                        
                        if edge_id not in edge_ids:
                            # Get source and target node IDs from the edge
                            source_id = None
                            target_id = None
                            
                            if hasattr(value, 'src_node') and hasattr(value, 'dest_node'):
                                # FalkorDB edge format
                                source_id = str(value.src_node)
                                target_id = str(value.dest_node)
                            elif hasattr(value, 'start_node') and hasattr(value, 'end_node'):
                                # Alternative format
                                source_id = str(value.start_node)
                                target_id = str(value.end_node)
                            
                            if source_id and target_id:
                                edge_ids.add(edge_id)
                                edges.append({
                                    'id': edge_id,
                                    'source': source_id,
                                    'target': target_id,
                                    'type': value.type if hasattr(value, 'type') else 'RELATES_TO',
                                    'properties': {}
                                })
                    except Exception as e:
                        logger.warning(f"Error processing edge: {e}")
        
        # Also return raw results for flexibility
        raw_results = []
        for record in results_list:
            if record is not None:
                try:
                    # Try to convert record to a serializable format
                    record_dict = {}
                    if hasattr(record, 'keys'):
                        for k in record.keys():
                            v = record.get(k)
                            # Skip non-serializable objects in raw results
                            if v is None or isinstance(v, (str, int, float, bool, list, dict)):
                                record_dict[k] = v
                    if record_dict:
                        raw_results.append(record_dict)
                except Exception as e:
                    # If can't convert to dict, skip
                    logger.debug(f"Skipping raw result due to: {e}")
                    pass
        
        return GraphQueryResponse(
            nodes=nodes,
            edges=edges,
            raw_results=raw_results
        )
        
    except Exception as e:
        logger.error(f"Error executing graph query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all", response_model=GraphQueryResponse)
async def get_all_graph_data(
    api_key: str = Depends(get_api_key)
) -> GraphQueryResponse:
    """
    Get all nodes and relationships from the graph.
    
    Uses separate queries for nodes and edges to avoid serialization issues.
    """
    try:
        logger.info("Getting all graph data using separate queries")
        
        nodes = []
        edges = []
        
        # First get all nodes
        node_results, _, _ = await falkor_driver.execute_query("MATCH (n) RETURN n")
        node_list = list(node_results) if node_results else []
        
        logger.info(f"Found {len(node_list)} nodes")
        
        for node_record in node_list:
            if hasattr(node_record, 'values'):
                for node in node_record.values():
                    if hasattr(node, 'properties'):
                        props = node.properties
                        node_id = str(props.get('uuid', f"node_{id(node)}"))
                        
                        # Get labels
                        labels = []
                        if hasattr(node, 'labels'):
                            labels = list(node.labels)
                        
                        nodes.append({
                            'id': node_id,
                            'label': props.get('name', props.get('title', 'Unknown')),
                            'type': labels[0] if labels else 'Entity',
                            'properties': dict(props)
                        })
        
        # Then get all relationships
        edge_results, _, _ = await falkor_driver.execute_query("MATCH (n)-[r]->(m) RETURN n, r, m")
        edge_list = list(edge_results) if edge_results else []
        
        logger.info(f"Found {len(edge_list)} relationships")
        
        for edge_record in edge_list:
            if hasattr(edge_record, 'values'):
                values = list(edge_record.values())
                if len(values) >= 3:
                    source_node, relationship, target_node = values[0], values[1], values[2]
                    
                    # Get source and target IDs
                    source_id = str(source_node.properties.get('uuid', f"node_{id(source_node)}")) if hasattr(source_node, 'properties') else None
                    target_id = str(target_node.properties.get('uuid', f"node_{id(target_node)}")) if hasattr(target_node, 'properties') else None
                    
                    if source_id and target_id:
                        rel_props = relationship.properties if hasattr(relationship, 'properties') else {}
                        edge_id = str(rel_props.get('uuid', f"edge_{id(relationship)}"))
                        
                        edges.append({
                            'id': edge_id,
                            'source': source_id,
                            'target': target_id,
                            'type': relationship.type if hasattr(relationship, 'type') else 'RELATES_TO',
                            'properties': dict(rel_props)
                        })
        
        logger.info(f"Processed {len(nodes)} nodes and {len(edges)} edges")
        
        return GraphQueryResponse(
            nodes=nodes,
            edges=edges,
            raw_results=[]
        )
        
    except Exception as e:
        logger.error(f"Error getting all graph data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/count")
async def get_graph_counts(
    api_key: str = Depends(get_api_key)
) -> dict:
    """
    Get count of nodes and relationships in the graph.
    """
    try:
        # Count nodes
        node_result, _, _ = await falkor_driver.execute_query("MATCH (n) RETURN count(n) as count")
        node_count = 0
        if node_result:
            node_count = list(node_result)[0].get('count', 0) if node_result else 0
        
        # Count relationships
        edge_result, _, _ = await falkor_driver.execute_query("MATCH ()-[r]->() RETURN count(r) as count")
        edge_count = 0
        if edge_result:
            edge_count = list(edge_result)[0].get('count', 0) if edge_result else 0
        
        return {
            "nodes": node_count,
            "edges": edge_count
        }
    except Exception as e:
        logger.error(f"Error getting graph counts: {e}")
        return {
            "nodes": 0,
            "edges": 0,
            "error": str(e)
        }