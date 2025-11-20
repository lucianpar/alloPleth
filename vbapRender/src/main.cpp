// sonoPleth VBAP Renderer for AlloSphere
// 
// renders spatial audio using Vector Base Amplitude Panning
// takes mono source files and spatial trajectory data
// outputs multichannel WAV for the AlloSphere's 54-speaker array
//
// key gotcha that took forever to debug:
// AlloLib expects speaker angles in degrees not radians
// so the JSON loader converts from radians to degrees when creating al::Speaker objects
// without this conversion VBAP silently fails and produces zero output

#include <iostream>
#include <string>
#include <filesystem>

#include "JSONLoader.hpp"
#include "LayoutLoader.hpp"
#include "VBAPRenderer.hpp"
#include "WavUtils.hpp"

namespace fs = std::filesystem;

int main(int argc, char *argv[]) {

    // parse command line args
    // old version used positional args which was error prone
    // switched to flagged args for clarity
    if (argc < 9) {
        std::cout << "Usage:\n"
                  << "  sonoPleth_vbap_render "
                  << "--layout layout.json "
                  << "--positions spatial.json "
                  << "--sources <folder> "
                  << "--out output.wav\n";
        return 1;
    }

    fs::path layoutFile, positionsFile, sourcesFolder, outFile;

    for (int i = 1; i < argc; i++) {
        std::string arg = argv[i];

        if (arg == "--layout") {
            layoutFile = argv[++i];
        } else if (arg == "--positions") {
            positionsFile = argv[++i];
        } else if (arg == "--sources") {
            sourcesFolder = argv[++i];
        } else if (arg == "--out") {
            outFile = argv[++i];
        }
    }

    // layout JSON has speaker positions in radians
    // these get converted to degrees when creating al::Speaker objects in VBAPRenderer
    std::cout << "Loading layout...\n";
    SpeakerLayoutData layout = LayoutLoader::loadLayout(layoutFile);

    // spatial trajectories with keyframes for each source
    std::cout << "Loading spatial instructions...\n";
    SpatialData spatial = JSONLoader::loadSpatialInstructions(positionsFile);

    // load all mono source files
    std::cout << "Loading source WAVs...\n";
    std::map<std::string, MonoWavData> sources =
        WavUtils::loadSources(sourcesFolder, spatial.sources, spatial.sampleRate);

    // main rendering happens here
    // this is where the degrees conversion and channel mapping fixes are critical
    std::cout << "Rendering...\n";
    VBAPRenderer renderer(layout, spatial, sources);
    MultiWavData output = renderer.render();

    // output has consecutive channels 0 to 53
    // if you need AlloSphere hardware channel numbers with gaps you can remap later
    std::cout << "Writing output WAV: " << outFile << "\n";
    WavUtils::writeMultichannelWav(outFile, output);

    std::cout << "Done.\n";
    return 0;
}
