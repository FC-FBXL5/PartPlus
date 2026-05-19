# <img src="/freecad/PartPlus/resources/icons/PartPlus_Workbench.svg" height="64"> FreeCAD_PartPlus

A workbench to prove that it is possible to build tools that can create Part solids as well as PartDesign features.

These PartDesign features are mounted to an existing body like any other feature created within the PartDesign workbench itself. The difference is, that a newly created shape does not only use boolean union and difference to add to or to cut from the existing geometry but it also uses boolean intersection to obtain the common geometry.

## Sources

Since this workbench was beyond available coding skills lots of functions from the **Gear** and the **SheetMetal** workbenches were reused (the Python way: Adopt, adapt, and improve ...). Thanks for already providing many of the solutions for occurring coding challanges.

## Tools

The tools have in common that they create solid shapes from either closed or open wires, enabling an easier way to create ribs and pipes with constant thickness.

### <img src="/freecad/PartPlus/resources/icons/PartPlus_Prismoid.svg" height="32"> Prismoid Shape

This creates a shape with constant cross-section along its distribution direction (only along the sketch normal at the moment). This corresponds to extrude a pad.

### <img src="/freecad/PartPlus/resources/icons/PartPlus_Toroid.svg" height="32"> Toroid Shape

This creates a shape with constant cross-section around an axis (only around either the horizontal or the vertical sketch axis at present). This corresponds to a revolve tool.

### <img src="/freecad/PartPlus/resources/icons/PartPlus_Distribution.svg" height="32"> Distribution Shape

This creates a shape by distributing a profile along a spine. This corresponds to a sweep or pipe tool. It also accepts several optional section wires to alter the cross-section along the spine.

### <img src="/freecad/PartPlus/resources/icons/PartPlus_Transition.svg" height="32"> Transition Shape

This creates a shape that performs a transition from one 2D shape to another, a profile wire and a section wire. This corresponds to a loft tool. It also accepts several optional section wires to control the cross-section between its limits.

## Release notes:

* v.0.0.1 - 18.Mai.2026: Initial version.
