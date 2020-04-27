import json
import jsons  # type: ignore
import math

from points import OrientedPoint, SplinePoint

from typing import Any, Dict, List, Union

Glyph = List[OrientedPoint]
Spline = List[Glyph]

# https://gist.github.com/simonw/7000493


class OrientedPointEncoder(json.JSONEncoder):
    def __init__(self, *args, **kwargs):
        """TODO: what is __init__ doing?
        """
        # print(f"Start __init__ OrientedPointEncoder")
        # print(f"args: {args}")
        # print(f"kwargs: {kwargs}")
        super().__init__(*args, **kwargs)

    def default(self, obj):
        """
        """
        if isinstance(obj, OrientedPoint):
            """
            """
            return {
                "_type": "OrientedPoint",
                "x": obj.x,
                "y": obj.y,
                "ori_deg": obj.ori_deg,
            }
        return super().default(obj)


class OrientedPointDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        """TODO: what is __init__ doing?
        """
        # print(f"Start __init__ OrientedPointDecoder")
        # print(f"args: {args}")
        # print(f"kwargs: {kwargs}")

        super().__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        """TODO: what is object_hook doing?
        """
        # print(f"Start object_hook for {obj}")

        if "_type" not in obj:
            return obj
        if obj["_type"] == "OrientedPoint":
            x = obj["x"]
            y = obj["y"]
            ori_deg = obj["ori_deg"]
            return OrientedPoint(x, y, ori_deg)
        return obj


def object_hook_OP(obj):
    """TODO: what is object_hook_OP doing?
    """
    print(f"Start object_hook_OP")

    if "_type" not in obj:
        return obj
    if obj["_type"] == "OrientedPoint":
        x = obj["x"]
        y = obj["y"]
        ori_deg = obj["ori_deg"]
        return OrientedPoint(x, y, ori_deg)
    return obj


def run_custom_json():
    """TODO: What is custom_json doing?
    """
    print(f"Starting run_custom_json")

    glyph = [
        OrientedPoint(0, 2, 3),
        OrientedPoint(3, -1, 3),
        OrientedPoint(7, 0, 3.1415),
        OrientedPoint(2, 0.54, 3),
    ]

    glyph_encoded = json.dumps(glyph, cls=OrientedPointEncoder)
    print(f"\nglyph_encoded:\n{glyph_encoded}")

    # decode using a custom decoder
    glyph_decoded = json.loads(glyph_encoded, cls=OrientedPointDecoder)
    # or just pass the object_hook method to use
    # decoded = json.loads(encoded, object_hook=object_hook_OP)
    print(f"glyph_decoded:\n{glyph_decoded}")

    spline = [
        glyph,
        [
            OrientedPoint(2, -1, 3),
            OrientedPoint(0.7436723, 0, 3.1511),
            OrientedPoint(2, 0.21, 3),
        ],
    ]
    spline_encoded = json.dumps(spline, cls=OrientedPointEncoder)
    print(f"\nspline_encoded:\n{spline_encoded}")
    spline_decoded = json.loads(spline_encoded, cls=OrientedPointDecoder)
    print(f"spline_decoded:\n{spline_decoded}")

    an_spline = {
        "source_file": "splne.txt",
        "total_points": sum(map(len, spline)),
        "spline": spline,
    }
    an_spline_encoded = json.dumps(an_spline, cls=OrientedPointEncoder, indent=4)
    print(f"\nan_spline_encoded:\n{an_spline_encoded}")
    an_spline_decoded = json.loads(an_spline_encoded, cls=OrientedPointDecoder)
    print(f"an_spline_decoded:\n{an_spline_decoded}")
    print(f"an_spline_decoded['source_file']: {an_spline_decoded['source_file']}")

    spt = SplinePoint(3, math.e, 5, 0)
    spt_encoded = json.dumps(spt, cls=OrientedPointEncoder)
    print(f"\nspt_encoded: {spt_encoded}")
    spt_decoded = json.loads(spt_encoded, cls=OrientedPointDecoder)
    print(f"spt_decoded: {spt_decoded}")


def run_jsons():
    """
    """
    glyph = [
        OrientedPoint(0, 2, 3),
        OrientedPoint(3, -1, 3),
        OrientedPoint(7, 0, 3.1415),
        OrientedPoint(2, 0.54, 3),
    ]

    glyph_encoded = jsons.dumps(glyph)
    print(f"\nglyph_encoded:\n{glyph_encoded}")
    glyph_decoded = jsons.loads(glyph_encoded, Glyph)
    print(f"\nglyph_decoded:\n{glyph_decoded}")

    spline = [
        glyph,
        [
            OrientedPoint(2, -1, 3),
            OrientedPoint(0.7436723, 0, 3.1511),
            OrientedPoint(2, 0.21, 3),
        ],
    ]
    spline_encoded = jsons.dumps(spline)
    print(f"\nspline_encoded:\n{spline_encoded}")
    spline_decoded = jsons.loads(spline_encoded, Spline)
    print(f"spline_decoded:\n{spline_decoded}")

    an_spline = {
        "source_file": "splne.txt",
        "total_points": sum(map(len, spline)),
        "spline": spline,
    }
    an_spline_encoded = jsons.dumps(an_spline, indent=4)
    print(f"\nan_spline_encoded:\n{an_spline_encoded}")
    an_spline_decoded = jsons.loads(an_spline_encoded, Dict[str, Union[Spline, Any]])
    print(f"an_spline_decoded:\n{an_spline_decoded}")


if __name__ == "__main__":
    # run_custom_json()
    run_jsons()
