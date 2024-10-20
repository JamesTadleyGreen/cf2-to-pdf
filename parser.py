import math
from pathlib import Path
from enum import Enum
from dataclasses import dataclass


class LineType(Enum):
    CUT = 1
    CREASE = 2
    PERF = 3
    SCORE = 4
    UNKNOWN = -1

    @classmethod
    def _missing_(cls, value):
        return cls.UNKNOWN


@dataclass
class SubroutineCall:
    name: str
    position: tuple[int, int]
    angle: float
    scale: tuple[int, int]

    def __repr__(self):
        return f"C,{self.name},{self.position[0]},{self.position[1]},{self.angle},{self.scale[0]},{self.scale[1]}"


@dataclass
class Line:
    pointage: int
    linetype: LineType
    start: tuple[int, int]
    end: tuple[int, int]
    nbridges: int
    wbridges: int

    def __repr__(self):
        return f"L,{self.pointage},{self.linetype.value},0,{self.start[0]},{self.start[1]},{self.end[0]},{self.end[1]},{self.nbridges},{self.wbridges}"

    def adjust(self, routine: SubroutineCall):
        self.translate(*routine.position)
        self.scale(*routine.scale)
        self.rotate(routine.angle, routine.position)
        return self

    def translate(self, dx, dy):
        self.start = (self.start[0] + dx, self.start[1] + dy)
        self.end = (self.end[0] + dx, self.end[1] + dy)

    def scale(self, x_scale, y_scale):
        pass

    def rotate(self, angle, origin):
        radians = math.radians(angle)

        def rotate_point(point):
            x, y = point
            x -= origin[0]
            y -= origin[1]
            new_x = x * math.cos(radians) - y * math.sin(radians)
            new_y = x * math.sin(radians) + y * math.cos(radians)
            return new_x + origin[0], new_y + origin[1]

        self.start = rotate_point(self.start)
        self.end = rotate_point(self.end)


class Arc:
    def __init__(
        self,
        pointage: int,
        linetype: LineType,
        start: tuple[int, int],
        end: tuple[int, int],
        centre: tuple[int, int],
        direction: int,
        nbridges: int,
        wbridges: int,
    ):
        self.pointage = pointage
        self.linetype = linetype
        self.start = start
        self.end = end
        self.centre = centre
        self.direction = direction
        self.nbridges = nbridges
        self.wbridges = wbridges

    def __repr__(self):
        return f"A,{self.pointage},{self.linetype.value},0,{self.start[0]},{self.start[1]},{self.end[0]},{self.end[1]},{self.centre[0]},{self.centre[1]},{self.direction},{self.nbridges},{self.wbridges}"

    def add_polar(self):
        self.radius = self.calculate_radius(self.centre, self.start)
        self.start_angle = math.pi + self.calculate_angle(
            self.centre, self.start if self.direction == 1 else self.end
        )
        self.end_angle = math.pi + self.calculate_angle(
            self.centre, self.end if self.direction == 1 else self.start
        )

    def calculate_radius(self, centre, point):
        return math.sqrt((centre[0] - point[0]) ** 2 + (centre[1] - point[1]) ** 2)

    def calculate_angle(self, centre, point):
        return math.atan2(centre[1] - point[1], centre[0] - point[0])

    def adjust(self, routine: SubroutineCall):
        self.translate(*routine.position)
        self.scale(*routine.scale)
        self.rotate(routine.angle, routine.position)
        self.add_polar()
        return self

    def translate(self, dx, dy):
        self.start = (self.start[0] + dx, self.start[1] + dy)
        self.end = (self.end[0] + dx, self.end[1] + dy)
        self.centre = (self.centre[0] + dx, self.centre[1] + dy)

    def scale(self, x_scale, y_scale):
        pass

    def rotate(self, angle, origin):
        radians = math.radians(angle)

        def rotate_point(point):
            x, y = point
            x -= origin[0]
            y -= origin[1]
            new_x = x * math.cos(radians) - y * math.sin(radians)
            new_y = x * math.sin(radians) + y * math.cos(radians)
            return new_x + origin[0], new_y + origin[1]

        self.start = rotate_point(self.start)
        self.end = rotate_point(self.end)
        self.centre = rotate_point(self.centre)


