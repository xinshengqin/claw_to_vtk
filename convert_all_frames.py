#!/usr/bin/python
from vtkOverlappingAMR import *
import numpy as np
from clawpack.pyclaw import Solution
import pdb
import sys
import os
from claw_find_overlapped import *


def convert_claw_to_vtk(frame, input_path, output_name, input_format):
    assert(isinstance(frame,int))
    sol = Solution(frame, path=input_path, file_format=input_format)
    set_overlapped_status(sol)

    global_origin = sol.state.patch.lower_global  # base patch
    global_origin.append(0.0)  # append z
    global_origin = np.array(global_origin)
    levels = [state.patch.level-1 for state in sol.states]
    # shift base level to 0
    level_count = {}
    level_spacing = {}  # spacing of each level
    for i, level in enumerate(levels):
        if level in level_count.keys():
            level_count[level] = level_count[level] + 1
        else:
            level_count[level] = 1
            spacing = sol.states[i].patch.delta
            spacing.append(spacing[0])  # dz = dx
            spacing = np.array(spacing)
            level_spacing[level] = spacing
    num_levels = len(level_count.keys())

# a list of num of patches at each level
    box_per_level = [item[1] for item in
                     sorted(level_count.items(),
                            key=lambda a: a[0])]
    box_per_level = np.array(box_per_level)
    AMRdata = vtkOverlappingAMR(global_origin, num_levels, box_per_level)

    states_sorted = sorted(sol.states, key=lambda a: a.patch.level)
    global_index = 0
#################################################
    for level in level_count.keys():
        nbox = level_count[level]
        block = vtkAMRBlock(level, nbox, level_spacing[level], global_origin)

        for index in range(box_per_level[level]):
            # ----each vtkAMRBlock can have multiple vtkAMRBox
            local_index = global_index + index
            origin = states_sorted[local_index].patch.lower_global
            origin.append(0.0)  # append z
            origin = np.array(origin)
            ndim = states_sorted[local_index].patch.num_cells_global
            ndim.append(0.0)  # mz
            ndim = np.array(ndim, dtype=np.int)
            ndim = ndim + 1  # ndim should be num of nodes
            amrbox = vtkAMRBox(origin, ndim)

            q = states_sorted[local_index].q
            for i in range(q.shape[0]-1):
                q_i = q[i, ...]
                q_i = q_i.transpose()
                amrbox.set_cell_data(q_i, "q_"+str(i))
            q_ol = q[-1, ...]  # last piece is used to mark overlapped cells
            q_ol = q_ol.transpose()
            amrbox.set_cell_data(q_ol, "vtkGhostType", "UInt8")

            # set vtkGhostType data
            # ghost_q = np.zeros(q[0, ...].shape, dtype=int)
            # ghost_q = ghost_q.transpose()
            # amrbox.set_cell_data(ghost_q, "vtkGhostType", data_type="UInt8")

            # shape = list(q1.shape)
            # shape.append(1)
            # point_data = np.ones( np.array(shape) + 1)
            # amrbox.set_point_data(point_data)
            block.attached_amrbox(amrbox)
            AMRdata.attached_block(level, block)
        global_index = global_index + box_per_level[level]

    AMRdata.write_ascii(output_name+str(frame))


def main(argv):
    input_path = '_output'
    output_dir = "vtk_output"

    if output_dir not in os.listdir('./'):
        os.mkdir(output_dir)
    os.chdir(output_dir)
    input_path = '../'+input_path

    assert((len(argv) == 3)), \
        "usage: python convert_all_frames.py <input format> <first frame> <last frame>"
    for frame in range(int(argv[1]), int(argv[2])):
        convert_claw_to_vtk(frame, input_path, 'acoustic_2d_', argv[0])


if __name__ == "__main__":
    main(sys.argv[1:])
