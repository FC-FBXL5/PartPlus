# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileNotice: Part of the PartPlus addon.
# -*- coding: utf-8 -*-
'''
PartPlus is a workbench providing tools to create
Part solid objects and PartDesign features
'''

import os
import FreeCAD as App
import FreeCADGui as Gui

MOD_PATH = os.path.dirname(__file__)
ICONSPATH = os.path.join(MOD_PATH, "resources", "icons")
TRANSLATIONSPATH = os.path.join(MOD_PATH, "resources", "translations")

Gui.addLanguagePath(TRANSLATIONSPATH)
Gui.updateLocale()

translate = App.Qt.translate
QT_TRANSLATE_NOOP = App.Qt.QT_TRANSLATE_NOOP

# Main class for the workbench
# init_gui.py will create an instance of the class
class PartPlusWorkbench(Gui.Workbench):

    #-----------------------------------------------------------------------
    # General Workbench Definitions
    #-----------------------------------------------------------------------

    MenuText = translate("Workbench", "PartPlus")
    ToolTip = translate("Workbench", "PartPlus Workbench")
    Icon = os.path.join(ICONSPATH, "PartPlusWorkbench.svg")

    COMMANDS = [
        "PrismoidShape",
        "ToroidShape",
        "TransitionShape",
        "DistributionShape",
    ]  # commands list for menu and toolbar

    def GetClassName(self):
        '''This function is mandatory if this is a full python workbench.'''
        return "Gui::PythonWorkbench"

    def Initialize(self):
        '''
        Import specific class commands and functions
        from the workbench modules
        '''
        from .commands import (
            PrismoidShapeCommand,  # Class command
            ToroidShapeCommand,
            TransitionShapeCommand,
            DistributionShapeCommand,
        )

        #-----------------------------------------------------------------------
        # Attach class commands to Menu & Toolbar items
        #-----------------------------------------------------------------------
        # Connect class command definition(s) with command class
        # Every command must ultimately be an object with the methods
        # GetResources(), IsActive(), and Activated()

        Gui.addCommand(
            "PrismoidShape",         # Menu or Toolbar Item Label, linked to
            PrismoidShapeCommand()   # specific Class Command
        )

        Gui.addCommand("ToroidShape", ToroidShapeCommand())

        Gui.addCommand("TransitionShape", TransitionShapeCommand())

        Gui.addCommand("DistributionShape", DistributionShapeCommand())

        #-----------------------------------------------------------------------
        # Add command definition to Menu & Toolbar
        #-----------------------------------------------------------------------

        # Add WB command definition(s) to Toolbar
        # Parameters: Toolbar Name, [Item label, ...]
        self.appendToolbar(QT_TRANSLATE_NOOP("Workbench", "PartPlus"), self.COMMANDS)

        # Add WB command definition(s) to Menu
        # Parameters: Menu Name, [Item label, ...]
        self.appendMenu(QT_TRANSLATE_NOOP("Workbench", "PartPlus"), self.COMMANDS)

    def Activated(self):
        '''Execute when the workbench is activated.'''
        return

    def Deactivated(self):
        '''Execute when the workbench is deactivated.'''
        return

    def ContextMenu(self, recipient):
        '''Execute whenever the user right-clicks on screen.'''
        # `recipient` will be either `view` or `tree`.
        # Add commands to the context menu.
        self.appendContextMenu(
            QT_TRANSLATE_NOOP("Workbench", "PartPlus"),
            self.COMMANDS
        )
      
from FreeCAD import Console
Console.PrintLog('freecad/PartPlus/workbench.py\n')
