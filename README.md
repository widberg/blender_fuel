# blender_fuel

Blender scripts for FUEL's object formats.

<sup>This repository is a relative of the main [FMTK repository](https://github.com/widberg/fmtk).</sup>

## Table of Contents

### `addons/blender_fuel`

The scripts in this directory operate on the object file directories. They are intended to be loaded as an addon and interacted with using the GUI.

### `legacy`

The scripts in this directory operate directly on the object files. They are intended to be run from the "Scripting" view. Currently these scripts are more complete than the new addon scripts. These scripts will be removed once the new scripts reach feature parity with them.

## Related Information

Information about FUEL's coordinate systems and how they differs from Blender's is available in the [fmtk wiki Coordinate Systems entry](https://github.com/widberg/fmtk/wiki/Coordinate-Systems). The defunct [FUEL Noesis scripts](https://github.com/widberg/fmt_fuel) can be read for additional information.

## Getting Started

### For Users

Copy the `addons/blender_fuel` directory to the Blender `scripts/addons` directory or set the scripts path in `Edit -> Preferences -> File Paths -> Data -> Scripts` to the root directory of the repository.

### For Developers

The [Blender Development](https://marketplace.visualstudio.com/items?itemName=JacquesLucke.blender-development) Visual Studio Code plugin can be used to ease development. Simply open the `addons/blender_fuel` subdirectory in Visual Studio Code and follow the directions on the extension page.
