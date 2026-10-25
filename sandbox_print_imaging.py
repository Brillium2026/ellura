#!/usr/bin/env python3
"""
FIRSTBREATH SANDBOX — PRINT GEOMETRY UNDERNEATH, IMAGING ON TOP
================================================================
Steven's ruling, 2026-10-25: write the sandbox using 3D printing
requirements underneath, with coloring, shading, and light in the
environment on top, and let the user make the final imaging decisions.

Two layers, kept separate, kept linked:

  LAYER 1 — GEOMETRY (printer truth)
    A real triangular mesh, in millimetres. A printer cannot print
    shading, so shading never changes this layer. This layer is
    checked before anything is called printer-ready:
      - every face is a triangle, none degenerate (area > 0)
      - every edge is shared by exactly 2 faces (watertight / closed)
      - signed volume > 0 (outward winding; flipped if needed)
      - bounding box, in mm, reported honestly
    Export is ASCII STL, the format printers read.

  LAYER 2 — IMAGING (what the eye judges)
    Material color, light direction, ambient + diffuse + specular
    highlight, view yaw/pitch, perspective projection. This layer
    changes only the picture, never the mesh. Changing color or
    light does not change volume, bounding box, or the STL.
    The user sees the shaded final image and approves it — or not.
    Approval is never automatic: a decision record starts
    approved=False and only becomes True when a person sets it.

No external libraries. Standard library only, so it runs on a
Chromebook, in Cloud Shell, anywhere Python 3 runs.
No stubs: every function below does what it says, or raises.
"""

import hashlib
import json
import math
import os
import struct

# ---------------------------------------------------------------------------
# Small vector helpers (tuples, no dependencies)
# ---------------------------------------------------------------------------

def vsub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def vcross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def vdot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def vlen(a):
    return math.sqrt(vdot(a, a))


def vnorm(a):
    n = vlen(a)
    if n == 0:
        raise ValueError("cannot normalize a zero vector")
    return (a[0] / n, a[1] / n, a[2] / n)


def rot_yaw_pitch(p, yaw, pitch):
    """Rotate a point: yaw around Y (width), then pitch around X (height).
    Same gyroscope axes as the room standard: yaw -> width, pitch -> height."""
    x, y, z = p
    cy, sy = math.cos(yaw), math.sin(yaw)
    x1 = x * cy + z * sy
    z1 = -x * sy + z * cy
    cp, sp = math.cos(pitch), math.sin(pitch)
    y2 = y * cp - z1 * sp
    z2 = y * sp + z1 * cp
    return (x1, y2, z2)


# ---------------------------------------------------------------------------
# LAYER 1 — GEOMETRY
# ---------------------------------------------------------------------------

