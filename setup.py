import sys

from setuptools import setup
from babel.messages import frontend as babel

try:
    from mwareeth import __version__
except SyntaxError as exc:
    sys.stderr.write(f"Unable to import Babel ({exc}). Are you running a supported version of Python?\n")
    sys.exit(1)


setup(
    cmdclass = {
        'compile_catalog': babel.compile_catalog,
        'extract_messages': babel.extract_messages,
        'init_catalog': babel.init_catalog,
        'update_catalog': babel.update_catalog,
    },
    packages = ['mwareeth'],
    message_extractors = {
        'mwareeth': [
            ('**.py', 'python', None),
        ],
    },
)
