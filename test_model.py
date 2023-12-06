
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
    "scenario2_1",
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
    # for scenario building (without female)
    s = s.replace("_rca", "") #scen 1
    s = s.replace("_ntp", "") #scen 2_1
    s = s.replace("_edu", "") #scen 2_2
    #s = s.replace("_ct", "")  #scen 3
    #s = s.replace("_ict", "") #scen 4
    # for scenario building (with female)
    s = s.replace("_ran", "") #scen 1
    s = s.replace("_ntn", "") #scen 2_1
    s = s.replace("_edn", "") #scen 2_2
    s = s.replace("_ctn", "")  #scen 3
    s = s.replace("_ic2", "") #scen 4
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

# Needed for female model development
db['lrxf_switch'] =  _ir.Series()
db['lrxf_switch'][_ir.yy(2000) >> _ir.yy(2021)] = [0]

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
    # p1.swap(span, ("lrxf", "res_lrxf"), ) # exogenized temporarily until FLFPR formula is ready
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

    baseline_scen = s1_female

# Scenario 1

if "scenario1" in scenarios_to_run:
    # Scenario 1 assumption 
    db_asu = _ir.Databox.from_sheet(
        "Scenarios_with_female/Scenario_1/result_scen1_asu.csv",
        name_row_transform=name_row_transform,
        description_row=False,
    )

    # Scenario 1 result for comparison 
    db_scen1 = _ir.Databox.from_sheet(
        "Scenarios_with_female/Scenario_1/result_scen1.csv",
        name_row_transform=name_row_transform,
        description_row=False,
    )

    # create the fcast database
    db2 = db1.copy()
    #db2.update(db_asu) #add the scenario assumpions from eview to the db, not needed if you set up the tunes below

    # add baseline shock to the simulation
    res_variable_list = [variable_name for variable_name in baseline_scen.get_names() if variable_name.startswith('res')]
    for variable_name in res_variable_list:
         db2[variable_name] = baseline_scen[variable_name]

    #
    # Scenario 1 tunes
    #

    # Assumptions to set
    # Set the size of investment in renewables per year until 2030 (bln USD)
    shock1 = 13.5
	# Set the size of investment in renewables per year from 2030 until 2050 (bln USD)"
    shock2 = 23
    # Initial Renewable Energy capacity
    initial_rc = db1['rc'][_ir.yy(2021)].get_data()
	# Set the size of the renewable energy capacity in 2030 (Exojoules)
    shock3 = 1.26 
    # Set the size of the renewable energy capacity in 2050 (Exojoules)
    shock4 = 6.5 
    # Set share of renewable investment financed by the government
    shock5 = 100
    
    # Set the year when the shock is first introduced
    YR1 = 2021
    # Enter number of years over which to spread the investment shock first period
    Y3 = 9
    # Enter number of years over which to spread the investment shock second period
    Y4 = 20

    # Create the investment periods:
        # 1st investment period
    start_date1          = _ir.yy(YR1)
    end_date1            = _ir.yy(YR1)+Y3
    investment_span_1    = start_date1 >> end_date1
        # 2nd investment period
    start_date2          = _ir.yy(YR1)+Y3+1
    end_date2            = _ir.yy(YR1)+Y3+Y4
    investment_span_2    = start_date2 >> end_date2
        # end: after investment period - not needed, this investment scenario is running until end_date

    # Scenario 1 tunes:
        # Add shocks
    #db2['res_ipr']      = db_asu['ipr_eviews'] + baseline_scen['res_ipr']
    db2['res_ipr'][investment_span_1] = baseline_scen['res_ipr'] + db1['ipr_eviews'] + 0.18*((1-shock5/100)*shock1)/db1['yen_S']*db1['yer']/db1['ipr']
    db2['res_ipr'][investment_span_2] = baseline_scen['res_ipr'] + db1['ipr_eviews'] + 0.05*((1-shock5/100)*shock2)/db1['yen_S']*db1['yer']/db1['ipr']
    db2['ipr_eviews']                 = 0

    #db2['res_rc']       = db_asu['rc_eviews'] + baseline_scen['res_rc']
    db2['res_rc'][investment_span_1]  = baseline_scen['res_rc'] + db1['rc_eviews'] + 0.3*(_ir.log(shock3) - _ir.log(initial_rc))/Y3
    db2['res_rc'][investment_span_2]  = baseline_scen['res_rc'] + db1['rc_eviews'] + 1.1*(_ir.log(shock4) - _ir.log(shock3))/Y4
    db2['rc_eviews']                  = 0

        # Exogenized variables
    db2['ogi'][investment_span_1] = db1['ogi'] + db1['exr'] * shock1 * shock5/100
    db2['ogi'][investment_span_2] = db1['ogi'] + db1['exr'] * shock2 * shock5/100

    db2['pr'] = db1['pr'].copy()
    
    for i in list(investment_span_1):
        pr_lag       = db2['pr'][i-1].get_data()
        pr_base      = db1['pr'][i].get_data()
        pr_base_lag  = db1['pr'][i-1].get_data()
        yen_S        = db1['yen_S'][i].get_data()
        db2['pr'][i] = (pr_lag)*(pr_base/pr_base_lag) - 0.2*(shock1/yen_S)

    for i in list(investment_span_2):
        pr_lag       = db2['pr'][i-1].get_data()
        pr_base      = db1['pr'][i].get_data()
        pr_base_lag  = db1['pr'][i-1].get_data()
        yen_S        = db1['yen_S'][i].get_data()   
        db2['pr'][i] = (pr_lag)*(pr_base/pr_base_lag) - 0.2*(shock2/yen_S)

    # # # other and better way of handeling the sequential shock (db_temp is not working properly)
    # s = """
    # !transition-variables
    #     !list(`lhs)
    # !exogenous-variables
    #     yen_S
    #     pr_base    
    # !transition-equations
    #     pr`lhs = pr[-1]*(pr_base/pr_base[-1]) - 0.2*shock1`par/yen_S[-1];
    # !parameters
    #     !list(`par)
    # """
    # db_temp =  db1.copy()
    # db_temp['pr_base'] = db_temp['pr'].copy()
    
    # shock_param = {'shock1': shock1}
    # m.assign(shock_param, )
    # m = _ir.Sequential.from_string(s,)
    # tmp_pr, *_ = m.simulate(db_temp, investment_span_1)
   
    p2 = _ir.PlanSimulate(m, span, )
    p2.swap(span, ("ogi", "res_ogi"), ) 
    p2.swap(span, ("pr", "res_pr"), ) 
    # p2.swap(span, ("lrxf", "res_lrxf"), )   # it is here to check how irispie LRXF formula works 

    s_scen1_female, *_ = m.simulate(db2, span, method="period", plan=p2, )


