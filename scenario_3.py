# Scenario 3 runner: ICT investment scenario


import irispie as ir
import os


SCENARIO_NAME = "Scenario 3 ICT investment"


OUTPUT_FILE_NAME = os.path.join(
    "scenario_data_files", "scenario_3.csv",
)


def run(model, input_db, sim_span, _, baseline_db, ):

    # Import the raw database and residuals from the baseline scenario
    db = input_db.copy()
    res_names = (n for n in model.get_names() if n.startswith("res_"))
    for n in res_names:
         db[n] = baseline_db[n]


    #
    # Scenario 4 tunes
    #

    start_sim = sim_span.start_date
    end_sim = sim_span.end_date

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

    # private investment shock
    db['res_ipr'][investment_span_1] = baseline_db['res_ipr'] + input_db['ipr_eviews'] + 0.2*((1-shock1a/100)*shock1)/input_db['yen']*input_db['yer']/input_db['ipr']
    db['res_ipr'][investment_span_2] = baseline_db['res_ipr'] + input_db['ipr_eviews'] + 0.2*((1-shock2a/100)*shock2)/input_db['yen']*input_db['yer']/input_db['ipr']
    db['res_ipr'][span_end]          = baseline_db['res_ipr'] + input_db['ipr_eviews']
    db['ipr_eviews']                 = 0

    # technolgy shock
    db['res_techl'][investment_span_1]  = baseline_db['res_techl'] + input_db['techl_eviews'] + 0.0022*shock1/input_db['yen']*100
    db['res_techl'][investment_span_2]  = baseline_db['res_techl'] + input_db['techl_eviews'] + 0.0022*shock1/input_db['yen']*100
    db['res_techl'][span_end]           = baseline_db['res_techl'] + input_db['techl_eviews']
    db['techl_eviews']                  = 0

    # financial inclusion shock
    db['res_finc'][investment_span_1]  = baseline_db['res_finc'] + input_db['finc_eviews'] + 0.4*shock1/input_db['yen']*100
    db['res_finc'][investment_span_2]  = baseline_db['res_finc'] + input_db['finc_eviews'] + 0.4*shock2/input_db['yen']*100
    db['res_finc'][span_end]           = baseline_db['res_finc'] + input_db['finc_eviews']
    db['finc_eviews']                  = 0

        # Exogenize variables

    # add government investement
    db['ogi'][investment_span_1] = input_db['ogi'] + shock1 * shock1a/100
    db['ogi'][investment_span_2] = input_db['ogi'] + shock2 * shock2a/100
    db['ogi'][span_end]          = input_db['ogi']
    # technical tune: overwrite relative redistribution
    db['rel_red']                = input_db['rel_red']


    plan = ir.PlanSimulate(model, sim_span, )
    plan.swap(sim_span, ("ogi", "res_ogi"), )
    plan.swap(sim_span, ("rel_red", "res_rel_red"), )
    # plan.swap(sim_span, ("lrxf", "res_lrxf"), )   # it is here to check how irispie LRXF formula works

    sim_db, *_ = model.simulate(db, sim_span, method="period", plan=plan, )

    sim_db.to_sheet(
        OUTPUT_FILE_NAME,
        description_row=False,
    )

    return sim_db

