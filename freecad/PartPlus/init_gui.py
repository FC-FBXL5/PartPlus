# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileNotice: Part of the PartPlus addon.
# -*- coding: utf-8 -*-

#-----------------------------------------------
# Workbench declarations moved to workbench.py !
#-----------------------------------------------

import FreeCADGui as Gui
from .workbench import PartPlusWorkbench

# Add workbench to the FreeCAD Gui (creates a class instance)
Gui.addWorkbench(PartPlusWorkbench())

from FreeCAD import Console
Console.PrintLog('freecad/PartPlus/init_gui.py\n')
