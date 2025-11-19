#include "JSONLoader.hpp"
#include <fstream>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

SpatialData JSONLoader::loadSpatialInstructions(const std::string &path) {
    std::ifstream f(path);
    if (!f.good()) throw std::runtime_error("Cannot open spatial JSON");

    json j;
    f >> j;

    SpatialData d;
    d.sampleRate = j["sampleRate"];

    for (auto &[name, kflist] : j["sources"].items()) {
        std::vector<Keyframe> frames;

        for (auto &k : kflist) {
            Keyframe kf;
            kf.time = k["time"];
            kf.x = k["cart"][0];
            kf.y = k["cart"][1];
            kf.z = k["cart"][2];
            frames.push_back(kf);
        }

        d.sources[name] = frames;
    }

    return d;
}
