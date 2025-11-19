
from src.packageADM.splitStems import splitChannelsToMono
from src.packageADM.createRenderInfo import createRenderInfoJSON

# NOT WORKING YET 

def packageForRender(sourceADM, processed_dir="processedData", output_dir="stagedForRender"):
    """Package data for rendering by splitting stems and creating render info JSON.
    
    Args:
        processed_dir (str): Directory containing processed data.
        output_dir (str): Directory to save packaged data for rendering.
    """
    # Create output directory
    
    # Split stems into individual audio files
    print("Attempting to run package for render -- splitting stems and creating render info...")
    createRenderInfoJSON(processed_dir=processed_dir)
    splitChannelsToMono(sourceADM, processed_dir=processed_dir, output_dir=output_dir)
    print(f"Packaged data for render in {output_dir}")
    

# if __name__ == "__main__":
#     packageForRender('sourceData/POE-ATMOS-FINAL.wav', processed_dir="processedData", output_dir="processedData/stageForRender")