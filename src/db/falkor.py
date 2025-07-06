from graphiti_core.driver.falkordb_driver import FalkorDriver
from src.config import settings

# FalkorDB connection using FalkorDriver
falkor_driver = FalkorDriver(
    host=settings.FALKORDB_HOST,  
    port=settings.FALKORDB_PORT,            
    username=settings.FALKORDB_USERNAME,          
    password=settings.FALKORDB_PASSWORD
)       