class Text:
    def __init__(
        self,
        pointage: int,
        linetype: LineType,
        start: tuple[int, int],
        angle: float,
        height: int,
        width: int,
        text: str,
    ):
        self.pointage = pointage
        self.linetype = linetype
        self.start = start
        self.angle = angle
        self.height = height
        self.width = width
        self.text = text

    def __repr__(self):
        return f"T,{self.pointage},{self.linetype.value},0,{self.start[0]},{self.start[1]},{self.angle},{self.height},{self.width}\n{self.text}"

    def adjust(self, routine: SubroutineCall):
        self.translate(*routine.position)
        # self.scale(*routine.scale)
        # self.rotate(routine.angle, routine.position)
        return self

    def translate(self, dx, dy):
        self.start = (self.start[0] + dx, self.start[1] + dy)


@dataclass
class Subroutine:
    name: str
    instructions: list[Line, Arc, Text]

    def __repr__(self):
        return "\n".join(
            [f"SUB,{self.name}"] + [i.__repr__()
                                    for i in self.instructions] + ["END"]
        )


class CF2:
    def __init__(
        self,
        dimensions: tuple[tuple[int, int], tuple[int, int]],
        parameters: dict | None = None,
        scale: tuple[int, int] = (1, 1),
        routine: list[Line, Arc, Text, SubroutineCall] | None = None,
        subroutines: list[Subroutine] | None = None,
    ):
        self.dimensions = dimensions
        self.parameters = parameters if parameters else {}
        self.scale = scale
        self.routine = routine if routine else []
        self.subroutines = subroutines if subroutines else []

    def __repr__(self):
        return "\n".join(
            ["$BOF", "V2", "ORDER", "END", "MAIN", "UM"]
            + [
                f"LL,{self.dimensions[0][0]},{self.dimensions[0][1]}",
                f"UR,{self.dimensions[1][0]},{self.dimensions[1][1]}",
                f"SCALE,{self.scale[0]},{self.scale[1]}",
            ]
            + [i.__repr__() for i in self.routine]
            + ["END"]
            + [i.__repr__() for i in self.subroutines]
            + ["$EOF"]
        )

    def flatten(self) -> list[Subroutine]:
        output = []
        for subroutine in self.routine:
            if isinstance(subroutine, SubroutineCall):
                for instruction in [
                    i for i in self.subroutines if i.name == subroutine.name
                ][0].instructions:
                    output.append(instruction.adjust(subroutine))
            else:
                output.append(subroutine)
        return output

    def combine(self, additional_cf2):
        self.parameters = self.parameters | additional_cf2.parameters
        self.dimensions = (
            min(self.dimensions[0], additional_cf2.dimensions[0]),
            max(self.dimensions[1], additional_cf2.dimensions[1]),
        )
        self.scale = self.scale  # TODO: Fix this
        self.routine += additional_cf2.routine
        self.subroutines += additional_cf2.subroutines

    def add_line(
        self,
        pointage: int,
        linetype: LineType,
        start: tuple[int, int],
        end: tuple[int, int],
        nbridges: int,
        wbridges: int,
    ):
        self.routine.append(
            Line(pointage, linetype, start, end, nbridges, wbridges))

    def add_arc(
        self,
        pointage: int,
        linetype: LineType,
        start: tuple[int, int],
        end: tuple[int, int],
        centre: tuple[int, int],
        direction: int,
        nbridges: int,
        wbridges: int,
    ):
        self.routine.append(
            Arc(pointage, linetype, start, end,
                centre, direction, nbridges, wbridges)
        )

    def add_text(
        self,
        pointage: int,
        linetype: LineType,
        start: tuple[int, int],
        angle: float,
        height: int,
        width: int,
        text: str,
    ):
        self.routine.append(Text(pointage, linetype, start,
                            angle, height, width, text))

    def add_subroutine(*args, **kwargs):
        raise NotImplementedError

    def write(self, path: Path):
        with open(path, "w") as f:
            f.write(self.__repr__())

    def to_pdf(self, path: Path):
        # create_pdf(path, self)
        pass


def get_between(xs: list[str], start: str, end: str) -> list[str]:
    start_index = end_index = -1
    for i, line in enumerate(xs):
        if line.startswith(start) and start_index == -1:
            start_index = i
        if line.startswith(end) and end_index == -1:
            end_index = i
    return xs[start_index + 1: end_index]


