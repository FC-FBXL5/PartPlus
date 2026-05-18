# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileNotice: Part of the PartPlus addon.
# -*- coding: utf-8 -*-
'''
This Tool creates a distribution shape, either a PartDesign feature or
a separate Part solid
'''

import FreeCAD as App
import FreeCADGui as Gui

import Part
import os
import math

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

from .PartPlusTools import (
    BaseShape,
    ViewProviderPartPlus,
    addLengthProperty,
    addBoolProperty,
    addAngleProperty,
    addStringProperty,
    addEnumProperty,
    updateTaskTitleIcon,
    loadIcon,
)

MOD_PATH = os.path.dirname(__file__)
ICONPATH = os.path.join(MOD_PATH, "resources", "icons")
SYMBOLSPATH = os.path.join(MOD_PATH, "resources", "symbols")
#TRANSLATIONSPATH = os.path.join(MOD_PATH, "resources", "translations")
##- Adds the translations folder path to the default search paths
#Gui.addLanguagePath(TRANSLATIONSPATH)
#Gui.updateLocale()

translate = App.Qt.translate
QT_TRANSLATE_NOOP = App.Qt.QT_TRANSLATE_NOOP

class DistributionShape(BaseShape):
    '''
    Adds a distribution shape
    '''
    def __init__(self, obj):
        super(DistributionShape, self).__init__(obj)
        '''
        Adds properties to the object
        '''

        #- Create a Spine property and
        #  store the first selected item (spine) in it:
        obj.addProperty(
            "App::PropertyLinkSub",
            "Spine",
            "BaseSpine",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "2D shape defining the spine"
            )
        ).Spine = Gui.Selection.getSelection()[0]
        #- Create a ProfileShapes property and store the rest of
        #  the selected items (profile, and cross-sections) in it:
        obj.addProperty(
            "App::PropertyLinkSubList",
            "Sections",
            "BaseSections",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "List of 2D shapes defining the profile and the cross-sections"
            )
        ).Sections = Gui.Selection.getSelection()[1:]
        # This command could not be invoked as long as the selecction does not
        # contain two or more sketches, shape binders, or sub-shape binders.

        #- Properties altered by this tool:
        self.addDistributionProperties(obj)

        self.obj = obj
        obj.Proxy = self

    def addDistributionProperties(self, obj):
        '''
        Creates the Distribution shape parameters including default values
        required for the initial build (without checking their existence)
        '''
        SHAPE_TYPES = (
            "Feature_Union",
            "Feature_Difference",
            "Feature_Intersection",
            "Feature_Base",
            "Solid",
            "Button"
        )
        PROFILE_OFFSETS = ("Middle", "Inside", "Outside")
        SPINE_MODES = ("Slide Parallel", "Right Corners", "Round Corners")
        addLengthProperty(
            obj,
            "ProfileThickness",
            translate(
                "App::Property",
                "Thickness of a hollow profile"
            ),
            2.0,
            "ParametersSections"
        )
        addLengthProperty(
            obj,
            "ProfileRadius",
            translate(
                "App::Property",
                "Inner radius of automatically filleted profile edges"
            ),
            4.0,
            "ParametersSections"
        )
        addBoolProperty(
            obj,
            "HollowProfile",
            translate(
                "App::Property",
                "Creates a hollow shape from a closed profile"
            ),
            False,
            "ParametersSections"
        )
        addBoolProperty(
            obj,
            "FilletProfile",
            translate(
                "App::Property",
                "Applies fillets to sharp corners of the profile"
            ),
            True,
            "ParametersSections"
        )
        addBoolProperty(
            obj,
            "FrenetMode",
            translate(
                "App::Property",
                "Toggles the Frenet mode for cross-sections"
            ),
            False,
            "ParametersDistribution"
        )
        addEnumProperty(
            obj,
            "ShapeType",
            translate(
                "App::Property",
                "Type of the created shape"
            ),
            SHAPE_TYPES,
            "ParametersShape"
        )
        addEnumProperty(
            obj,
            "ProfileOffset",
            translate(
                "App::Property",
                "Side of the created shape"
            ),
            PROFILE_OFFSETS,
            "ParametersSections"
        )
        addEnumProperty(
            obj,
            "SpineMode",
            translate(
                "App::Property",
                "The way the cross-section follows the spine"
            ),
            SPINE_MODES,
            "ParametersDistribution"
        )

    def execute(self, obj):
        '''
        This will run whenever a property has changed.

        Note:
            This method is mandatory.
        '''
        #- Call the shape building method
        new_shape = self.generateDistributionShape(obj)

        self.finishNewShape(obj, new_shape)

    def generateDistributionShape(self, obj):
        '''
        Creates a Distribution shape
        '''
        # profile_list = obj.ProfileShapes - only used once
        spine_shape = obj.Spine

        profile_thickness = obj.ProfileThickness.Value
        profile_radius = obj.ProfileRadius.Value
        profile_offset = obj.ProfileOffset
        hollow_profile = obj.HollowProfile
        fillet_profile = obj.FilletProfile
        frenet_mode = obj.FrenetMode
        spine_mode = obj.SpineMode

        #- Extract spine segments
        spine_wire = spine_shape[0].Shape.Wires[0]
        # Part.show(spine_wire)
        #- Extract segments of profile and cross-Sections
        closed_wires = []
        open_wires = []
        for item in obj.Sections: # was profile_list:
            wire_list = item[0].Shape.Wires[0]
            matrix = item[0].getGlobalPlacement().Rotation
            cross_section_normal = (
                matrix.multVec(App.Vector(0, 0, 1))
            ).normalize()
            if wire_list.isClosed():
                closed_wires.append((wire_list, cross_section_normal))
            else:
                open_wires.append((wire_list, cross_section_normal))

        if closed_wires != [] and open_wires != []:
            Print("Operation aborted! - It is not allowed to mix open and closed wires!")
            return

        transition = 0
        if spine_mode == "Right Corners":
            transition = 1
        elif spine_mode == "Round Corners":
            transition = 2

        if closed_wires != []:
            if not hollow_profile:
                slice_list = []
                for item in closed_wires:
                    slice_list.append(item[0])
                distribution_shape = spine_wire.makePipeShell(
                    slice_list, # List of wires: Profile, cross-Sections
                    True,  # isSolid
                    frenet_mode,  # isFrenet
                    transition,  # transition - 0: default, 1: right corners, 2:round corners
                )
            else:
                outer_list = []
                inner_list = []
                for item in closed_wires:
                    outer_strip = self.modifiedWire(
                        item[0],  # Original profile
                        item[1],
                        10,  # length, arbitrary value for the strip width
                        fillet_profile,
                        profile_radius,
                        profile_thickness,
                        profile_offset,
                        1.0,  # sign, ???
                    )
                    dist = item[0].Vertexes[0].Point.distanceToPlane(
                        App.Vector(0, 0, 0), item[1]
                    )
                    slice_wire = outer_strip.slice(item[1], dist)
                    outer_list.append(slice_wire[0])
                    #Part.show(slice_wire[0], "slice_wire")
                    inner_wire = slice_wire[0].makeOffset2D(
                        -profile_thickness,  # offset
                        1,  # join: 0 = arcs, 1 = tangent, 2 = intersection
                        False,  # fill
                        False,  # openResult
                        False, # intersection
                    )
                    inner_list.append(inner_wire)
                    #Part.show(inner_wire, "inner_wire")
                outer_shape = spine_wire.makePipeShell(
                    outer_list, # List of wires: Profile, cross-Sections
                    True,  # isSolid
                    frenet_mode,  # isFrenet
                    transition,  # transition - 0: default, 1: right corners, 2:round corners
                )
                inner_shape = spine_wire.makePipeShell(
                    inner_list, # List of wires: Profile, cross-Sections
                    True,  # isSolid
                    frenet_mode,  # isFrenet
                    transition,  # transition - 0: default, 1: right corners, 2:round corners
                )
                distribution_shape = outer_shape.cut(inner_shape)
        else:
            slice_list = []
            for item in open_wires:
                outer_strip = self.modifiedWire(
                    item[0],  # Original profile
                    item[1],  # normal of the profile
                    10,  # length, arbitrary value for the strip width
                    fillet_profile,
                    profile_radius,
                    profile_thickness,
                    profile_offset,
                    1.0,  # sign, ???
                )  # Returns a filleted (if possible) outer strip of faces
                # Part.show(outer_strip, "outer_strip")

                dist = item[0].Vertexes[0].Point.distanceToPlane(
                    App.Vector(0, 0, 0), item[1]
                )
                slice_wire = outer_strip.slice(item[1], dist)

                profile_shape = slice_wire[0].makeOffset2D(
                    profile_thickness,  # offset
                    1,  # join: 0 = arcs, 1 = tangent, 2 = intersection
                    True,  # fill
                    True,  # openResult
                    False, # intersection
                )
                #Part.show(profile_shape, "distr_shape")
                wire_list = profile_shape.OuterWire #.Shape.Wires[0]
                slice_list.append(wire_list)
            distribution_shape = spine_wire.makePipeShell(
                slice_list, # List of wires: Profile, cross-Sections
                True,  # isSolid
                frenet_mode,  # isFrenet
                transition,  # transition - 0: default, 1: right corners, 2:round corners
            )
        return distribution_shape  # Returns a shape

