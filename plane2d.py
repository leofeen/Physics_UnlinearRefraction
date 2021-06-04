import math
from typing import Union
import numpy as np
from math import radians, degrees, sqrt, tan, atan, fabs


class Point:
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y

    def __str__(self):
        return f'({self.x}; {self.y})'

    def __eq__(self, o) -> bool:
        if not isinstance(o, Point):
            return False
        return (self.x == o.x) and (self.y == o.y)

    def __hash__(self) -> int:
        return hash(self.__repr__())

    def __repr__(self) -> str:
        return f'Point({self.x}, {self.y})'


class Line:
    def __init__(self, sample_coordinates: Point, angle: float=None, angle_coefficient: float=None):
        #TODO: make static work with line segments
        """Angle in degrees"""
        if angle == None and angle_coefficient == None:
            raise ValueError('Neither angle or coefficient was not given')
        if angle_coefficient == None:
            self.angle = angle
            while self.angle < -180 or self.angle > 180:
                if self.angle < -180:
                    self.angle += 360
                else:
                    self.angle -= 360
            if self.angle != 90 and self.angle != -90:
                self.angle_coefficient = tan(radians(angle))
                self.angle = degrees(atan(self.angle_coefficient))
            else:
                self.angle_coefficient = math.inf
                self.angle = 90
        else:
            self.angle_coefficient = angle_coefficient
            if self.angle_coefficient != math.inf:
                self.angle = degrees(atan(angle_coefficient))
            else:
                self.angle = 90
        self.sample_coordinates = sample_coordinates
        if self.angle_coefficient != math.inf:
            self.oy_segment = sample_coordinates.y - self.angle_coefficient*sample_coordinates.x
        else:
            self.oy_segment = None

    def get_y_coordinate(self, x):
        if self.angle_coefficient != math.inf:
            return self.angle_coefficient*x + self.oy_segment
        else:
            return x if x == self.sample_coordinates.x else None

    def get_direction_to_point(self, point: Point):
        if self.angle == 90:
            if point.x == self.sample_coordinates.x:
                return 's'
            if point.x < self.sample_coordinates.x:
                return 'lou'
            return 'rod'
        line_y = self.get_y_coordinate(point.x)
        if line_y == point.y:
            return 's'
        if line_y < point.y and self.angle >= 0:
            return 'lou' #left-or-up
        elif line_y > point.y and self.angle >= 0:
            return 'rod' #right-or-down
        elif line_y < point.y:
            return 'rou' #right-or-up
        return 'lod' #left-or-down

    def get_distance_from_a_point(self, point: Point):
        if self.angle_coefficient != math.inf:
            return fabs(self.angle_coefficient*point.x - point.y + self.oy_segment) / sqrt(self.angle_coefficient**2 + 1)
        return fabs(point.x - self.sample_coordinates.x)

    def get_intersection_point(self, line: Union['Line', 'LineSegment']):
        return Line.get_intersection_point(line, self)

    def __repr__(self) -> str:
        return f'Line({self.sample_coordinates}, {self.angle})'

    @staticmethod
    def angle_between(first_line, second_line):
        a1 = first_line.angle
        a2 = second_line.angle
        if a1 == a2:
            return 0
        if (a1 > 0 and a2 > 0) or (a1 < 0 and a2 > 0):
            angle = fabs(a1 - a2)
        else:    
            angle = fabs(a1) + fabs(a2)
        return angle if angle <= 90 else 180 - angle
        
    @staticmethod
    def perpendicular_line(line, point_from=None):
        if point_from == None:
            coordinates = line.sample_coordinates
        else:
            coordinates = point_from
        if line.angle_coefficient != 0:
            k = -1 / line.angle_coefficient
            return Line(coordinates, angle_coefficient=k)
        return Line(coordinates, 90)

    @staticmethod
    def get_intersection_point(first_line: Union['Line', 'LineSegment'], second_line: Union['Line', 'LineSegment']):
        if isinstance(first_line, LineSegment):
            first_line = first_line.reconstruct_line()
        if isinstance(second_line, LineSegment):
            second_line = second_line.reconstruct_line()
        if first_line.angle_coefficient == second_line.angle_coefficient:
            return None
        if first_line.oy_segment != None and second_line.oy_segment != None:
            x = (second_line.oy_segment - first_line.oy_segment) / (first_line.angle_coefficient - second_line.angle_coefficient)
            return Point(x, first_line.get_y_coordinate(x))
        if first_line.oy_segment == None:
            x = first_line.sample_coordinates.x
            return Point(x, second_line.get_y_coordinate(x))
        x = second_line.sample_coordinates.x
        return Point(x, first_line.get_y_coordinate(x))

    @staticmethod
    def construct_by_two_points(first_point: Point, second_point: Point):
        if first_point.x != second_point.x:
            angle_coefficient = (second_point.y - first_point.y) / (second_point.x - first_point.x)
        else:
            angle_coefficient = math.inf
        return Line(first_point, angle_coefficient=angle_coefficient)


