import sys
import os

# Resolve API setup
RESOLVE_SCRIPT_API = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules"
RESOLVE_SCRIPT_LIB = "/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so"
os.environ['RESOLVE_SCRIPT_API'] = RESOLVE_SCRIPT_API
os.environ['RESOLVE_SCRIPT_LIB'] = RESOLVE_SCRIPT_LIB
sys.path.append(RESOLVE_SCRIPT_API)

# Python 3.12 compatibility shim for imp module (removed in 3.12)
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
    if len(sys.argv) < 2:
        print("Usage: python3 import_video.py <video_path>")
        sys.exit(1)
        
    video_path = os.path.abspath(sys.argv[1])
    video_name = os.path.basename(video_path)
    
    try:
        import DaVinciResolveScript as dvr_script
        resolve = dvr_script.scriptapp("Resolve")
        if not resolve:
            print("Error: Could not connect to DaVinci Resolve.")
            sys.exit(1)
            
        project_manager = resolve.GetProjectManager()
        project = project_manager.GetCurrentProject()
        
        if not project:
            print("Error: No active project found. Run Step 1 first.")
            sys.exit(1)
            
        media_pool = project.GetMediaPool()
        root_folder = media_pool.GetRootFolder()
        
        # Import Video
        print(f"Importing video: {video_path}")
        media_items = media_pool.ImportMedia([video_path])
        if not media_items:
            print(f"Error: Failed to import video '{video_path}'. Check path.")
            sys.exit(1)
            
        video_clip = media_items[0]
        
        # Create Timeline
        timeline_name = "Main Timeline"
        print(f"Creating timeline '{timeline_name}' from video clip...")
        timeline = media_pool.CreateTimelineFromClips(timeline_name, [video_clip])
        
        if timeline:
            print(f"Successfully created timeline and imported video.")
            project_manager.SaveProject()
        else:
            print("Error: Failed to create timeline.")
            sys.exit(1)
            
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
