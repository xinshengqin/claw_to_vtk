from vtkOverlappingAMR import *
import numpy as np
from clawpack.pyclaw import Solution
import pdb

frame = 6
path = '../acoustics_2d_radial/_output'
sol = Solution(frame, path=path, file_format='ascii')
global_origin = sol.state.patch.lower_global  # base patch
global_origin.append(0.0)  # append z
global_origin = np.array(global_origin)
levels = [state.patch.level-1 for state in sol.states]  # shift base level to 0
level_count = {}
level_spacing = {}  # spacing of each level
for i, level in enumerate(levels):
    if level in level_count.keys():
        level_count[level] = level_count[level] + 1
    else:
        level_count[level] = 1
        spacing = sol.states[i].patch.delta
        spacing.append(1.0)  # dz
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

        q = states_sorted[local_index].get_q_global()
        q1 = q[0, ...]
        q2 = q[1, ...]
        q3 = q[2, ...]
        q1 = q1.transpose()
        q2 = q2.transpose()
        q3 = q3.transpose()
        amrbox.set_cell_data(q1, "q1")
        amrbox.set_cell_data(q2, "q2")
        amrbox.set_cell_data(q3, "q3")

        # shape = list(q1.shape)
        # shape.append(1)
        # point_data = np.ones( np.array(shape) + 1)
        # amrbox.set_point_data(point_data)
        block.attached_amrbox(amrbox)
        AMRdata.attached_block(level, block)
    global_index = global_index + box_per_level[level]

AMRdata.write_ascii('test_amr')
