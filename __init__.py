# ##### BEGIN GPL LICENSE BLOCK #####
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

# This project is me practicing how to write an add-on
# Might have lots of problems
# -- Hans Chiu

import bpy
from bpy.props import FloatProperty
from . lens_creator import MESH_OT_lens_mesh_add # all the fancy stuff

bl_info = {
    "name": "Lens Creator",
    "author": "Hans Chiu",
    "description": "a very simple lens generator",
    "blender": (2, 80, 0),
    "version": (0, 0, 1),
    "location": "View3D > Add > Mesh",
    "warning": "",
    "category": "Add Mesh"
}


classes = (
    MESH_OT_lens_mesh_add,
)


def menu_func(self, context):
    """ my lens button menu (just one button) """
    layout = self.layout
    layout.operator_context = 'INVOKE_REGION_WIN'
    layout.separator()
    layout.operator("mesh.lens_mesh_add", text="Lens", icon="MESH_CIRCLE")


register_class, unregister_class = bpy.utils.register_classes_factory(classes)


def register():
    register_class()
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func) # put the button into menu


def unregister():
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func) # take away the button from menu
    unregister_class()

