from __future__ import print_function
import os
import shutil
import pymake
from pymake.autotest import get_namefiles, compare_budget
import config


def compare(namefile1, namefile2):
    """
    Compare the results from two simulations
    """

    # Compare budgets from the list files in namefile1 and namefile2
    outfile = os.path.join(os.path.split(namefile1)[0], 'bud.cmp')
    success = compare_budget(namefile1, namefile2, max_cumpd=0.01, max_incpd=0.01,
                   outfile=outfile)
    return success


def run_mfusg(namefile, regression=True):
    """
    Run the simulation.

    """

    # Set root as the directory name where namefile is located
    testname = os.path.dirname(namefile).split(os.sep)[-1]

    # Set nam as namefile name without path
    nam = os.path.basename(namefile)

    # Setup
    testpth = os.path.join(config.testdir, testname)
    pymake.setup(namefile, testpth)

    # run test models
    print('running model...{}'.format(testname))
    exe_name = os.path.abspath(config.target)
    success, buff = pymake.run_model(exe_name, nam, model_ws=testpth,
                                     silent=True)

    # If it is a regression run, then setup and run the model with the
    # release target
    success_reg = True
    if regression:
        testname_reg = os.path.basename(config.target_release)
        testpth_reg = os.path.join(testpth, testname_reg)
        pymake.setup(namefile, testpth_reg)
        print('running regression model...{}'.format(testname_reg))
        exe_name = os.path.abspath(config.target_release)
        success, buff = pymake.run_model(exe_name, nam, model_ws=testpth_reg,
                                         silent=True)

        # Make comparison
        success_reg = compare(os.path.join(testpth, nam),
                              os.path.join(testpth_reg, nam))

    # Clean things up
    if success and not config.retain:
        pymake.teardown(testpth)
    assert success and success_reg

    return


def test_mfusg():
    namefiles = get_namefiles(config.testpaths[0])
    for namefile in namefiles:
        yield run_mfusg, namefile
    return


if __name__ == '__main__':
    namefiles = get_namefiles(config.testpaths[0])
    for namefile in namefiles:
        run_mfusg(namefile)
