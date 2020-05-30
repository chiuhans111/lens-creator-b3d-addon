# This module contains all the fancy stuff that generates the lens mesh,
# Also creates a operator that do the generation of the lens

import math
import bpy


def area_from_three_sides(a, b, c):
    """ Calculates the area of triangle forms by given three side's length """
    s = (a+b+c)/2
    return math.sqrt(s*(s-a)*(s-b)*(s-c))


def auto_semi_diameter(r1, r2, thic):
    """ Calculates proper diameter from radius and thickness """
    t = abs(r1+r2-thic)
    if r1 == 0 and r2 == 0:
        return 0
    if r1 == 0 or r2 == 0:
        return math.sqrt(r1**2+r2**2-t**2)

    return area_from_three_sides(abs(r1), abs(r2), t)/t*2


def gen_verts(seg, semi_dia, radius, z_offset=0):
    """Generates all the vertices of the surface,
    the topology done here is the grid like but circle outside thing,
    Should be modified if better topology is needed.

    the lens will be generated on x-y plane, facing z+

    Args:
        seg (int): segments of the surface
             (total vertices = (seg*2+1)*(seg*2+1) )
        semi_dia (float): semi-diameter of the lens
        radius (float): the curvature radius of the lens surface
        z_offset (float): offsets the vertices in z
                          (z += offset)
    """

    verts = []  # stores all the vertices [(x,y,z), (x,y,z) ...]
    radius_sq = radius*radius  # the squared radius

    if radius!=0 and semi_dia > abs(radius):
        semi_dia = abs(radius)

    # generates all the vertices i:x-axis j:y-axis
    for i in range(-seg, seg+1):
        for j in range(-seg, seg+1):

            u = abs(i/seg)
            v = abs(j/seg)

            # new topology formula maybe better
            x = u*math.sqrt((v - u + 2)/(u*v - u - v + 2))*(-v + 2)/2*semi_dia
            y = v*math.sqrt((u - v + 2)/(u*v - u - v + 2))*(-u + 2)/2*semi_dia

            if i < 0:
                x *= -1
            if j < 0:
                y *= -1

            r = math.sqrt(x**2 + y**2)

            z = 0

            # calculates the z term
            if abs(radius) > r:
                z = math.sqrt(radius_sq-r*r)
            if radius > 0:
                z = -z

            # offset the z
            z += radius + z_offset

            verts.append((x, y, z))
    return verts


def gen_mesh_faces(seg, offset=0, inverse=False):
    """ Generates face indices that forms the mesh.

    the mesh is like:
     0  1  2  3
     4  5  6  7
     8  9 10 11
    12 13 14 15

    output will be:
    [(0,1,5,4), (1,2,6,5), ... , (10,11,15,14)]

    Args:
        seg (int): segments
        offset (int): offset in vertice index
        inverse (bool): reverse the face (=flip the normal)
    """

    faces = []
    span = seg*2+1
    for i in range(seg*2):
        for j in range(seg*2):
            n = i+j*span + offset
            if inverse:
                faces.append((n+span,  n+span+1, n+1, n))
            else:
                faces.append((n, n+1, n+span+1, n+span))
    return faces


def get_vert_loop_ids(seg, offset=0):
    """ Get the vertices ids of the outside loop of the lens

    for example:
     0  1  2  3
     4  5  6  7
     8  9 10 11
    12 13 14 15

    will have a output of: [0,1,2,3,7,11,15,14,13,12,8,4]

    Args:
        seg (int): segments
        offset (int): offset in vertice index
    """

    w = seg*2+1
    loop = list(range(w)) + list(range(w*2-1, w*w, w))\
        + list(range(w*w-w, w*w-1))[::-1] + list(range(w, w*w-w, w))[::-1]
    return [n+offset for n in loop]


def gen_loop_faces(loop1, loop2):
    """ Generates face indices that bridges two loop 
    given by 'get_vert_loop_ids' function
    """
    faces = []
    l = len(loop1)
    for i in range(l):
        faces.append((
            loop1[(i+1) % l],
            loop1[i],
            loop2[i],
            loop2[(i+1) % l]
        ))
    return faces


def get_edge_pairs(faces):
    """ get all the edge indices from face indices,
    as this function is unnecessary for the mesh generation,
    might be removed in the future.
    """
    edges = []
    for face in faces:
        for i in range(len(face)):
            a = face[i]
            b = face[(i+1) % len(face)]
            edges.append((min(a, b), max(a, b)))
    return list(set(edges))


class MESH_OT_lens_mesh_add(bpy.types.Operator):
    """Create lens mesh"""

    bl_idname = "mesh.lens_mesh_add"
    bl_label = "Lens Mesh"
    bl_options = {'REGISTER', 'UNDO'}

    radius1: bpy.props.FloatProperty(name="Radius 1",
                                     description="Specify the radius of the surface 1, 0 for plane",
                                     default=0)

    radius2: bpy.props.FloatProperty(name="Radius 2",
                                     description="Specify the radius of the surface 2, 0 for plane",
                                     default=0)

    semi_diameter: bpy.props.FloatProperty(name="Semi-Diameter",
                                           description="Specify the diameter of the lens, 0 for auto",
                                           default=1, min=0)

    thickness: bpy.props.FloatProperty(name="Thickness",
                                       description="Specify the thickness of the lens",
                                       default=0)

    segments: bpy.props.IntProperty(name="Segments",
                                    description="Specify the segments of the surface",
                                    default=5, min=1)

    def execute(self, context):

        # diameter solve
        if self.semi_diameter == 0:
            self.semi_diameter = auto_semi_diameter(
                self.radius1, -self.radius2, self.thickness
            )

        # creating mesh data
        verts = []
        faces = []

        # surface 1
        verts += gen_verts(self.segments, self.semi_diameter,
                           self.radius1)
        faces += gen_mesh_faces(self.segments)
        sur1_vert_count = len(verts)  # count the offset in vertices

        # surface 2
        verts += gen_verts(self.segments, self.semi_diameter,
                           self.radius2, self.thickness)
        faces += gen_mesh_faces(self.segments, sur1_vert_count, inverse=True)

        # bridge loops
        loop1 = get_vert_loop_ids(self.segments)
        loop2 = get_vert_loop_ids(self.segments, sur1_vert_count)
        faces += gen_loop_faces(loop1, loop2)

        # apply the mesh
        edges = get_edge_pairs(faces)
        mesh = bpy.data.meshes.new("Lens")
        mesh.from_pydata(verts, edges, faces)

        # smooth shading
        for f in mesh.polygons:
            f.use_smooth = True

        # put the mesh into the scene
        from bpy_extras import object_utils
        object_utils.object_data_add(context, mesh, operator=None)

        # bpy.ops.object.mode_set(mode='EDIT')
        # bpy.ops.object.shade_smooth()

        return {'FINISHED'}
