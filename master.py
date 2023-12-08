# Master file for running ESCAP scenarios

import irispie as ir

import utils
import sys

import scenario_baseline
import scenario_1
import scenario_2_1
import scenario_2_2


ir.min_irispie_version_required("0.25.0", )


# Setup which scenarios to run
scenarios_to_run = (
    "baseline",
    #"scenario_1",
    #"scenario_2_1",
    "scenario_2_2",
    #"scenario3",
    #"scenario4",
    "compare",
)



#
# Set up dates
#

start_sim = ir.yy(2021)
end_hist = start_sim - 1
end_sim = ir.yy(2050)
end_short_tune = ir.yy(2026)
sim_span = start_sim >> end_sim
short_tune_span = start_sim >> end_short_tune


#
# Read input databox
#


input_db = ir.Databox.from_sheet(
    "result_baseline_female.csv",
    name_row_transform=utils.rename_input_data,
    description_row=False,
)

db_res = ir.Databox.from_sheet(
    "result_residuals_female.csv",
    name_row_transform=utils.rename_input_data,
    description_row=False,
)

input_db.update(db_res, )


#
# Technical variable for female model
#

input_db['lrxf_switch'] =  ir.Series(dates=ir.yy(2000)>>end_sim, values=0, )



#
# Create model object with user funtions
#

model = ir.Simultaneous.from_file(
    "escap-vnm.model",
    context=utils.function_context,
    deterministic=True,
)

#
# Read in and assign baseline parameters
#

baseline_parameters = utils.read_parameters_from_csv("escap-vnm-parameters.csv", )
model.assign(baseline_parameters, )


#
# Baseline
#

if "baseline" in scenarios_to_run:

    sim_db_baseline = scenario_baseline.run(
        model, input_db,
        sim_span, short_tune_span,
    )

else:

    sim_db_baseline = ir.Databox.from_sheet(
        scenario_baseline.OUTPUT_FILE_NAME,
        description_row=False,
    )

#
# Scenario 1
#

if "scenario_1" in scenarios_to_run:

    sim_db_1 = scenario_1.run(
        model, input_db,
        sim_span, short_tune_span, sim_db_baseline,
    )


#
# Scenario 2_1
#

if "scenario_2_1" in scenarios_to_run:

    sim_db_2_1 = scenario_2_1.run(
        model, input_db,
        sim_span, short_tune_span, sim_db_baseline,
    )

#
# Scenario 2_2
#

if "scenario_2_2" in scenarios_to_run:

    sim_db_2_2 = scenario_2_2.run(
        model, input_db,
        sim_span, short_tune_span, sim_db_baseline,
    )


sys.exit()

# Scenario 2_2

