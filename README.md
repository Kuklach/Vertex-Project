# Vertex Projection

Vertex Projection is a simple yet powerful Blender addon that allows you to project edges or vertices onto a plane defined by the cursor location and normal. If you're tired of manually selecting vertices and scaling them to zero, or creating custom transform orientations for similar tasks, this addon can be a helpful solution without the need for heavy and expensive addons.

<img src="./assets/Example.gif" width="50%" height="50%"/>

## Features

- Project edges or vertices onto a plane defined by the cursor location and normal
- Ability to project vertices from the positive, negative, or closest side of the plane
- Option to use vertices or edges
- Option to use an alternative normal vector for vertices only projection
- Customizable visual helpers

## Installation

1. Download the latest release from the [Releases page](https://github.com/Kuklach/Vertex-Project/releases).
2. In Blender, go to `Edit` > `Preferences` > `Add-ons` and click the `Install` button.
3. Navigate to the downloaded file and select it to install the addon.
4. Enable the addon by checking the box next to "Vertex Project" in the addon list.

## Usage

1. Open the 3D View and select the desired object.
2. Go to the sidebar (`N` key) and find the "Kuklach Tools" panel.
3. You can define the plane normal from 2 or 3 selected vertices, or manually set it using the provided options. The plane's position is defined by the 3D cursor.
4. Once you have set up your projection plane, click the "Positive", "Negative", or "Closest" button to project the selected vertices or edges onto the plane.
5. The "Closest" option will project the vertex of each edge that is closest to the projection plane. The "Positive" or "Negative" options will project vertices closest to the positive or negative side of the plane, respectively.
6. To better understand the projection, you can enable the visual helpers to see the projection plane, its positive and negative directions, and preview lines from the vertices to the plane (for vertex projection only).
7. To project only vertices, enable the "Use Vertices Only" option.
8. You can also use a custom normal for vertex-only projection in the "Vertex Projection Options" tab.

## Customization

You can customize the appearance of the visual helpers by going to `Edit` > `Preferences` > `Add-ons` > `Vertex Project`.
