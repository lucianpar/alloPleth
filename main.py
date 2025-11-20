from src.analyzeADM.extractMetadata import extractMetaData
from src.analyzeADM.parser import parseMetadata, getGlobalData
#from src.visObjects import animateObjects
from src.analyzeADM.checkAudioChannels import exportAudioActivity
from src.analyzeADM.checkAudioChannels import exportAudioActivity
from src.packageADM.packageForRender import packageForRender


#current pipeline:
# 1. set source
#2. extract ADM metadata from source wav
#3. parse ADM metadata into internal data structure (optionally export json for analysis)
#4. analyze audio channels for content (generate containsAudio.json)
#5. run packageForRender - this runs repackage (split stems) and createRenderInfo (spatial instructions json)
#5. 



sourceADMFile = "sourceData/POE-ATMOS-FINAL.wav"
processedDataDir = "processedData"


extractedMetadata = None
#commenting out for now

print("\nChecking audio channels for content...")
exportAudioActivity(sourceADMFile,output_path="processedData/containsAudio.json", threshold_db=-100)

print("Extracting ADM metadata from WAV file...")
extractedMetadata = extractMetaData(sourceADMFile, "processedData/currentMetaData.xml")


if extractedMetadata:
    xmlPath = extractedMetadata
    print(f"Using extracted XML metadata at {xmlPath}")
else:
    print("Using default XML metadata file")
    xmlPath = "data/POE-ATMOS-FINAL-metadata.xml"

# Extract all object metada (position and width are key here), direct speaker (used for channel based surround mixing and Low Freqeuency Effect channel) global data. toggle exporting a human readable json file for analysis. printing summary is based on that json file. for now, the rest of the pipeline uses the json's, but this can be changed later to use the internal format directly. potentially keeping 1 json for debugging?
print("Parsing ADM metadata...")
# this internal format is not up to date
reformattedMetadata = parseMetadata(xmlPath, ToggleExportJSON=True, TogglePrintSummary=True) 

#analyze audio channel data for later use in removing obselete channels 

packageForRender(sourceADMFile, processedDataDir)






print("\nDone")

