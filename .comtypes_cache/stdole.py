from enum import IntFlag

import comtypes.gen._00020430_0000_0000_C000_000000000046_0_2_0 as __wrapper_module__
from comtypes.gen._00020430_0000_0000_C000_000000000046_0_2_0 import (
    IFont, FONTITALIC, FONTBOLD, BSTR, OLE_XPOS_PIXELS, CoClass,
    IUnknown, VgaColor, GUID, FONTSIZE, Default, DISPMETHOD,
    IFontDisp, dispid, OLE_OPTEXCLUSIVE, DISPPARAMS, EXCEPINFO,
    OLE_XSIZE_HIMETRIC, StdPicture, OLE_YSIZE_CONTAINER, IPictureDisp,
    OLE_ENABLEDEFAULTBOOL, Picture, HRESULT, OLE_XPOS_CONTAINER,
    _lcid, DISPPROPERTY, OLE_YPOS_HIMETRIC, Font, Library,
    OLE_CANCELBOOL, COMMETHOD, Gray, OLE_YSIZE_PIXELS, FontEvents,
    OLE_HANDLE, OLE_YPOS_CONTAINER, FONTUNDERSCORE, IDispatch,
    IFontEventsDisp, Unchecked, OLE_XPOS_HIMETRIC, OLE_COLOR,
    OLE_YPOS_PIXELS, OLE_XSIZE_CONTAINER, OLE_YSIZE_HIMETRIC, Checked,
    Color, IEnumVARIANT, VARIANT_BOOL, _check_version,
    OLE_XSIZE_PIXELS, FONTNAME, IPicture, FONTSTRIKETHROUGH,
    typelib_path, Monochrome, StdFont
)


class OLE_TRISTATE(IntFlag):
    Unchecked = 0
    Checked = 1
    Gray = 2


class LoadPictureConstants(IntFlag):
    Default = 0
    Monochrome = 1
    VgaColor = 2
    Color = 4


__all__ = [
    'IFont', 'Font', 'FONTITALIC', 'Library', 'OLE_CANCELBOOL',
    'FONTBOLD', 'Gray', 'OLE_XPOS_PIXELS', 'OLE_YSIZE_PIXELS',
    'FontEvents', 'VgaColor', 'OLE_HANDLE', 'FONTSIZE', 'Default',
    'OLE_YPOS_CONTAINER', 'IFontDisp', 'FONTUNDERSCORE',
    'IFontEventsDisp', 'Unchecked', 'OLE_OPTEXCLUSIVE',
    'OLE_XPOS_HIMETRIC', 'OLE_COLOR', 'OLE_YPOS_PIXELS',
    'OLE_XSIZE_HIMETRIC', 'OLE_XSIZE_CONTAINER', 'OLE_YSIZE_HIMETRIC',
    'LoadPictureConstants', 'StdPicture', 'OLE_YSIZE_CONTAINER',
    'Checked', 'Color', 'IPictureDisp', 'OLE_ENABLEDEFAULTBOOL',
    'Picture', 'StdFont', 'OLE_XSIZE_PIXELS', 'FONTNAME',
    'OLE_TRISTATE', 'IPicture', 'OLE_XPOS_CONTAINER',
    'FONTSTRIKETHROUGH', 'typelib_path', 'Monochrome',
    'OLE_YPOS_HIMETRIC'
]