# Scenario 2_1

if "scenario2_1" in scenarios_to_run:
    # Scenario 2_1 assumption 
    db_asu2_1 = _ir.Databox.from_sheet(
        "Scenarios_with_female/Scenario_2_1/result_scen2_1_asu.csv",
        name_row_transform=name_row_transform,
        description_row=False,
    )

    # Scenario 2_1 result for comparison 
    db_scen2_1 = _ir.Databox.from_sheet(
        "Scenarios_with_female/Scenario_2_1/result_scen2_1.csv",
        name_row_transform=name_row_transform,
        description_row=False,
    )

    # create the fcast database
    db2_1 = db1.copy()
    # db2_1.update(db_asu2_1) #add the scenario assumpions to the db

    # add baseline shock to the simulation
    res_variable_list = [variable_name for variable_name in baseline_scen.get_names() if variable_name.startswith('res')]
    for variable_name in res_variable_list:
         db2_1[variable_name] = baseline_scen[variable_name]

    #
    # Scenario 2_1 tunes
    #

    # Assumptions to set
    # Set the size of investment in infrastructure projects per year (as bln LCY)
    shock1  = 51757 # 51757 + 1500 + 426899 + 8604
    # Set share of infrastructre investment financed by the government
    shock1a = 99 # 100
	# Set the size of investment in health sector per year (as bln LCY)
    shock2  = 1500 #51757 + 1500 + 426899 + 8604
    # Set share of health investment financed by the government
    shock2a = 73 #100
	# Set the size of investment in social protection per year (as bln LCY)
    shock3  = 426899 #51757 + 1500 + 426899 + 8604
    # Set share of socia protection investment financed by the government
    shock3a = 3 #100
    # Set the size of investment in education per year (as bln LCY)
    shock4  = 8604 #51757 + 1500 + 426899 + 8604
    # Set share of education spending financed by the government
    shock4a = 91 # 100
    
    # Set the year when the shock is first introduced
    YR1 = 2021
    # Enter number of years over which to spread the investment shock first period
    Y3 = 5

    # Calculatethe overall education spending as % of GDP
    educ_spending = 100*shock4 * Y3 / db1['yen'][_ir.yy(2020)].get_data() 

    # Create the investment periods:
        # 1st investment period
    start_date1          = _ir.yy(YR1)
    end_date1            = _ir.yy(YR1)+Y3-1
    investment_span_1    = start_date1 >> end_date1
        # end: after investment period
    span_end             = end_date1+1 >> end_date

    # Scenario 2_1 tunes:
        # Add shocks
    #db2_1['res_ipr']                = baseline_scen['res_ipr'] + db_asu2_1['ipr_eviews']
    db2_1['res_ipr'][investment_span_1]   = baseline_scen['res_ipr'] + db1['ipr_eviews'] + 0.001*((1-shock1a/100)*shock1 + (1-shock2a/100)*shock2 + (1-shock3a/100)*shock3 + (1-shock4a/100)*shock4)/db1['yen']*db1['yer']/db1['ipr']
    db2_1['res_ipr'][span_end]            = baseline_scen['res_ipr'] + db1['ipr_eviews']
    db2_1['ipr_eviews']                   = 0

    #db2_1['res_techl']                = baseline_scen['res_techl'] + db_asu2_1['techl_eviews']
    db2_1['res_techl'][investment_span_1] = baseline_scen['res_techl'] + db1['techl_eviews'] + 0.1*shock4/db1['yen'] + 0.2* shock1/db1['yen']
    db2_1['res_techl'][span_end]          = baseline_scen['res_techl'] + db1['techl_eviews']
    db2_1['techl_eviews']                 = 0

    #db2_1['res_gini_disp']      = baseline_scen['res_gini_disp'] + db_asu2_1['gini_disp_eviews']
    db2_1['res_gini_disp'][start_date1 >> start_date1 + 25] = baseline_scen['res_gini_disp'] + db1['gini_disp_eviews'] - 0.005*(shock4)/db1['yen']*100
    db2_1['res_gini_disp'][start_date1 + 25 + 1 >> end_date]= baseline_scen['res_gini_disp'] + db1['gini_disp_eviews']
    db2_1['gini_disp_eviews']             = 0

    #db2_1['res_pm25']           = baseline_scen['res_pm25'] + db_asu2_1['pm25_eviews']
    db2_1['res_pm25'][start_date1 >> start_date1 + 9] = baseline_scen['res_pm25'] + db1['pm25_eviews'] - 0.6*shock1/db1['yen']
    db2_1['res_pm25'][start_date1 + 9 + 1 >> end_date]= baseline_scen['res_pm25'] + db1['pm25_eviews']
    db2_1['pm25_eviews']                  = 0

    #db2_1['res_rel_red']        = baseline_scen['res_rel_red'] + db_asu2_1['rel_red_eviews']
    db2_1['res_rel_red'][investment_span_1] = baseline_scen['res_rel_red'] + db1['rel_red_eviews'] +  0.8* (1-(shock3a/100))* shock3/db1['yen']*100
    db2_1['res_rel_red'][span_end]          = baseline_scen['res_rel_red'] + db1['rel_red_eviews']
    db2_1['rel_red_eviews']                 = 0

    #db2_1['rpdi_eviews']        = db_asu2_1['rpdi_eviews'] # no shock in iripie on this variable, overwrite the eviews constant shock
    db2_1['rpdi_eviews']                    = (1-(shock3a/100))* shock3 / db1['hic']
    db2_1['rpdi_eviews'][span_end]          = baseline_scen['rpdi_eviews']


        # Exogenized variables
    db2_1['ogi'][investment_span_1]     = db1['ogi'] + shock1 * (shock1a/100) + shock4 * (shock4a/100)
    db2_1['ogi'][span_end]              = db2_1['ogi']

    db2_1['exph'][investment_span_1]    = db1['exph'] + shock2 * (shock2a/100)
    db2_1['exph'][span_end]             = db2_1['exph']

    db2_1['expsp'][investment_span_1]   = db1['expsp'] + shock3 * (shock3a/100)
    db2_1['expsp'][span_end]            = db2_1['expsp']

    # calculate eff shock
    db2_1['eff'] = db1['eff'].copy()    
    for i in list(start_date1 >> start_date1 + 9):
        eff_lag         = db2_1['eff'][i-1].get_data()
        eff_base        = db1['eff'][i].get_data()
        eff_base_lag    = db1['eff'][i-1].get_data()
        yen             = db1['yen'][i].get_data()    
        db2_1['eff'][i] = (eff_lag) + (eff_base-eff_base_lag) + 0.01*(100*(shock1/yen)/0.62)

    for i in list(start_date1 + 9 + 1 >> end_date):
        eff_lag         = db2_1['eff'][i-1].get_data()
        eff_base        = db1['eff'][i].get_data()
        eff_base_lag    = db1['eff'][i-1].get_data()
        yen             = db1['yen'][i].get_data()    
        db2_1['eff'][i] = (eff_lag) + (eff_base-eff_base_lag)
 
    # calculate skrat shock
    db2_1['skrat'] = db1['skrat'].copy()
    for i in list(_ir.yy(2023)>>_ir.yy(2023)+Y3-1):
        skrat_lag         = db2_1['skrat'][i-1].get_data()
        skrat_base        = db1['skrat'][i].get_data()
        skrat_base_lag    = db1['skrat'][i-1].get_data()    
        db2_1['skrat'][i] = (skrat_base_lag)*(skrat_base/skrat_base_lag)*(1+(educ_spending/Y3)/100)

    for i in list(_ir.yy(2023)+Y3 >> end_date):
        skrat_lag         = db2_1['skrat'][i-1].get_data()
        skrat_base        = db1['skrat'][i].get_data()
        skrat_base_lag    = db1['skrat'][i-1].get_data()       
        db2_1['skrat'][i] = (skrat_base_lag)*(skrat_base/skrat_base_lag)


    p2 = _ir.PlanSimulate(m, span, )
    p2.swap(span, ("ogi", "res_ogi"), )
    p2.swap(span, ("exph", "res_exph"), ) 
    p2.swap(span, ("expsp", "res_expsp"), ) 
    p2.swap(span, ("eff", "res_eff"), ) 
    #p2.swap(span, ("lrxf", "res_lrxf"), )   # it is here to check how irispie LRXF formula works
    p2.swap(span, ("skrat", "res_skrat"), ) 
    

    s_scen2_1_female, *_ = m.simulate(db2_1, span, method="period", plan=p2, )
    s_scen2_1_female.to_sheet("s_scen2_1_female.csv", )


