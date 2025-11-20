from src.analyzeADM.extractMetadata import extractMetaData
from src.analyzeADM.parser import parseMetadata, getGlobalData
#from src.visObjects import animateObjects
from src.analyzeADM.checkAudioChannels import exportAudioActivity
from src.analyzeADM.checkAudioChannels import exportAudioActivity
from src.packageADM.packageForRender import packageForRender
from src.createRender import runVBAPRender
from src.analyzeRender import analyzeRenderOutput


#current pipeline:
# 1. set source
#2. extract ADM metadata from source wav
#3. parse ADM metadata into internal data structure (optionally export json for analysis)
#4. analyze audio channels for content (generate containsAudio.json)
#5. run packageForRender - this runs repackage (split stems) and createRenderInfo (spatial instructions json)
#6. run create render - runs allolib vbap renderer to create spatial render
#7. run analyze render -- creates pdf in processedData/ to show db analysis of each channel in final render



#configure (in gui??)
sourceADMFile = "sourceData/POE-ATMOS-FINAL.wav"
sourceSpeakerLayout = "vbapRender/allosphere_layout.json"
createRenderAnalysis = True
#end configure 

#default
processedDataDir = "processedData"
finalOutputRenderFile = "processedData/spatial_render.wav"
finalOutputRenderAnalysisPDF = "processedData/spatial_render_analysis.pdf"


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

#splits audio channels and creates instructions to deliver to rendering app 
packageForRender(sourceADMFile, processedDataDir)

#calls allo app to run the render
runVBAPRender(source_folder="processedData/stageForRender",
    render_instructions="processedData/stageForRender/renderInstructions.json",
    speaker_layout=sourceSpeakerLayout,
    output_file=finalOutputRenderFile)

#render analysis - checks dB levels over time for each channel in final render
if (createRenderAnalysis):
    print("\nAnalyzing rendered spatial audio...")
    analyzeRenderOutput(render_file=finalOutputRenderFile,
         output_pdf=finalOutputRenderAnalysisPDF)

print("\nDone")

