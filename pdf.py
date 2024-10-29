import cairo
import math
import numpy as np
from os import path

from cf2.parser import Line, Arc, Text, CF2, LineType

POINTS_TO_MM = 2.83465

LINE_TYPES = {
    LineType.CUT: {"rgb": (1, 0, 1), "dash": None},
    LineType.CREASE: {"rgb": (0, 1, 1), "dash": [10, 5]},
    LineType.PERF: {"rgb": (0, 0.75, 0), "dash": [2, 2]},
    LineType.SCORE: {"rgb": (0.75, 0.75, 0), "dash": [2, 2]},
    LineType.UNKNOWN: {"rgb": (1, 0, 0), "dash": None},
}


def set_line_style(context: cairo.Context, linetype: LineType):
    context.set_source_rgb(*LINE_TYPES[linetype]["rgb"])
    if LINE_TYPES[linetype]["dash"] is not None:
        context.set_dash(LINE_TYPES[linetype]["dash"])
    else:
        context.set_dash([])


def add_line(context: cairo.Context, line: Line) -> None:
    set_line_style(context, line.linetype)
    context.set_line_width(line.pointage)
    context.move_to(line.start[0] * POINTS_TO_MM, line.start[1] * POINTS_TO_MM)
    context.line_to(line.end[0] * POINTS_TO_MM, line.end[1] * POINTS_TO_MM)
    context.stroke()


def calculate_radius(centre, point):
    return math.sqrt((centre[0] - point[0]) ** 2 + (centre[1] - point[1]) ** 2)


def calculate_angle(centre, point):
    return math.atan2(centre[1] - point[1], centre[0] - point[0])


def convert_to_polar(arc: Arc) -> tuple[float, float, float]:
    radius = calculate_radius(arc.centre, arc.start)
    start_angle = math.pi + calculate_angle(
        arc.centre, arc.start if arc.direction == 1 else arc.end
    )
    end_angle = math.pi + calculate_angle(
        arc.centre, arc.end if arc.direction == 1 else arc.start
    )
    return start_angle, end_angle, radius


def add_arc(context: cairo.Context, arc: Arc) -> None:
    set_line_style(context, arc.linetype)
    context.set_line_width(arc.pointage)
    start_angle, end_angle, radius = convert_to_polar(arc)
    if start_angle == end_angle:
        arc.start_angle = 0
        arc.end_angle = 2 * math.pi
    context.arc(*arc.centre * POINTS_TO_MM, radius, start_angle, end_angle)
    context.stroke()


def add_text(context: cairo.Context, text: Text) -> None:
    context.move_to(text.start[0] * POINTS_TO_MM, text.start[1] * POINTS_TO_MM)
    context.rotate(text.angle)
    context.scale(1, -1)
    context.show_text(text.text)
    context.scale(1, -1)
    context.rotate(-text.angle)


def draw_instructions(context: cairo.Context, instructions: list[Line, Arc, Text]):
    for instruction in instructions:
        match instruction:
            case Line():
                add_line(context, instruction)
            case Arc():
                add_arc(context, instruction)
            case Text():
                add_text(context, instruction)


def create_pdf(output: path, cf2: CF2) -> None:
    dimensions = tuple(-np.subtract(*cf2.dimensions) * POINTS_TO_MM)
    surface = cairo.PDFSurface(output, *dimensions)
    context = cairo.Context(surface)
    # Flipping y-axis due to cairo oddities
    context.set_matrix(cairo.Matrix(1, 0, 0, -1))
    context.translate(
        -cf2.dimensions[0][0] * POINTS_TO_MM,
        -dimensions[1] - cf2.dimensions[0][1] * POINTS_TO_MM,
    )
    context.set_line_width(5)
    context.set_source_rgb(0, 0, 1)
    instructions = cf2.flatten()
    draw_instructions(context, instructions)
    context.stroke()
