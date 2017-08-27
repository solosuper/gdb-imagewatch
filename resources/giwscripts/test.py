# -*- coding: utf-8 -*-

"""
Module developed for quick testing the ImageWatch shared library
"""

import math
import time

import numpy

from giwscripts import giwwindow
from giwscripts import symbols
from giwscripts.debuggers.interfaces import BridgeInterface


def giwtest(script_path):
    """
    Entry point for the testing mode.
    """

    dummy_debugger = DummyDebugger()

    window = giwwindow.GdbImageWatchWindow(script_path, dummy_debugger)
    window.initialize_window()

    # Wait for window to initialize
    while not window.is_running():
        time.sleep(0.5)

    window.update_available_variables(dummy_debugger.get_available_symbols())

    for buffer in dummy_debugger.get_available_symbols():
        window.plot_variable(buffer)

    while window.is_running():
        time.sleep(0.5)

    window.terminate()
    exit(0)


def gen_color(pos, k, f_a, f_b):
    """
    Generates a color for the pixel at (pos[0], pos[1]) with coefficients k[0]
    and k[1], and colouring functions f_a and f_b that map R->[-1, 1].
    """
    return (f_a(pos[0] * f_b(pos[1]/k[0])/k[1]) + 1) * 255 / 2


def gen_buffers(width, height):
    """
    Generate sample buffers
    """
    channels = [3, 1]

    types = [{'numpy': numpy.uint8, 'giw': symbols.GIW_TYPES_UINT8},
             {'numpy': numpy.float32, 'giw': symbols.GIW_TYPES_FLOAT32}]

    tex1 = [None] * width * height * channels[0]
    tex2 = [None] * width * height * channels[1]

    for pos_y in range(0, height):
        for pos_x in range(0, width):
            pixel_pos = [pos_x, pos_y]

            buffer_pos = pos_y * channels[0] * width + channels[0] * pos_x

            tex1[buffer_pos + 0] = gen_color(
                pixel_pos, [20, 80], math.cos, math.cos)
            tex1[buffer_pos + 1] = gen_color(
                pixel_pos, [50, 200], math.sin, math.cos)
            tex1[buffer_pos + 2] = gen_color(
                pixel_pos, [30, 120], math.cos, math.cos)

            buffer_pos = pos_y * channels[1] * width + channels[1] * pos_x

            for channel in range(0, channels[1]):
                tex2[buffer_pos + channel] = (
                    math.exp(math.cos(pos_x / 5.0) *
                             math.sin(pos_y / 5.0)))

    tex_arr1 = numpy.asarray(tex1, types[0]['numpy'])
    tex_arr2 = numpy.asarray(tex2, types[1]['numpy'])
    mem1 = memoryview(tex_arr1)
    mem2 = memoryview(tex_arr2)
    rowstride = width

    return {
        'sample_buffer_1': [
            mem1,
            width, height, channels[0],
            types[0]['giw'],
            rowstride,
            'rgba'
        ],
        'sample_buffer_2': [
            mem2,
            width, height, channels[1],
            types[1]['giw'],
            rowstride,
            'rgba'
        ]
    }


class DummyDebugger(BridgeInterface):
    """
    Very simple implementation of a debugger bridge for the sake of the test
    mode.
    """
    def __init__(self):
        width = 400
        height = 200
        self._buffers = gen_buffers(width, height)

    def get_casted_pointer(self, typename, debugger_object):
        """
        No need to cast anything in this example
        """
        return debugger_object

    def register_event_handlers(self, events):
        """
        No need to register events in this example
        """
        pass

    def get_available_symbols(self):
        """
        Return the names of the available sample buffers
        """
        return self._buffers

    def get_buffer_metadata(self, var_name):
        """
        Search in the list of available buffers and return the requested one
        """
        for buffer in self._buffers:
            if buffer == var_name:
                return self._buffers[buffer]

    def queue_request(self, callable_request):
        callable_request()
