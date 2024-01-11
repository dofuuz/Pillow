#
# The Python Imaging Library
# $Id$
#
# a simple math add-on for the Python Imaging Library
#
# History:
# 1999-02-15 fl   Original PIL Plus release
# 2005-05-05 fl   Simplified and cleaned up for PIL 1.1.6
# 2005-09-12 fl   Fixed int() and float() for Python 2.4.1
#
# Copyright (c) 1999-2005 by Secret Labs AB
# Copyright (c) 2005 by Fredrik Lundh
#
# See the README file for information on usage and redistribution.
#
from __future__ import annotations

import builtins
from types import CodeType
from typing import Any

from . import Image, _imagingmath


class _Operand:
    """Wraps an image operand, providing standard operators"""

    def __init__(self, im: Image.Image):
        self.im = im

    def __fixup(self, im1: _Operand | float) -> Image.Image:
        # convert image to suitable mode
        if isinstance(im1, _Operand):
            # argument was an image.
            if im1.im.mode in ("1", "L"):
                return im1.im.convert("I")
            elif im1.im.mode in ("I", "F"):
                return im1.im
            else:
                msg = f"unsupported mode: {im1.im.mode}"
                raise ValueError(msg)
        else:
            # argument was a constant
            if isinstance(im1, (int, float)) and self.im.mode in ("1", "L", "I"):
                return Image.new("I", self.im.size, im1)
            else:
                return Image.new("F", self.im.size, im1)

    def apply(
        self,
        op: str,
        im1: _Operand | float,
        im2: _Operand | float | None = None,
        mode: str | None = None,
    ) -> _Operand:
        im_1 = self.__fixup(im1)
        if im2 is None:
            # unary operation
            out = Image.new(mode or im_1.mode, im_1.size, None)
            im_1.load()
            try:
                op = getattr(_imagingmath, op + "_" + im_1.mode)
            except AttributeError as e:
                msg = f"bad operand type for '{op}'"
                raise TypeError(msg) from e
            _imagingmath.unop(op, out.im.id, im_1.im.id)
        else:
            # binary operation
            im_2 = self.__fixup(im2)
            if im_1.mode != im_2.mode:
                # convert both arguments to floating point
                if im_1.mode != "F":
                    im_1 = im_1.convert("F")
                if im_2.mode != "F":
                    im_2 = im_2.convert("F")
            if im_1.size != im_2.size:
                # crop both arguments to a common size
                size = (
                    min(im_1.size[0], im_2.size[0]),
                    min(im_1.size[1], im_2.size[1]),
                )
                if im_1.size != size:
                    im_1 = im_1.crop((0, 0) + size)
                if im_2.size != size:
                    im_2 = im_2.crop((0, 0) + size)
            out = Image.new(mode or im_1.mode, im_1.size, None)
            im_1.load()
            im_2.load()
            try:
                op = getattr(_imagingmath, op + "_" + im_1.mode)
            except AttributeError as e:
                msg = f"bad operand type for '{op}'"
                raise TypeError(msg) from e
            _imagingmath.binop(op, out.im.id, im_1.im.id, im_2.im.id)
        return _Operand(out)

    # unary operators
    def __bool__(self) -> bool:
        # an image is "true" if it contains at least one non-zero pixel
        return self.im.getbbox() is not None

    def __abs__(self) -> _Operand:
        return self.apply("abs", self)

    def __pos__(self) -> _Operand:
        return self

    def __neg__(self) -> _Operand:
        return self.apply("neg", self)

    # binary operators
    def __add__(self, other: _Operand | float) -> _Operand:
        return self.apply("add", self, other)

    def __radd__(self, other: _Operand | float) -> _Operand:
        return self.apply("add", other, self)

    def __sub__(self, other: _Operand | float) -> _Operand:
        return self.apply("sub", self, other)

    def __rsub__(self, other: _Operand | float) -> _Operand:
        return self.apply("sub", other, self)

    def __mul__(self, other: _Operand | float) -> _Operand:
        return self.apply("mul", self, other)

    def __rmul__(self, other: _Operand | float) -> _Operand:
        return self.apply("mul", other, self)

    def __truediv__(self, other: _Operand | float) -> _Operand:
        return self.apply("div", self, other)

    def __rtruediv__(self, other: _Operand | float) -> _Operand:
        return self.apply("div", other, self)

    def __mod__(self, other: _Operand | float) -> _Operand:
        return self.apply("mod", self, other)

    def __rmod__(self, other: _Operand | float) -> _Operand:
        return self.apply("mod", other, self)

    def __pow__(self, other: _Operand | float) -> _Operand:
        return self.apply("pow", self, other)

    def __rpow__(self, other: _Operand | float) -> _Operand:
        return self.apply("pow", other, self)

    # bitwise
    def __invert__(self) -> _Operand:
        return self.apply("invert", self)

    def __and__(self, other: _Operand | float) -> _Operand:
        return self.apply("and", self, other)

    def __rand__(self, other: _Operand | float) -> _Operand:
        return self.apply("and", other, self)

    def __or__(self, other: _Operand | float) -> _Operand:
        return self.apply("or", self, other)

    def __ror__(self, other: _Operand | float) -> _Operand:
        return self.apply("or", other, self)

    def __xor__(self, other: _Operand | float) -> _Operand:
        return self.apply("xor", self, other)

    def __rxor__(self, other: _Operand | float) -> _Operand:
        return self.apply("xor", other, self)

    def __lshift__(self, other: _Operand | float) -> _Operand:
        return self.apply("lshift", self, other)

    def __rshift__(self, other: _Operand | float) -> _Operand:
        return self.apply("rshift", self, other)

    # logical
    def __eq__(self, other):
        return self.apply("eq", self, other)

    def __ne__(self, other):
        return self.apply("ne", self, other)

    def __lt__(self, other: _Operand | float) -> _Operand:
        return self.apply("lt", self, other)

    def __le__(self, other: _Operand | float) -> _Operand:
        return self.apply("le", self, other)

    def __gt__(self, other: _Operand | float) -> _Operand:
        return self.apply("gt", self, other)

    def __ge__(self, other: _Operand | float) -> _Operand:
        return self.apply("ge", self, other)