if App.GuiUp:

    from .PartPlusTaskPanels import DistributionShapeTaskPanel

    class DistributionShapeViewProvider(ViewProviderPartPlus):
        '''
        Individual view provider features for distribution shape objects.
        '''

        def claimChildren(self):
            '''
            This one moves the sketches unter the object in the tree view
            '''
            objs = []
            if hasattr(self, "Object") and hasattr(self.Object, "Sections"):
                for item in self.Object.Sections:
                    objs.append(item[0])
                #objs.append(self.Object.ProfileShape)
            if hasattr(self, "Object") and hasattr(self.Object, "Spine"):
                objs.append(self.Object.Spine[0])
            return objs

        def getTaskPanel(self, obj):
            return DistributionShapeTaskPanel(obj)

        def loadSvg(self, shape_type = "Solid"):
            print("loadSvg, shape_type: ", shape_type)
            '''
            -- Distribution Shape --  check icon
            Returns an embedded svg file with customized colors according
            to the shape type
            '''
            FACE_COLOR = {
                "Solid": "888",
                "Feature_Base": "48f",
                "Feature_Union": "0c0",
                "Feature_Difference": "c00",
                "Feature_Intersection": "00c",
                "Button": "f6d"
            }
            WIRE_COLOR = {
                "Solid": "333",
                "Feature_Base": "003",
                "Feature_Union": "030",
                "Feature_Difference": "300",
                "Feature_Intersection": "003",
                "Button": "300"
            }
            return '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
            <svg
            xmlns="http://www.w3.org/2000/svg"
            version="1.1"
            width="64" height="64"
            viewBox="0 0 64 64">
            <defs id="defs3561">
            <linearGradient
              id="linearGradient1"
              x1="0" y1="0"
              x2="0.7" y2="1">
              <stop
                offset="0"
                style="stop-color:#222; stop-opacity:0.3"/>
              <stop
                offset="0.5"
                style="stop-color:#222; stop-opacity:0.0"/>
              <stop
                offset="1"
                style="stop-color:#222; stop-opacity:0.5"/>
            </linearGradient>
            <linearGradient
              id="linearGradient2"
              x1="0" y1="0"
              x2="0.7" y2="1">
              <stop
                offset="0"
                style="stop-color:#222; stop-opacity:0.1"/>
              <stop
                offset="1"
                style="stop-color:#222; stop-opacity:0.4"/>
            </linearGradient>
            </defs>
            <g
            id="outlines"
            style="display:inline; fill:#{col1}; fill-opacity:1.0; fill-rule:nonzero;
            stroke:#{col2}; stroke-width:2; stroke-miterlimit:4; stroke-linejoin:round">
            <path
              style="stroke:#a40000;stroke-width:6;"
              d="m 5,51 54,-39"/>
            <path
              style="stroke:#f33"
              d="m 5,51 54,-39"/>
            <path
              d="m 3,21 c 20,0 32,22 32,38 L 61,39 C 61,23 49,7 35,7 z"/>
            <path
              d="M 35,59 C 35,43 23,21 3,21 l 4,14 c 8,0 14,8 14,18 z"/>
            </g>
            <g
            id="shading"
            style="display:inline;fill-rule:nonzero; stroke:none">
            <path
              style="fill:url(#linearGradient1)"
              d="M 12,20 35.0,10 C 48,10 57,25 58.2,37.5 L 37,54 C 37,44 27,24 12,20 z"/>
            <path
              style="fill:url(#linearGradient2)"
              d="M 32,54.5 C 32,44 20.6,25 6.6,24 L 9,32.1 C 14,34 21.3,36 23.8,51 z"/>
            </g>

            </svg>'''.format(
            col1 = FACE_COLOR[shape_type],
            col2 = WIRE_COLOR[shape_type]
            )

from FreeCAD import Console
Console.PrintLog('freecad/PartPlus/PartPlusDistributionCmd.py\n')
