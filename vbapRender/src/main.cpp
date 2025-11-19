#include <iostream>
#include <string>
#include <filesystem>

#include "JSONLoader.hpp"
#include "LayoutLoader.hpp"
#include "VBAPRenderer.hpp"
#include "WavUtils.hpp"

namespace fs = std::filesystem;

int main(int argc, char *argv[]) {

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

    std::cout << "Loading layout...\n";
    SpeakerLayoutData layout = LayoutLoader::loadLayout(layoutFile);

    std::cout << "Loading spatial instructions...\n";
    SpatialData spatial = JSONLoader::loadSpatialInstructions(positionsFile);

    std::cout << "Loading source WAVs...\n";
    std::map<std::string, MonoWavData> sources =
        WavUtils::loadSources(sourcesFolder, spatial.sources, spatial.sampleRate);

    std::cout << "Rendering...\n";
    VBAPRenderer renderer(layout, spatial, sources);
    MultiWavData output = renderer.render();

    std::cout << "Writing output WAV: " << outFile << "\n";
    WavUtils::writeMultichannelWav(outFile, output);

    std::cout << "Done.\n";
    return 0;
}
