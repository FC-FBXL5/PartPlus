# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileNotice: Part of the PartPlus addon.
# -*- coding: utf-8 -*-

import FreeCAD as App
import FreeCADGui as Gui

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

class PartPlusShapeTaskPanel(object):
    '''
    Root class for all Partee task panels.
    Provides shared methods for all task panels.
    '''

    def __init__(self, obj):

        self.obj = obj

    #---------------------------------------------------------------------------
    # Group boxes and sub-boxes including widgets
    #---------------------------------------------------------------------------

    def groupBoxWithGrid(self, title = "", icon = None):
        '''Creates an empty instance of a QGroupBox providing a QGridLayout'''
        groupBox = QGroupBox(title)
        grid = QGridLayout()
        groupBox.setLayout(grid)
        return groupBox, grid

    def addSingleProfileWidgets(self, grid):
        '''Provides widgets to control a profile shape'''

        self.button_sketch = QLabel("Profile Shape")
        grid.addWidget(self.button_sketch, 0, 0)

        self.line_edit_sketch = QLineEdit()
        grid.addWidget(self.line_edit_sketch, 0, 1, 1, -1)
        self.line_edit_sketch.setText(self.profile_shape[0].Name)

        self.label_profile = QLabel("Profile")
        #self.label_cross_section.setStyleSheet("color : #00f; background-color : #faa;")
        grid.addWidget(self.label_profile, 1, 0)

        self.button_profile = QPushButton("Hollow/Rib") #("Solid")
        self.button_profile.setStyleSheet("background-color:#ffa")
        self.button_profile.setToolTip(
            "Toggles whether the shape will be solid or hollow"
        )
        self.button_profile.clicked.connect(
            self.onButtonProfileClicked
        )
        grid.addWidget(self.button_profile, 1, 1, 1, -1)

        self.button_profile_offset = QPushButton("Middle")
        self.button_profile_offset.setStyleSheet("background-color:#aff")
        self.button_profile_offset.setToolTip(
            "Toggles whether the shape will be one-sided or symmetric"
        )
        self.button_profile_offset.clicked.connect(
            self.onButtonProfileOffsetClicked
        )
        grid.addWidget(self.button_profile_offset, 2, 1)

        self.button_offset_side = QPushButton("This side")
        self.button_offset_side.setToolTip(
            "Toggles to which side the wall thickness grows"
        )
        self.button_offset_side.clicked.connect(
            self.onButtonOffsetSideClicked
        )
        grid.addWidget(self.button_offset_side, 2, 2)

        self.label_thickness = QLabel("Wall Thickness")
        grid.addWidget(self.label_thickness, 4, 0)

        self.ds_box_thickness = QDoubleSpinBox()
        self.ds_box_thickness.setValue(self.profile_thickness)
        self.button_offset_side.setToolTip(
            "Sets the wall thickness of the profile"
        )
        self.ds_box_thickness.valueChanged.connect(
            self.onDoubleSpinBoxThicknessChanged
        )
        grid.addWidget(self.ds_box_thickness, 4, 1, 1, -1)

        self.button_fillet_profile = QPushButton("Automatic Fillets")
        self.button_fillet_profile.setToolTip(
            "Toggles if open/hollow profiles are automatically filletd"
        )
        self.button_fillet_profile.clicked.connect(
            self.onButtonFilletProfileClicked
        )
        grid.addWidget(self.button_fillet_profile, 5, 1, 1, -1)

        self.label_radius = QLabel("Inner Radius")
        grid.addWidget(self.label_radius, 6, 0)

        self.ds_box_radius = QDoubleSpinBox()
        self.ds_box_radius.setValue(self.profile_radius)
        self.button_offset_side.setToolTip(
            "Sets the inner radius for automatically filleted edges"
        )
        self.ds_box_radius.valueChanged.connect(
            self.onDoubleSpinBoxRadiusChanged
        )
        grid.addWidget(self.ds_box_radius, 6, 1, 1, -1)

        #- Activate/deactivate widgets according to hollow profile option
        if self.hollow_profile:
            self.button_profile.setText("Hollow/Rib")
            self.hollow_profile = True
            self.button_profile_offset.show()
            self.button_fillet_profile.show()
            self.label_thickness.show()
            self.ds_box_thickness.show()
            self.label_radius.show()
            self.ds_box_radius.show()
            if self.button_profile_offset.text() == "Offset":
                self.button_offset_side.show()
            else:
                self.button_offset_side.hide()
        else:
            self.button_profile.setText("Solid")
            self.hollow_profile = False
            self.button_profile_offset.hide()
            self.button_fillet_profile.hide()
            self.button_offset_side.hide()
            self.label_thickness.hide()
            self.ds_box_thickness.hide()
            self.label_radius.hide()
            self.ds_box_radius.hide()

    def addProfilesWidgets(self, grid):
        '''Provides widgets to control a profile shape and cross-sections'''

        self.button_sketch = QLabel("Profile Shape")
        grid.addWidget(self.button_sketch, 0, 0)

        self.line_edit_sketch = QLineEdit()
        grid.addWidget(self.line_edit_sketch, 0, 1, 1, -1)

        if hasattr(self.obj, "ProfileShape"):
            self.line_edit_sketch.setText(self.profile_shape.Name)
        else:
            self.line_edit_sketch.setText(self.obj.Sections[0][0].Name)

        '''self.button_sketch = QLabel("Profile Shape")
        grid.addWidget(self.button_sketch, 0, 0)
        self.line_edit_sketch.setText(self.profile_shape.Name)'''

        self.label_profile_type = QLabel("Profile Type")
        grid.addWidget(self.label_profile_type, 1, 0)

        self.button_profile = QPushButton("Hollow/Rib") #("Solid")
        self.button_profile.setStyleSheet("background-color:#ffa")
        self.button_profile.setToolTip(
            "Toggles whether the shape will be solid or hollow"
        )
        self.button_profile.clicked.connect(
            self.onButtonProfileClicked
        )
        grid.addWidget(self.button_profile, 1, 1, 1, -1)

        self.offset_type = QLabel("Offset Type")
        grid.addWidget(self.offset_type, 2, 0)

        self.button_profile_offset = QPushButton("Middle")
        self.button_profile_offset.setStyleSheet("background-color:#aff")
        self.button_profile_offset.setToolTip(
            "Toggles whether the shape will be one-sided or symmetric"
        )
        self.button_profile_offset.clicked.connect(
            self.onButtonProfileOffsetClicked
        )
        grid.addWidget(self.button_profile_offset, 2, 1)

        self.button_offset_side = QPushButton("This side")
        self.button_offset_side.setToolTip(
            "Toggles to which side the wall thickness grows"
        )
        self.button_offset_side.clicked.connect(
            self.onButtonOffsetSideClicked
        )
        grid.addWidget(self.button_offset_side, 2, 2)

        self.label_thickness = QLabel("Wall Thickness")
        grid.addWidget(self.label_thickness, 4, 0)

        self.ds_box_thickness = QDoubleSpinBox()
        self.ds_box_thickness.setValue(self.profile_thickness)
        self.button_offset_side.setToolTip(
            "Sets the wall thickness of the profile"
        )
        self.ds_box_thickness.valueChanged.connect(
            self.onDoubleSpinBoxThicknessChanged
        )
        grid.addWidget(self.ds_box_thickness, 4, 1, 1, -1)

        self.button_fillet_profile = QPushButton("Automatic Fillets")
        self.button_fillet_profile.setToolTip(
            "Toggles if open/hollow profiles are automatically filletd"
        )
        self.button_fillet_profile.clicked.connect(
            self.onButtonFilletProfileClicked
        )
        grid.addWidget(self.button_fillet_profile, 5, 1, 1, -1)

        self.label_radius = QLabel("Inner Radius")
        grid.addWidget(self.label_radius, 6, 0)

        self.ds_box_radius = QDoubleSpinBox()
        self.ds_box_radius.setValue(self.profile_radius)
        self.button_offset_side.setToolTip(
            "Sets the inner radius for automatically filleted edges"
        )
        self.ds_box_radius.valueChanged.connect(
            self.onDoubleSpinBoxRadiusChanged
        )
        grid.addWidget(self.ds_box_radius, 6, 1, 1, -1)

        self.label_cross_sections = QLabel()
        self.label_cross_sections.setText(
            "Number of Cross-Sections: {}".format(len(self.obj.Sections))
        )
        grid.addWidget(self.label_cross_sections, 7, 0, 1, -1)

        #- Activate/deactivate widgets according to hollow profile option
        if self.hollow_profile:
            self.button_profile.setText("Hollow/Rib")
            self.hollow_profile = True
            self.button_profile_offset.show()
            self.button_fillet_profile.show()
            self.label_thickness.show()
            self.ds_box_thickness.show()
            self.label_radius.show()
            self.ds_box_radius.show()
            if self.button_profile_offset.text() == "Offset":
                self.button_offset_side.show()
            else:
                self.button_offset_side.hide()
        else:
            self.button_profile.setText("Solid")
            self.hollow_profile = False
            self.button_profile_offset.hide()
            self.button_fillet_profile.hide()
            self.button_offset_side.hide()
            self.label_thickness.hide()
            self.ds_box_thickness.hide()
            self.label_radius.hide()
            self.ds_box_radius.hide()

    def addFeatureWidgets(self, grid):
        '''Provides widgets to choose the feature type'''

        self.radio_button_shape_1 = QRadioButton("Additive Shape")
        #self.radio_button_shape_1.setToolTip(self.tool_tip_buttons)
        self.radio_button_shape_1.setChecked(True)
        #self.radio_button_shape_1.hide()
        self.radio_button_shape_1.toggled.connect(
            self.onRadioButtonShapeToggled
            )
        grid.addWidget(self.radio_button_shape_1, 0, 0)

        self.radio_button_shape_2 = QRadioButton("Subtractive Shape")
        #self.radio_button_shape_2.setToolTip(self.tool_tip_buttons)
        self.radio_button_shape_2.setChecked(False)
        #self.radio_button_shape_2.hide()
        self.radio_button_shape_2.toggled.connect(
            self.onRadioButtonShapeToggled
            )
        grid.addWidget(self.radio_button_shape_2, 1, 0)

        self.radio_button_shape_3 = QRadioButton("Common Shape")
        #self.radio_button_shape_3.setToolTip(self.tool_tip_buttons)
        self.radio_button_shape_3.setChecked(False)
        #self.radio_button_shape_3.hide()
        self.radio_button_shape_3.toggled.connect(
            self.onRadioButtonShapeToggled
            )
        grid.addWidget(self.radio_button_shape_3, 2, 0)

        #- Group the buttons
        self.group_buttons_shape = QButtonGroup()
        self.group_buttons_shape.addButton(self.radio_button_shape_1)
        self.group_buttons_shape.addButton(self.radio_button_shape_2)
        self.group_buttons_shape.addButton(self.radio_button_shape_3)

        #- Set active button according to shape type
        if self.shape_type == "Feature_Difference":
            self.radio_button_shape_2.setChecked(True)
        elif self.shape_type == "Feature_Intersection":
            self.radio_button_shape_3.setChecked(True)
        else:
            self.radio_button_shape_1.setChecked(True)

    def addUpdateWidgets(self, grid):
        '''Provides widgets to choose manual update'''

        self.button_update = QPushButton("Manual Update -->")
        self.button_update.setToolTip("Toggles the update mode")
        self.button_update.setEnabled(True)
        self.button_update.clicked.connect(self.onButtonUpdate)
        grid.addWidget(self.button_update, 1, 0)

        self.button_apply = QPushButton("Apply")
        self.button_apply.setToolTip("Updates the shapes")
        self.button_apply.setEnabled(False)
        self.button_apply.clicked.connect(self.onButtonApply)
        grid.addWidget(self.button_apply, 1, 1)

    def addDistributeLengthWidgets(self, grid):
        '''Provides widgets to choose distribution direction and extent'''

        self.label_direction = QLabel("Direction")
        grid.addWidget(self.label_direction, 1, 0)

        self.button_two_sided = QPushButton("One sided")
        self.button_two_sided.setToolTip("Enables two sided distribution")
        self.button_two_sided.show()
        self.button_two_sided.clicked.connect(self.onButtonTwoSidedPrismoid)
        grid.addWidget(self.button_two_sided, 1, 1)

        self.button_reverse = QPushButton("Forward")
        self.button_reverse.setToolTip("Reverts the distribution direction")
        self.button_reverse.show()
        self.button_reverse.clicked.connect(self.onButtonReversePrismoid)
        grid.addWidget(self.button_reverse, 1, 2)

        self.button_symmetric = QPushButton("Two lengths")
        self.button_symmetric.setToolTip(
            "Toggles between symmetric and a second length"
        )
        self.button_symmetric.hide()
        self.button_symmetric.clicked.connect(self.onButtonSymmetricPrismoid)
        grid.addWidget(self.button_symmetric, 1, 2)

        self.label_length = QLabel("Length")
        grid.addWidget(self.label_length, 2, 0)

        self.ds_box_length = QDoubleSpinBox()
        self.ds_box_length.setMaximum(10000)
        self.ds_box_length.setValue(self.forward_length)
        self.ds_box_length.valueChanged.connect(
            self.onDoubleSpinBoxLengthChanged
        )
        grid.addWidget(self.ds_box_length, 2, 1)

        self.ds_box_other_length = QDoubleSpinBox()
        self.ds_box_other_length.setMaximum(10000)
        self.ds_box_other_length.setValue(self.reverse_length)
        #self.ds_box_other_length.hide()
        self.ds_box_other_length.setEnabled(False)
        self.ds_box_other_length.valueChanged.connect(
            self.onDoubleSpinBoxOtherLengthChanged
        )
        grid.addWidget(self.ds_box_other_length, 2, 2)

        if not self.two_sided_shape:
            self.button_two_sided.setText("One sided")
            self.button_reverse.show()
            if self.reverse_shape:
                self.button_reverse.setText("Reverse")
            self.button_symmetric.hide()
            self.ds_box_other_length.setEnabled(False)
        else:
            self.button_two_sided.setText("Two sided")
            self.button_reverse.hide()
            self.button_symmetric.show()
            if self.symmetric_shape:
                self.button_symmetric.setText("Symmetric")
            self.ds_box_other_length.setEnabled(True)

    def addDistributeAngleWidgets(self, grid):
        '''Provides widgets to choose distribution direction and extent'''

        self.button_axis = QPushButton("Around V-Axis")
        self.button_axis.setToolTip(
            "Toggles the rotation around the h- or v-axis of the profile shape"
        )
        self.button_axis.show()
        self.button_axis.clicked.connect(self.onButtonAxisToroid)
        grid.addWidget(self.button_axis, 1, 0)

        #self.label_direction = QLabel("Direction")
        #grid.addWidget(self.label_direction, 1, 0)

        self.button_two_sided = QPushButton("One sided")
        self.button_two_sided.setToolTip("Enables two sided distribution")
        self.button_two_sided.show()
        self.button_two_sided.clicked.connect(self.onButtonTwoSidedToroid)
        grid.addWidget(self.button_two_sided, 1, 1)

        self.button_reverse = QPushButton("Forward")
        self.button_reverse.setToolTip("Reverts the distribution direction")
        self.button_reverse.show()
        self.button_reverse.clicked.connect(self.onButtonReverseToroid)
        grid.addWidget(self.button_reverse, 1, 2)

        self.button_symmetric = QPushButton("Two angles")
        self.button_symmetric.setToolTip(
            "Toggles between symmetric and a second angle"
        )
        self.button_symmetric.hide()
        self.button_symmetric.clicked.connect(self.onButtonSymmetricToroid)
        grid.addWidget(self.button_symmetric, 1, 2)

        self.label_angle = QLabel("Angle")
        grid.addWidget(self.label_angle, 2, 0)

        self.ds_box_angle = QDoubleSpinBox()
        self.ds_box_angle.setMaximum(360)
        self.ds_box_angle.setValue(self.forward_angle)
        self.ds_box_angle.valueChanged.connect(
            self.onDoubleSpinBoxAngleChanged
        )
        grid.addWidget(self.ds_box_angle, 2, 1)

        self.ds_box_other_angle = QDoubleSpinBox()
        self.ds_box_other_angle.setMaximum(360)
        self.ds_box_other_angle.setValue(self.reverse_angle)
        #self.ds_box_other_length.hide()
        self.ds_box_other_angle.setEnabled(False)
        self.ds_box_other_angle.valueChanged.connect(
            self.onDoubleSpinBoxOtherAngleChanged
        )
        grid.addWidget(self.ds_box_other_angle, 2, 2)

        if not self.two_sided_shape:
            self.button_two_sided.setText("One sided")
            self.button_reverse.show()
            if self.reverse_shape:
                self.button_reverse.setText("Reverse")
            self.button_symmetric.hide()
            self.ds_box_other_angle.setEnabled(False)
        else:
            self.button_two_sided.setText("Two sided")
            self.button_reverse.hide()
            self.button_symmetric.show()
            if self.symmetric_shape:
                self.button_symmetric.setText("Symmetric")
            self.ds_box_other_angle.setEnabled(True)

    #---------------------------------------------------------------------------
    # Logic blocks controlling the interaction of widgets
    #---------------------------------------------------------------------------
    # Profile shape:
    def onButtonProfileClicked(self, value):
        '''Toggles whether the profile is hollow or solid'''
        if self.button_profile.text() == "Solid":
            self.button_profile.setText("Hollow/Rib")
            self.hollow_profile = True
            self.button_profile_offset.show()
            self.button_fillet_profile.show()
            self.label_thickness.show()
            self.ds_box_thickness.show()
            self.label_radius.show()
            self.ds_box_radius.show()
            if self.button_profile_offset.text() == "Offset":
                self.button_offset_side.show()
            self.button_apply.setEnabled(True)
        else:
            self.button_profile.setText("Solid")
            self.hollow_profile = False
            self.button_profile_offset.hide()
            self.button_fillet_profile.hide()
            self.button_offset_side.hide()
            self.label_thickness.hide()
            self.ds_box_thickness.hide()
            self.label_radius.hide()
            self.ds_box_radius.hide()
            self.button_apply.setEnabled(True)

        if self.auto_recompute:
            self.onButtonApply()

    def onButtonProfileOffsetClicked(self, value):
        '''
        Toggles whether the profile thickness is positioned symmetrically
        across the profile center line
        '''
        if self.button_profile_offset.text() == "Middle":
            self.button_profile_offset.setText("Offset")
            if self.button_offset_side.text() == "This side":
                self.profile_offset = "Inside"
            else:
                self.profile_offset = "Outside"
            self.button_offset_side.show()
            self.button_apply.setEnabled(True)
        else:
            self.button_profile_offset.setText("Middle")
            self.profile_offset = "Middle"
            self.button_offset_side.hide()
            self.button_apply.setEnabled(True)

        if self.auto_recompute:
            self.onButtonApply()

    def onButtonOffsetSideClicked(self, value):
        '''
        Toggles the direction of the profile thickness according to
        the profile center line
        '''
        if self.button_offset_side.text() == "This side":
            self.button_offset_side.setText("Other side")
            self.profile_offset = "Outside"
            self.button_apply.setEnabled(True)
        else:
            self.button_offset_side.setText("This side")
            self.profile_offset = "Inside"
            self.button_apply.setEnabled(True)

        if self.auto_recompute:
            self.onButtonApply()

    def onDoubleSpinBoxThicknessChanged(self, value):
        self.profile_thickness = value
        self.button_apply.setEnabled(True)

    def onButtonFilletProfileClicked(self, value):
        '''
        Toggles if open/hollow profiles are automatically filletd
        '''
        if self.button_fillet_profile.text() == "Automatic Fillets":
            self.button_fillet_profile.setText("No Fillets")
            self.fillet_profile = False
            self.ds_box_radius.setEnabled(False)
            self.button_apply.setEnabled(True)
        else:
            self.button_fillet_profile.setText("Automatic Fillets")
            self.fillet_profile = True
            self.ds_box_radius.setEnabled(True)
            self.button_apply.setEnabled(True)

        if self.auto_recompute:
            self.onButtonApply()

    def onDoubleSpinBoxRadiusChanged(self, value):
        self.profile_radius = value
        self.button_apply.setEnabled(True)

    # Prismoid distribution:
    def onButtonTwoSidedPrismoid(self, value):
        '''
        Toggles one sided or two sided distribution
        '''
        if self.button_two_sided.text() == "One sided":
            self.button_two_sided.setText("Two sided")
            self.two_sided_shape = True
            self.button_reverse.hide()
            self.button_symmetric.show()
            self.ds_box_other_length.setEnabled(True)
            self.button_apply.setEnabled(True)
        else:
            self.button_two_sided.setText("One sided")
            self.two_sided_shape = False
            self.button_reverse.show()
            self.button_reverse.setText("Forward")
            self.reverse_shape = False
            self.button_symmetric.hide()
            self.button_symmetric.setText("Two Lengths")
            self.symmetric_shape = False
            self.ds_box_other_length.setEnabled(False)
            self.button_apply.setEnabled(True)

        if self.auto_recompute:
            self.onButtonApply()

    def onButtonReversePrismoid(self, value):
        '''
        Toggles between one sided and two sided distribution
        '''
        if self.button_reverse.text() == "Forward":
            self.button_reverse.setText("Reverse")
            self.reverse_shape = True
            #self.button_two_sided.show()
            #self.ds_box_other_length.setEnabled(True)
            self.button_apply.setEnabled(True)
        else:
            self.button_reverse.setText("Forward")
            self.reverse_shape = False
            #self.button_two_sided.show()
            #self.ds_box_other_length.setEnabled(False)
            self.button_apply.setEnabled(True)

        if self.auto_recompute:
            self.onButtonApply()

    def onButtonSymmetricPrismoid(self, value):
        '''
        Toggles one sided or two sided distribution
        '''
        if self.button_symmetric.text() == "Symmetric":
            self.button_symmetric.setText("Two Lengths")
            self.symmetric_shape = False
            #self.ds_box_other_length.show()
            self.ds_box_other_length.setEnabled(True)
            self.button_apply.setEnabled(True)
        else:
            self.button_symmetric.setText("Symmetric")
            self.symmetric_shape = True
            #self.ds_box_other_length.hide()
            self.ds_box_other_length.setEnabled(False)
            self.button_apply.setEnabled(True)

        if self.auto_recompute:
            self.onButtonApply()

    def onDoubleSpinBoxLengthChanged(self, value):
        self.forward_length = value
        self.button_apply.setEnabled(True)

    def onDoubleSpinBoxOtherLengthChanged(self, value):
        self.reverse_length = value
        self.button_apply.setEnabled(True)

    # Toroid distribution
    def onButtonAxisToroid(self, value):
        '''Toggles the automatic update'''
        if self.button_axis.text() == "Around V-Axis":
            self.button_axis.setText("Around H-Axis")
            self.vertical_axis = False
        else:
            self.button_axis.setText("Around V-Axis")
            self.vertical_axis = True

        self.button_apply.setEnabled(True)

        if self.auto_recompute:
            self.onButtonApply()

    def onButtonTwoSidedToroid(self, value):
        '''
        Toggles one sided or two sided distribution
        '''
        if self.button_two_sided.text() == "One sided":
            self.button_two_sided.setText("Two sided")
            self.two_sided_shape = True
            self.button_reverse.hide()
            self.button_symmetric.show()
            self.ds_box_other_angle.setEnabled(True)
            self.button_apply.setEnabled(True)
        else:
            self.button_two_sided.setText("One sided")
            self.two_sided_shape = False
            self.button_reverse.show()
            self.button_reverse.setText("Forward")
            self.reverse_shape = False
            self.button_symmetric.hide()
            self.button_symmetric.setText("Two Angles")
            self.symmetric_shape = False
            self.ds_box_other_angle.setEnabled(False)
            self.button_apply.setEnabled(True)

        if self.auto_recompute:
            self.onButtonApply()

    def onButtonReverseToroid(self, value):
        '''
        Toggles between one sided and two sided distribution
        '''
        if self.button_reverse.text() == "Forward":
            self.button_reverse.setText("Reverse")
            self.reverse_shape = True
            self.button_apply.setEnabled(True)
        else:
            self.button_reverse.setText("Forward")
            self.reverse_shape = False
            self.button_apply.setEnabled(True)

        if self.auto_recompute:
            self.onButtonApply()

    def onButtonSymmetricToroid(self, value):
        '''
        Toggles one sided or two sided distribution
        '''
        if self.button_symmetric.text() == "Symmetric":
            self.button_symmetric.setText("Two Angles")
            self.symmetric_shape = False
            #self.ds_box_other_length.show()
            self.ds_box_other_angle.setEnabled(True)
            self.button_apply.setEnabled(True)
        else:
            self.button_symmetric.setText("Symmetric")
            self.symmetric_shape = True
            #self.ds_box_other_length.hide()
            self.ds_box_other_angle.setEnabled(False)
            self.button_apply.setEnabled(True)

        if self.auto_recompute:
            self.onButtonApply()

    def onDoubleSpinBoxAngleChanged(self, value):
        self.forward_angle = value
        self.button_apply.setEnabled(True)

    def onDoubleSpinBoxOtherAngleChanged(self, value):
        self.reverse_angle = value
        self.button_apply.setEnabled(True)

    # Feature type:
    def onRadioButtonShapeToggled(self, value):
        '''
        Selects the type of shape
        '''
        # get the radio button that sent the signal
        if not value:
            return
        for button in self.group_buttons_shape.buttons():
            if button.isChecked():
                if button.text().startswith("Subtractive"):
                    self.shape_type = "Feature_Difference"
                elif button.text().startswith("Common"):
                    self.shape_type = "Feature_Intersection"
                else:
                    self.shape_type = "Feature_Union"

                self.button_apply.setEnabled(True)
                if self.auto_recompute:
                    self.onButtonApply()
                return

    # Update:
    def onButtonUpdate(self, value):
        '''Toggles the automatic update'''
        if self.button_update.text() == "Automatic Update":
            self.button_update.setText("Manual Update -->")
            self.auto_recompute = False
        else:
            self.button_update.setText("Automatic Update")
            self.auto_recompute = True

    def onButtonApply(self, value = None):
        '''
        Updates the object parameters with the task panel settings
        and runs a recompute
        '''

        # self.obj.ProfileShape = self.profile_shape - shouldn't change
        self.obj.ProfileThickness = self.profile_thickness
        self.obj.ProfileRadius = self.profile_radius
        self.obj.ProfileOffset = self.profile_offset #string from 2 variables
        self.obj.HollowProfile = self.hollow_profile
        self.obj.FilletProfile = self.fillet_profile
        self.obj.ShapeType = self.shape_type
        if hasattr(self.obj, "Reverse"):
            self.obj.Reverse = self.reverse_shape
            self.obj.Symmetric = self.symmetric_shape
            self.obj.TwoSided = self.two_sided_shape
            if hasattr(self.obj, "ForwardAngle"):
                self.obj.ForwardAngle = self.forward_angle
                self.obj.ReverseAngle = self.reverse_angle
                self.obj.VerticalAxis = self.vertical_axis
            elif hasattr(self.obj, "ForwardLength"):
                self.obj.ForwardLength = self.forward_length
                self.obj.ReverseLength = self.reverse_length

        App.ActiveDocument.recompute()
        self.button_apply.setEnabled(False)


    def accept(self):
        '''
        This is triggered by the panel's OK button.
        '''
        # Collect results
        if self.button_apply.isEnabled():
            self.onButtonApply()  # To not skip the latest changes
        Gui.Control.closeDialog()
        print("Accepted. ")

    def reject(self):
        '''
        This is triggered by the panel's Cancel button.
        '''
        # This still lacks a proper functionality
        Gui.Control.closeDialog()
        print("Canceled, there is nothing left to do!")

