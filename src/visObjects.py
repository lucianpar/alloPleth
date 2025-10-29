import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation
from .parser import parseTimecodeToSeconds, getPositionAtTime
import numpy as np


def animateObjects(objects_dict, duration_seconds, fps=10):
    """Create animation of ADM object positions over time."""
    
    # Debug: Print sample of our data
    print("\nFirst few time blocks for first object:")
    first_obj_name = list(objects_dict.keys())[0]
    first_blocks = objects_dict[first_obj_name][:3]  # First 3 blocks
    for block in first_blocks:
        print(f"Time: {block['rtime']}, Duration: {block['duration']}")
        print(f"Position: ({block['x']}, {block['y']}, {block['z']})")
    
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")
    
    numFrames = int(duration_seconds * fps)
    timePoints = np.linspace(0, duration_seconds, numFrames)
    print(f"\nAnimation setup:")
    print(f"Duration: {duration_seconds}s, FPS: {fps}")
    print(f"Frame count: {numFrames}")
    print(f"Time range: {timePoints[0]}s to {timePoints[-1]}s")
    
    def update(frame):
        ax.clear()
        time_seconds = timePoints[frame]
        
        # Debug first frame
        if frame == 0:
            print(f"\nFirst frame debug:")
            print(f"Time: {time_seconds}s")
            
        positions_found = False
        for name, blocks in objects_dict.items():
            position = getPositionAtTime(blocks, time_seconds)
            if position:
                positions_found = True
                x, y, z = position['x'], position['y'], position['z']
                ax.scatter(x, y, z, s=100, alpha=0.6)
                ax.text(x, y, z, name, fontsize=7)
        
        if frame == 0 and not positions_found:
            print("WARNING: No positions found in first frame!")
        
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        ax.set_title(f"ADM Object Positions - Time: {time_seconds:.2f}s")
        ax.set_xlim([-1.5, 1.5])
        ax.set_ylim([-1.5, 1.5])
        ax.set_zlim([-0.5, 1.5])
        
        return ax,
    
    anim = animation.FuncAnimation(fig, update, frames=numFrames, 
                                   interval=1000/fps, blit=False)
    plt.show()
    
    return anim
