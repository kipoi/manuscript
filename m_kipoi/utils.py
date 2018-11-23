import pickle
from collections import OrderedDict
from tqdm import tqdm
import sys
import os


def write_bcolz(arr, fname, create_dirs=True, **kwargs):
    import bcolz
    """Save a bcolz array to file

    Args
      fname: file name
      arr: numpy array
      create_dirs: recursively create the target dictionary
    """
    if create_dirs:
        os.makedirs(os.path.dirname(fname), exist_ok=True)
    c = bcolz.carray(arr, rootdir=fname, mode='w', **kwargs)
    c.flush()


def read_bcolz(fname):
    import bcolz
    """Load the bcolz array from memory (all at once)
    """
    return bcolz.open(fname)[:]


def write_pkl(obj, fname, create_dirs=True):
    if create_dirs:
        os.makedirs(os.path.dirname(fname), exist_ok=True)
    with open(fname, 'wb') as f:
        pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)


def read_pkl(fname):
    with open(fname, 'rb') as f:
        return pickle.load(f)


def flatten_dict(dd, separator='_', prefix=''):
    return OrderedDict([(prefix + separator + k if prefix else k, v)
                        for kk, vv in dd.items()
                        for k, v in flatten_dict(vv, separator, kk).items()
                        ]) if isinstance(dd, OrderedDict) else OrderedDict([(prefix, dd)])


def ensure_dirs(fname):
    """Ensure that the basepath of the given file path exists.
    Args:
      fname: (full) file path
    """
    required_path = "/".join(fname.split("/")[:-1])
    if not os.path.exists(required_path):
        os.makedirs(required_path)


def get_env_executable(env):
    """Returns a path to the kipoi exectuable
    """
    py_bin = os.environ.get("CONDA_PYTHON_EXE")
    if not py_bin:
        py_bin = sys.executable
    # sys.executable
    return os.path.abspath(os.path.join(py_bin, "../../envs/{env}/bin/kipoi".format(env=env)))