class PrismoidShapeTaskPanel(PartPlusShapeTaskPanel):
    '''
    Control panel for PrismoidShape objects.

    Changes properties (which in turn starts the execute() method
    of the PrismoidShape class)
    '''

    def __init__(self, obj):
        # obj is the visual representation view provider
        #- Make some class-wide settings
        self.obj = obj
        self.auto_recompute = False
        #- Retrieve class values from the object
        self.profile_shape = obj.ProfileShape
        self.profile_thickness = obj.ProfileThickness
        self.profile_radius = obj.ProfileRadius
        self.profile_offset = obj.ProfileOffset
        self.hollow_profile = obj.HollowProfile
        self.fillet_profile = obj.FilletProfile
        self.forward_length = obj.ForwardLength
        self.reverse_length = obj.ReverseLength
        self.two_sided_shape = obj.TwoSided
        self.reverse_shape = obj.Reverse
        self.symmetric_shape = obj.Symmetric
        self.shape_type = obj.ShapeType

        #- Add a QGroupBox container with a QGridLayout to group widgets
        self.group_box_0, self.grid_0 = self.groupBoxWithGrid()
        self.group_box_0.setWindowTitle("Prismoid Parameters")
        #- Add sub-boxes
        self.group_box_1, self.grid_1 = self.groupBoxWithGrid("Profile")
        self.group_box_1.setStyleSheet("background-color:#dec")
        self.grid_0.addWidget(self.group_box_1, 0, 0)

        self.group_box_2, self.grid_2 = self.groupBoxWithGrid("Distribution")
        self.group_box_2.setStyleSheet("background-color:#def")
        self.grid_0.addWidget(self.group_box_2, 1, 0)

        self.group_box_3, self.grid_3 = self.groupBoxWithGrid("Feature Type")
        self.group_box_3.setStyleSheet("background-color:#fed")
        self.grid_0.addWidget(self.group_box_3, 2, 0)

        self.group_box_4, self.grid_4 = self.groupBoxWithGrid("Update")
        self.group_box_4.setStyleSheet("background-color:#ddd")
        self.grid_0.addWidget(self.group_box_4, 10, 0)

        #- Add some widgets to the grids
        self.addSingleProfileWidgets(self.grid_1)

        self.addDistributeLengthWidgets(self.grid_2)

        self.addUpdateWidgets(self.grid_4)

        self.addFeatureWidgets(self.grid_3)

        self.form = self.group_box_0
        #- Hide the profile shape object
        obj.ProfileShape[0].Visibility = True  # [0] according to LinkSub

