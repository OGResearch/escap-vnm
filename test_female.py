

import irispie as _ir


def name_row_transform(s):
    s = s.lower()
    s = s.replace("obs", "__yearly__")
    s = s.replace("vnm_", "")
    s = s.replace("_0", "")
    s = s.replace("$", "_S")
    s = s.replace("_a", "_eviews") #add eviews shocks (tunes from eviews baseline)
    # for scenario building
    s = s.replace("_rca", "") #scen 1
    s = s.replace("_ntp", "") #scen 2_1
    s = s.replace("_edu", "") #scen 2_2
    s = s.replace("_ct", "")  #scen 3
    s = s.replace("_ict", "") #scen 4
    return s

db = _ir.Databox.from_sheet(
    "result_baseline_female.csv", # result_baseline_correct.csv, result_baseline_female
    name_row_transform=name_row_transform,
    description_row=False,
)

source = """

# !variables
# 
#     lrxf_cond_1
#     lrfx_dynamics_1
#     lrxf_cond_2
#     lrfx_dynamics_2
#     lrxf_switch
#     lrxf
# 
# !exogenous-variables
# 
#     yer
#     popt
#     skrat
# 

!parameters

    c0_lrxf
    c1_lrxf
    c2_lrxf
    c3_lrxf
    c4_lrxf
    c5_lrxf
    ss_lrxf

    lrxf_sigma_1
    lrxf_sigma_2


!substitutions

    lrxf_cond_1 := ((yer*1000/popt/c5_lrxf) - 1);
    lrxf_cond_2 := (lrxf[-1] - (ss_lrxf - 0.02));

    lrfx_ss_dynamics := (ss_lrxf);
    lrfx_trans_dynamics := (c1_lrxf + c2_lrxf*log(yer*1000/popt) + c3_lrxf*log(yer*1000/popt)**2 + c4_lrxf*skrat);


!equations

    lrxf_switch = logistic($lrxf_cond_1$ * lrxf_sigma_1) * logistic($lrxf_cond_2$ * lrxf_sigma_2);

    lrxf = ...
        + c0_lrxf * lrxf[-1] ...
        + (1 - c0_lrxf) * ((1 - lrxf_switch) * $lrfx_trans_dynamics$ +  lrxf_switch * $lrfx_ss_dynamics$) ...
    ;

"""

m = _ir.Sequential.from_string(source, )

p = {
    "c0_lrxf": 0.65672,
    "c1_lrxf": 4.4441532,
    "c2_lrxf": -0.7084184,
    "c3_lrxf": 0.0345780,
    "c4_lrxf": 0.005,
    "c5_lrxf": 37609,
    "ss_lrxf": 0.87,
    "lrxf_sigma_1": 100,
    "lrxf_sigma_2": 500,
}

m.assign(p, )

s, *_ = m.simulate(db, _ir.yy(2021,...,2040), )