class Mesh:
    """A triangular mesh in millimetres. vertices: [(x, y, z), ...]
    faces: [(i, j, k), ...] indices into vertices, outward winding."""

    def __init__(self, vertices, faces, units="mm"):
        self.vertices = [tuple(float(c) for c in v) for v in vertices]
        self.faces = [tuple(int(i) for i in f) for f in faces]
        if len(self.faces) == 0:
            raise ValueError("mesh has no faces")
        for f in self.faces:
            if len(f) != 3:
                raise ValueError(f"face is not a triangle: {f}")
            for i in f:
                if not (0 <= i < len(self.vertices)):
                    raise ValueError(f"face index out of range: {f}")
        self.units = units

    def face_normal(self, f):
        a, b, c = (self.vertices[i] for i in f)
        return vnorm(vcross(vsub(b, a), vsub(c, a)))

    def face_area(self, f):
        a, b, c = (self.vertices[i] for i in f)
        return 0.5 * vlen(vcross(vsub(b, a), vsub(c, a)))

    def signed_volume(self):
        """Divergence-theorem volume. Positive = outward winding."""
        total = 0.0
        for f in self.faces:
            a, b, c = (self.vertices[i] for i in f)
            total += vdot(a, vcross(b, c)) / 6.0
        return total

    def ensure_outward(self):
        if self.signed_volume() < 0:
            self.faces = [(f[0], f[2], f[1]) for f in self.faces]

    def bounding_box(self):
        xs = [v[0] for v in self.vertices]
        ys = [v[1] for v in self.vertices]
        zs = [v[2] for v in self.vertices]
        return {"min": (min(xs), min(ys), min(zs)),
                "max": (max(xs), max(ys), max(zs)),
                "size": (max(xs) - min(xs), max(ys) - min(ys),
                         max(zs) - min(zs))}

    def validate_printer_ready(self):
        """Return (ready, report). ready is True only if every check passes.
        No check is faked: a failing check is reported, not hidden."""
        errors = []
        for f in self.faces:
            if self.face_area(f) <= 1e-12:
                errors.append(f"degenerate face (zero area): {f}")
        edge_count = {}
        for f in self.faces:
            for e in ((f[0], f[1]), (f[1], f[2]), (f[2], f[0])):
                key = tuple(sorted(e))
                edge_count[key] = edge_count.get(key, 0) + 1
        open_edges = [e for e, n in edge_count.items() if n != 2]
        if open_edges:
            errors.append(f"not watertight: {len(open_edges)} edge(s) "
                          f"shared by != 2 faces, e.g. {open_edges[:3]}")
        vol = self.signed_volume()
        if vol <= 0:
            errors.append(f"signed volume is not positive: {vol}")
        box = self.bounding_box()
        if any(s <= 0 for s in box["size"]):
            errors.append(f"flat bounding box (a size is 0): {box['size']}")
        return (len(errors) == 0, {
            "ready": len(errors) == 0,
            "errors": errors,
            "units": self.units,
            "vertices": len(self.vertices),
            "faces": len(self.faces),
            "volume_mm3": round(vol, 4),
            "bounding_box_mm": {k: tuple(round(c, 4) for c in v)
                                for k, v in box.items()},
            "watertight": len(open_edges) == 0,
        })

    def to_stl_ascii(self, name="sandbox_object"):
        lines = [f"solid {name}"]
        for f in self.faces:
            n = self.face_normal(f)
            lines.append(f"  facet normal {n[0]:.6e} {n[1]:.6e} {n[2]:.6e}")
            lines.append("    outer loop")
            for i in f:
                v = self.vertices[i]
                lines.append(f"      vertex {v[0]:.6e} {v[1]:.6e} {v[2]:.6e}")
            lines.append("    endloop")
            lines.append("  endfacet")
        lines.append(f"endsolid {name}")
        return "\n".join(lines) + "\n"

    def geometry_hash(self):
        return hashlib.sha256(self.to_stl_ascii().encode("utf-8")).hexdigest()


