"""Unit and integration tests for Image & Vision domain (use image)."""

import os
import pytest
from doomscript.compiler.engine import execute, export_to_python
from doomscript.domains.image.runtime import (
    DoomImage,
    create_blank_image,
    open_image,
    image_dimensions,
    image_width,
    image_height,
    resize_image,
    crop_image,
    rotate_image,
    flip_image,
    filter_image,
    adjust_image,
    draw_on_image,
    save_image,
)


def test_image_runtime_direct(tmp_path):
    img = create_blank_image(400, 300, color="red")
    assert image_dimensions(img) == (400, 300)
    assert image_width(img) == 400
    assert image_height(img) == 300

    # Resize by dimensions
    resized = resize_image(img, width=200, height=150)
    assert resized.size == (200, 150)

    # Resize by percent
    pct = resize_image(img, percent=50.0)
    assert pct.size == (200, 150)

    # Crop
    cropped = crop_image(img, 10, 10, 110, 90)
    assert cropped.size == (100, 80)

    # Rotate
    rotated = rotate_image(img, 90)
    assert rotated is not None

    # Flip
    flipped = flip_image(img, "horizontal")
    assert flipped is not None

    # Filter
    gray = filter_image(img, "grayscale")
    assert gray.mode == "L"

    # Draw text
    annotated = draw_on_image(img, "TEST", x=10, y=10, color="white")
    assert annotated is not None

    # Save
    out_file = str(tmp_path / "test_out.png")
    saved_path = save_image(img, out_file)
    assert os.path.exists(saved_path)
    assert os.path.getsize(saved_path) > 0


def test_image_domain_script_execution(tmp_path):
    out_img = str(tmp_path / "canvas.png").replace("\\", "/")
    source = f"""use image

create blank image with width 500, height 400, color "white" into canvas
dimensions of canvas into dims
width of canvas into w
height of canvas into h
resize canvas to width 250, height 200 into half_canvas
resize canvas by 50 percent into pct_canvas
crop canvas from 50, 50 to 250, 200 into cropped
rotate canvas by 45 degrees into rotated
flip canvas horizontally into flipped
apply grayscale to canvas into gray
draw text "DoomScript" on canvas at 10, 10 with color "black"
save image canvas to "{out_img}"
"""
    env = execute(source)
    assert env["dims"] == (500, 400)
    assert env["w"] == 500
    assert env["h"] == 400
    assert env["half_canvas"].size == (250, 200)
    assert env["pct_canvas"].size == (250, 200)
    assert env["cropped"].size == (200, 150)
    assert env["gray"].mode == "L"
    assert os.path.exists(out_img)


def test_image_domain_python_export():
    source = """use image

create blank image with width 300, height 200 into img
resize img to width 150, height 100 into small_img
crop small_img from 0, 0 to 50, 50 into icon
"""
    py_code = export_to_python(source)
    assert "create_blank_image" in py_code
    assert "resize_image" in py_code
    assert "crop_image" in py_code
