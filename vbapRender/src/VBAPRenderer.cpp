#include "VBAPRenderer.hpp"
#include <cmath>
#include <iostream>

VBAPRenderer::VBAPRenderer(const SpeakerLayoutData &layout,
                           const SpatialData &spatial,
                           const std::map<std::string, MonoWavData> &sources)
    : mLayout(layout), mSpatial(spatial), mSources(sources),
      mSpeakers(), mVBAP(mSpeakers, true)
{
    // Convert our layout data into AlloLib Speakers vector
    for (const auto &spk : layout.speakers) {
        mSpeakers.emplace_back(al::Speaker(
            spk.deviceChannel,
            spk.azimuth,
            spk.elevation,
            0, // group
            spk.radius
        ));
    }
    
    // Reinitialize VBAP with the populated speakers
    mVBAP = al::Vbap(mSpeakers, true);
    mVBAP.compile();
}

al::Vec3f VBAPRenderer::interpolateDir(const std::vector<Keyframe> &kfs, double t) {

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

    // Determine output length = longest source
    size_t totalSamples = 0;
    for (auto &[name, wav] : mSources) {
        totalSamples = std::max(totalSamples, wav.samples.size());
    }

    MultiWavData out;
    out.sampleRate = sr;
    out.channels = numSpeakers;
    out.samples.resize(numSpeakers);
    for (auto &c : out.samples) c.resize(totalSamples, 0.0f);

    // Create AudioIOData for VBAP to write into
    al::AudioIOData audioIO;
    audioIO.framesPerSecond(sr);
    audioIO.channelsOut(numSpeakers);
    
    // Process sample by sample (or use renderBuffer for blocks)
    for (size_t i = 0; i < totalSamples; i++) {
        double timeSec = (double)i / (double)sr;
        
        // Prepare output buffers for this frame
        std::vector<float> frameOutputs(numSpeakers, 0.0f);
        audioIO.frame(i);
        
        for (auto &[name, kfs] : mSpatial.sources) {
            const MonoWavData &src = mSources.at(name);
            float sample = (i < src.samples.size() ? src.samples[i] : 0.0f);
            
            // Get interpolated direction
            al::Vec3f dir = interpolateDir(kfs, timeSec);
            
            // Use VBAP's renderSample - this writes directly to audioIO
            mVBAP.renderSample(audioIO, dir, sample, i);
        }
        
        // Copy from audioIO to our output
        for (int ch = 0; ch < numSpeakers; ch++) {
            out.samples[ch][i] = audioIO.out(ch, i);
        }
    }

    return out;
}
