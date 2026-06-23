import logging

class RelativeSeconds(logging.Formatter):
    def format(self, record):
        # Convert milliseconds to seconds (float)
        record.relativeCreated = record.relativeCreated / 1000.0
        # Call the parent class's format method
        return super().format(record)
    
# Configure the logging
formatter = RelativeSeconds('%(asctime)s - %(threadName)s - %(relativeCreated)fs - %(levelname)s - %(name)s - %(message)s')
logging.basicConfig(level=logging.INFO)
# logging.basicConfig(level=logging.DEBUG)
logging.root.handlers[0].setFormatter(formatter)

# Limit memory usage
import os
if "MEM_LIMIT" in os.environ:
    mem_limit_mb = int(os.environ["MEM_LIMIT"])
    mem_limit_bytes = mem_limit_mb * 1024 * 1024
    import resource
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    resource.setrlimit(resource.RLIMIT_AS, (mem_limit_bytes, hard))

# import arcgis
# arcgis.env.verbose = True
