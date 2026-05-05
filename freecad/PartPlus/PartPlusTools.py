# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileNotice: Part of the PartPlus addon.
# -*- coding: utf-8 -*-
'''
This is a tool collection for the PartPlus workbench
'''

import FreeCAD as App
import FreeCADGui as Gui
import Part
import os
from PySide import QtCore
from PySide import QtGui
from PySide import QtWidgets
from PySide.QtGui import (QGroupBox, QMessageBox, QIcon)
from PySide.QtWidgets import (
    QGridLayout,
    QLabel,
    QCheckBox,
    QDoubleSpinBox,
    QPushButton,
    QRadioButton,
    QButtonGroup,
    QLineEdit
)

MOD_PATH = os.path.dirname(__file__)
ICONPATH = os.path.join(MOD_PATH, "resources", "icons")
SYMBOLSPATH = os.path.join(MOD_PATH, "resources", "symbols")
#TRANSLATIONSPATH = os.path.join(MOD_PATH, "resources", "translations")
##- Adds the translations folder path to the default search paths
#Gui.addLanguagePath(TRANSLATIONSPATH)
#Gui.updateLocale()

QT_TRANSLATE_NOOP = App.Qt.QT_TRANSLATE_NOOP

def addProperty(
    object,
    property_type,
    property_name,
    property_tip,
    default_value = None,
    parameter_group = "Parameters",
    read_only = False,
    is_hiddden = False,
    attributes = 0
):
    '''
    Adds a property to a given object.

    Arguments:
        object: The object to which the property should be added.
        property_type: The type of the property (e.g., "App::PropertyLength",
            "App::PropertyBool").
        property_name: The name of the property. Non-translatable.
        property_tip: The tooltip for the property. Need to be translated
            from outside.
        default_value: The default value for the property (optional).
        parameter_group: The parameter group to which the property should
            belong (default is "Parameters"). If group name is "Hidden",
            the property will not be shown in the Property View.
        read_only: Property can not be edited.
        is_hiddden: Property is not shown in the Property View.
    '''
    #print("addProperty object: ", object)
    if not hasattr(object, property_name):
        #print("hasattr", object)
        if parameter_group == "Hidden":
            is_Hiddden = True
        object.addProperty(
            property_type,
            property_name,
            parameter_group,
            property_tip,
            attributes,
            read_only,
            is_hiddden
        )
        if default_value is not None:
            setattr(object, property_name, default_value)

def addLengthProperty(
    object,
    property_name,
    property_tip,
    default_value,
    parameter_group = "Parameters"
):
    addProperty(
        object,
        "App::PropertyLength",
        property_name,
        property_tip,
        default_value,
        parameter_group
    )

def addBoolProperty(
    object,
    property_name,
    property_tip,
    default_value,
    parameter_group = "Parameters"
):
    addProperty(
        object,
        "App::PropertyBool",
        property_name,
        property_tip,
        default_value,
        parameter_group
    )

def addAngleProperty(
    object,
    property_name,
    property_tip,
    default_value,
    parameter_group = "Parameters"
):
    addProperty(
        object,
        "App::PropertyAngle",
        property_name,
        property_tip,
        default_value,
        parameter_group
    )

def addStringProperty(
    object,
    property_name,
    property_tip,
    default_value,
    parameter_group = "Parameters"
):
    addProperty(
        object,
        "App::PropertyString",
        property_name,
        property_tip,
        default_value,
        parameter_group
    )

def addEnumProperty(
    object,
    property_name,
    property_tip,
    default_value,
    parameter_group = "Parameters"
):
    addProperty(
        object,
        "App::PropertyEnumeration",
        property_name,
        property_tip,
        default_value,
        parameter_group
    )

def isSketchObject(obj):
    return obj.TypeId.startswith("Sketcher::")

def getParentBody(obj):
    if hasattr(obj, "getParent"):
        return obj.getParent()
    if hasattr(obj, "getParents"):  # Probably FreeCadLink version.
        if len(obj.getParents()) == 0:
            return None
        return obj.getParents()[0][0]
    return None

def isPartDesign(obj):
    if isSketchObject(obj):
        parent = getParentBody(obj)
        if parent is None:
            return False
        return isinstance(parent, Part.BodyBase)
    return obj.TypeId.startswith("PartDesign::")

