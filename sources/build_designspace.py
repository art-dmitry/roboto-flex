"""
build designspace
"""
from fontTools.designspaceLib import DesignSpaceDocument, SourceDescriptor, InstanceDescriptor, AxisDescriptor, RuleDescriptor
from defcon import Font
import shutil
from distutils.dir_util import copy_tree
import os
from glob import glob


IGNORE_UFOS = [
    "RobotoFlex_opsz14_wght1000_wdth25.ufo",
]

SRC_DIR = "1A-drawings"

SRC_SUB_DIRS = [
    "Duovars",
    "Mains",
    os.path.join("Mains", "slnt"),
    "Parametric Axes",
    "Quadravars",
    "Trivars",
]

AXIS_DFLTS = {
    "wght": 400,
    "wdth": 75,
    "opsz": 0,
    "slnt": 0,
    "YTLC": 514,
}

OPSZ_MAP = {
    8.0: -1,
    14.0: 0,
    0: 0,
    36.0: 0.492,
    84.0: 0.946,
    144.0: 1.0
}


def get_ufos(fp):
    """Get ufo paths"""
    ufo_fps = []
    for dir_ in SRC_SUB_DIRS:
        ufos = glob(os.path.join(SRC_DIR, dir_, "*.ufo"))
        ufo_fps += ufos
    return ufo_fps


def parse_axis_vals(filename):
    """Extract axis values from a ufo filename.
    
    RobotoFlex-wght1000-wdth25.ufo --> {wght: 1000, wdth: 25}
    """
    res = {}
    s = filename.replace(".ufo", "")
    s = s.replace("RobotoFlex-", "")
    tokens = s.split("_")
    for token in tokens:
        for i in range(len(token)):
            if token[i].isdigit() or token[i] == "-":
                res[token[:i]] = int(token[i:])
                break
    # populate missing dflt vals
    for k,v in AXIS_DFLTS.items():
        if k not in res:
            res[k] = v
    # transform opsz to ds units
    res["opsz"] = OPSZ_MAP[res["opsz"]]
    return res



def build_designspace(ufo_paths):
    """Build the final designspace"""
    doc = DesignSpaceDocument()

    axes = [
        dict(minimum=400, maximum=700, default=400, name="wght", tag="wght", labelNames={"en": "wght"}, map=[], hidden=0),
        dict(minimum=75, maximum=100, default=75, name="wdth", tag="wdth", labelNames={"en": "wdth"}, map=[], hidden=0),
        dict(minimum=8, maximum=144, default=14, name="opsz", tag="opsz", labelNames={"en": "opsz"}, map=[ (8.0, -1), (14.0, 0), (36.0, 0.492), (84.0, 0.946), (144.0, 1.0) ], hidden=0),
        dict(minimum=-10, maximum=0, default=0, name="slnt", tag="slnt", labelNames={"en": "slnt"}, map=[], hidden=1),
        dict(minimum=416, maximum=570, default=514, name="YTLC", tag="YTLC", labelNames={"en": "YTLC"}, map=[], hidden=1),
    ]
    # Add axes
    for ax in axes:
        axis = AxisDescriptor(**ax)
        doc.addAxis(axis)
    
    # Add sources
    for fp in ufo_paths:
        if os.path.basename(fp) in IGNORE_UFOS:
            continue
        filename = os.path.basename(fp)
        axis_vals = parse_axis_vals(filename)
        src = {"filename": fp, "location": axis_vals, "familyName": "Roboto Flex"}
        source = SourceDescriptor(**src)
        doc.addSource(source)
    
    # Add symbol currency rules
    for glyph in (
        "dollar",
        "coloncurrency",
        "won",
        "cent",
        "uni20B2",
        "uni20B1",
        "naira",
        "uni20B5",
        "diagonalbarO"
    ):
        replacement = f"{glyph}.rvrn"
        wght_rule = {
            "conditionSets": [[{"name": "wght", "minimum": 600, "maximum": 1000}]],
            "subs": [(glyph, replacement)]
        }
        r1 = RuleDescriptor(**wght_rule)
        doc.addRule(r1)

        wdth_rule = {
            "conditionSets": [[{"name": "wdth", "minimum": 25, "maximum": 85}]],
            "subs": [(glyph, replacement)]
        }
        r2 = RuleDescriptor(**wdth_rule)
        doc.addRule(r2)
    return doc


def main():
    # write designspace
    ufo_paths = get_ufos(SRC_DIR)
    assert len(ufo_paths) == 72, "There should be 72 ufos!"
    ds = build_designspace(ufo_paths)
    ds_path = "RobotoFlex.designspace"
    ds.write(ds_path)
    print(f"Saving {ds_path}")
    

if __name__ == "__main__":
    main()
