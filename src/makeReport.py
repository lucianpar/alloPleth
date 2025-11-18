#!/usr/bin/env python3
# filepath: src/generate_report.py
import os
import json
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from src.createSpatialInstructions import assignChannels, loadProcessedData, parseTimecodeToSeconds

def load_all(processed_dir="processedData"):
    os.makedirs(processed_dir, exist_ok=True)
    return loadProcessedData(processed_dir)

def summarize(data):
    # reuse assignChannels to get mapping and audio status (assignChannels returns (mapping, audio_status))
    channel_mapping, audio_status = assignChannels(data)

    # compute channel -> has_audio mapping (1-indexed channels in channel_mapping)
    channel_has_audio = {}
    for name, ch in channel_mapping.items():
        channel_has_audio[ch] = audio_status.get(name, False)

    # compute static/dynamic counts by inspecting objectData
    static = 0
    dynamic = 0
    object_details = {}
    for obj_name, blocks in data.get("objectData", {}).items():
        if not blocks:
            continue
        # determine dynamic
        is_dynamic = False
        if len(blocks) > 1:
            first_pos = (blocks[0].get("x", 0), blocks[0].get("y", 0), blocks[0].get("z", 0))
            is_dynamic = any((b.get("x", 0), b.get("y", 0), b.get("z", 0)) != first_pos for b in blocks)
        if is_dynamic:
            dynamic += 1
        else:
            static += 1
        object_details[obj_name] = {
            "dynamic": is_dynamic,
            "channel": channel_mapping.get(obj_name)
        }

    return {
        "channel_mapping": channel_mapping,
        "channel_has_audio": channel_has_audio,
        "static_count": static,
        "dynamic_count": dynamic,
        "object_details": object_details,
        "global": data.get("globalData", {})
    }

def make_report(summary, output_pdf="forExport/report.pdf"):
    os.makedirs(os.path.dirname(output_pdf) or ".", exist_ok=True)
    with PdfPages(output_pdf) as pdf:
        # Page 1: text summary
        fig = plt.figure(figsize=(8.5, 11))
        fig.clf()
        txt = []
        txt.append("SonoPleth - Processing Report")
        txt.append("")
        txt.append("Global metadata:")
        for k, v in (summary["global"] or {}).items():
            txt.append(f"  {k}: {v}")
        txt.append("")
        txt.append(f"Total channels assigned: {len(summary['channel_mapping'])}")
        txt.append(f"Channels with audio: {sum(1 for v in summary['channel_has_audio'].values() if v)}")
        txt.append(f"Static objects: {summary['static_count']}")
        txt.append(f"Dynamic objects: {summary['dynamic_count']}")
        txt.append("")
        txt.append("Note: Channel numbering: DirectSpeakers first, then objects.")
        fig.text(0.02, 0.98, "\n".join(txt), va="top", fontsize=10, family="monospace")
        pdf.savefig(fig)
        plt.close(fig)

        # Page 2: channel audio bar chart
        channels = sorted(summary["channel_has_audio"].keys())
        has_audio = [1 if summary["channel_has_audio"].get(c, False) else 0 for c in channels]
        fig, ax = plt.subplots(figsize=(10,4))
        ax.bar(channels, has_audio, color=["tab:blue" if v else "lightgray" for v in has_audio])
        ax.set_xlabel("Channel number")
        ax.set_ylabel("Contains audio (1=yes, 0=no)")
        ax.set_title("Per-channel audio presence")
        ax.set_ylim(-0.1, 1.1)
        pdf.savefig(fig)
        plt.close(fig)

        # Page 3: static vs dynamic pie
        labels = ["Static", "Dynamic"]
        sizes = [summary["static_count"], summary["dynamic_count"]]
        fig, ax = plt.subplots(figsize=(6,6))
        if sum(sizes) == 0:
            ax.text(0.5, 0.5, "No objects found", ha="center", va="center")
        else:
            ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90, colors=["#66c2a5", "#fc8d62"])
        ax.set_title("Static vs Dynamic objects")
        pdf.savefig(fig)
        plt.close(fig)

    print(f"Report written to {output_pdf}")

if __name__ == "__main__":
    data = load_all("processedData")
    summary = summarize(data)
    make_report(summary, output_pdf="forExport/report.pdf")