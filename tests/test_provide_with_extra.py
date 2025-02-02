from dataclasses import dataclass
from typing import List, Optional

import pytest

from dataclass_mapper import map_to, mapper, provide_with_extra


@dataclass
class Target:
    x: int


@mapper(Target, {"x": provide_with_extra()})
@dataclass
class Source:
    pass


def test_provide_with_extra_simple():
    @mapper(Target, {"x": provide_with_extra()})
    @dataclass
    class Source:
        pass

    assert map_to(Source(), Target, {"x": 42}) == Target(x=42)


def test_provide_with_extra_missing_extra():

    with pytest.raises(TypeError) as excinfo:
        map_to(Source(), Target)
    assert (
        "When mapping an object of 'Source' to 'Target' the field 'x' needs to be provided in the `extra` dictionary"
        == str(excinfo.value)
    )


def test_provide_with_extra_recursive_simple():
    @dataclass
    class TargetCollection:
        field: Target

    @mapper(TargetCollection)
    @dataclass
    class SourceCollection:
        field: Source

    source_collection = SourceCollection(field=Source())
    target_collection = TargetCollection(field=Target(x=1))

    assert map_to(source_collection, TargetCollection, extra={"field": {"x": 1}}) == target_collection


def test_provide_with_extra_recursive_optional():
    @dataclass
    class TargetCollection:
        optional_field: Optional[Target]

    @mapper(TargetCollection)
    @dataclass
    class SourceCollection:
        optional_field: Optional[Source]

    # no extra necessary for None
    source_collection = SourceCollection(optional_field=None)
    target_collection = TargetCollection(optional_field=None)
    assert map_to(source_collection, TargetCollection) == target_collection

    # extra necessary for not None
    source_collection = SourceCollection(optional_field=Source())
    target_collection = TargetCollection(optional_field=Target(x=2))
    assert (
        map_to(
            source_collection,
            TargetCollection,
            extra={"optional_field": {"x": 2}},
        )
        == target_collection
    )


def test_provide_with_extra_recursive_list():
    @dataclass
    class TargetCollection:
        fields: List[Target]

    @mapper(TargetCollection)
    @dataclass
    class SourceCollection:
        fields: List[Source]

    source_collection = SourceCollection(fields=[Source(), Source()])
    target_collection = TargetCollection(fields=[Target(x=0), Target(x=1)])

    assert (
        map_to(
            source_collection,
            TargetCollection,
            extra={"fields": [{"x": 0}, {"x": 1}]},
        )
        == target_collection
    )
