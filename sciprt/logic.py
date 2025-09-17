# -*- coding: utf-8 -*-


import os
import sys
import time
import pprint
import re
try:
    import nuke
except ImportError:
    pass

def extract_frame_number(file_name) -> int:
    """
    Extract frame number from the file name, accommodating various padding styles.

    Args:
        file_name (str): The name of the file from which to extract the frame number.

    Returns:
        int: The extracted frame number, or None if not found.
    """
    match = re.search(r'(\d+)(?=\.[^.]+$)', file_name)
    if match:
        return int(match.group(1))
    return None

def get_exr_channels(file_path: str) -> list:
    """
    Extract channels from an EXR file, excluding specific layers.

    Args:
        file_path (str): The path to the EXR file.

    Returns:
        list: A list of channel names excluding specified layers.
    """
    try:
        exr_file = nuke.createNode("Read", inpanel=False)
        exr_file['file'].fromUserText(file_path)
        channels = exr_file.channels()
        
        # TODO: Add filtering options if needed
        _filter = ['N.', 'albedo.', 'normal.']

        filtered_channels = [
            ch for ch in channels
            if not any(ch.startswith(excluded) for excluded in _filter)
        ]
        nuke.delete(exr_file)
        return list(filtered_channels)
    except Exception as e:
        print(f"Error reading EXR file: {e}")
        return []

def validate_exr_channels(node: nuke.Node, frame_number: int, target_layers: list) -> tuple:
    """
    Validate EXR channels using Shuffle and CurveTool nodes.

    Args:
        node (nuke.Node): The Nuke node to analyze.
        frame_number (int): The frame number to evaluate.
        target_layers (list): List of target layers to validate.

    Returns:
        tuple: A tuple containing two lists - valid layers and empty layers.
    """
    empty_layers = []
    valid_layers = []

    shuffle = nuke.createNode('Shuffle', inpanel=False)
    shuffle.setInput(0, node)
    curve_tool = nuke.createNode('CurveTool', inpanel=False)
    w, h = curve_tool.width(), curve_tool.height()

    for layer in target_layers:
        shuffle['in'].setValue(layer)
        curve_tool['operation'].setValue('Max Luma Pixel')
        curve_tool['ROI'].setValue((0, 0, w, h))
        nuke.execute(curve_tool, frame_number, frame_number)
        max_data = curve_tool['maxlumapixvalue'].value()
        min_data = curve_tool['minlumapixvalue'].value()
        max_val = max(max_data)
        min_val = max(min_data)

        if max_val == 0 and min_val == 0:
            empty_layers.append(layer)
        else:
            valid_layers.append(layer)

    nuke.delete(curve_tool)
    nuke.delete(shuffle)

    return valid_layers, empty_layers

def analyze_sequence(dir_path: str, frame_step=1) -> tuple:
    """
    Analyze an image sequence in a directory to identify valid and empty channels.

    Args:
        dir_path (str): The path to the directory containing EXR files.
        frame_step (int, optional): The frame step for analysis. Defaults to 1.

    Returns:
        tuple: A tuple containing valid channels, empty channels, and the first seen frame for each channel.
    """
    print(f"Analyzing sequence in directory: {dir_path}\n")
    files = sorted([f for f in os.listdir(dir_path) if f.endswith('.exr')])
    if not files:
        print("No EXR files found in the directory.")
        return

    first_frame_path = os.path.join(dir_path, files[0]).replace(os.sep, '/')
    initial_channels = get_exr_channels(first_frame_path)
    if not initial_channels:
        print("Failed to retrieve channels from the first frame.")
        return

    print(f"Initial Channels: {initial_channels}")
    
    temp_channels = []
    for ch in initial_channels:
        if not ch.split('.')[0] in temp_channels:
            temp_channels.append(ch.split('.')[0])
    initial_channels = temp_channels

    remaining_channels = initial_channels[:]
    channel_status = {ch: True for ch in initial_channels}
    channel_first_seen = {}
    
    for i, file_name in enumerate(files):
        if not i % frame_step == 0:
            continue

        frame_path = os.path.join(dir_path, file_name).replace(os.sep, '/')
        if not os.path.exists(frame_path):
            print(f"File not found: {frame_path}")
            continue

        node = nuke.createNode("Read", f"file {{{frame_path}}}", inpanel=False)
        frame_number = extract_frame_number(file_name)
        if not frame_number:
            print(f"Could not extract frame number from file name: {file_name}")
            nuke.delete(node)
            continue

        valid_channels, empty_channels = validate_exr_channels(node, frame_number, remaining_channels)

        print(f"\n=== Frame {frame_number} Analysis ===")
        print(f"Valid Channels: {valid_channels}")
        print(f"Empty Channels: {empty_channels}")

        for ch in valid_channels:
            if ch not in channel_first_seen:
                channel_first_seen[ch] = frame_number

        for ch in valid_channels:
            channel_status[ch] = False

        remaining_channels = [ch for ch in remaining_channels if channel_status[ch]]

        nuke.delete(node)

        if not remaining_channels:
            print("All channels have been validated. Stopping further checks.")
            break

    empty_channels = [ch for ch, is_empty in channel_status.items() if is_empty]
    valid_channels = [ch for ch, is_empty in channel_status.items() if not is_empty]

    return valid_channels, empty_channels, channel_first_seen

def main(dir_path: str):
    start_time = time.time()
    frame_step = 10
    valid_channels, empty_channels, channel_first_seen = analyze_sequence(dir_path, frame_step)
    print("\n=== Final Channel Analysis ===\n")
    print(f"Valid Channels: {valid_channels}\n")
    print(f"Empty Channels: {empty_channels}")
    print(f"\nElapsed time: {time.time() - start_time:.2f} seconds\n")
    
    log_path = os.path.join(dir_path, "empty_channels.log")
    with open(log_path, "w") as f:
        f.write("[Empty Channels Analysis]\n")
        f.write(f"  - Directory: {dir_path}\n")
        f.write(f"  - Frame Step: {frame_step}\n")
        f.write(f"  - Elapsed Time: {time.time() - start_time:.2f} seconds\n\n")
        f.write(f"[Valid Channels]: {valid_channels}\n\n")
        f.write(f"[Empty Channels]: {empty_channels}\n\n")
        f.write("[Valid Channels Data]\n")
        f.write(pprint.pformat(channel_first_seen))
            
    print(f"Log file saved: {log_path}")
    

if __name__ == "__main__":
    directory_path = "/path/to/your/image_sequence"
    main(directory_path)
