import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation
from .parser import parseTimecodeToSeconds, getPositionAtTime
import numpy as np


def animateObjects(objects_dict, duration_seconds, fps=10, speed_multiplier=1.0):
    """
        objects_dict (dict): Dictionary of object positions
        duration_seconds (float): Duration to animate
        fps (int): Frames per second for animation
        speed_multiplier (float): Multiplier for animation speed (e.g., 2.0 = twice as fast)
    """
    
    # Calculate actual time range from the data
    min_time = float('inf')
    max_time = 0
    for name, blocks in objects_dict.items():
        for block in blocks:
            start = parseTimecodeToSeconds(block['rtime'])
            duration = parseTimecodeToSeconds(block['duration'])
            min_time = min(min_time, start)
            max_time = max(max_time, start + duration)
    
    print(f"Data time range: {min_time:.2f}s to {max_time:.2f}s")
    print(f"Playback speed: {speed_multiplier}x")
    
    # Use data's time range if shorter than requested duration
    duration_seconds = min(duration_seconds, max_time)
    
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")
    
    numFrames = int(duration_seconds * fps)
    timePoints = np.linspace(min_time, duration_seconds, numFrames)
    
    def update(frame):
        ax.clear()
        time_seconds = timePoints[frame]
        
        positions_found = False
        for name, blocks in objects_dict.items():
            position = getPositionAtTime(blocks, time_seconds)
            if position:
                positions_found = True
                x, y, z = position['x'], position['y'], position['z']
                ax.scatter(x, y, z, s=100, alpha=0.6)
                ax.text(x, y, z, name, fontsize=7)
                
                # Add trajectory line (optional)
                prev_positions = []
                for t in timePoints[:frame+1]:
                    pos = getPositionAtTime(blocks, t)
                    if pos:
                        prev_positions.append((pos['x'], pos['y'], pos['z']))
                if prev_positions:
                    prev_positions = np.array(prev_positions)
                    ax.plot(prev_positions[:,0], prev_positions[:,1], prev_positions[:,2], 
                           alpha=0.2, linestyle='--')
        
        if frame == 0 and not positions_found:
            print(f"WARNING: No positions found at time {time_seconds:.2f}s")
        
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        ax.set_title(f"ADM Object Positions - Time: {time_seconds:.2f}s (Speed: {speed_multiplier}x)")
        ax.set_xlim([-1.5, 1.5])
        ax.set_ylim([-1.5, 1.5])
        ax.set_zlim([-0.5, 1.5])
        ax.grid(True)
        
        return ax,
    
    # Adjust interval based on speed multiplier
    interval = (1000/fps) / speed_multiplier
    
    anim = animation.FuncAnimation(fig, update, frames=numFrames, 
                                   interval=interval, blit=False)
    plt.show()
    
    return anim
