from src.analyzeADM.extractMetadata import extractMetaData
from src.analyzeADM.parser import parseMetadata, getGlobalData
from src.analyzeADM.checkAudioChannels import exportAudioActivity
from src.packageADM.packageForRender import packageForRender
from src.createRender import runVBAPRender
from src.analyzeRender import analyzeRenderOutput
import sys


#current pipeline:
# 1. set source
#2. extract ADM metadata from source wav
#3. parse ADM metadata into internal data structure (optionally export json for analysis)
#4. analyze audio channels for content (generate containsAudio.json)
#5. run packageForRender - this runs repackage (split stems) and createRenderInfo (spatial instructions json)
#6. run create render - runs allolib vbap renderer to create spatial render
#7. run analyze render -- creates pdf in processedData/ to show db analysis of each channel in final render


def run_pipeline(sourceADMFile, sourceSpeakerLayout, createRenderAnalysis=True):
    """
    Run the complete ADM to spatial audio pipeline
    
    Args:
        sourceADMFile: path to source ADM WAV file
        sourceSpeakerLayout: path to speaker layout JSON
        createRenderAnalysis: whether to create render analysis PDF
    """
    processedDataDir = "processedData"
    finalOutputRenderFile = "processedData/spatial_render.wav"
    finalOutputRenderAnalysisPDF = "processedData/spatial_render_analysis.pdf"

    print("\nChecking audio channels for content...")
    exportAudioActivity(sourceADMFile, output_path="processedData/containsAudio.json", threshold_db=-100)

    print("Extracting ADM metadata from WAV file...")
    extractedMetadata = extractMetaData(sourceADMFile, "processedData/currentMetaData.xml")

    if extractedMetadata:
        xmlPath = extractedMetadata
        print(f"Using extracted XML metadata at {xmlPath}")
    else:
        print("Using default XML metadata file")
        xmlPath = "data/POE-ATMOS-FINAL-metadata.xml"

    print("Parsing ADM metadata...")
    reformattedMetadata = parseMetadata(xmlPath, ToggleExportJSON=True, TogglePrintSummary=True) 

    print("\nPackaging audio for render...")
    packageForRender(sourceADMFile, processedDataDir)

    print("\nRunning VBAP spatial renderer...")
    runVBAPRender(
        source_folder="processedData/stageForRender",
        render_instructions="processedData/stageForRender/renderInstructions.json",
        speaker_layout=sourceSpeakerLayout,
        output_file=finalOutputRenderFile
    )

    if createRenderAnalysis:
        print("\nAnalyzing rendered spatial audio...")
        analyzeRenderOutput(
            render_file=finalOutputRenderFile,
            output_pdf=finalOutputRenderAnalysisPDF
        )

    print("\nDone")


if __name__ == "__main__":
    # CLI mode - parse arguments
    if len(sys.argv) >= 2:
        sourceADMFile = sys.argv[1]
        sourceSpeakerLayout = sys.argv[2] if len(sys.argv) >= 3 else "vbapRender/allosphere_layout.json"
        createRenderAnalysis = True if len(sys.argv) < 4 else sys.argv[3].lower() in ['true', '1', 'yes']
        
        run_pipeline(sourceADMFile, sourceSpeakerLayout, createRenderAnalysis)
    
    else:
        # default mode
        print("Usage: python runPipeline.py <sourceADMFile> [sourceSpeakerLayout] [createAnalysis]")
        print("\nRunning with default configuration...")
        
        sourceADMFile = "sourceData/POE-ATMOS-FINAL.wav"
        sourceSpeakerLayout = "vbapRender/allosphere_layout.json"
        createRenderAnalysis = True
        
        run_pipeline(sourceADMFile, sourceSpeakerLayout, createRenderAnalysis)

