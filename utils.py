"""
"""


#[
from __future__ import annotations
from typing import (Any, Iterable, )
import csv as _cs
#]


_DEFAULT_VARIANTS = ("Baseline", )

def read_parameters_from_csv(
    file_path: str,
    variants: str | Iterable[str] = None,
) -> dict[str, Any]:
    """
    """
    #[
    variants = _resolve_variants(variants, )
    with open(file_path, "r") as file:
        dict_reader = _cs.DictReader(file, )
        return {
            row["Parameter"]: _get_variants(row, variants)
            for row in dict_reader if _is_valid_row(row, )
        }
    #]


def _resolve_variants(
    variants: str | Iterable[str],
    ) -> Iterable[str]:
    """
    """
    if variants is None:
        variants = _DEFAULT_VARIANTS
    elif isinstance(variants, str):
        variants = (variants, )
    return tuple(v for v in variants)


def _get_variants(
    row: dict[str, Any],
    variants: Iterable[str],
) -> float | list[float]:
    """
    """
    output = [ float(row[variant]) for variant in variants ]
    if len(output) == 1:
        output = output[0]
    return output


def _is_valid_row(row: dict[str, Any], ) -> bool:
    """
    """
    return (
        row["Parameter"].strip()
        and not row["Parameter"].strip().startswith("#")
    )