# Scenario 2_2

if "scenario2_2" in scenarios_to_run:
    # Scenario 2_2 assumptions 
    db_asu2_2 = _ir.Databox.from_sheet(
        "Scenarios_with_female/Scenario_2_2/result_scen2_2_asu.csv",
        name_row_transform=name_row_transform,
        description_row=False,
    )

    # Scenario 2_2 result for comparison 
    db_scen2_2 = _ir.Databox.from_sheet(
        "Scenarios_with_female/Scenario_2_2/result_scen2_2.csv",
        name_row_transform=name_row_transform,
        description_row=False,
    )

    # create the fcast database
    db2_2 = db1.copy()
    #db2_2.update(db_asu2_2) #add the scenario assumpions to the db

    # add baseline shock to the simulation
    res_variable_list = [variable_name for variable_name in baseline_scen.get_names() if variable_name.startswith('res')]
    for variable_name in res_variable_list:
         db2_2[variable_name] = baseline_scen[variable_name]

    #
    # Scenario 2_2 tunes
    #

    # Assumptions to set
    # Set the size of additional education spending per year (as bln LCY)
    shock1  = 159108
    # Set if additional spending is from debt (True) or from reallocation (False)
    shock1a = True	
    # Set the year when the shock is first introduced
    YR1     = 2023
    # Enter number of years over which to spread the education investment shock
    Y3      = 8
    # Calculatethe overall education spending as % of GDP (take 2026 as a base to get roughly and avergae 5% extra spending)
    educ_spending = 100*shock1 * Y3 / db1['yen'][_ir.yy(2026)].get_data() 


    # Create the investment periods:
        # 1st investment period
    start_date1          = _ir.yy(YR1)
    end_date1            = _ir.yy(YR1)+Y3-1
    investment_span_1    = start_date1 >> end_date1
        # end: after investment period
    span_end             = end_date1+1 >> end_date

    # Scenario 2_2 tunes:
        # Add shocks
    #db2_2['res_techl']         = baseline_scen['res_techl'] + db_asu2_2['techl_eviews']
    db2_2['res_techl'][investment_span_1]                     = baseline_scen['res_techl'] + db1['techl_eviews'] + 0.001*shock1/db1['yen']*100
    db2_2['res_techl'][span_end]                              = baseline_scen['res_techl'] + db1['techl_eviews'] 
    db2_2['techl_eviews'][start_date1 >> end_date]            = 0

    #db2_2['res_gini_disp']  = baseline_scen['res_gini_disp'] + db_asu2_2['gini_disp_eviews']
    db2_2['res_gini_disp'][start_date1 >> end_date1 + 1 + 25] = baseline_scen['res_gini_disp'] + db1['gini_disp_eviews'] - 0.006*(shock1)/db1['yen']*100
    db2_2['gini_disp_eviews'][start_date1 >> end_date]        = 0

        # exogenize additional variables
    p3 = _ir.PlanSimulate(m, span, )

       # Exogenize variables
    if shock1a: # extra investment in educ from debt
        db2_2['ogc'][investment_span_1] = db1['ogc'] + shock1
        db2_2['ogc'][span_end]          = db1['ogc']
        p3.swap(start_date1 >> end_date, ("ogc", "res_ogc"), ) 
    else: # extra investment in educ from reallocation of other investment
        db2_2['ogc'][investment_span_1] = db1['ogc'] + shock1
        db2_2['ogc'][span_end]          = db1['ogc']
        db2_2['ogi'][investment_span_1] = db1['ogi'] - shock1
        db2_2['ogi'][span_end]          = db1['ogi']    
        p3.swap(start_date1 >> end_date, ("ogi", "res_ogi"), )
        p3.swap(start_date1 >> end_date, ("ogc", "res_ogc"), ) 

        # calculate skrat shock
    db2_2['skrat'] = db1['skrat'].copy()
    for i in list(_ir.yy(2023)>>_ir.yy(2023)+Y3-1):
        skrat_lag         = db2_2['skrat'][i-1].get_data()
        skrat_base        = db1['skrat'][i].get_data()
        skrat_base_lag    = db1['skrat'][i-1].get_data() 
        db2_2['skrat'][i] = (skrat_lag)*(skrat_base/skrat_base_lag)*(1+(educ_spending/Y3)/100)

    for i in list(_ir.yy(2023)+Y3 >> end_date):
        skrat_lag         = db2_2['skrat'][i-1].get_data()
        skrat_base        = db1['skrat'][i].get_data()
        skrat_base_lag    = db1['skrat'][i-1].get_data()    
        db2_2['skrat'][i] = (skrat_lag)*(skrat_base/skrat_base_lag)
    
    #p3.swap(span, ("lrxf", "res_lrxf"), )   # it is here to check how irispie LRXF formula works
    p3.swap(span, ("skrat", "res_skrat"), ) 
  
    s_scen2_2_female, *_ = m.simulate(db2_2, span, method="period", plan=p3, )
    s_scen2_2_female.to_sheet("s_scen2_2_female.csv", )


