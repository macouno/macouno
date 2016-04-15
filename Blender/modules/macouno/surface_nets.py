# The MIT License (MIT)
#
# Copyright (c) 2012-2013 Mikola Lysenko
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
 
# Original JS author:
# SurfaceNets in JavaScript
#
# Written by Mikola Lysenko (C) 2012
# MIT License
#
# Based on: S.F. Gibson, "Constrained Elastic Surface Nets". (1998) MERL Tech Report.
#
# Transpiled to Python by Angus Hollands (agoose77) 2016

import bpy
from array import array
from collections import namedtuple
from itertools import product
from math import ceil, sqrt


MesherResult = namedtuple("MesherResult", "vertices faces")
Volume = namedtuple("Volume", "data dimms")


def ones_of(n):
    return (1.0 for i in range(n))

def zeros_of(n):
    return (0 for i in range(n))


def _build_cube_edges():
    cube_edges = array('l', zeros_of(24))

    k = 0
    for i, j in product(range(8), (1, 2, 4)):
        p = i ^ j

        if (i <= p):
            cube_edges[k] = i
            k += 1
            cube_edges[k] = p
            k += 1

    return cube_edges


def _build_edge_table(cube_edges):
    edge_table = array('l', zeros_of(256))
    for i in range(256):
        em = 0
        for j in range(0, 24, 2):
            a = bool(i & (1 << cube_edges[j]))
            b = bool(i & (1 << cube_edges[j + 1]))

            if a != b:
                em |= (1 << (j >> 1))

        edge_table[i] = em

    return edge_table


class SurfaceNetMesher:
    _cube_edges = _build_cube_edges()
    _edge_table = _build_edge_table(_cube_edges)

    def __init__(self):
        self._buffer = array('l', zeros_of(4096))

    def mesh_volume(self, data, dims):
        edge_table = self._edge_table
        cube_edges = self._cube_edges
        buffer = self._buffer

        vertices = []
        faces = []
        n = 0
        x = array('l', zeros_of(3))
        R = array('l', [1, dims[0] + 1, (dims[0] + 1) * (dims[1] + 1)])
        grid = array('f', zeros_of(8))
        buf_no = 1

        # Resize buffer if necessary
        if R[2] * 2 > len(buffer):
            buffer.extend(zeros_of(R[2] * 2))

        # March over the voxel grid
        for x_2 in range(dims[2] - 1):
            # m is the pointer into the buffer we are going to use.
            # This is slightly obtuse because javascript does not have good support for packed data structures, so we must use typed arrays :(
            # The contents of the buffer will be the indices of the vertices on the previous x/y slice of the volume

            m = 1 + (dims[0] + 1) * (1 + buf_no * (dims[1] + 1))

            for x_1 in range(dims[1] - 1):
                for x_0 in range(dims[0] - 1):
                    # Read in 8 field values around this vertex and store them in an array
                    # Also calculate 8-bit mask, like in marching cubes, so we can speed up sign checks later
                    mask = 0
                    g = 0
                    idx = n

                    for k in range(2):
                        for j in range(2):
                            for i in range(2):
                                p = data[idx]
                                grid[g] = p

                                if p < 0:
                                    mask |= 1 << g

                                g += 1
                                idx += 1

                            idx += dims[0] - 2

                        idx += dims[0] * (dims[1] - 2)

                    if not (mask == 0 or mask == 0xff):
                        edge_mask = edge_table[mask]
                        v = [0.0, 0.0, 0.0]
                        e_count = 0

                        # For every edge of the cube...
                        for i in range(12):
                            # Use edge mask to check if it is crossed
                            if not (edge_mask & (1 << i)):
                                continue

                            # If it did, increment number of edge crossings
                            e_count += 1

                            # Now find the point of intersection:
                            # Unpack vertices
                            e0 = cube_edges[i << 1]
                            e1 = cube_edges[(i << 1) + 1]

                            # Unpack grid values
                            g0 = grid[e0]
                            g1 = grid[e1]
                            # Compute point of intersection
                            t = g0 - g1

                            if abs(t) > 1e-6:
                                t = g0 / t

                            else:
                                continue

                            # Interpolate vertices and add up intersections (this can be done without multiplying)
                            k = 1
                            for j in range(3):
                                a = e0 & k
                                b = e1 & k

                                if a != b:
                                    v[j] += (1 - t) if a else t

                                elif a:
                                    v[j] += 1

                                k <<= 1

                        # Now we just average the edge intersections and add them to coordinate
                        s = 1.0 / e_count
                        for i in range(3):
                            v[i] = x[i] + s * v[i]

                        # Add vertex to buffer, store pointer to vertex index in buffer
                        buffer[m] = len(vertices)
                        vertices.append(v)

                        # Now we need to add faces together, to do this we just loop over 3 basis components
                        for i in range(3):
                            # The first three entries of the edge_mask count the crossings along the edge
                            if not (edge_mask & (1 << i)):
                                continue

                            # i = axes we are point along.  iu, iv = orthogonal axes
                            iu = (i + 1) % 3
                            iv = (i + 2) % 3

                            # If we aren't on a boundary
                            if not x[iu] or not x[iv]:
                                continue

                            # Look up adjacent edges in buffer
                            du = R[iu]
                            dv = R[iv]

                            # Remember to flip orientation depending on the sign of the corner.
                            if mask & 1:
                                faces.append([buffer[m], buffer[m - du], buffer[m - du - dv], buffer[m - dv]])

                            else:
                                faces.append([buffer[m], buffer[m - dv], buffer[m - du - dv], buffer[m - du]])

                    # END STEP while x[0] < dims[0] - 1:
                    x[0] = x_0
                    n += 1
                    m += 1

                # END STEP while x[1] < dims[1] - 1:
                x[1] = x_1
                n += 1
                m += 2

            # End March over the voxel grid
            x[2] = x_2
            n += dims[0]
            buf_no ^= 1
            R[2] *= -1

        return MesherResult(vertices, faces)


def make_volume(dims, f):
    res = [2 + ceil((dims[i][1] - dims[i][0]) / dims[i][2]) for i in range(3)]
    volume = array('f', zeros_of(res[0] * res[1] * res[2]))
    n = 0

    z = dims[2][0] - dims[2][2]
    for k in range(res[2]):

        y = dims[1][0] - dims[1][2]
        for j in range(res[1]):

            x = dims[0][0] - dims[0][2]
            for i in range(res[0]):
                volume[n] = f(x, y, z)

                x += dims[0][2]
                n += 1

            y += dims[1][2]

        z += dims[2][2]

    return Volume(volume, res)
	
	
def create_dot():
    return make_volume(
        [[-1.0, 1.0, 1.0],
         [-1.0, 1.0, 1.0],
         [-1.0, 1.0, 1.0]],
        lambda x, y, z: x * x + y * y + z * z - 1.0
    )

def create_sphere():
    return make_volume(
        [[-1.0, 1.0, 0.25],
         [-1.0, 1.0, 0.25],
         [-1.0, 1.0, 0.25]],
        lambda x, y, z: x * x + y * y + z * z - 1.0
    )


def create_torus():
    return make_volume(
        [[-2.0, 2.0, 0.2],
         [-2.0, 2.0, 0.2],
         [-1.0, 1.0, 0.2]],
        lambda x, y, z: pow(1.0 - sqrt(x * x + y * y), 2) + z * z - 0.25
    )


def mesh_from_data(vertices, faces, name="MesherResult"):
    mesh_data = bpy.data.meshes.new("cube_mesh_data")
    mesh_data.from_pydata(vertices, [], faces)
    mesh_data.update()  # (calc_edges=True) not needed here
    return mesh_data