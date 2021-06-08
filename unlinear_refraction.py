import math

from visual2d import VisualPlane, Color
from plane2d import Point
from opticallines import RefractionLine
from light_beam import LightBeam
from visuallight import LightBeamSceneManager, generate_nonpoint_beam


WIDTH_OF_BEAM = 16
BEAM_PRESICION = 1
HEIGTH_OF_BEAM = 4
STARTING_HEIGHT = 700
def equation(x: float):
    return 2 + math.sin(2*x) # 2 added to shift result in range [1; 3]

plane = VisualPlane(1000, path_to_image_folder='./unlinear_refractions')

BEAM = [
    (LightBeam(Point(100, 900), -45), Color.RED, True),
]

lines = []
beams = generate_nonpoint_beam(WIDTH_OF_BEAM, HEIGTH_OF_BEAM, BEAM_PRESICION, Point(100, 900), -45, Color.RED)

previous_refraction_coefficient = 1
for depth in range(STARTING_HEIGHT, 0, -2):
    new_refraction_coefficient = equation((STARTING_HEIGHT - depth)/100)
    lines.append((RefractionLine(Point(500, depth), previous_refraction_coefficient, new_refraction_coefficient, 0), (0, 0, 150)))
    previous_refraction_coefficient = new_refraction_coefficient

scene = LightBeamSceneManager(plane, beams=BEAM, lines=lines, refraction_coefficients_management=False)
scene.draw_picture('Sine equation, beam with infinitly small width')

scene.regroup_scene(beams=beams, lines=lines, refraction_coefficients_management=False)
scene.draw_picture('Sine equation, beam with some width')