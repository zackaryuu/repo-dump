
class _CtxImports:
    import os
    import shutil
    import subprocess
    import re
    import sys
    import json
    import time
    import datetime
    import pathlib
    import tempfile
    import platform
    import glob
    import yaml
    import csv
    import random
    import string
    import zipfile

    def __setattr__(self, name, value):
        raise AttributeError("CtxImports is immutable")
        
    def __delattr__(self, name):
        raise AttributeError("CtxImports is immutable")
        
CtxImports = _CtxImports()