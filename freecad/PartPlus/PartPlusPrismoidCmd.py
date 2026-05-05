# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileNotice: Part of the PartPlus addon.
# -*- coding: utf-8 -*-
'''
This Tool creates a prismoid shape, either a PartDesign feature or
a separate Part solid
'''

import FreeCAD as App
import FreeCADGui as Gui

import Part
import os
import math  # to use some predefined conversions

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
    #PartPlusShapeTaskPanel,
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

class PrismoidShape(BaseShape):
    '''
    Adds a prismoid shape
    '''
    def __init__(self, obj):
        super(PrismoidShape, self).__init__(obj)
        '''
        Adds properties to the object
        '''

        #- Create ProfileShape property and store the selected item in it:
        obj.addProperty(
            "App::PropertyLinkSub",
            "ProfileShape",
            "BaseProfile",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "2D shape defining the cross-section"
            )
        ).ProfileShape = Gui.Selection.getSelection()[0]
        # This command could not be invoked as long as the selecction does not
        # contain exactly one sketch, shape binder, or sub-shape binder.

        #- Properties altered by this tool:
        self.addPrismoidProperties(obj)

        self.obj = obj
        obj.Proxy = self

    def addPrismoidProperties(self, obj):
        '''
        Creates the Prismoid parameters including default values required
        for the initial build
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
        addLengthProperty(
            obj,
            "ForwardLength",
            translate(
                "App::Property",
                "Length along the chosen direction "
            ),
            10.0,
            "ParametersDistribution"
        )
        addLengthProperty(
            obj,
            "ReverseLength",
            translate(
                "App::Property",
                "Length in opposite direction "
            ),
            5.0,
            "ParametersDistribution"
        )
        addLengthProperty(
            obj,
            "ProfileThickness",
            translate(
                "App::Property",
                "Thickness of a hollow profile"
            ),
            2.0,
            "ParametersBaseProfile"
        )
        addLengthProperty(
            obj,
            "ProfileRadius",
            translate(
                "App::Property",
                "Inner radius of automatically filleted profile edges"
            ),
            4.0,
            "ParametersBaseProfile"
        )
        addBoolProperty(
            obj,
            "Symmetric",
            translate(
                "App::Property",
                "Equal extrusion on both sides of the profile plane"
            ),
            False,
            "ParametersDistribution"
        )
        addBoolProperty(
            obj,
            "Reverse",
            translate(
                "App::Property",
                "Reverses the extrusion direction"
            ),
            False,
            "ParametersDistribution"
        )
        addBoolProperty(
            obj,
            "TwoSided",
            translate(
                "App::Property",
                "Toggles one sided or two sided distribution"
            ),
            False,
            "ParametersDistribution"
        )
        addBoolProperty(
            obj,
            "HollowProfile",
            translate(
                "App::Property",
                "Creates a hollow shape from a closed profile"
            ),
            False,
            "ParametersBaseProfile"
        )
        addBoolProperty(
            obj,
            "FilletProfile",
            translate(
                "App::Property",
                "Applies fillets to sharp corners of the profile"
            ),
            True,
            "ParametersBaseProfile"
        )
        addEnumProperty(
            obj,
            "ShapeType",
            translate(
                "App::Property",
                "Type of the created shape"
            ),
            SHAPE_TYPES,
            "ParametersBaseProfile"
        )
        addEnumProperty(
            obj,
            "ProfileOffset",
            translate(
                "App::Property",
                "Toggles whether profile thicknes grows symmetrically or single-sided"
            ),
            PROFILE_OFFSETS,
            "ParametersBaseProfile"
        )

    def execute(self, obj):
        '''
        This will run whenever a property has changed.

        Note: This method is mandatory!
        '''
        #- Call the shape building method
        new_shape = self.generatePrismoidShape(obj)

        self.finishNewShape(obj, new_shape)

    def generatePrismoidShape(self, obj):
        '''
        Creates a prismoid shape
        '''
        profile_shape = obj.ProfileShape[0]

        profile_thickness = obj.ProfileThickness.Value
        profile_radius = obj.ProfileRadius.Value
        profile_offset = obj.ProfileOffset
        hollow_profile = obj.HollowProfile
        fillet_profile = obj.FilletProfile
        forward_length = obj.ForwardLength.Value
        reverse_length = obj.ReverseLength.Value
        two_sided_shape = obj.TwoSided
        symmetric_shape = obj.Symmetric
        reverse_shape = obj.Reverse

        #- Finding the normal, x-, and y-direction of the profie shape
        matrix = profile_shape.getGlobalPlacement().Rotation
        normal = (matrix.multVec(App.Vector(0, 0, 1))).normalize()
        # Not used in this tool:
        # local_x_axis = (matrix.multVec(App.Vector(1, 0, 0))).normalize()
        # local_y_axis = (matrix.multVec(App.Vector(0, 1, 0))).normalize()

        wire_list = profile_shape.Shape.Wires[0]
        
        #- Set direction - should be adjustible in the future
        direction_vector = normal
        
        if reverse_shape:
            direction_vector *= -1

        if not two_sided_shape:
            reverse_length = 0

        if symmetric_shape:
            reverse_length = forward_length / 2
            forward_length /= 2

        if wire_list.isClosed():
            if not hollow_profile:
                # If the outline is closed, and the hollow_profile option not selected
                # create a face & extrude it. Accepts holes in the face.
                profile_face = Part.makeFace(
                    profile_shape.Shape.Wires,
                    "Part::FaceMakerBullseye"
                )
            else:
                outer_strip = self.modifiedWire(
                    wire_list,  # Original profile
                    profile_normal,
                    10,  # length, arbitrary value for the strip width
                    fillet_profile,
                    profile_radius,
                    profile_thickness,
                    profile_offset,
                    1.0,  # sign, ???
                )  # Returns a filleted (if possible) outer strip of faces
                # Part.show(outer_strip, "outer_strip")

                #- Obtain a single wire from the strip border that is
                #  touching the sketch plane - borrowed from SheetMetal WB
                dist = wire_list.Vertexes[0].Point.distanceToPlane(
                    App.Vector(0, 0, 0), profile_normal
                )
                #- Extract a wire from the thickness layer onto the sketch plane
                slice_wire = outer_strip.slice(profile_normal, dist)
                # Part.show(slice_wire[0], "slice_wire[0]")

                profile_face = slice_wire[0].makeOffset2D(
                    -profile_thickness,  # offset
                    1,  # join: 0 = arcs, 1 = tangent, 2 = intersection
                    True,  # fill
                    False,  # openResult
                    False, # intersection
                )
        else:
            #wire_list = profile_shape.Shape.Wires[0]
            outer_strip = self.modifiedWire(
                wire_list,  # Original profile
                profile_normal,
                10,  # length, arbitrary value for the strip width
                fillet_profile,
                profile_radius,
                profile_thickness,
                profile_offset,
                1.0,  # sign, ???
            )  # Returns a filleted (if possible) outer strip of faces
            # Part.show(outer_strip, "outer_strip")

            dist = wire_list.Vertexes[0].Point.distanceToPlane(
                App.Vector(0, 0, 0), profile_normal
            )
            slice_wire = outer_strip.slice(profile_normal, dist)
            # Part.show(slice_wire[0], "slice_wire[0]")

            profile_face = slice_wire[0].makeOffset2D(
                profile_thickness,  # offset
                1,  # join: 0 = arcs, 1 = tangent, 2 = intersection
                True,  # fill
                True,  # openResult
                False, # intersection
            )

        #- Move the 2D base geometry in reverse direction.
        profile_face.translate(direction_vector * -reverse_length)

        prismoid_shape = profile_face.extrude(
            direction_vector * (forward_length + reverse_length)
        )
        #! It seems like moving the 3D geometry doesn't work
        #! prismoid_shape.translate(direction_vector * -reverse_length)

        return prismoid_shape  # Returns a shape

if App.GuiUp:

    class PrismoidShapeViewProvider(ViewProviderPartPlus):
        '''
        Individual view provider features for prismoid shape objects.
        '''

        def claimChildren(self):
            '''
            This one moves the sketches unter the object in the tree view
            '''
            objs = []
            if hasattr(self, "Object") and hasattr(self.Object, "ProfileShape"): #"PrismaticShape"
                objs.append(self.Object.ProfileShape[0])
            return objs

        def loadSvg(self, shape_type = "Solid"):
            '''
            -- Prismoid --
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
Console.PrintLog('freecad/PartPlus/PartPlusPrismoidCmd.py\n')
