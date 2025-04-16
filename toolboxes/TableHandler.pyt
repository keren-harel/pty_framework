
import arcpy
import sys
from pathlib import Path
from importlib import reload

ROOT = str(Path(__file__).parents[1].absolute()) # ../pyt_framework
SHEET_NAME = "table_modification"

def add_to_root(folders):
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)
    for folder in folders:
        if rf"{ROOT}\{folder}" not in sys.path:
            sys.path.insert(1, rf"{ROOT}\{folder}")

add_to_root(['utils', 'enums', 'configuration'])

# Import dynamic modules with pyt_reload prefix
import utils.common as pyt_reload_common
import enums.excel_values as pyt_reload_excel_values

# Inline reloader of dynamic modules
[
    print(f"Reloaded {reload(module).__name__}")
    for module_name, module in globals().items()
    if module_name.startswith("pyt_reload")
]

# Import the Tool Importer function
from utils.common import *
from enums.excel_values import LayerNameExcel

class Toolbox:
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = "toolbox"

        # List of tool classes associated with this toolbox
        self.tools = [Tool_1, Tool_2]


class Tool_1:
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Create New Layer"
        self.description = ""

    def getParameterInfo(self):
        """Define the tool parameters."""

        param0 = arcpy.Parameter(
        displayName="Layer Name",
        name="layer_name",
        datatype="GPString",
        parameterType="Required",
        direction="Input")

        param0.filter.type = "ValueList"
        param0.filter.list = ["line_remarks_discussion_1", "line_remarks_discussion_2"]

        return [param0]

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        SPATIAL_REFERENCE = arcpy.SpatialReference(2039)

        aprx = arcpy.mp.ArcGISProject("CURRENT")
        gdb_path = aprx.defaultGeodatabase
        layer_name = parameters[0].valueAsText
        configuration_path = os.path.join(ROOT, "configuration")
        excel_path = os.path.join(configuration_path, "fields.xlsx")

        arcpy.env.overwriteOutput = True
        arcpy.CreateFeatureclass_management(gdb_path,
                                            layer_name,
                                            "Polyline",
                                            spatial_reference=SPATIAL_REFERENCE)

        df = load_excel_data(excel_path, SHEET_NAME)
        layer_df = df[df[ExcelColumns.TABLE_NAME.value] == layer_name]
        add_fields_to_layer_from_excel(layer_df, layer_name, gdb_path)

        aprx = arcpy.mp.ArcGISProject("CURRENT")
        active_map = aprx.activeMap
        active_map.addDataFromPath(os.path.join(gdb_path, layer_name))

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return

class Tool_2:
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Modify Layer"
        self.description = ""

    def getParameterInfo(self):
        """Define parameter definitions"""

        param1 = arcpy.Parameter(
        displayName="Layer Name",
        name="layer_name",
        datatype="GPString",
        parameterType="Required",
        direction="Input")

        param1.filter.type = "ValueList"
        param1.filter.list = ["final_stands_online_template", "kkl_line_remarks_online_template",
        "survey_points"]

        param0 = arcpy.Parameter(
            displayName="Select Layer from Map",
            name="in_layer",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )
        param0.filter.type = "ValueList"
        param0.filter.list = []

        return [param1, param0] # consider changing to dict or namedtuple

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""

        if parameters[0].valueAsText == "final_stands_online_template" or parameters[0].valueAsText == "kkl_line_remarks_online_template":

            aprx = arcpy.mp.ArcGISProject("CURRENT")
            map_obj = aprx.activeMap

            if map_obj:
                full_paths = [
                layer.dataSource
                for layer in map_obj.listLayers()
                if layer.isFeatureLayer and hasattr(layer, "dataSource")
            ]

                parameters[1].filter.list = full_paths

        if parameters[0].valueAsText == "survey_points":
            aprx = arcpy.mp.ArcGISProject("CURRENT")
            default_gdb = aprx.defaultGeodatabase

            if default_gdb:
                arcpy.env.workspace = default_gdb
                feature_classes = arcpy.ListFeatureClasses()

                if feature_classes:
                    full_paths = [f"{default_gdb}\\{fc}" for fc in feature_classes]
                    parameters[1].filter.list = full_paths

        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool.""" # TODO: change the docs!

        configuration_path = os.path.join(ROOT, "configuration")
        excel_path = os.path.join(configuration_path, "fields.xlsx")
        layer_name_excel = parameters[0].valueAsText
        layer_path = parameters[1].valueAsText
        gdb_path = os.path.dirname(layer_path)
        layer_name = os.path.basename(layer_path)

        df = load_excel_data(excel_path, SHEET_NAME)
        layer_df = df[df[ExcelColumns.TABLE_NAME.value] == layer_name_excel]

        is_verified = verify_required_fields(layer_path, layer_df)
        arcpy.AddMessage(is_verified)
        if not is_verified:
            arcpy.AddMessage("enter")
            return

        remove_extra_fields_from_layer(layer_df, layer_path)

        to_add_df = layer_df[layer_df[ExcelColumns.TO_ADD.value].notna()]
        add_fields_to_layer_from_excel(to_add_df, layer_name, gdb_path)

        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return

