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
    try:
        import DaVinciResolveScript as dvr_script
        resolve = dvr_script.scriptapp("Resolve")
        if not resolve:
            print("Error: Could not connect to DaVinci Resolve. Is it running?")
            sys.exit(1)
            
        project_manager = resolve.GetProjectManager()
        project_name = "translate"
        
        # Check if project exists
        existing_project = project_manager.LoadProject(project_name)
        if existing_project:
            print(f"Project '{project_name}' already exists. Deleting for a clean start...")
            project_manager.CloseProject(existing_project)
            if project_manager.DeleteProject(project_name):
                print(f"Successfully deleted existing project '{project_name}'.")
            else:
                print(f"Error: Failed to delete project '{project_name}'.")
                sys.exit(1)
        
        # Create new project
        new_project = project_manager.CreateProject(project_name)
        if new_project:
            print(f"Successfully created new project '{project_name}'.")
        else:
            print(f"Error: Failed to create project '{project_name}'.")
            sys.exit(1)
            
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