def parse_parameters(parameters: list[str]) -> dict:
    return {}


def parse_dimensions(lower_left: str, upper_right: str) -> tuple[float, float]:
    ll, *ll_pos = lower_left.split(",")[:3]
    ur, *ur_pos = upper_right.split(",")[:3]
    assert ll == "LL"
    assert ur == "UR"
    ll_pos = map(lambda x: float(x), ll_pos)
    ur_pos = map(lambda x: float(x), ur_pos)
    return (tuple(ll_pos), tuple(ur_pos))


def parse_scale(scale: str) -> tuple[int, int]:
    s, x_scale, y_scale = scale.split(",")[:3]
    assert s == "SCALE"
    return (x_scale, y_scale)


def parse_subroutines(subroutines: list[str]) -> list[Subroutine]:
    output = {}
    subroutine = []
    subname = subroutines.pop(0).split(",")[1]
    for line in subroutines:
        if line.startswith("SUB"):
            output[subname] = subroutine
            subname = line.split(",")[1]
            subroutine = []
        elif line == "END":
            continue
        else:
            subroutine.append(line)
        output[subname] = subroutine
    return [
        Subroutine(name, parse_subroutine(instructions))
        for name, instructions in output.items()
    ]


def parse_subroutine_call(details: list[str]) -> SubroutineCall:
    return SubroutineCall(
        details[0],
        (float(details[1]), float(details[2])),
        float(details[3]),
        (float(details[4]), float(details[5])),
    )


def parse_line(details: list[str]) -> Line:
    return Line(
        pointage=int(details[0]),
        linetype=LineType(int(details[1])),
        start=(float(details[3]), float(details[4])),
        end=(float(details[5]), float(details[6])),
        nbridges=int(float(details[7])),
        wbridges=int(float(details[8])),
    )


def parse_arc(details: list[str]) -> Arc:
    return Arc(
        pointage=int(details[0]),
        linetype=LineType(int(details[1])),
        start=(float(details[3]), float(details[4])),
        end=(float(details[5]), float(details[6])),
        centre=(float(details[7]), float(details[8])),
        direction=int(details[9]),
        nbridges=int(float(details[10])),
        wbridges=int(float(details[11])),
    )


def parse_text(details: list[str], text: str) -> Text:
    return Text(
        pointage=details[0],
        linetype=LineType(details[1]),
        start=(float(details[3]), float(details[4])),
        angle=float(details[5]),
        height=float(details[6]),
        width=float(details[7]),
        text=text,
    )


def parse_subroutine(lines: list[str]) -> [Line, Arc, Text, SubroutineCall]:
    skip = set()
    output = []
    for i, line in enumerate(lines):
        if i in skip:
            continue
        char, *details = line.split(",")
        match char:
            case "L":
                output.append(parse_line(details))
            case "A":
                output.append(parse_arc(details))
            case "T":
                skip.add(i + 1)
                output.append(parse_text(details, lines[i + 1]))
            case "C":
                output.append(parse_subroutine_call(details))
    return output


def get_sections(
    lines: list[str],
) -> tuple[dict, str, tuple[int, int], tuple[int, int], str, list[str]]:
    parameters = parse_parameters(get_between(lines, "ORDER", "END"))
    main = get_between(lines, "MAIN", "$EOF")
    unit = main.pop(0)
    lower_left = main.pop(0)
    upper_right = main.pop(0)
    dimensions = parse_dimensions(lower_left, upper_right)
    scale = parse_scale(main.pop(0))
    routine_divider = main.index("END")
    routine = parse_subroutine(main[:routine_divider])
    subroutines = parse_subroutines(
        main[routine_divider + 1:])  # For END and $EOF
    return parameters, unit, dimensions, scale, routine, subroutines


def parse_cf2(path: Path) -> CF2:
    with open(path, "r") as f:
        lines = f.read().splitlines()
    assert lines.pop(0) == "$BOF"
    assert lines.pop(0) == "V2"
    parameters, unit, dimensions, scale, routine, subroutines = get_sections(
        lines)
    assert unit == "UM"
    return CF2(dimensions, parameters, scale, routine, subroutines)
