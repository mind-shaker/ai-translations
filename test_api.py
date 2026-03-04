import os
import sys
import importlib.util
import types

RESOLVE_SCRIPT_API = '/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules'
RESOLVE_SCRIPT_LIB = '/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so'
os.environ['RESOLVE_SCRIPT_API'] = RESOLVE_SCRIPT_API
os.environ['RESOLVE_SCRIPT_LIB'] = RESOLVE_SCRIPT_LIB
sys.path.append(RESOLVE_SCRIPT_API)

def load_dynamic(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

imp = types.ModuleType('imp')
imp.load_dynamic = load_dynamic
sys.modules['imp'] = imp

import DaVinciResolveScript as dvr_script
resolve = dvr_script.scriptapp('Resolve')
mp = resolve.GetProjectManager().GetCurrentProject().GetMediaPool()
tl = resolve.GetProjectManager().GetCurrentProject().GetCurrentTimeline()

print("MediaPool.AppendToTimeline doc:")
print(help(mp.AppendToTimeline))

print("Timeline methods:")
print([attr for attr in dir(tl) if not attr.startswith('_')])
