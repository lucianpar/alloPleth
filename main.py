from src.extractMetadata import extractMetaData
from src.parser import parseMetadata, getGlobalData
#from src.visObjects import animateObjects
from src.createSpatialInstructions import createSpatialInstructionsCSV


extractedMetadata = None
#commenting out for now
print("Extracting ADM metadata from WAV file...")
extractedMetadata = extractMetaData("sourceData/POE-ATMOS-FINAL.wav", "processedData/currentMetaData.xml")


if extractedMetadata:
    xmlPath = extractedMetadata
    print(f"Using extracted XML metadata at {xmlPath}")
else:
    print("Using default XML metadata file")
    xmlPath = "data/POE-ATMOS-FINAL-metadata.xml"

# Extract all object metada (position and width are key here). toggle exporting a human readable json file for analysis. printing summary is based on that json file. for now, the animation is not based on the json file, but directly from the parsed data structure
print("Parsing ADM metadata...")
reformattedMetadata = parseMetadata(xmlPath, ToggleExportJSON=True, TogglePrintSummary=True)
#this json is useful for debugging and analysis. currently using an internal data structure for animation / realtime spatialization

'''commenting out for now, need to deep dive
#Animate positions over time (first 60 seconds) - not working yet
# print("\nCreating animation")
# animateObjects(reformattedMetadata, duration_seconds=60, fps=10, speed_multiplier=10.0)


'''

print("\nCreating spatial instructions...")
spatialInstructions = createSpatialInstructionsCSV(
    processed_dir="processedData",
    output_path="forExport/spatialInstructions.json"
)

print("\nDone")