class LineSegment:
    def __init__(self, first_point: Point, second_point: Point):
        self.related_line = Line.construct_by_two_points(first_point, second_point)
        if first_point.x <= second_point.x:
            self.endpoints = [first_point, second_point]
        else:
            self.endpoints = [second_point, first_point]

    def reconstruct_line(self):
        return self.related_line

    def check_intersection(self, line: Line):
        possible_intersection_point = Line.get_intersection_point(self.related_line, line)
        if (min(self.endpoints[0].x, self.endpoints[1].x) <= possible_intersection_point.x <= max(self.endpoints[0].x, self.endpoints[1].x)
            and min(self.endpoints[0].y, self.endpoints[1].y) <= possible_intersection_point.y <= max(self.endpoints[0].y, self.endpoints[1].y)):
            return True
        return False
    
    def get_intersection_point(self, line: Union[Line, 'LineSegment']):
        return Line.get_intersection_point(line, self)

    def get_intersection(self, line: Union[Line, 'LineSegment']):
        if isinstance(line, Line):
            is_intersect = self.check_intersection(line)
        elif isinstance(line, LineSegment):
            is_intersect = self.check_intersection(line.reconstruct_line()) & line.check_intersection(self.reconstruct_line())
        intersection_point = self.get_intersection_point(line)
        return (is_intersect, intersection_point, self.reconstruct_line())
        


class Plane:
    ORIGIN = Point(0, 0)

    def __init__(self, width, height=None):
        """Pass only width to get a square"""
        self._plane = []
        if height != None:
            for _ in range(height):
                self._plane.append([0]*width)
        else:
            for _ in range(width):
                self._plane.append([0]*width)
        self._plane = np.array(self._plane, int)
        self.width = width
        if height != None:
            self.height = height
        else:
            self.height = width
        self.borders = {
            'left': Line(self.ORIGIN, 90),
            'bottom': Line(self.ORIGIN, 0),
            'top': Line(Point(self.width, self.height), 0),
            'right': Line(Point(self.width, self.height), 90),
        }
        self.objects_on_plane = []

    def size(self):
        return (self.width, self.height)

    def get_point(self, coordinates:Point):
        if coordinates.x >= self.width or coordinates.y >= self.height or coordinates.x < 0 or coordinates.y < 0:
            return None
        return self._plane[coordinates.y][coordinates.x]

    def set_point(self, coordinates:Point, value:int):
        if coordinates.x >= self.width or coordinates.y >= self.height or coordinates.x < 0 or coordinates.y < 0:
            return None
        self._plane[coordinates.y][coordinates.x] = value

    def borders_as_list(self):
        return [self.borders[key] for key in self.borders]

    def append_object(self, object_to_append):
        self.objects_on_plane.append(object_to_append)

    def get_closest_object(self, point: Point):
        closest = None
        min_distance = math.inf
        for obj in self.objects_on_plane:
            distance = obj.get_distance_from_a_point(point)
            if distance < min_distance:
                closest = obj
        return closest