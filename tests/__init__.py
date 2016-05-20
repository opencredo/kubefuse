from myna import shim
import unittest

tmpdir = None

def setUp():
    global tmpdir
    tmpdir = shim.setup_shim_for('kubectl')	

def tearDown():
    global tmpdir
    shim.teardown_shim_dir(tmpdir)
