from clawpack.pyclaw import Solution
import numpy as np


def getClawOutput():
    frame = 3  # decide reading data at which time
    sol = Solution(frame, path='acoustics_2d_radial/_output',
                   file_format='ascii')
    print "number of states in this Solution object:", len(sol.states)
    result = list(sol.state.q[1, :].flatten('F'))
    return result


def getAllOriginsAndSpacing(frame, level):
    assert(isinstance(frame, int))
    input_path = 'acoustics_2d_radial/_output'
    input_format = 'ascii'
    sol = Solution(frame, path=input_path, file_format=input_format)
    # may need to sort these states in the future
    # but for now, assume each time we it's in the same order
    result = []
    print "Call python function: getAllOriginsAndSpacing."
    for state in sol.states:
        if (state.patch.level == level+1):
            origin = list(state.patch.lower_global)
            origin.append(0.0)  # z=0 for 2D
            print "Origin: ", origin
            for i in range(3):
                result.append(origin[i])
            spacing = list(state.patch.delta)
            spacing.append(spacing[0])  # dz=dx
            print "Spacing: ", spacing
            for i in range(3):
                result.append(spacing[i])
    print "\n"
    return result


def getLevels(frame):
    assert(isinstance(frame, int))
    input_path = 'acoustics_2d_radial/_output'
    input_format = 'ascii'
    sol = Solution(frame, path=input_path, file_format=input_format)

    levels = [state.patch.level-1 for state in sol.states]
    # shift base level to 0, since the base level in clawpack
    # is 1 while the base level in VTK is 0
    level_count = {}
    level_spacing = {}  # spacing of each level
    print "Call python function: getLevels."
    for i, level in enumerate(levels):
        if level in level_count.keys():
            level_count[level] = level_count[level] + 1
        else:
            level_count[level] = 1
            spacing = sol.states[i].patch.delta
            spacing.append(spacing[0])  # dz = dx
            spacing = np.array(spacing)
            level_spacing[level] = spacing

    # a list of num of patches at each level
    box_per_level = [item[1] for item in
                     sorted(level_count.items(),
                            key=lambda a: a[0])]
    box_per_level = np.array(box_per_level)
    print "box_per_level in python:"
    print box_per_level
    print "\n"

    return list(box_per_level)


def multiply():
    c = 12345*6789
    print 'The result of 12345 x 6789 :', c
    a = np.ones((3, 4))
    return list(a.flatten('F'))