if "scenario2_2" in scenarios_to_run:
    # Scenario 2_2 assumptions
    db_asu2_2 = ir.Databox.from_sheet(
        "Scenarios_with_female/Scenario_2_2/result_scen2_2_asu.csv",
        name_row_transform=utils.rename_input_data,
        description_row=False,
    )

    # Scenario 2_2 result for comparison
    db_scen2_2 = ir.Databox.from_sheet(
        "Scenarios_with_female/Scenario_2_2/result_scen2_2.csv",
        name_row_transform=utils.rename_input_data,
        description_row=False,
    )

    # create the fcast database
    db2_2 = db1.copy()
    #db2_2.update(db_asu2_2) #add the scenario assumpions to the input_db

    # add baseline shock to the simulation
    res_variable_list = [variable_name for variable_name in baseline_db.get_names() if variable_name.startswith('res')]
    for variable_name in res_variable_list:
         db2_2[variable_name] = baseline_db[variable_name]

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
    educ_spending = 100*shock1 * Y3 / db1['yen'][ir.yy(2026)].get_data()


    # Create the investment periods:
        # 1st investment period
    start_date1          = ir.yy(YR1)
    end_date1            = ir.yy(YR1)+Y3-1
    investment_span_1    = start_date1 >> end_date1
        # end: after investment period
    span_end             = end_date1+1 >> end_sim

    # Scenario 2_2 tunes:
        # Add shocks
    #db2_2['res_techl']         = baseline_db['res_techl'] + db_asu2_2['techl_eviews']
    db2_2['res_techl'][investment_span_1]                     = baseline_db['res_techl'] + db1['techl_eviews'] + 0.001*shock1/db1['yen']*100
    db2_2['res_techl'][span_end]                              = baseline_db['res_techl'] + db1['techl_eviews']
    db2_2['techl_eviews'][start_date1 >> end_sim]            = 0

    #db2_2['res_gini_disp']  = baseline_db['res_gini_disp'] + db_asu2_2['gini_disp_eviews']
    db2_2['res_gini_disp'][start_date1 >> end_date1 + 1 + 25] = baseline_db['res_gini_disp'] + db1['gini_disp_eviews'] - 0.006*(shock1)/db1['yen']*100
    db2_2['gini_disp_eviews'][start_date1 >> end_sim]        = 0

        # exogenize additional variables
    p3 = ir.PlanSimulate(model, sim_span, )

       # Exogenize variables
    if shock1a: # extra investment in educ from debt
        db2_2['ogc'][investment_span_1] = db1['ogc'] + shock1
        db2_2['ogc'][span_end]          = db1['ogc']
        p3.swap(start_date1 >> end_sim, ("ogc", "res_ogc"), )
    else: # extra investment in educ from reallocation of other investment
        db2_2['ogc'][investment_span_1] = db1['ogc'] + shock1
        db2_2['ogc'][span_end]          = db1['ogc']
        db2_2['ogi'][investment_span_1] = db1['ogi'] - shock1
        db2_2['ogi'][span_end]          = db1['ogi']
        p3.swap(start_date1 >> end_sim, ("ogi", "res_ogi"), )
        p3.swap(start_date1 >> end_sim, ("ogc", "res_ogc"), )

        # calculate skrat shock
    db2_2['skrat'] = db1['skrat'].copy()
    for i in list(ir.yy(2023)>>ir.yy(2023)+Y3-1):
        skrat_lag         = db2_2['skrat'][i-1].get_data()
        skrat_base        = db1['skrat'][i].get_data()
        skrat_base_lag    = db1['skrat'][i-1].get_data()
        db2_2['skrat'][i] = (skrat_lag)*(skrat_base/skrat_base_lag)*(1+(educ_spending/Y3)/100)

    for i in list(ir.yy(2023)+Y3 >> end_sim):
        skrat_lag         = db2_2['skrat'][i-1].get_data()
        skrat_base        = db1['skrat'][i].get_data()
        skrat_base_lag    = db1['skrat'][i-1].get_data()
        db2_2['skrat'][i] = (skrat_lag)*(skrat_base/skrat_base_lag)

    #p3.swap(sim_span, ("lrxf", "res_lrxf"), )   # it is here to check how irispie LRXF formula works
    p3.swap(sim_span, ("skrat", "res_skrat"), )

    s_scen2_2_female, *_ = model.simulate(db2_2, sim_span, method="period", plan=p3, )
    s_scen2_2_female.to_sheet("s_scen2_2_female.csv", )


# Scenario 3

if "scenario3" in scenarios_to_run:
    # Scenario 3 assumptions
    db_asu3 = ir.Databox.from_sheet(
        "Scenarios_with_female/Scenario_3/result_scen3_asu.csv",
        name_row_transform=utils.rename_input_data,
        description_row=False,
    )

    # Scenario 3 result for comparison
    db_scen3 = ir.Databox.from_sheet(
        "Scenarios_with_female/Scenario_3/result_scen3.csv",
        name_row_transform=utils.rename_input_data,
        description_row=False,
    )

    # create the fcast database
    db3 = db1.copy()
    db3.update(db_asu3) #add the scenario assumpions to the input_db

    # add baseline shock to the simulation
    res_variable_list = [variable_name for variable_name in baseline_db.get_names() if variable_name.startswith('res')]
    for variable_name in res_variable_list:
         db3[variable_name] = baseline_db[variable_name]

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
    start_date1          = ir.yy(2022)
    end_date1            = ir.yy(YR1)+Y1-1
    tax_span             = start_date1 >> end_sim #tax is collected
    span_end             = end_date1+1 >> end_sim #after final tax rate is in place

    # Scenario 3 shocks:
        # Add shocks

        # Exogenize additional variables
    # generate the carbon tax rate series
    db3['gcarbr'][ir.yy(2021)] = - shock0
    db3['gcarbr'][ir.yy(2022)] = db3['gcarbr'][ir.yy(2021)].get_data() + shock0/Y2 + shock1
    db3['gcarbr'][ir.yy(2023)] = db3['gcarbr'][ir.yy(2022)].get_data() + shock0/Y2 + (shock2-shock1)
    for i in list(ir.yy(2024) >> end_date1):
        db3['gcarbr'][i] = db3['gcarbr'][i-1].get_data() + (shock3-shock2)/Y1
    db3['gcarbr'][span_end] = shock3
    # generate tax revenue spending shocks
    db3['sharesp'][tax_span]    = shock4/100
    db3['shareh'][tax_span]     = shock5/100
    db3['sharee'][tax_span]     = shock6/100
    db3['sharex'][tax_span]     = shock7/100

    p4 = ir.PlanSimulate(model, sim_span, )
    p4.swap(sim_span, ("gcarbr", "res_gcarbr"), )
    p4.swap(sim_span, ("sharee", "res_sharee"), )
    p4.swap(sim_span, ("sharesp", "res_sharesp"), )
    p4.swap(sim_span, ("shareh", "res_shareh"), )
    p4.swap(sim_span, ("sharex", "res_sharex"), )
    #p4.swap(sim_span, ("lrxf", "res_lrxf"), )   # it is here to check how irispie LRXF formula works


    s_scen3_female, *_ = model.simulate(db3, sim_span, method="period", plan=p4, )
    s_scen3_female.to_sheet("s_scen3_female.csv", )

