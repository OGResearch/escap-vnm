
import re as _re
import json as _js


def _read_equations(x: str) -> tuple[str, ...]:
    return _re.findall(r"^.*;", x, _re.MULTILINE)

def _get_lhs_names(eqn: tuple[str, ...]) -> tuple[str, ...]:
    lhs = [ i.split("=")[0].strip() for i in eqn ]
    return tuple(_re.search(r"\w+\b(?!\()", i).group() for i in lhs)

def _get_func_names(x: str) -> tuple[str, ...]:
    return tuple(set(_re.findall(r"\b\w+\b(?=\()", x)))


with open("escap-vnm.model", "r") as fid:
    m = fid.read()

with open("escap-vnm-externals.model", "r") as fid:
    x = fid.read()


m = _re.sub(r"[`!]\w+", "", m, )
x = _re.sub(r"[`!]\w+", "", x, )

names = _re.findall(r"\b[a-z]\w*\b(?!\()", m)
names = tuple(i for i in set(names) if not i.startswith("res_"))

vnm_names = tuple(i for i in names if i.startswith("vnm_"))
wld_names = tuple(i for i in names if i.startswith("wld_"))
usa_names = tuple(i for i in names if i.startswith("usa_"))

rest = set(names).difference(vnm_names + wld_names + usa_names)

if rest:
    raise ValueError("Unaccounted names")

m_func_names = _get_func_names(m, )
m_func_names = set(m_func_names).difference(("diff", "diff_log", "log", "exp"))


m_eqn = _read_equations(m, )
m_lhs_names = _get_lhs_names(m_eqn, )

if len(m_lhs_names) != len(set(m_lhs_names)):
    raise ValueError("Duplicate LHS names in model equations")

x_eqn = _read_equations(x, )
x_lhs_names = _get_lhs_names(x_eqn, )

with open("vnm-variables.json", "w+") as fid:
    _js.dump(vnm_names, fid, indent=4)

with open("wld-variables.json", "w+") as fid:
    _js.dump(wld_names, fid, indent=4)

with open("usa-variables.json", "w+") as fid:
    _js.dump(usa_names, fid, indent=4)

with open("func-names.json", "w+") as fid:
    _js.dump(tuple(m_func_names), fid, indent=4)


