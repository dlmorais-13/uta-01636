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

# import arcgis
# arcgis.env.verbose = True