def box_mesh(w, d, h, cx=0.0, cy=0.0, cz=0.0):
    """A box, centred at (cx, cy, cz), sizes in mm. 12 triangles, watertight."""
    x0, x1 = cx - w / 2.0, cx + w / 2.0
    y0, y1 = cy - d / 2.0, cy + d / 2.0
    z0, z1 = cz, cz + h
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
         (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    quads = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
             (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    faces = []
    for a, b, c, d_ in quads:
        faces.append((a, b, c))
        faces.append((a, c, d_))
    m = Mesh(v, faces)
    m.ensure_outward()
    return m


def house_mesh(w=40.0, d=30.0, wall_h=20.0, roof_h=12.0):
    """Demo object: ONE solid, not two solids stacked. A pentagonal
    cross-section (walls + roof peak) extruded along Y. No interior
    faces, so it validates watertight. Volume = pentagon area x depth:
    (w*wall_h + w*roof_h/2) * d."""
    x0, x1 = -w / 2.0, w / 2.0
    y0, y1 = -d / 2.0, d / 2.0
    sec = [(x0, 0.0), (x1, 0.0), (x1, wall_h), (0.0, wall_h + roof_h),
           (x0, wall_h)]
    verts = [(x, y0, z) for (x, z) in sec] + [(x, y1, z) for (x, z) in sec]
    n = len(sec)
    faces = []
    # Side walls: winding (a, c, b) / (a, d, c) so side normals point
    # outward, matching the end caps.
    for i in range(n):
        j = (i + 1) % n
        a, b = i, j
        c, d_ = j + n, i + n
        faces.append((a, c, b))
        faces.append((a, d_, c))
    # End caps: fan-triangulate each pentagon.
    for ring, flip in ((0, False), (n, True)):
        for i in range(1, n - 1):
            f = (ring, ring + i, ring + i + 1)
            faces.append((f[0], f[2], f[1]) if flip else f)
    m = Mesh(verts, faces)
    m.ensure_outward()
    return m


def merge_meshes(meshes):
    """Combine meshes into one vertex/face list (no boolean union —
    that is stated, not faked)."""
    verts, faces = [], []
    for m in meshes:
        off = len(verts)
        verts.extend(m.vertices)
        faces.extend([(a + off, b + off, c + off) for a, b, c in m.faces])
    return Mesh(verts, faces)


# ---------------------------------------------------------------------------
# LAYER 2 — IMAGING
# ---------------------------------------------------------------------------

def shade_color(base_rgb, normal, light_dir, view_dir,
                ambient=0.25, diffuse=0.65, specular=0.35, shininess=32.0):
    """Lambert diffuse + Blinn-Phong highlight, clamped 0..1.
    base_rgb: (r, g, b) 0..255. light_dir/view_dir: unit vectors
    pointing TO the light / TO the viewer. Returns (r, g, b) 0..255."""
    ndotl = max(0.0, vdot(normal, light_dir))
    half = vnorm(tuple(light_dir[i] + view_dir[i] for i in range(3)))
    spec = (max(0.0, vdot(normal, half)) ** shininess) if ndotl > 0 else 0.0
    out = []
    for ch in base_rgb:
        v = ch * (ambient + diffuse * ndotl) + 255.0 * specular * spec
        out.append(int(round(max(0, min(255, v)))))
    return tuple(out)


def rgb_hex(rgb):
    return "#%02x%02x%02x" % rgb


def render_svg(mesh, width=640, height=480, yaw=0.6, pitch=0.35,
               base_rgb=(62, 142, 196), light_dir=(0.5, 0.5, 1.0),
               distance=180.0, focal=520.0):
    """Render the mesh as shaded SVG polygons, painter-sorted far to near.
    Returns (svg_text, face_report). The mesh is never modified."""
    light = vnorm(light_dir)
    view = (0.0, 0.0, 1.0)
    projected = []
    for v in mesh.vertices:
        r = rot_yaw_pitch(v, yaw, pitch)
        projected.append(r)
    cx = sum(p[0] for p in projected) / len(projected)
    cy = sum(p[1] for p in projected) / len(projected)
    cz = sum(p[2] for p in projected) / len(projected)
    screen = []
    for (x, y, z) in projected:
        dx, dy, dz = x - cx, y - cy, z - cz
        scale = focal / max(1.0, distance - dz)
        screen.append((width / 2.0 + dx * scale, height / 2.0 - dy * scale, dz))
    entries = []
    for f in mesh.faces:
        n = mesh.face_normal(f)
        rn = rot_yaw_pitch(n, yaw, pitch)
        if rn[2] <= 0:
            continue
        depth = sum(screen[i][2] for i in f) / 3.0
        colour = shade_color(base_rgb, rn, light, view)
        poly = " ".join(f"{screen[i][0]:.1f},{screen[i][1]:.1f}" for i in f)
        entries.append((depth, poly, rgb_hex(colour), colour))
    entries.sort(key=lambda e: e[0])
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" '
             f'width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
             f'<rect width="100%" height="100%" fill="#0b1220"/>']
    for _, poly, hexcol, _ in entries:
        parts.append(f'<polygon points="{poly}" fill="{hexcol}" '
                     f'stroke="#0b1220" stroke-width="0.5"/>')
    parts.append("</svg>")
    report = {"faces_drawn": len(entries),
              "faces_total": len(mesh.faces),
              "yaw": yaw, "pitch": pitch,
              "base_rgb": base_rgb, "light_dir": light_dir}
    return "\n".join(parts), report


# ---------------------------------------------------------------------------
# FINAL IMAGING DECISION — the user, not the code, approves
# ---------------------------------------------------------------------------

def final_image_decision(mesh, view_params, base_rgb, light_dir,
                         approved=False, approved_by="", notes=""):
    """Build the decision record. approved defaults to False and is
    only True when a person explicitly sets it. Changing colour/light
    never changes geometry_hash, volume, or bounding box."""
    ready, vreport = mesh.validate_printer_ready()
    return {
        "geometry": {
            "hash_sha256": mesh.geometry_hash(),
            "printer_ready": ready,
            "volume_mm3": vreport["volume_mm3"],
            "bounding_box_mm": vreport["bounding_box_mm"],
            "vertices": vreport["vertices"],
            "faces": vreport["faces"],
            "validation_errors": vreport["errors"],
        },
        "imaging": {
            "base_rgb": base_rgb,
            "light_dir": light_dir,
            "view_yaw": view_params.get("yaw"),
            "view_pitch": view_params.get("pitch"),
        },
        "decision": {
            "approved": bool(approved),
            "approved_by": approved_by,
            "notes": notes,
        },
    }


# ---------------------------------------------------------------------------
# DEMO / CLI
# ---------------------------------------------------------------------------

def main(out_dir="sandbox-output"):
    os.makedirs(out_dir, exist_ok=True)
    mesh = house_mesh()
    ready, vreport = mesh.validate_printer_ready()
    print("GEOMETRY (printer layer)")
    print(f"  vertices: {vreport['vertices']}  faces: {vreport['faces']}")
    print(f"  volume: {vreport['volume_mm3']} mm3")
    print(f"  bounding box: {vreport['bounding_box_mm']}")
    print(f"  watertight: {vreport['watertight']}  printer_ready: {ready}")
    if vreport["errors"]:
        for e in vreport["errors"]:
            print(f"  ERROR: {e}")
    stl_path = os.path.join(out_dir, "sandbox_house.stl")
    with open(stl_path, "w") as fh:
        fh.write(mesh.to_stl_ascii("sandbox_house"))
    print(f"  STL written: {stl_path}")

    print("\nIMAGING (eye layer — does not change the mesh)")
    base_rgb = (62, 142, 196)
    light_dir = (0.5, 0.5, 1.0)
    svg, sreport = render_svg(mesh, base_rgb=base_rgb, light_dir=light_dir)
    svg_path = os.path.join(out_dir, "sandbox_house.svg")
    with open(svg_path, "w") as fh:
        fh.write(svg)
    print(f"  SVG written: {svg_path}  faces drawn: {sreport['faces_drawn']}"
          f"/{sreport['faces_total']}")

    svg2, _ = render_svg(mesh, base_rgb=(196, 90, 62),
                         light_dir=(-0.6, 0.4, 1.0))
    with open(os.path.join(out_dir, "sandbox_house_alt_colour.svg"), "w") as fh:
        fh.write(svg2)
    print("  Alt-colour render written (geometry hash unchanged)")

    decision = final_image_decision(
        mesh, {"yaw": 0.6, "pitch": 0.35}, base_rgb, light_dir,
        approved=False, approved_by="",
        notes="Draft decision: user has not approved the final image yet. "
              "Set approved=True with a name to approve.")
    dec_path = os.path.join(out_dir, "final_image_decision.json")
    with open(dec_path, "w") as fh:
        json.dump(decision, fh, indent=2)
    print(f"\nDECISION (user approves, code does not): {dec_path}")
    print(f"  approved: {decision['decision']['approved']}  "
          f"printer_ready: {decision['geometry']['printer_ready']}")
    print("\nSANDBOX BUILT. Open the SVG to judge the final image. "
          "The STL is the printer file, unchanged by colour or light.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())