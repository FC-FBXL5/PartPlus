# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileNotice: Part of the PartPlus addon.
# -*- coding: utf-8 -*-

import FreeCAD as App
import FreeCADGui as Gui
import os

MOD_PATH = os.path.dirname(__file__)
ICONSDIR = os.path.join(MOD_PATH, "resources", "icons")
TRANSLATIONSPATH = os.path.join(MOD_PATH, "resources", "translations")

QT_TRANSLATE_NOOP = App.Qt.QT_TRANSLATE_NOOP

#-------------------------------------------------------------------------------
# Import modules
#-------------------------------------------------------------------------------
from .PartPlusTools import (
    BaseShape,
    ViewProviderPartPlus,
    #PartPlusShapeTaskPanel,
    #updateTaskTitleIcon,
    #svgToPixmap
)  # Collection of shared general settings and methods
from .PartPlusPrismoidCmd import (
    PrismoidShape,
    PrismoidShapeViewProvider,
    #PrismoidShapeTaskPanel
)
from .PartPlusToroidCmd import (
    ToroidShape,
    ToroidShapeViewProvider,
    #ToroidShapeTaskPanel
)
from .PartPlusTransitionCmd import (
    TransitionShape,
    TransitionShapeViewProvider,
    #TransitionShapeTaskPanel
)
from .PartPlusDistributionCmd import (
    DistributionShape,
    DistributionShapeViewProvider,
    #DistributionShapeTaskPanel
)

#-------------------------------------------------------------------------------
# Class based commands
#-------------------------------------------------------------------------------

class BaseCommand(object):
    '''Superclass for commands'''
    NAME = ""
    PARTPLUS_FUNCTION = None
    PARTPLUS_VIEW_PROVIDER = None
    #PARTPLUS_TASK_PANEL = None
    #ICONSDIR = os.path.join(os.path.dirname(__file__), "icons")

    def __init__(self):
        pass

    def IsActive(self):
        '''
        Deactivates (greys out) commands unless a document is active
        '''
        if App.ActiveDocument is None:
            return False
        else:
            return True

    def Activated(self):
        Gui.doCommandGui("import freecad.PartPlus.commands")
        Gui.doCommandGui(
            "freecad.PartPlus.commands.{}.createFeaturePython()".format(self.__class__.__name__)
        )  # Prints the given string in the Pyrhon console and runs it.
        # Example:
        # "freecad.PartPlus.commands.PrismoidShapeCommand.createFeaturePython()"
        App.ActiveDocument.recompute()
        Gui.SendMsgToActiveView("ViewFit")

    @classmethod
    def createFeaturePython(cls):
        '''This is launched from the Python Console'''
        if App.GuiUp:
            # borrowed from threaded profiles
            # puts the item into an active container
            body = Gui.ActiveDocument.ActiveView.getActiveObject("pdbody")
            part = Gui.ActiveDocument.ActiveView.getActiveObject("part")

            if body:
                feature_list = []
                for item in body.Group:
                    if item.TypeId.startswith("PartDesign::"):
                        feature_list.append(item)
                if len(feature_list) > 0:
                    obj = App.ActiveDocument.addObject(
                        "PartDesign::FeatureAdditivePython",
                        ("Add" + cls.NAME)
                    )
                else:
                    obj = App.ActiveDocument.addObject(
                        "PartDesign::FeaturePython",
                        cls.NAME
                    )
                '''
                objsub = App.ActiveDocument.addObject(
                    "PartDesign::FeatureSubtractivePython",
                    ("Sub"+ cls.NAME)
                )'''
            else:
                obj = App.ActiveDocument.addObject(
                    "Part::FeaturePython",
                    cls.NAME
                )

            cls.PARTPLUS_VIEW_PROVIDER(obj.ViewObject, cls.Pixmap)
            cls.PARTPLUS_FUNCTION(obj)

            if body:
                body.addObject(obj)
            elif part:
                part.Group += [obj]
        else:
            obj = App.ActiveDocument.addObject("Part::FeaturePython", cls.NAME)
            cls.PARTPLUS_FUNCTION(obj)

        App.ActiveDocument.recompute()
        return
        panel = cls.PARTPLUS_TASK_PANEL(obj)
        updateTaskTitleIcon(panel)
        Gui.Control.showDialog(panel)
        return

    def GetResources(self):
        return {
            "Pixmap": self.Pixmap,
            "MenuText": self.MenuText,
            "ToolTip": self.ToolTip,
        }

class PrismoidShapeCommand(BaseCommand):
    NAME = "PrismoidShape"  # the document object
    PARTPLUS_FUNCTION = PrismoidShape  # the class conrolled by Data properties
    PARTPLUS_VIEW_PROVIDER = PrismoidShapeViewProvider  # the class conrolled by View properties
    #PARTPLUS_TASK_PANEL = PrismoidShapeTaskPanel
    Pixmap = os.path.join(ICONSDIR, "PartPlus_Prismoid.svg")  # just a path...
    MenuText = QT_TRANSLATE_NOOP("PartPlus_PrismoidShape", "Prismoid Shape")
    ToolTip = QT_TRANSLATE_NOOP(
        "Partee_PrismoidShape",
        """Creates a Prismoid Shape
1. Select a profile (Sketch, Shape Binder, or Sub-Shape Binder)
2. Invoke this tool"""
    )

    def IsActive(self):
        '''
        This is used to deactivate (grey out) the command as long as
        the selection does not contain the required items. In this case
        exactly one SketchObject, ShapeBinder, or SubShapeBinder.
        '''
        #- Check if the number of selected items is exactly one
        if len(Gui.Selection.getSelection()) != 1:
            return False
        #- Check if the selection contains a valid item
        selobj = Gui.Selection.getSelection()[0]
        if not (
            selobj.isDerivedFrom("Sketcher::SketchObject")
            or selobj.isDerivedFrom("PartDesign::ShapeBinder")
            or selobj.isDerivedFrom("PartDesign::SubShapeBinder")
        ):
            return False
        return True