class ToroidShapeTaskPanel(PartPlusShapeTaskPanel):
    '''
    Control panel for ToroidShape objects.

    Changes properties (which in turn starts the execute() method
    of the ToroidShape class)
    '''

    def __init__(self, obj):
        # obj is the visual representation view provider
        #- Make some class-wide settings
        self.obj = obj
        self.auto_recompute = False
        #- Retrieve class values from the object
        self.profile_shape = obj.ProfileShape
        self.profile_thickness = obj.ProfileThickness
        self.profile_radius = obj.ProfileRadius
        self.profile_offset = obj.ProfileOffset
        self.hollow_profile = obj.HollowProfile
        self.fillet_profile = obj.FilletProfile
        self.vertical_axis = obj.VerticalAxis
        self.forward_angle = obj.ForwardAngle
        self.reverse_angle = obj.ReverseAngle
        self.two_sided_shape = obj.TwoSided
        self.reverse_shape = obj.Reverse
        self.symmetric_shape = obj.Symmetric
        self.shape_type = obj.ShapeType

        #- Add a QGroupBox container with a QGridLayout to group widgets
        self.group_box_0, self.grid_0 = self.groupBoxWithGrid()
        self.group_box_0.setWindowTitle("Toroid Parameters")
        #- Add sub-boxes
        self.group_box_1, self.grid_1 = self.groupBoxWithGrid("Profile")
        self.group_box_1.setStyleSheet("background-color:#dec")
        self.grid_0.addWidget(self.group_box_1, 0, 0)

        self.group_box_2, self.grid_2 = self.groupBoxWithGrid("Distribution")
        self.group_box_2.setStyleSheet("background-color:#def")
        self.grid_0.addWidget(self.group_box_2, 1, 0)

        self.group_box_3, self.grid_3 = self.groupBoxWithGrid("Feature Type")
        self.group_box_3.setStyleSheet("background-color:#fed")
        self.grid_0.addWidget(self.group_box_3, 2, 0)

        self.group_box_4, self.grid_4 = self.groupBoxWithGrid("Update")
        self.group_box_4.setStyleSheet("background-color:#ddd")
        self.grid_0.addWidget(self.group_box_4, 10, 0)

        #- Add some widgets to the grids
        self.addSingleProfileWidgets(self.grid_1)

        self.addDistributeAngleWidgets(self.grid_2)

        self.addUpdateWidgets(self.grid_4)

        self.addFeatureWidgets(self.grid_3)

        self.form = self.group_box_0
        #- Hide the profile shape object
        obj.ProfileShape[0].Visibility = True