# Scenario 4

if "scenario4" in scenarios_to_run:
    # Scenario 4 assumptions
    db_asu4 = ir.Databox.from_sheet(
        "Scenarios_with_female/Scenario_4/result_scen4_asu.csv",
        name_row_transform=utils.rename_input_data,
        description_row=False,
    )

    # Scenario 4 result for comparison
    db_scen4 = ir.Databox.from_sheet(
        "Scenarios_with_female/Scenario_4/result_scen4.csv",
        name_row_transform=utils.rename_input_data,
        description_row=False,
    )

    # create the fcast database
    db4 = db1.copy()
    # db4.update(db_asu4) #add the scenario assumpions to the input_db, not needed if you set up the tunes below

    # add baseline shock to the simulation
    res_variable_list = [variable_name for variable_name in baseline_db.get_names() if variable_name.startswith('res')]
    for variable_name in res_variable_list:
         db4[variable_name] = baseline_db[variable_name]

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
    start_date1          = ir.yy(YR1)
    end_date1            = ir.yy(YR1)+Y3-1
    investment_span_1    = start_date1 >> end_date1
        # 2nd investment period
    start_date2          = ir.yy(YR1)+Y3
    end_date2            = ir.yy(YR1)+Y3+Y4-1
    investment_span_2    = start_date2 >> end_date2
        # end: after investment period
    span_end             = end_date2+1 >> end_sim

    # Scenario 4 tunes:
        # Add shocks
        # db4['res_ipr']               = baseline_db['res_ipr'] + db_asu4['ipr_eviews']
    db4['res_ipr'][investment_span_1] = baseline_db['res_ipr'] + db1['ipr_eviews'] + 0.2*((1-shock1a/100)*shock1)/db1['yen']*db1['yer']/db1['ipr']
    db4['res_ipr'][investment_span_2] = baseline_db['res_ipr'] + db1['ipr_eviews'] + 0.2*((1-shock2a/100)*shock2)/db1['yen']*db1['yer']/db1['ipr']
    db4['res_ipr'][span_end]          = baseline_db['res_ipr'] + db1['ipr_eviews']
    db4['ipr_eviews']                 = 0

        #db4['res_techl']                = baseline_db['res_techl'] + db_asu4['techl_eviews']
    db4['res_techl'][investment_span_1]  = baseline_db['res_techl'] + db1['techl_eviews'] + 0.0022*shock1/db1['yen']*100
    db4['res_techl'][investment_span_2]  = baseline_db['res_techl'] + db1['techl_eviews'] + 0.0022*shock1/db1['yen']*100
    db4['res_techl'][span_end]           = baseline_db['res_techl'] + db1['techl_eviews']
    db4['techl_eviews']                  = 0

        #db4['res_finc']                = baseline_db['res_finc'] + db_asu4['finc_eviews']
    db4['res_finc'][investment_span_1]  = baseline_db['res_finc'] + db1['finc_eviews'] + 0.4*shock1/db1['yen']*100
    db4['res_finc'][investment_span_2]  = baseline_db['res_finc'] + db1['finc_eviews'] + 0.4*shock2/db1['yen']*100
    db4['res_finc'][span_end]           = baseline_db['res_finc']  + db1['finc_eviews']
    db4['finc_eviews']                  = 0

        # Exogenize variables
    db4['ogi'][investment_span_1] = db1['ogi'] + shock1 * shock1a/100
    db4['ogi'][investment_span_2] = db1['ogi'] + shock2 * shock2a/100
    db4['ogi'][span_end]          = db1['ogi']
    db4['rel_red']                = db1['rel_red']

    p4 = ir.PlanSimulate(model, sim_span, )
    p4.swap(sim_span, ("ogi", "res_ogi"), )
    p4.swap(sim_span, ("rel_red", "res_rel_red"), )
    #p4.swap(sim_span, ("lrxf", "res_lrxf"), )  # it is here to check how irispie LRXF formula works

    s_scen4_female, *_ = model.simulate(db4, sim_span, method="period", plan=p4, )
    s_scen4_female.to_sheet("s_scen4_female.csv", )

#
# Compare scenarios
#

if "compare" in scenarios_to_run:

    scenario  = s_scen3_female # replace me with the scenario
    reference = db_scen3 # replace me with the reference databox
    tolerance = 0.1 # set up the difference you allow in % (0.1 means 0.1%)
    cmp_year  = ir.yy(2050) # set up the year when you want to compare the scenarios

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