class ToroidShapeCommand(BaseCommand):
    NAME = "ToroidShape"
    PARTPLUS_FUNCTION = ToroidShape
    PARTPLUS_VIEW_PROVIDER = ToroidShapeViewProvider
    #PARTPLUS_TASK_PANEL = ToroidShapeTaskPanel
    Pixmap = os.path.join(ICONSDIR, "PartPlus_Toroid.svg")
    MenuText = QT_TRANSLATE_NOOP("PartPlus_ToroidShape", "Toroidal Shape")
    ToolTip = QT_TRANSLATE_NOOP(
        "PartPlus_ToroidShape",
        """Creates a Toroid Shape
1. Select a profile (Sketch, Shape Binder, or Sub-Shape Binder)
2. Invoke this tool"""
    )

    def IsActive(self):
        '''
        This is used to deactivate (grey out) the command as long as
        the selection does not contain the required items. In this case
        exactly one SketchObject, ShapeBinder, or SubShapeBinder.
        '''
        #- Check if the number of selected items is exactly one
        if len(Gui.Selection.getSelection()) != 1:
            return False
        #- Check if the selection contains a valid item
        selobj = Gui.Selection.getSelection()[0]
        if not (
            selobj.isDerivedFrom("Sketcher::SketchObject")
            or selobj.isDerivedFrom("PartDesign::ShapeBinder")
            or selobj.isDerivedFrom("PartDesign::SubShapeBinder")
        ):
            return False
        return True

class DistributionShapeCommand(BaseCommand):
    NAME = "DistributionShape"
    PARTPLUS_FUNCTION = DistributionShape
    PARTPLUS_VIEW_PROVIDER = DistributionShapeViewProvider
    #PARTPLUS_TASK_PANEL = DistributionShapeTaskPanel
    Pixmap = os.path.join(ICONSDIR, "PartPlus_Distribution.svg")
    MenuText = QT_TRANSLATE_NOOP(
        "PartPlus_DistributionShape",
        "Distribution Shape"
    )
    ToolTip = QT_TRANSLATE_NOOP(
        "PartPlus_DistributionShape",
        """Creates a Distribution Shape
1. Select a profile (Sketch, Shape Binder, or Sub-Shape Binder)
2. Select a cross-section (Sketch, Shape Binder, or Sub-Shape Binder)
3. Optionally select more cross-sections
4. Invoke this tool"""
    )

    def IsActive(self):
        '''
        This is used to deactivate (grey out) the command as long as
        the selection does not contain the required items. In this case
        exactly one SketchObject, ShapeBinder, or SubShapeBinder.
        '''
        #- Check if the number of selected items is exactly two
        if len(Gui.Selection.getSelection()) < 2:
            return False
        #- Check if the selection contains 2 0r more valid items
        selected = Gui.Selection.getSelection()
        for selobj in selected:
            if not (
                selobj.isDerivedFrom("Sketcher::SketchObject")
                or selobj.isDerivedFrom("PartDesign::ShapeBinder")
                or selobj.isDerivedFrom("PartDesign::SubShapeBinder")
            ):
                return False
        return True

class TransitionShapeCommand(BaseCommand):
    NAME = "TransitionShape"
    PARTPLUS_FUNCTION = TransitionShape
    PARTPLUS_VIEW_PROVIDER = TransitionShapeViewProvider
    #PARTPLUS_TASK_PANEL = TransitionShapeTaskPanel
    Pixmap = os.path.join(ICONSDIR, "PartPlus_Transition.svg")
    MenuText = QT_TRANSLATE_NOOP("PartPlus_TransitionShape", "Transition Shape")
    ToolTip = QT_TRANSLATE_NOOP(
        "PartPlus_TransitionShape",
        """Creates a Transition Shape
1. Select a Spine (Sketch, Shape Binder, or Sub-Shape Binder)
2. Select a profile (Sketch, Shape Binder, or Sub-Shape Binder)
3. Optionally select cross-sections (Sketch, Shape Binder, or Sub-Shape Binder)
4. Invoke this tool"""
    )

    def IsActive(self):
        '''
        This is used to deactivate (grey out) the command as long as
        the selection does not contain the required items. In this case
        exactly one SketchObject, ShapeBinder, or SubShapeBinder.
        '''
        #- Check if the number of selected items is exactly one
        if len(Gui.Selection.getSelection()) < 2:
            return False
        #- Check if the selection contains 2 or more valid items
        selected = Gui.Selection.getSelection()
        for selobj in selected:
            if not (
                selobj.isDerivedFrom("Sketcher::SketchObject")
                or selobj.isDerivedFrom("PartDesign::ShapeBinder")
                or selobj.isDerivedFrom("PartDesign::SubShapeBinder")
            ):
                return False
        return True

from FreeCAD import Console
Console.PrintLog('freecad/PartPlus/commands.py\n')
