from graphiti_core.driver.falkordb_driver import FalkorDriver

# FalkorDB connection using FalkorDriver
falkor_driver = FalkorDriver(
    host='localhost',        # or os.environ.get('FALKORDB_HOST', 'localhost')
    port='6379',            # or os.environ.get('FALKORDB_PORT', '6379')
    username=None,          # or os.environ.get('FALKORDB_USERNAME', None)
    password=None           # or os.environ.get('FALKORDB_PASSWORD', None)
)