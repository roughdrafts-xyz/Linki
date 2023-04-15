from hypothesis import strategies

from linki.id import SHA224


@strategies.composite
def an_id(draw: strategies.DrawFn):
    _id = draw(strategies.from_regex(SHA224, fullmatch=True))
    return _id