# conversions
def imagemath_int(self: _Operand) -> _Operand:
    return _Operand(self.im.convert("I"))


def imagemath_float(self: _Operand) -> _Operand:
    return _Operand(self.im.convert("F"))


# logical
def imagemath_equal(self: _Operand, other: _Operand | float | None) -> _Operand:
    return self.apply("eq", self, other, mode="I")


def imagemath_notequal(self: _Operand, other: _Operand | float | None) -> _Operand:
    return self.apply("ne", self, other, mode="I")


def imagemath_min(self: _Operand, other: _Operand | float | None) -> _Operand:
    return self.apply("min", self, other)


def imagemath_max(self: _Operand, other: _Operand | float | None) -> _Operand:
    return self.apply("max", self, other)


def imagemath_convert(self: _Operand, mode: str) -> _Operand:
    return _Operand(self.im.convert(mode))


ops = {}
for k, v in list(globals().items()):
    if k[:10] == "imagemath_":
        ops[k[10:]] = v


def eval(expression: str, _dict: dict[str, Any] = {}, **kw: Any) -> Any:
    """
    Evaluates an image expression.

    :param expression: A string containing a Python-style expression.
    :param options: Values to add to the evaluation context.  You
                    can either use a dictionary, or one or more keyword
                    arguments.
    :return: The evaluated expression. This is usually an image object, but can
             also be an integer, a floating point value, or a pixel tuple,
             depending on the expression.
    """

    # build execution namespace
    args = ops.copy()
    for k in list(_dict.keys()) + list(kw.keys()):
        if "__" in k or hasattr(builtins, k):
            msg = f"'{k}' not allowed"
            raise ValueError(msg)

    args.update(_dict)
    args.update(kw)
    for k, v in args.items():
        if hasattr(v, "im"):
            args[k] = _Operand(v)

    compiled_code = compile(expression, "<string>", "eval")

    def scan(code: CodeType) -> None:
        for const in code.co_consts:
            if type(const) is type(compiled_code):
                scan(const)

        for name in code.co_names:
            if name not in args and name != "abs":
                msg = f"'{name}' not allowed"
                raise ValueError(msg)

    scan(compiled_code)
    out = builtins.eval(expression, {"__builtins": {"abs": abs}}, args)
    try:
        return out.im
    except AttributeError:
        return out
