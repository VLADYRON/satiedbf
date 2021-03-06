# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui
from .dbfread import DBF
import os
import glob
import fnmatch
from Controller.caches import memoize

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8

    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


def _get_icon(src):
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap(_fromUtf8(src)), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    return icon


def _get_img(src):
    img = QtGui.QPixmap(_fromUtf8(src))
    return img


def ipat(pat):
    """Convert glob pattern to case insensitive form."""

    (dirname, pat) = os.path.split(pat)

    # Convert '/path/to/test.fpt' => '/path/to/[Tt][Ee][Ss][Tt].[]' 
    newpat = ''
    for c in pat:
        if c.isalpha:
            u = c.upper()
            l = c.lower()
            if u != l:
                newpat = newpat + '[' + u + l + ']'
            else:
                newpat += c
        else:
            newpat += c

    newpat = os.path.join(dirname, newpat)

    return newpat


def ifnmatch(name, pat):
    """Case insensitive version of fnmatch.fnmatch()"""
    return fnmatch.fnmatch(name, ipat(pat))


def iglob(pat):
    """Case insensitive version of glob.glob()"""
    return glob.glob(ipat(pat))


def ifind(pat, ext=None):
    """Look for a file in a case insensitive way.
    Returns filename it a matching file was found, or None if it was not.
    """

    if ext:
        pat = os.path.splitext(pat)[0] + ext

    files = iglob(pat)
    if files:
        return files[0]  # Return an arbitrary file
    else:
        return None

# https://github.com/zopefoundation/zope.dottedname/blob/master/src/zope/dottedname/resolve.py
def resolve(name, module=None):
    """Resolve ``name`` to a Python object via imports / attribute lookups.
    If ``module`` is None, ``name`` must be "absolute" (no leading dots).
    If ``module`` is not None, and ``name`` is "relative" (has leading dots),
    the object will be found by navigating relative to ``module``.
    Returns the object, if found.  If not, propagates the error.
    """
    name = name.split('.')
    if not name[0]:
        if module is None:
            raise ValueError("relative name without base module")
        module = module.split('.')
        name.pop(0)
        while not name[0]:
            module.pop()
            name.pop(0)
        name = module + name

    used = name.pop(0)
    found = __import__(used)
    for n in name:
        used += '.' + n
        try:
            found = getattr(found, n)
        except AttributeError:
            __import__(used)
            found = getattr(found, n)

    return found


class DBFRead(object):
    """ """

    def __init__(self, filename, encoding='latin1',
                 char_decode_errors='strict', ignore_missing_memofile=True):

        self.encoding = encoding
        self.ignore_missing_memofile = ignore_missing_memofile
        self.char_decode_errors = 'strict'
        self.filename = ifind(filename)

        if not self.filename:
            raise DBFNotFound('could not find file {!r}'.format(filename))

        else:
            self.filename = filename

        self.dbf = DBF(filename, encoding=self.encoding,
                       ignore_missing_memofile=self.ignore_missing_memofile,
                       char_decode_errors=self.char_decode_errors, load=False)

    @property
    def meta_data(self):
        header = self.dbf.header.__dict__

        header['date'] = str(self.dbf.date)
        header['filename'] = self.dbf.filename
        header['name'] = self.dbf.name

        return header

    @property
    def fields(self):
        return self.dbf.field_names

    @memoize
    def parseDBF(self):
        """ """
        # https://github.com/olemb/dbfread
        return [dict(i) for i in self.dbf]


def pyqt_pdb():
    """ """
    from pdb import set_trace

    # Stop the QT check for gui event loop and put the break point
    QtCore.pyqtRemoveInputHook()
    set_trace()
