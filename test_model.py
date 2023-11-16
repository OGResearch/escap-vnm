

import irispie as _ir
import scipy as _sp
import numpy as _np
import copy as _cp
import time as _ti
import sys as _sy
import utils as _ut

#
# Read input data
#

def name_row_transform(s):
    s = s.lower()
    s = s.replace("obs", "__yearly__")
    s = s.replace("vnm_", "")
    s = s.replace("_0", "")
    s = s.replace("$", "_S")
    return s

db = _ir.Databox.from_sheet(
    "result_baseline_1108.csv",
    name_row_transform=name_row_transform,
    description_row=False,
)


#
# Create model object with user funtions
#

gamma_inv = _sp.stats.gamma(0.5, ).ppf

lognorm_cdf = \
    lambda x, mu, sigma: _sp.stats.lognorm.cdf(x, s=sigma, scale=_np.exp(mu), )

context = {
    "gamma_inv": gamma_inv,
    "lognorm_cdf": lognorm_cdf,
}

m = _ir.Simultaneous.from_file(
    "escap-vnm.model",
    context=context,
    deterministic=True,
)


#
# Read in and assign baseline parameters
#

baseline_parameters = \
    _ut.read_parameters_from_csv("escap-vnm-parameters.csv", )

m.assign(baseline_parameters, )


#
# Set up simulation
#

start_date = _ir.yy(2022)
end_date = _ir.yy(2026)
span = start_date >> end_date

p = _ir.PlanSimulate(m, span, )


#
# Baseline simulation
#

db0 = db.copy()
s0, *_ = m.simulate(db0, span, method="period", plan=p, )


#
# Simulation with 10% shock to PCR
#

db1 = db.copy()
db1["res_pcr"] = 0.10
s1, *_ = m.simulate(db1, span, method="period", plan=p, )


#
# Save simulation data
#

s0.to_sheet("s0.csv", )
s1.to_sheet("s1.csv", )