class TransitionShapeTaskPanel(PartPlusShapeTaskPanel):
    '''
    Control panel for TransitionShape objects.

    Canges properties (which in turn starts the execute() method
    of the PrismoidShape class)
    '''

    def __init__(self, obj):
        # obj is the visual representation view provider
        #- Make some class-wide settings
        self.obj = obj
        self.auto_recompute = False
        #- Retrieve class values from the object
        self.profile_shape = obj.ProfileShape[0]
        self.profile_thickness = obj.ProfileThickness
        self.profile_radius = obj.ProfileRadius
        self.profile_offset = obj.ProfileOffset
        self.hollow_profile = obj.HollowProfile
        self.fillet_profile = obj.FilletProfile
        self.shape_type = obj.ShapeType

        #- Add a QGroupBox container with a QGridLayout to group widgets
        self.group_box_0, self.grid_0 = self.groupBoxWithGrid()
        self.group_box_0.setWindowTitle("Transition Shape Parameters")
        #- Add sub-boxes
        self.group_box_1, self.grid_1 = self.groupBoxWithGrid("Outline")
        self.group_box_1.setStyleSheet("background-color:#dec")
        self.grid_0.addWidget(self.group_box_1, 0, 0)

        self.group_box_2, self.grid_2 = self.groupBoxWithGrid("Distribution")
        self.group_box_2.setStyleSheet("background-color:#def")
        self.grid_0.addWidget(self.group_box_2, 1, 0)

        self.group_box_3, self.grid_3 = self.groupBoxWithGrid("Feature Type")
        self.group_box_3.setStyleSheet("background-color:#fed")
        self.grid_0.addWidget(self.group_box_3, 2, 0)

        self.group_box_4, self.grid_4 = self.groupBoxWithGrid("Update")
        self.group_box_4.setStyleSheet("background-color:#ddd")
        self.grid_0.addWidget(self.group_box_4, 10, 0)

        #- Add some widgets to the grids
        self.addProfilesWidgets(self.grid_1)

        #self.addDistributeAngleWidgets(self.grid_2)

        self.addUpdateWidgets(self.grid_4)

        self.addFeatureWidgets(self.grid_3)

        self.form = self.group_box_0
        #- Hide the profile shape object
        obj.ProfileShape[0].Visibility = True
        return

