"""
Custom search configurations for Texas Ontology Protocol entities.

This module provides specialized search filters and configurations
for searching Fort Worth municipal data.
"""

from typing import List, Optional, Dict, Any
from graphiti_core.search.search_filters import SearchFilters


class TOPSearchConfig:
    """Search configurations for Texas Ontology Protocol entities."""
    
    @staticmethod
    def government_entities_filter() -> SearchFilters:
        """Filter for government entities only."""
        # Simplified to avoid FalkorDB label OR issues
        # Will search without label filtering and rely on content matching
        return SearchFilters()
    
    @staticmethod
    def political_positions_filter() -> SearchFilters:
        """Filter for political positions and office holders."""
        # Simplified to avoid FalkorDB label OR issues
        return SearchFilters()
    
    @staticmethod
    def legal_documents_filter() -> SearchFilters:
        """Filter for legal documents."""
        # Simplified to avoid FalkorDB label OR issues
        return SearchFilters()
    
    @staticmethod
    def geographic_entities_filter() -> SearchFilters:
        """Filter for geographic and boundary entities."""
        # Simplified to avoid FalkorDB label OR issues
        return SearchFilters()
    
    @staticmethod
    def government_relationships_filter() -> SearchFilters:
        """Filter for government relationship edges."""
        return SearchFilters(
            edge_types=[
                "Governs",
                "HasJurisdictionOver",
                "PartOf",
                "ReportsTo"
            ]
        )
    
    @staticmethod
    def political_relationships_filter() -> SearchFilters:
        """Filter for political relationship edges."""
        return SearchFilters(
            edge_types=[
                "HoldsPosition",
                "AppointedBy",
                "ElectedTo"
            ]
        )
    
    @staticmethod
    def active_entities_filter(reference_date: Optional[str] = None) -> SearchFilters:
        """Filter for currently active entities (not superseded)."""
        # This would need custom implementation in Graphiti
        # For now, return all entities
        return SearchFilters()
    
    @staticmethod
    def by_entity_type(entity_type: str) -> SearchFilters:
        """Filter by specific entity type."""
        return SearchFilters(
            node_labels=[entity_type]
        )
    
    @staticmethod
    def by_department_type(dept_type: str) -> SearchFilters:
        """Filter departments by type (e.g., 'public_safety', 'utility')."""
        # This would require attribute filtering
        return SearchFilters(
            node_labels=["Department"]
        )


class TOPSearchQueries:
    """Pre-defined search queries for common Fort Worth information needs."""
    
    @staticmethod
    async def search_current_officials(graphiti, include_appointed: bool = True):
        """Search for all current elected and appointed officials."""
        # Use descriptive search query instead of label filtering
        query = "current Fort Worth officials mayors council members"
        if include_appointed:
            query += " city manager appointed positions"
        
        # No label filtering to avoid FalkorDB issues
        filter_config = SearchFilters()
        
        return await graphiti.search(
            query=query
        )
    
    @staticmethod
    async def search_city_departments(graphiti, dept_type: Optional[str] = None):
        """Search for city departments, optionally filtered by type."""
        query = "Fort Worth city departments"
        if dept_type:
            query += f" {dept_type}"
        
        # No label filtering to avoid FalkorDB issues
        filter_config = SearchFilters()
        
        return await graphiti.search(
            query=query
        )
    
    @staticmethod
    async def search_council_districts(graphiti, district_number: Optional[int] = None):
        """Search for council districts."""
        query = "Fort Worth city council districts"
        if district_number:
            query += f" district {district_number}"
        
        # No label filtering to avoid FalkorDB issues
        filter_config = SearchFilters()
        
        return await graphiti.search(
            query=query
        )
    
    @staticmethod
    async def search_recent_ordinances(graphiti, days: int = 30):
        """Search for recent ordinances."""
        return await graphiti.search(
            query=f"Fort Worth ordinances passed in last {days} days"
        )
    
    @staticmethod
    async def search_by_relationship(graphiti, relationship_type: str, entity_name: str):
        """Search based on relationship type."""
        # For now, search without edge filters due to FalkorDB compatibility
        return await graphiti.search(
            query=f"{entity_name} {relationship_type}"
        )
    
    @staticmethod
    async def search_organizational_hierarchy(graphiti, root_entity: str = "Fort Worth"):
        """Search organizational hierarchy starting from a root entity."""
        # For now, search without edge filters due to FalkorDB compatibility
        return await graphiti.search(
            query=f"{root_entity} organizational structure hierarchy"
        )


# Helper function for enhanced search with TOP filters
async def top_search(
    graphiti,
    query: str,
    entity_category: Optional[str] = None,
    limit: int = 10
) -> List[Any]:
    """
    Perform a search with TOP-specific filters.
    
    Args:
        graphiti: Graphiti instance
        query: Search query
        entity_category: Category to filter ('government', 'political', 'legal', 'geographic')
        limit: Maximum number of results to return
    
    Returns:
        Search results
    """
    # Build filter based on category
    filter_config = None
    
    if entity_category == "government":
        filter_config = TOPSearchConfig.government_entities_filter()
    elif entity_category == "political":
        filter_config = TOPSearchConfig.political_positions_filter()
    elif entity_category == "legal":
        filter_config = TOPSearchConfig.legal_documents_filter()
    elif entity_category == "geographic":
        filter_config = TOPSearchConfig.geographic_entities_filter()
    
    # Perform search
    results = await graphiti.search(
        query=query,
        search_filter=filter_config
    )
    
    # Apply limit manually if specified
    if limit and len(results) > limit:
        results = results[:limit]
    
    return results