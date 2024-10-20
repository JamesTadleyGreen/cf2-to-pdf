import cairo
import math
import numpy as np
from os import path

from cf2.parser import Line, Arc, Text, CF2, LineType

LINE_TYPES = {
    LineType.CUT: {"width": 1, "rgb": (1, 0, 1), "dash": None},
    LineType.CREASE: {"width": 1, "rgb": (0, 1, 1), "dash": [10, 5]},
    LineType.PERF: {"width": 1, "rgb": (0, 0.75, 0), "dash": [2, 2]},
    LineType.SCORE: {"width": 1, "rgb": (0.75, 0.75, 0), "dash": [2, 2]},
    LineType.UNKNOWN: {"width": 1, "rgb": (1, 0, 0), "dash": None},
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
    context.move_to(*line.start)
    context.line_to(*line.end)
    context.stroke()


def add_arc(context: cairo.Context, arc: Arc) -> None:
    set_line_style(context, arc.linetype)
    context.set_line_width(arc.pointage)
    if arc.start_angle == arc.end_angle:
        arc.start_angle = 0
        arc.end_angle = 2 * math.pi
    context.arc(*arc.centre, arc.radius, arc.start_angle, arc.end_angle)
    context.stroke()


def add_text(context: cairo.Context, text: Text) -> None:
    context.move_to(*text.start)
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
    dimensions = tuple(-np.subtract(*cf2.dimensions))
    surface = cairo.PDFSurface(output, *dimensions)
    context = cairo.Context(surface)
    # Flipping y-axis due to cairo oddities
    context.set_matrix(cairo.Matrix(1, 0, 0, -1))
    context.translate(-cf2.dimensions[0][0], -
                      dimensions[1] - cf2.dimensions[0][1])
    context.set_line_width(5)
    context.set_source_rgb(0, 0, 1)
    instructions = cf2.flatten()
    draw_instructions(context, instructions)
    context.stroke()