class DistributionShapeTaskPanel(PartPlusShapeTaskPanel):
    '''
    Control panel for DistributionShape objects.

    Canges properties (which in turn starts the execute() method
    of the PrismoidShape class)
    '''

    def __init__(self, obj):
        # obj is the visual representation view provider
        #- Make some class-wide settings
        self.obj = obj
        self.auto_recompute = False
        #- Retrieve class values from the object
        self.profile_shapes = obj.Sections[0]
        spine_shape = obj.Spine
        self.profile_thickness = obj.ProfileThickness
        self.profile_radius = obj.ProfileRadius
        self.profile_offset = obj.ProfileOffset
        self.hollow_profile = obj.HollowProfile
        self.fillet_profile = obj.FilletProfile
        self.shape_type = obj.ShapeType

        #- Add a QGroupBox container with a QGridLayout to group widgets
        self.group_box_0, self.grid_0 = self.groupBoxWithGrid()
        self.group_box_0.setWindowTitle("Distribution Shape Parameters")
        #- Add sub-boxes
        self.group_box_1, self.grid_1 = self.groupBoxWithGrid("Outline")
        self.group_box_1.setStyleSheet("background-color:#dec")
        self.grid_0.addWidget(self.group_box_1, 0, 0)

        self.group_box_2, self.grid_2 = self.groupBoxWithGrid("Distribution")
        self.group_box_2.setStyleSheet("background-color:#def")
        self.grid_0.addWidget(self.group_box_2, 1, 0)

        self.group_box_3, self.grid_3 = self.groupBoxWithGrid("Feature Type")
        self.group_box_3.setStyleSheet("background-color:#fed")
        self.grid_0.addWidget(self.group_box_3, 2, 0)

        self.group_box_4, self.grid_4 = self.groupBoxWithGrid("Update")
        self.group_box_4.setStyleSheet("background-color:#ddd")
        self.grid_0.addWidget(self.group_box_4, 10, 0)

        #- Add some widgets to the grids
        self.addProfilesWidgets(self.grid_1)

        #self.addDistributeAngleWidgets(self.grid_2)

        self.addUpdateWidgets(self.grid_4)

        self.addFeatureWidgets(self.grid_3)

        self.form = self.group_box_0
        #- Hide the profile shape object
        obj.Sections[0][0].Visibility = True
        return


from FreeCAD import Console
Console.PrintLog('freecad/PartPlus/PartPlusTaskPanels.py\n')
