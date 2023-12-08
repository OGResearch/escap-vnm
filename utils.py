"""
"""


#[
from __future__ import annotations
from typing import (Any, Iterable, )
import csv
import numpy
import scipy
#]


_DEFAULT_VARIANTS = ("Baseline", )


def rename_input_data(s):
    s = s.lower()
    s = s.replace("obs", "__yearly__")
    s = s.replace("vnm_", "")
    s = s.replace("_0", "")
    s = s.replace("$", "_S")
    #
    # Add eviews shocks (tunes from eviews baseline)
    s = s.replace("_a", "_eviews")
    #
    # For scenario building (without female)
    for n in (
        "_rca", "_ntp", "_edu",
        # "_ct", "_ict",
        "_ran", "_ntn", "_edn", "_ctn", "_ic2"
    ):
        s = s.replace(n, "")
    #
    return s


gamma_inv = scipy.stats.gamma(0.5, ).ppf

lognorm_cdf = \
    lambda x, mu, sigma: scipy.stats.lognorm.cdf(x, s=sigma, scale=numpy.exp(mu), )

function_context = {
    "gamma_inv": gamma_inv,
    "lognorm_cdf": lognorm_cdf,
}


def read_parameters_from_csv(
    file_path: str,
    variants: str | Iterable[str] = None,
) -> dict[str, Any]:
    """
    """
    #[
    variants = _resolve_variants(variants, )
    with open(file_path, "r") as file:
        dict_reader = csv.DictReader(file, )
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


