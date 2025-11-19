#pragma once

#include <map>
#include <string>
#include <vector>
#include <al/math/al_Vec.hpp>
#include <al/sound/al_Vbap.hpp>
#include <al/io/al_AudioIOData.hpp>

#include "JSONLoader.hpp"
#include "LayoutLoader.hpp"
#include "WavUtils.hpp"

class VBAPRenderer {
public:
    VBAPRenderer(const SpeakerLayoutData &layout,
                 const SpatialData &spatial,
                 const std::map<std::string, MonoWavData> &sources);

    MultiWavData render();

private:
    SpeakerLayoutData mLayout;
    SpatialData mSpatial;
    const std::map<std::string, MonoWavData> &mSources;
    
    al::Speakers mSpeakers;
    al::Vbap mVBAP;

    float blockSize = 256.0f;

    al::Vec3f interpolateDir(const std::vector<Keyframe> &kfs, double t);
};