# Scenario 3

if "scenario3" in scenarios_to_run:
    # Scenario 3 assumptions 
    db_asu3 = _ir.Databox.from_sheet(
        "Scenarios_with_female/Scenario_3/result_scen3_asu.csv",
        name_row_transform=name_row_transform,
        description_row=False,
    )

    # Scenario 3 result for comparison 
    db_scen3 = _ir.Databox.from_sheet(
        "Scenarios_with_female/Scenario_3/result_scen3.csv",
        name_row_transform=name_row_transform,
        description_row=False,
    )

    # create the fcast database
    db3 = db1.copy()
    db3.update(db_asu3) #add the scenario assumpions to the db

    # add baseline shock to the simulation
    res_variable_list = [variable_name for variable_name in baseline_scen.get_names() if variable_name.startswith('res')]
    for variable_name in res_variable_list:
         db3[variable_name] = baseline_scen[variable_name]

    #
    # Scenario 3 tunes
    #

    # Assumptions to set
    # Set the level of carbon subsidies (US$ per tonne CO2) in 2021
    shock0 = 13.9
    # Set the level of carbon tax (US$ per tonne CO2) in 2022
    shock1 = 12	
    # Set the level of carbon tax (US$ per tonne CO2) in 2023
    shock2 = 25
    # Set the level of carbon tax (US$ per tonne CO2) in 2040
    shock3 = 90

    # Set the share of the extra carbon tax income to be used as compensation payment on social protection (in % of carbon tax income)
    shock4 = 0
    # Set the share of the extra carbon tax income to be used as compensation payment on health protection (in % of carbon tax income)
    shock5 = 0
    # Set the share of the extra carbon tax income to be used for enviromental protection (in % of carbon tax income)
    shock6 = 0
    # Set the share of the extra carbon tax income to be used for energy efficiency (in % of carbon tax income)
    shock7 = 0
 
    # Set the year when the shocks are introduced
    YR1 = 2023
    # Enter number of years over when carbon tax is implemented
    Y1  = 17
    # Enter number of years over when carbon subsidy is eased
    Y2  = 2

    # Create the investment periods:
        # 1st investment period
    start_date1          = _ir.yy(2022)
    end_date1            = _ir.yy(YR1)+Y1-1
    tax_span             = start_date1 >> end_date #tax is collected
    span_end             = end_date1+1 >> end_date #after final tax rate is in place

    # Scenario 3 shocks:
        # Add shocks
 
        # Exogenize additional variables
    # generate the carbon tax rate series
    db3['gcarbr'][_ir.yy(2021)] = - shock0
    db3['gcarbr'][_ir.yy(2022)] = db3['gcarbr'][_ir.yy(2021)].get_data() + shock0/Y2 + shock1 
    db3['gcarbr'][_ir.yy(2023)] = db3['gcarbr'][_ir.yy(2022)].get_data() + shock0/Y2 + (shock2-shock1) 
    for i in list(_ir.yy(2024) >> end_date1):
        db3['gcarbr'][i] = db3['gcarbr'][i-1].get_data() + (shock3-shock2)/Y1
    db3['gcarbr'][span_end] = shock3
	# generate tax revenue spending shocks
    db3['sharesp'][tax_span]	= shock4/100
    db3['shareh'][tax_span]	    = shock5/100
    db3['sharee'][tax_span]	    = shock6/100
    db3['sharex'][tax_span] 	= shock7/100

    p4 = _ir.PlanSimulate(m, span, )
    p4.swap(span, ("gcarbr", "res_gcarbr"), )
    p4.swap(span, ("sharee", "res_sharee"), ) 
    p4.swap(span, ("sharesp", "res_sharesp"), ) 
    p4.swap(span, ("shareh", "res_shareh"), ) 
    p4.swap(span, ("sharex", "res_sharex"), ) 
    #p4.swap(span, ("lrxf", "res_lrxf"), )   # it is here to check how irispie LRXF formula works
  

    s_scen3_female, *_ = m.simulate(db3, span, method="period", plan=p4, )
    s_scen3_female.to_sheet("s_scen3_female.csv", )

