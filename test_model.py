
import irispie as _ir
import scipy as _sp
import numpy as _np
import copy as _cp
import time as _ti
import sys as _sy
import utils as _ut
import csv


_ir.min_irispie_version_required("0.25.0", )

# Setup which scenarios to run
scenarios_to_run = (
    "baseline",
    #"scenario1",
    #"scenario2_1",
    #"scenario2_2",
    #"scenario3",
    #"scenario4",
    "compare",
)

#
# Read input data
#

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

db_res = _ir.Databox.from_sheet(
    "result_residuals_female.csv", # result_residuals1.csv, result_residuals_female
    name_row_transform=name_row_transform,
    description_row=False,
)

db.update(db_res)

#
# Rescaling exercise
#

# import the description file
def csv_to_dict(csv_file_path):
    result_dict = {}
    
    with open(csv_file_path, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        

        for row in csv_reader:
            # Assuming the first column contains unique keys
            key = row.pop(csv_reader.fieldnames[0])
            result_dict[key] = row
    
    return result_dict

csv_file_path = 'variable_description.csv'
db_desc = csv_to_dict(csv_file_path)

prefix_to_remove = 'VNM_'
db_desc = {key.replace(prefix_to_remove, '', 1): value for key, value in db_desc.items()}

# Filter the variables to rescale - it is not nescessarly to do, model is working anyway
# if you turn this on adjust the c0_xtn variable in the parameter file

#unit_to_filter = 'bln LCY'

# Create a list to store keys that meet the condition
# filtered_keys = []

# # Iterate over the dictionary items
# for key, value in db_desc.items():
#     if 'unit' in value and value['unit'] == unit_to_filter:
#         filtered_keys.append(key)

# # Rescale the bln LCY variables (and their residuals) and exchange rate variable
# for variable_name in filtered_keys:
#     column_name = variable_name
#     column_name_eviews = variable_name + '_eviews'
#     column_name_eviews2 = variable_name + 'b'

#     if column_name.lower() in db.get_names():
#         print(column_name)
#         db[column_name.lower()] = db[column_name.lower()]/1000
#     if column_name_eviews.lower() in db.get_names():
#         print(column_name_eviews)
#         db[column_name_eviews.lower()] = db[column_name_eviews.lower()]/1000
#     if column_name_eviews2.lower() in db.get_names():
#         print(column_name_eviews2)
#         db[column_name_eviews2.lower()] = db[column_name_eviews2.lower()]/1000

    #if abs(db[variable_name.lower()](_ir.yy(2020))) < 100:
    #    print(variable_name)

#db['exr'] = db['exr']/1000
#db['exr_eviews'] = db['exr_eviews']/1000


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

start_date = _ir.yy(2021)
end_date = _ir.yy(2050)
span = start_date >> end_date
span_short = start_date >> _ir.yy(2026)


#
# Baseline simulation
#

db0 = db.copy()
#s0, *_ = m.simulate(db0, span, method="period", )
#s0.to_sheet("s0.csv", )

    
#
# Simulation plan in baseline scenario
#

if "baseline" in scenarios_to_run:
    p1 = _ir.PlanSimulate(m, span, )

    # Female LFPR block
    p1.swap(span, ("popwaf", "res_popwaf"), ) # should be tuned until 2050
    p1.swap(span, ("lrxf", "res_lrxf"), ) # exogenized temporarily until FLFPR formula is ready
    p1.swap(span, ("skrat", "res_skrat"), ) # education variable, should be exogenized always

    # GDP items
    p1.swap(span_short, ("gcr", "res_gcr"), )
    p1.swap(span_short, ("pcr", "res_pcr"), )
    #p1.swap(span_short, ("itr", "res_ipr"), )
    p1.swap(span_short, ("ipr", "res_ipr"), )
    p1.swap(span_short, ("igr", "res_igr"), )
    p1.swap(span_short, ("scr", "res_scr"), )
    p1.swap(span_short, ("xtr", "res_xtr"), )
    p1.swap(span_short, ("mtr", "res_mtr"), )
    # Budget expenditure items
    # p1.swap(span, ("exp", "res_ogi"), ) # exp is an identity withouth shock, enrun_genizing one subitem of exp // might want to change this
    p1.swap(span_short, ("expe", "res_expe"), )
    p1.swap(span_short, ("exph", "res_exph"), ) 
    p1.swap(span_short, ("expsp", "res_expsp"), )
    p1.swap(span_short, ("ogc", "res_ogc"), ) 
    p1.swap(span_short, ("ogi", "res_ogi"), ) 
    p1.swap(span_short, ("gip", "res_gip"), ) 
    # Budget revenue items
    # p1.swap(span, ("exp", "res_ogi"), ) # exp is an identity withouth shock, enrun_genizing one subitem of exp // might want to change this
    p1.swap(span_short, ("tax", "res_taxr"), )
    p1.swap(span_short, ("ctax", "res_ctaxr"), ) 
    p1.swap(span_short, ("itax", "res_itaxr"), )
    p1.swap(span_short, ("gtrade", "res_gtrader"), ) 
    #p1.swap(span, ("revg", "res_revg"), ) this one we treat as fully exogenous
    p1.swap(span_short, ("gcom", "res_gcom"), )
    p1.swap(span_short, ("goth", "res_goth"), )

    # Other variables
    p1.swap(span, ("eff", "res_eff"), ) # should be tuned until 2050
    p1.swap(span, ("popt", "res_popt"), ) # should be tuned until 2050
    p1.swap(span, ("popwa", "res_popwa"), ) # should be tuned until 2050
    p1.swap(span_short, ("yed", "res_yed"), )
    p1.swap(span_short, ("yft", "res_yft"), )
    p1.swap(span_short, ("exr", "res_exr"), )
    p1.swap(span_short, ("hic", "res_hic"), )
    p1.swap(span_short, ("gdn", "res_gdn"), )
    p1.swap(span_short, ("glnt", "res_glnt"), )

    # Exogenize these ranrun_m extra baseline variables
    p1.swap(span, ("expeb", "res_expeb"), )
    p1.swap(span, ("exphb", "res_exphb"), )
    p1.swap(span, ("expspb", "res_expspb"), )
    p1.swap(span, ("gcarbb", "res_gcarbb"), )

    # Equivalent to:
    # p1.exogenize(start_date, ("hic", "pcr"), )
    # p1.endogenize(start_date, ("res_hic", "res_pcr"), )

    db1 = db.copy()

    s1_female, *_ = m.simulate(db1, span, method="period", plan=p1, )
    s1_female.to_sheet("s1_female.csv", )

#
# Scenario builder
#

# Scenario 1

if "scenario1" in scenarios_to_run:
    # Scenario 1 assumption 
    db_asu = _ir.Databox.from_sheet(
        "Scenario_1/result_scen1_asu.csv",
        name_row_transform=name_row_transform,
        description_row=False,
    )

    # Scenario 1 result for comparison 
    db_scen1 = _ir.Databox.from_sheet(
        "Scenario_1/result_scen1.csv",
        name_row_transform=name_row_transform,
        description_row=False,
    )

    # create the fcast database
    db2 = db1.copy()
    db2.update(db_asu) #add the scenario assumpions to the db

    # add baseline shock to the simulation
    res_variable_list = [variable_name for variable_name in s1.get_names() if variable_name.startswith('res')]
    for variable_name in res_variable_list:
         db2[variable_name] = s1[variable_name]

    # Scenario 1 tunes:
        # add shocks
    db2['res_ipr']      = db_asu['ipr_eviews'] + s1['res_ipr']
    db2['ipr_eviews']   = 0

    db2['res_rc']       = db_asu['rc_eviews'] + s1['res_rc']
    db2['rc_eviews']    = 0

        # exogenize additional variables
    p2 = _ir.PlanSimulate(m, span, )
    p2.swap(span, ("ogi", "res_ogi"), ) 
    p2.swap(span, ("pr", "res_pr"), ) 
    

    s_scen1, *_ = m.simulate(db2, span, method="period", plan=p2, )


# Scenario 2_1

if "scenario2_1" in scenarios_to_run:
    # Scenario 2_1 assumption 
    db_asu2_1 = _ir.Databox.from_sheet(
        "Scenario_2_1/result_scen2_1_asu.csv",
        name_row_transform=name_row_transform,
        description_row=False,
    )

    # Scenario 2_1 result for comparison 
    db_scen2_1 = _ir.Databox.from_sheet(
        "Scenario_2_1/result_scen2_1.csv",
        name_row_transform=name_row_transform,
        description_row=False,
    )

    # create the fcast database
    db2_1 = db1.copy()
    db2_1.update(db_asu2_1) #add the scenario assumpions to the db

    # add baseline shock to the simulation
    res_variable_list = [variable_name for variable_name in s1.get_names() if variable_name.startswith('res')]
    for variable_name in res_variable_list:
         db2_1[variable_name] = s1[variable_name]

    # Scenario 2_1 tunes:
        # add shocks
    db2_1['res_ipr']            = s1['res_ipr'] + db_asu2_1['ipr_eviews']
    db2_1['ipr_eviews']         = 0

    db2_1['res_techl']          = s1['res_techl'] + db_asu2_1['techl_eviews']
    db2_1['techl_eviews']       = 0

    db2_1['res_gini_disp']      = s1['res_gini_disp'] + db_asu2_1['gini_disp_eviews']
    db2_1['gini_disp_eviews']   = 0

    db2_1['res_pm25']           = s1['res_pm25'] + db_asu2_1['pm25_eviews']
    db2_1['pm25_eviews']        = 0

    db2_1['res_rel_red']        = s1['res_rel_red'] + db_asu2_1['rel_red_eviews']
    db2_1['rel_red_eviews']     = 0

    db2_1['rpdi_eviews']        = db_asu2_1['rpdi_eviews'] # no shock in iripie on this variable, overwrite the eviews constant shock

        # exogenize additional variables
    p2 = _ir.PlanSimulate(m, span, )
    p2.swap(span, ("ogi", "res_ogi"), )
    p2.swap(span, ("exph", "res_exph"), ) 
    p2.swap(span, ("expsp", "res_expsp"), ) 
    p2.swap(span, ("eff", "res_eff"), ) 
    

    s_scen2_1, *_ = m.simulate(db2_1, span, method="period", plan=p2, )
    s_scen2_1.to_sheet("s_scen2_1.csv", )


# Scenario 2_2

if "scenario2_2" in scenarios_to_run:
    # Scenario 2_2 assumptions 
    db_asu2_2 = _ir.Databox.from_sheet(
        "Scenario_2_2/result_scen2_2_asu.csv",
        name_row_transform=name_row_transform,
        description_row=False,
    )

    # Scenario 2_2 result for comparison 
    db_scen2_2 = _ir.Databox.from_sheet(
        "Scenario_2_2/result_scen2_2.csv",
        name_row_transform=name_row_transform,
        description_row=False,
    )

    # create the fcast database
    db2_2 = db1.copy()
    db2_2.update(db_asu2_2) #add the scenario assumpions to the db

    # add baseline shock to the simulation
    res_variable_list = [variable_name for variable_name in s1.get_names() if variable_name.startswith('res')]
    for variable_name in res_variable_list:
         db2_2[variable_name] = s1[variable_name]

    # Scenario 2_2 tunes:
        # add shocks
    db2_2['res_techl']         = s1['res_techl'] + db_asu2_2['techl_eviews']
    db2_2['techl_eviews']      = 0

    db2_2['res_gini_disp']     = s1['res_gini_disp'] + db_asu2_2['gini_disp_eviews']
    db2_2['gini_disp_eviews']  = 0

        # exogenize additional variables
    p3 = _ir.PlanSimulate(m, span, )
    p3.swap(span, ("ogi", "res_ogi"), )
    p3.swap(span, ("ogc", "res_ogc"), ) 
  

    s_scen2_2, *_ = m.simulate(db2_2, span, method="period", plan=p3, )
    s_scen2_2.to_sheet("s_scen2_2.csv", )


# Scenario 3

if "scenario3" in scenarios_to_run:
    # Scenario 3 assumptions 
    db_asu3 = _ir.Databox.from_sheet(
        "Scenario_3/result_scen3_asu.csv",
        name_row_transform=name_row_transform,
        description_row=False,
    )

    # Scenario 3 result for comparison 
    db_scen3 = _ir.Databox.from_sheet(
        "Scenario_3/result_scen3.csv",
        name_row_transform=name_row_transform,
        description_row=False,
    )

    # create the fcast database
    db3 = db1.copy()
    db3.update(db_asu3) #add the scenario assumpions to the db

    # add baseline shock to the simulation
    res_variable_list = [variable_name for variable_name in s1.get_names() if variable_name.startswith('res')]
    for variable_name in res_variable_list:
         db3[variable_name] = s1[variable_name]

    # Scenario 3 tunes
    # add shocks
 
    # exogenize additional variables
    p4 = _ir.PlanSimulate(m, span, )
    p4.swap(span, ("gcarbr", "res_gcarbr"), )
    p4.swap(span, ("sharee", "res_sharee"), ) 
    p4.swap(span, ("sharesp", "res_sharesp"), ) 
    p4.swap(span, ("shareh", "res_shareh"), ) 
    p4.swap(span, ("sharex", "res_sharex"), ) 
  

    s_scen3, *_ = m.simulate(db3, span, method="period", plan=p4, )
    s_scen3.to_sheet("s_scen3.csv", )

# Scenario 4

if "scenario4" in scenarios_to_run:
    # Scenario 4 assumptions 
    db_asu4 = _ir.Databox.from_sheet(
        "Scenario_4/result_scen4_asu.csv",
        name_row_transform=name_row_transform,
        description_row=False,
    )

    # Scenario 4 result for comparison 
    db_scen4 = _ir.Databox.from_sheet(
        "Scenario_4/result_scen4.csv",
        name_row_transform=name_row_transform,
        description_row=False,
    )

    # create the fcast database
    db4 = db1.copy()
    db4.update(db_asu4) #add the scenario assumpions to the db

    # add baseline shock to the simulation
    res_variable_list = [variable_name for variable_name in s1.get_names() if variable_name.startswith('res')]
    for variable_name in res_variable_list:
         db4[variable_name] = s1[variable_name]

    # Scenario 4 tunes
    # add shocks
    db4['res_ipr']            = s1['res_ipr'] + db_asu4['ipr_eviews']
    db4['ipr_eviews']         = 0

    db4['res_techl']          = s1['res_techl'] + db_asu4['techl_eviews']
    db4['techl_eviews']       = 0

    db4['res_finc']           = s1['res_finc'] + db_asu4['finc_eviews']
    db4['finc_eviews']        = 0
 
    # exogenize additional variables
    p4 = _ir.PlanSimulate(m, span, )
    p4.swap(span, ("ogi", "res_ogi"), )
    p4.swap(span, ("rel_red", "res_rel_red"), )  

    s_scen4, *_ = m.simulate(db4, span, method="period", plan=p4, )
    s_scen4.to_sheet("s_scen4.csv", )

#
# Compare scenarios
#

if "compare" in scenarios_to_run:

    scenario = s1_female # replace me with the scenario
    reference = db # replace me with the reference databox
    tolerance = 0.1 # set up the difference you allow in % (0.1 means 0.1%)
    cmp_year = _ir.yy(2050) # set up the year when you want to compare the scenarios

    tmp = {}
    variable_list = reference.get_names()

    discrep_db = {
        name: (scenario[name] / reference[name]) * 100 - 100
        for name in scenario.keys()
        if name in reference.keys()
    }

    messages = [
        f'Variable {name}: {tmp[name](_ir.yy(cmp_year))} (value > {tolerance} in {cmp_year})'
        for name in discrep_db.keys()
        if abs(discrep_db[name](cmp_year)) > tolerance
    ]

    if messages:
        print("\n".join(messages))
    else:
        print("No discrepancies found")

