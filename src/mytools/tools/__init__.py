"""Tool plugin loader – fallback if entry points not used."""
from pathlib import Path
import importlib.util
import inspect
import sys
from .base import BaseTool

def discover_tools(tool_dir=None):
    """Scan tools directory and load all subclasses of BaseTool."""
    if tool_dir is None:
        tool_dir = Path(__file__).parent
    tools = {}
    for file in tool_dir.glob("*.py"):
        if file.name == "__init__.py" or file.name == "base.py":
            continue
        module_name = f"mytools.tools.{file.stem}"
        spec = importlib.util.spec_from_file_location(module_name, file)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and issubclass(obj, BaseTool)
                        and obj != BaseTool):
                    tools[file.stem] = obj
    return tools