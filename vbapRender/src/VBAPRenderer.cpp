#include "VBAPRenderer.hpp"
#include <cmath>
#include <iostream>

VBAPRenderer::VBAPRenderer(const SpeakerLayoutData &layout,
                           const SpatialData &spatial,
                           const std::map<std::string, MonoWavData> &sources)
    : mLayout(layout), mSpatial(spatial), mSources(sources),
      mSpeakers(), mVBAP(mSpeakers, true)

      //note: might need to remap channels for sphere later? to account for gaps in channel numbering?
{
    // CRITICAL FIX 1: AlloLib's al::Speaker expects angles in DEGREES not radians
    // The AlloSphere layout JSON stores angles in radians but al::Speaker internally
    // converts to radians using toRad() which assumes degree input
    // Without this conversion you get speaker positions at completely wrong angles
    // like -77.7 radians instead of -77.7 degrees which is way outside valid range
    // This caused VBAP to fail silently and produce zero output
    //
    // CRITICAL FIX 2: AlloSphere hardware uses non-consecutive channel numbers 1-60 with gaps
    // but VBAP needs consecutive 0-based indices for AudioIOData buffer access
    // We use array index i as the VBAP channel and ignore the original deviceChannel numbers
    // The output WAV will have consecutive channels 0-53 which can be remapped later
    // if you need the original hardware channel routing
    // Old approach tried to preserve deviceChannel which caused out-of-bounds crashes
    // because AudioIOData only allocates channels 0 to numSpeakers-1
    
    for (size_t i = 0; i < layout.speakers.size(); i++) {
        const auto &spk = layout.speakers[i];
        mSpeakers.emplace_back(al::Speaker(
            i,                                    // consecutive 0-based channel index
            spk.azimuth * 180.0f / M_PI,          // radians to degrees
            spk.elevation * 180.0f / M_PI,        // radians to degrees
            0,                                    // group id
            spk.radius                            // distance from center
        ));
    }
    
    // compile builds the speaker triplet mesh for VBAP algorithm
    // this finds all valid triangles of 3 speakers that can spatialize sound
    mVBAP = al::Vbap(mSpeakers, true);
    mVBAP.compile();
}

al::Vec3f VBAPRenderer::interpolateDir(const std::vector<Keyframe> &kfs, double t) {
    // linear interpolation between keyframes for smooth spatial motion
    // takes time in seconds and returns normalized direction vector
    
    if (kfs.size() == 1) {
        return al::Vec3f(kfs[0].x, kfs[0].y, kfs[0].z).normalize();
    }

    Keyframe k1, k2;
    for (int i = 0; i < kfs.size() - 1; i++) {
        if (t >= kfs[i].time && t <= kfs[i+1].time) {
            k1 = kfs[i];
            k2 = kfs[i+1];
            break;
        }
    }

    double u = (t - k1.time) / (k2.time - k1.time);
    al::Vec3f v(
        (1-u)*k1.x + u*k2.x,
        (1-u)*k1.y + u*k2.y,
        (1-u)*k1.z + u*k2.z
    );
    v.normalize();
    return v;
}

MultiWavData VBAPRenderer::render() {
    int sr = mSpatial.sampleRate;
    int numSpeakers = mLayout.speakers.size();

    size_t totalSamples = 0;
    for (auto &[name, wav] : mSources) {
        totalSamples = std::max(totalSamples, wav.samples.size());
    }

    std::cout << "Rendering " << totalSamples << " samples (" 
              << (double)totalSamples / sr << " sec) to " 
              << numSpeakers << " speakers from " << mSources.size() << " sources\n";

    // output uses consecutive channels 0 to numSpeakers-1
    // this is simpler than trying to maintain the AlloSphere hardware channel gaps
    // if you need to remap to hardware channels later just create a channel routing map
    MultiWavData out;
    out.sampleRate = sr;
    out.channels = numSpeakers;
    out.samples.resize(numSpeakers);
    for (auto &c : out.samples) c.resize(totalSamples, 0.0f);

    // CRITICAL: must call framesPerBuffer BEFORE channelsOut
    // otherwise AudioIOData throws assertion failures about buffer size not being set
    // the AlloLib API is picky about initialization order
    const int bufferSize = 512;
    al::AudioIOData audioIO;
    audioIO.framesPerBuffer(bufferSize);
    audioIO.framesPerSecond(sr);
    audioIO.channelsIn(0);
    audioIO.channelsOut(numSpeakers);
    
    std::vector<float> sourceBuffer(bufferSize);
    
    int blocksProcessed = 0;
    for (size_t blockStart = 0; blockStart < totalSamples; blockStart += bufferSize) {
        size_t blockEnd = std::min(totalSamples, blockStart + bufferSize);
        size_t blockLen = blockEnd - blockStart;
        
        if (blocksProcessed % 1000 == 0) {
            std::cout << "  Block " << blocksProcessed << " (" 
                      << (int)(100.0 * blockStart / totalSamples) << "%)\n" << std::flush;
        }
        blocksProcessed++;
        
        // zero out the audio buffer before accumulating sources
        // VBAP uses += to accumulate multiple sources into the same speakers
        audioIO.zeroOut();
        
        int sourceIdx = 0;
        for (auto &[name, kfs] : mSpatial.sources) {
            const MonoWavData &src = mSources.at(name);
            
            // copy source samples into buffer for this block
            for (size_t i = 0; i < blockLen; i++) {
                size_t globalIdx = blockStart + i;
                sourceBuffer[i] = (globalIdx < src.samples.size()) ? src.samples[globalIdx] : 0.0f;
            }
            
            // get spatial direction for this source at current time
            double timeSec = (double)blockStart / (double)sr;
            al::Vec3f dir = interpolateDir(kfs, timeSec);
            
            // renderBuffer finds the best speaker triplet for this direction
            // calculates VBAP gains and mixes the source into the output channels
            // this accumulates into audioIO so multiple sources can overlap
            mVBAP.renderBuffer(audioIO, dir, sourceBuffer.data(), blockLen);
            sourceIdx++;
        }
        
        // copy the rendered audio from AudioIOData into our output buffer
        // must call frame(0) to reset the read position before accessing samples
        audioIO.frame(0);
        for (size_t i = 0; i < blockLen; i++) {
            for (int ch = 0; ch < numSpeakers; ch++) {
                out.samples[ch][blockStart + i] += audioIO.out(ch, i);
            }
        }

    }
    
    std::cout << "\n";
    return out;
}
