import sys
import os
import json

# Resolve API setup
RESOLVE_SCRIPT_API = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules"
RESOLVE_SCRIPT_LIB = "/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so"
os.environ['RESOLVE_SCRIPT_API'] = RESOLVE_SCRIPT_API
os.environ['RESOLVE_SCRIPT_LIB'] = RESOLVE_SCRIPT_LIB
sys.path.append(RESOLVE_SCRIPT_API)

# Python 3.12 compatibility shim
import types
import importlib.util

def load_dynamic(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is not None and spec.loader is not None:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    return None

imp = types.ModuleType('imp')
imp.load_dynamic = load_dynamic
sys.modules['imp'] = imp

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 assemble_timeline.py <video_path> <metadata.json>")
        sys.exit(1)

    video_filename = sys.argv[1]  # e.g. how.mp4
    input_path = sys.argv[2]      # e.g. how_fixed_en_audio.json

    try:
        import DaVinciResolveScript as dvr_script
        resolve = dvr_script.scriptapp("Resolve")
        if not resolve:
            print("Error: Could not connect to DaVinci Resolve.")
            sys.exit(1)

        project_manager = resolve.GetProjectManager()
        project = project_manager.GetCurrentProject()

        project_name = "translate"
        if not project or project.GetName() != project_name:
            print(f"Loading project '{project_name}'...")
            project = project_manager.LoadProject(project_name)
            if not project:
                print(f"Error: Project '{project_name}' not found. Run Step 1 first.")
                sys.exit(1)

        timeline = project.GetCurrentTimeline()
        if not timeline:
            print("Error: No timeline found. Run Step 2 first.")
            sys.exit(1)

        frame_rate = float(project.GetSetting("timelineFrameRate"))
        start_offset = timeline.GetStartFrame()
        print(f"Timeline Frame Rate: {frame_rate}")
        print(f"Timeline Start Offset: {start_offset} frames")

        if not os.path.exists(input_path):
            print(f"Error: {input_path} not found.")
            sys.exit(1)

        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        media_pool = project.GetMediaPool()
        root_folder = media_pool.GetRootFolder()

        # Create or find "English Dub" folder in Media Pool
        dub_folder = None
        for folder in root_folder.GetSubFolderList():
            if folder.GetName() == "English Dub":
                dub_folder = folder
                break
        if not dub_folder:
            dub_folder = media_pool.AddSubFolder(root_folder, "English Dub")

        media_pool.SetCurrentFolder(dub_folder)

        # New JSON format: data has "segments" list with "start_seconds", "end_seconds", "audio_path"
        segments = data.get("segments", [])
        print(f"Found {len(segments)} segments in JSON.")

        # Collect valid audio paths
        audio_paths = []
        for segment in segments:
            path = segment.get("audio_path")
            if path and os.path.exists(path):
                audio_paths.append(os.path.abspath(path))
            else:
                idx = segment.get("index", "?")
                print(f"Warning: Audio file not found for segment {idx} (start: {segment.get('start', '?')})")

        if not audio_paths:
            print("Error: No valid audio files found.")
            sys.exit(1)

        print(f"Importing {len(audio_paths)} audio files to media pool...")
        imported_clips = media_pool.ImportMedia(audio_paths)
        if not imported_clips:
            print("Error: Failed to import clips.")
            sys.exit(1)

        # Map filename -> clip object
        clip_map = {}
        for clip in imported_clips:
            clip_map[clip.GetName()] = clip

        # Find original video clip in Media Pool
        video_clip = None
        for clip in root_folder.GetClipList():
            if clip.GetName() == video_filename:
                video_clip = clip
                break
        if not video_clip:
            print(f"Warning: Original video clip '{video_filename}' not found in Media Pool root.")

        print("Preparing clips for timeline placement (Audio Track 2)...")

        import wave

        success_count = 0
        timeline_items = []

        for segment in segments:
            audio_path = segment.get("audio_path")
            if not audio_path or not os.path.exists(audio_path):
                continue

            # Use start_seconds from new JSON format
            start_seconds = segment.get("start_seconds")
            end_seconds = segment.get("end_seconds")
            if start_seconds is None or end_seconds is None:
                print(f"Warning: Missing timing for segment {segment.get('index', '?')}, skipping.")
                continue

            # Get filename to look up clip in map
            filename = os.path.basename(audio_path)
            audio_clip = clip_map.get(filename)
            if not audio_clip:
                print(f"Warning: Clip '{filename}' not found in imported clips, skipping.")
                continue

            # Calculate start frame in timeline
            record_frame = start_offset + int(start_seconds * frame_rate)

            # Get actual audio duration from WAV file
            try:
                with wave.open(audio_path, 'rb') as wf:
                    n_frames = wf.getnframes()
                    sample_rate = wf.getframerate()
                    duration_sec = n_frames / float(sample_rate)
                    audio_duration_frames = int(duration_sec * frame_rate)
            except Exception as e:
                print(f"Warning: Could not read WAV for '{filename}': {e}")
                audio_duration_frames = int((end_seconds - start_seconds) * frame_rate)

            timeline_items.append({
                "mediaPoolItem": audio_clip,
                "startFrame": 0,
                "endFrame": audio_duration_frames,
                "recordFrame": record_frame,
                "trackIndex": 2,
                "mediaType": 2
            })
            success_count += 1

        print(f"Placing {len(timeline_items)} audio clips on timeline...")
        media_pool.AppendToTimeline(timeline_items)

        print(f"\nDone! Successfully placed {success_count}/{len(segments)} segments on the timeline.")
        project_manager.SaveProject()

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()