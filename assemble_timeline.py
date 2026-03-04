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
            
        # Get Frame Rate to calculate frames from timestamps
        frame_rate = float(project.GetSetting("timelineFrameRate"))
        print(f"Timeline Frame Rate: {frame_rate}")

        input_path = "how_en_audio.json"
        if not os.path.exists(input_path):
            print(f"Error: {input_path} not found. Run Step 6 first.")
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

        segments = data.get("segments", [])
        print(f"Importing and placing {len(segments)} audio clips...")

        # To avoid adding one by one which is slow, we can import all first
        audio_paths = []
        for segment in segments:
            path = segment.get("audio_path")
            if path and os.path.exists(path):
                # Ensure absolute path
                abs_path = os.path.abspath(path)
                audio_paths.append(abs_path)
            else:
                print(f"Warning: Audio file not found for segment starting at {segment.get('start')}")

        print("Importing media to pool...")
        imported_clips = media_pool.ImportMedia(audio_paths)
        if not imported_clips:
            print("Error: Failed to import clips.")
            sys.exit(1)

        # Map filename to clip object for easy lookup
        clip_map = {}
        for clip in imported_clips:
            clip_map[clip.GetName()] = clip

        # Find the original video clip in the Media Pool
        video_clip = None
        for clip in root_folder.GetClipList():
            if clip.GetName() == "how.mp4":
                video_clip = clip
                break
        
        if not video_clip:
            print("Warning: Original video clip 'how.mp4' not found in Media Pool root.")

        print("Preparing clips for precise timeline placement (Video Track 2, Audio Track 2)...")
        
        import wave
        
        success_count = 0
        timeline_items = []

        for i, segment in enumerate(segments):
            start_time = segment.get("start")
            end_time = segment.get("end")
            audio_path = segment.get("audio_path")
            filename = f"en_{i+1:03d}.wav"
            audio_clip = clip_map.get(filename)
            
            if not audio_clip or not audio_path or not os.path.exists(audio_path):
                continue

            # Calculate start frame in timeline
            record_frame = int(start_time * frame_rate)
            
            # Get audio clip length in frames
            try:
                with wave.open(audio_path, 'rb') as f:
                    n_frames = f.getnframes()
                    sample_rate = f.getframerate()
                    duration_sec = n_frames / float(sample_rate)
                    audio_duration_frames = int(duration_sec * frame_rate)
            except Exception as e:
                print(f"Warning: Could not get duration for {filename}: {e}")
                audio_duration_frames = int((end_time - start_time) * frame_rate)

            # Place Audio on Audio Track 2 (mediaType 2 = Audio)
            audio_info = {
                "mediaPoolItem": audio_clip,
                "startFrame": 0,
                "endFrame": audio_duration_frames,
                "recordFrame": record_frame,
                "trackIndex": 2,
                "mediaType": 2
            }
            
            # Place Video Segment on Video Track 2 (if video_clip found, mediaType 1 = Video)
            if video_clip:
                video_start_frame = int(start_time * frame_rate)
                video_end_frame = video_start_frame + audio_duration_frames # match audio duration
                
                video_info = {
                    "mediaPoolItem": video_clip,
                    "startFrame": video_start_frame,
                    "endFrame": video_end_frame,
                    "recordFrame": record_frame,
                    "trackIndex": 2,
                    "mediaType": 1
                }
                timeline_items.append(video_info)

            timeline_items.append(audio_info)
            success_count += 1

        print(f"Appending {len(timeline_items)} items to timeline...")
        # A single API call to append avoids placement drifting
        media_pool.AppendToTimeline(timeline_items)

        print(f"Successfully prepared and placed {success_count} segments on the timeline.")
        project_manager.SaveProject()
            
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