# Scenario 4

if "scenario4" in scenarios_to_run:
    # Scenario 4 assumptions 
    db_asu4 = _ir.Databox.from_sheet(
        "Scenarios_with_female/Scenario_4/result_scen4_asu.csv",
        name_row_transform=name_row_transform,
        description_row=False,
    )

    # Scenario 4 result for comparison 
    db_scen4 = _ir.Databox.from_sheet(
        "Scenarios_with_female/Scenario_4/result_scen4.csv",
        name_row_transform=name_row_transform,
        description_row=False,
    )

    # create the fcast database
    db4 = db1.copy()
    # db4.update(db_asu4) #add the scenario assumpions to the db, not needed if you set up the tunes below

    # add baseline shock to the simulation
    res_variable_list = [variable_name for variable_name in baseline_scen.get_names() if variable_name.startswith('res')]
    for variable_name in res_variable_list:
         db4[variable_name] = baseline_scen[variable_name]

    #
    # Scenario 4 tunes
    #

    # Assumptions to set:
    # Set the size of investment in ICT per year between 2021-2025 (as bln LCY)
    shock1  = 20890
	# Set share of ICT investment financed by the government between 2021-2025 (%)"
    shock1a = 7
    # Set the size of investment in ICT per year between 2026-2030 (as bln LCY)
    shock2  = 32450
	# Set share of ICT investment financed by the government between 2026-2030 (%)"
    shock2a = 3
    # Set the year when the shock is first introduced
    YR1 = 2021
    # Enter number of years over which to spread the investment shock first period
    Y3  = 5
    # Enter number of years over which to spread the investment shock second period
    Y4  = 5

    # Create the investment periods:
        # 1st investment period
    start_date1          = _ir.yy(YR1)
    end_date1            = _ir.yy(YR1)+Y3-1
    investment_span_1    = start_date1 >> end_date1
        # 2nd investment period
    start_date2          = _ir.yy(YR1)+Y3
    end_date2            = _ir.yy(YR1)+Y3+Y4-1
    investment_span_2    = start_date2 >> end_date2
        # end: after investment period
    span_end             = end_date2+1 >> end_date

    # Scenario 4 tunes:
        # Add shocks
        # db4['res_ipr']               = baseline_scen['res_ipr'] + db_asu4['ipr_eviews']
    db4['res_ipr'][investment_span_1] = baseline_scen['res_ipr'] + db1['ipr_eviews'] + 0.2*((1-shock1a/100)*shock1)/db1['yen']*db1['yer']/db1['ipr']
    db4['res_ipr'][investment_span_2] = baseline_scen['res_ipr'] + db1['ipr_eviews'] + 0.2*((1-shock2a/100)*shock2)/db1['yen']*db1['yer']/db1['ipr']
    db4['res_ipr'][span_end]          = baseline_scen['res_ipr'] + db1['ipr_eviews']
    db4['ipr_eviews']                 = 0

        #db4['res_techl']                = baseline_scen['res_techl'] + db_asu4['techl_eviews']
    db4['res_techl'][investment_span_1]  = baseline_scen['res_techl'] + db1['techl_eviews'] + 0.0022*shock1/db1['yen']*100
    db4['res_techl'][investment_span_2]  = baseline_scen['res_techl'] + db1['techl_eviews'] + 0.0022*shock1/db1['yen']*100
    db4['res_techl'][span_end]           = baseline_scen['res_techl'] + db1['techl_eviews']
    db4['techl_eviews']                  = 0

        #db4['res_finc']                = baseline_scen['res_finc'] + db_asu4['finc_eviews']
    db4['res_finc'][investment_span_1]  = baseline_scen['res_finc'] + db1['finc_eviews'] + 0.4*shock1/db1['yen']*100
    db4['res_finc'][investment_span_2]  = baseline_scen['res_finc'] + db1['finc_eviews'] + 0.4*shock2/db1['yen']*100
    db4['res_finc'][span_end]           = baseline_scen['res_finc']  + db1['finc_eviews']
    db4['finc_eviews']                  = 0
 
        # Exogenize variables
    db4['ogi'][investment_span_1] = db1['ogi'] + shock1 * shock1a/100
    db4['ogi'][investment_span_2] = db1['ogi'] + shock2 * shock2a/100
    db4['ogi'][span_end]          = db1['ogi']
    db4['rel_red']                = db1['rel_red']

    p4 = _ir.PlanSimulate(m, span, )
    p4.swap(span, ("ogi", "res_ogi"), )
    p4.swap(span, ("rel_red", "res_rel_red"), )  
    #p4.swap(span, ("lrxf", "res_lrxf"), )  # it is here to check how irispie LRXF formula works

    s_scen4_female, *_ = m.simulate(db4, span, method="period", plan=p4, )
    s_scen4_female.to_sheet("s_scen4_female.csv", )

#
# Compare scenarios
#

if "compare" in scenarios_to_run:

    scenario  = s_scen3_female # replace me with the scenario
    reference = db_scen3 # replace me with the reference databox
    tolerance = 0.1 # set up the difference you allow in % (0.1 means 0.1%)
    cmp_year  = _ir.yy(2050) # set up the year when you want to compare the scenarios

    tmp = {}
    variable_list = reference.get_names()

    discrep_db = {
        name: (scenario[name] / reference[name]) * 100 - 100
        for name in scenario.keys()
        if name in reference.keys()
    }

    messages = [
        f'Variable {name}: {discrep_db[name](cmp_year)} (value > {tolerance} in {cmp_year})'
        for name in discrep_db.keys()
        if abs(discrep_db[name](cmp_year)) > tolerance
    ]

    if messages:
        print("\n".join(messages))
    else:
        print("No discrepancies found")

