from src.configCPP import setupCppTools
from src.analyzeADM.extractMetadata import extractMetaData
from src.analyzeADM.parser import parseMetadata, getGlobalData
from src.analyzeADM.checkAudioChannels import exportAudioActivity
from src.packageADM.packageForRender import packageForRender
from src.createRender import runVBAPRender
from src.analyzeRender import analyzeRenderOutput
import sys


# Current pipeline:
# 1. Setup C++ tools - install bwfmetaedit, initialize git submodules (allolib), build VBAP renderer
# 2. Extract ADM metadata from source WAV using bwfmetaedit
# 3. Parse ADM metadata into internal data structure (optionally export JSON for analysis)
# 4. Analyze audio channels for content (generate containsAudio.json)
# 5. Run packageForRender - split stems and create spatial instructions JSON
# 6. Run VBAP renderer - create multichannel spatial render
# 7. Analyze render output - create PDF with dB analysis of each channel in final render


def run_pipeline(sourceADMFile, sourceSpeakerLayout, createRenderAnalysis=True):
    """
    Run the complete ADM to spatial audio pipeline
    
    Args:
        sourceADMFile: path to source ADM WAV file
        sourceSpeakerLayout: path to speaker layout JSON
        createRenderAnalysis: whether to create render analysis PDF
    """
    # Step 1: Setup C++ tools and dependencies
    print("\n" + "="*80)
    print("STEP 1: Setting up C++ tools and dependencies")
    print("="*80)
    if not setupCppTools():
        print("\n✗ Error: C++ tools setup failed")
        print("Cannot continue without required tools.")
        return False
    
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