def updateTaskTitleIcon(task):
    from PySide import QtGui
    if hasattr(task, "form"):
        if hasattr(task.obj.ViewObject.Proxy, "getIcon"):
            task.form.setWindowIcon(
                QtGui.QIcon(task.obj.ViewObject.Proxy.getIcon())
            )
    return

def loadIcon(self, shape_type = "Solid"):
    '''Loads an icon from an embedded svg file'''
    #- Load an svg file colored accordiing to the shape type
    svg_bytes = bytearray(
        self.loadSvg(shape_type),
        encoding='utf-8'
    )
    #- Create a QImage from the svg file
    qimage = QtGui.QImage.fromData(svg_bytes)
    #- Create a QIcon via a QPixmap from the QImage
    icon = QtGui.QIcon(QtGui.QPixmap(qimage))
    return icon #self.icons[self.Object.ShapeStatus]

class BaseShape:
    '''
    Shared content for all related commands
    '''
    def __init__(self, obj):
        self.make_attachable(obj)

    def make_attachable(self, obj):
        '''
        Needed to make this object "attachable",
        aka able to attach parameterically to other objects
        cf. https://wiki.freecad.org/Scripted_objects_with_attachment
        '''
        obj.addExtension("Part::AttachExtensionPython")
        # unveil the "Placement" property, which seems hidden by default in PartDesign
        obj.setEditorMode("Placement", 0)  # non-readonly non-hidden

    def modifiedWire(
        self,
        wire_list = None,
        normal = None,
        length = 10.0,
        fillet_profile = False,
        profile_radius = 4.0,
        profile_thickness = 2.0,
        profile_offset = "Middle",
        sign = 1.0
    ):
        '''
        Refines the given wire list derived from the profile sketch
        according to given thickness and inner radius of the profile.
        It also fillets sharp corners with a constant inner radius.

        To take left and right bends into accont we have to find the
        centerline that uses the same radius for both bends that is
        the inner radius extended by one half of the thickness.
        The result is shifted/copied in the opposite direction of
        the thickness and returned (to be used to create the inner surface
        and finally be offset to create a solid shape in a later step.

        This works via exruding prismatic shapes from the wires.
        '''
        #- Extrude a prismatic shape of faces from the wire list.
        #  This is the center line for the Middle option
        wire_extr = wire_list.extrude(normal * sign * length)
        # Part.show(wire_extr, "wire_extr_Middle")

        if profile_thickness == 0.0:  # short-cut for 2D spine wires
            try:
                result_extr = wire_extr.makeFillet(
                    (profile_radius),
                    6.0,  # Test for conical fillets
                    wire_extr.Edges
                )  # May fail if fillets would consume whole edges
            except:
                result_extr = wire_extr
                print("Cannot fillet profile!")
                print("Check if fillets would consume whole edges")
            return result_extr

        #- Shift the prismatic shape halfway in positive or negative
        #  thickness direction to gain the centerline for either
        #  the Inside option, or the Outside option.
        if profile_offset == "Inside":
            wire_extr = wire_extr.makeOffsetShape(
                profile_thickness / 2.0 * sign,
                0.0,
                fill=False,
                join=2
            )
        elif profile_offset == "Outside":
            wire_extr = wire_extr.makeOffsetShape(
                -profile_thickness / 2.0 * sign,
                0.0,
                fill=False,
                join=2
            )
        # Part.show(wire_extr, "wire_extr_InOut")
        #- Create fillets at non-tangen face connections of the copy
        if fillet_profile:
            try:
                result_extr = wire_extr.makeFillet(
                    (profile_radius + profile_thickness / 2.0),
                    wire_extr.Edges
                )  # May fail if fillets would consume whole edges
            except:
                result_extr = wire_extr
                print("Cannot fillet profile!")
                print("Check if fillets would consume whole edges")
        else:
            result_extr = wire_extr
        # Part.show(filleted_extr, "filleted_extr_center")
        #- Shift the result shape - thickness layer
        result_extr = result_extr.makeOffsetShape(
            -profile_thickness / 2.0 * sign,
            0.0,
            fill = False,
            join = 2
        )
        # Part.show(result_extr, "filleted_extr_final")
        return result_extr

    def joinWithBaseFeature(
        self,
        base_shape,
        new_shape,
        shape_type = "Feature_Union"
    ):
        if shape_type == "Feature_Union":
            result_shape = base_shape.fuse(new_shape)
        elif shape_type == "Feature_Difference":
            result_shape = base_shape.cut(new_shape)
        elif shape_type == "Feature_Intersection":
            result_shape = base_shape.common(new_shape)
        else:
            shape_type = "Feature_Union"
            result_shape = base_shape.fuse(new_shape)

        result_shape.transformShape(
            self.obj.Placement.inverse().toMatrix(), True
        )  # account for setting obj.Shape below moves the shape
        #    to obj.Placement, ignoring its previous placement
        return shape_type, result_shape
        #self.obj.ShapeType = shape_type
        #self.obj.Shape = result_shape

    def finishNewShape(self, obj, new_shape):
        '''
        Finishes a newly created shape either as a Part solid or
        as a PartDesign feature depending on the shape type
        '''
        if hasattr(obj, "BaseFeature"):
            # Only PartDesign bodies and features have a base feature property
            if obj.BaseFeature != None:
                # If a base feature exists the new shape has to be fused with,
                # cut from, or intersected with the base feature
                new_shape.Placement = (
                    obj.Placement
                )  # ensure the shape is placed correctly before joining
                obj.ShapeType, obj.Shape = self.joinWithBaseFeature(
                    obj.BaseFeature.Shape,
                    new_shape,
                    obj.ShapeType
                )
            else:
                # The new shape is used as base shape directly
                obj.ShapeType = "Feature_Base"
                obj.Shape = new_shape
        else:
            # not a PartDesign body
            obj.ShapeType = "Solid"
            obj.Shape = new_shape

        return

    def generatePartPlusShape(self, obj):
        '''
        This method has to return the TopoShape of the gear.
        '''
        raise NotImplementedError("generateNewShape not implemented")

    def onChanged(self, fp, prop):
        '''Do something when a property has changed'''
        # App.Console.PrintMessage("Changed property: " + str(prop) + "\n")
        pass

    def loads(self, state):
        pass

    def dumps(self):
        pass

    def __setstate__(self, state):
        pass

    def __getstate__(self):
        pass


