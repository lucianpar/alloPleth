// VBAPRenderer - spatial audio renderer using AlloLib's VBAP implementation
//
// important notes if you need to debug this again:
// 
// 1. al::Speaker constructor expects angles in DEGREES not radians
//    the layout JSON has radians so we convert in the constructor
//    without this VBAP silently produces zeros
//
// 2. AlloSphere hardware uses non-consecutive channel numbers 1-60 with gaps
//    but we use consecutive 0-53 indices for VBAP and the output WAV
//    this avoids out-of-bounds crashes when accessing AudioIOData buffers
//    can remap to hardware channels later if needed
//
// 3. AudioIOData initialization order matters
//    must call framesPerBuffer before channelsOut or you get assertion failures
//
// 4. VBAP uses += to accumulate sources so call zeroOut before each block
//
// 5. must call audioIO.frame(0) before reading output samples

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
    
    // not currently used but left here in case you need to remap channels later
    // would map consecutive VBAP indices to AlloSphere hardware channels
    std::vector<int> mVbapToDevice;

    float blockSize = 256.0f;

    // linear interpolation between spatial keyframes
    al::Vec3f interpolateDir(const std::vector<Keyframe> &kfs, double t);
};