class ViewProviderPartPlus:
    '''
    The base Viewprovider for the PartPlus shapes
    '''

    def __init__(self, obj, icon_fn=None):
        '''Receives the new object from commands.py'''
        #- Set this object to the proxy object of the actual view provider
        obj.Proxy = self
        self.Object = obj.Object

        self._check_attr()
        if icon_fn:
            self.icon_fn = icon_fn

    def _check_attr(self):
        '''
        Check for missing attributes.
        '''
        if not hasattr(self, "icon_fn"):
            self.icon_fn = self.loadIcon("Feature_Base") #"Feature_Intersection")  # Check in commands
            setattr(
                self,
                "icon_fn",
                self.icon_fn,
            )

    def attach(self, obj):
        self.Object = obj.Object  # from SheetMetal

    def getIcon(self):
        '''Returns the embedded icon'''
        self._check_attr()
        return self.icon_fn

    def setupContextMenu(self, viewObject, menu):
        action = menu.addAction(App.Qt.translate(
            "QObject", "Edit %1").replace("%1", viewObject.Object.Label))
        action.triggered.connect(lambda: self.startDefaultEditMode(viewObject))
        return False

    def startDefaultEditMode(self, viewObject):
        '''Launched by right-click'''
        viewObject.Document.setEdit(viewObject.Object, 0)

    def setEdit(self, vobj, mode):
        if mode != 0:
            return None
        if not hasattr(self, "getTaskPanel"):
            return False
        panel = self.getTaskPanel(vobj.Object)
        updateTaskTitleIcon(panel)
        if isPartDesign(self.Object):
            self.Object.ViewObject.Visibility = True
        App.ActiveDocument.openTransaction(self.Object.Name)
        Gui.Control.showDialog(panel)
        return True

    def unsetEdit(self, _vobj, _mode):
        Gui.Control.closeDialog()
        if hasattr(_vobj.Object, "ProfileShape"):
            _vobj.Object.ProfileShape.ViewObject.Visibility = False
            #_vobj.Object.ProfileShape[0].ViewObject.Visibility = False
        _vobj.Object.ViewObject.Visibility = True
        return False

    def dumps(self):
        self._check_attr()
        return {"icon_fn": self.icon_fn}

    def loads(self, state):
        if state and "icon_fn" in state:
            self.icon_fn = state["icon_fn"]

from FreeCAD import Console
Console.PrintLog('freecad/PartPlus/PartPlusTools.py\n')
