# Scenario 2_1 runner: National target program scenario


import irispie as ir
import os


SCENARIO_NAME = "Scenario 2_1 National target program"


OUTPUT_FILE_NAME = os.path.join(
    "scenario_data_files", "scenario_2_1.csv",
)


def run(model, input_db, sim_span, _, baseline_db, ):
    
    # Import the raw database and residuals from the baseline scenario
    db = input_db.copy()
    res_names = (n for n in model.get_names() if n.startswith("res_"))
    for n in res_names:
         db[n] = baseline_db[n].copy()

    #
    # Scenario 2_1 tunes
    #
    
    start_sim = sim_span.start_date
    end_sim = sim_span.end_date


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
    # YR1 = 2021

    # Enter number of years over which to spread the investment shock first period
    Y3 = 5

    # Calculatethe overall education spending as % of GDP
    educ_spending = 100*shock4 * Y3 / db['yen'][ir.yy(2020)].get_data()

    # Create the investment periods:
        # 1st investment period
    start_date1          = start_sim #ir.yy(YR1)
    end_date1            = start_sim + Y3 - 1 #ir.yy(YR1)+Y3-1
    investment_span_1    = start_date1 >> end_date1
        # end: after investment period
    span_end             = end_date1+1 >> end_sim

    # Scenario 2_1 tunes:
        # Add shocks
    
    # private investment shock
    db['res_ipr'][investment_span_1]   = baseline_db['res_ipr'] + input_db['ipr_eviews'] \
        + 0.001*((1-shock1a/100)*shock1 + (1-shock2a/100)*shock2 + (1-shock3a/100)*shock3 \
        + (1-shock4a/100)*shock4)/input_db['yen']*input_db['yer']/input_db['ipr']
    db['res_ipr'][span_end]            = baseline_db['res_ipr'] + input_db['ipr_eviews']
    
    db['ipr_eviews']                   = 0

    
    # technology shock
    db['res_techl'][investment_span_1] = baseline_db['res_techl'] + input_db['techl_eviews'] \
        + 0.1*shock4/input_db['yen'] + 0.2* shock1/input_db['yen']

    db['res_techl'][span_end]          = baseline_db['res_techl'] + input_db['techl_eviews']

    db['techl_eviews']                 = 0

    
    # inequality shock
    db['res_gini_disp'][start_date1 >> start_date1 + 25] = baseline_db['res_gini_disp'] + input_db['gini_disp_eviews'] - 0.005*(shock4)/input_db['yen']*100
   
    db['res_gini_disp'][start_date1 + 25 + 1 >> end_sim]= baseline_db['res_gini_disp'] + input_db['gini_disp_eviews']
    
    db['gini_disp_eviews']             = 0

    
    # pollution shock
    db['res_pm25'][start_date1 >> start_date1 + 9] = baseline_db['res_pm25'] + input_db['pm25_eviews'] \
        - 0.6*shock1/input_db['yen']
    
    db['res_pm25'][start_date1 + 9 + 1 >> end_sim]= baseline_db['res_pm25'] + input_db['pm25_eviews']
    
    db['pm25_eviews']                  = 0

    
    # redistribution shock
    db['res_rel_red'][investment_span_1] = baseline_db['res_rel_red'] + input_db['rel_red_eviews'] \
        +  0.8* (1-(shock3a/100))* shock3/input_db['yen']*100
    
    db['res_rel_red'][span_end]          = baseline_db['res_rel_red'] + input_db['rel_red_eviews']
    
    db['rel_red_eviews']                 = 0

    # no shock in iripie on this variable, overwrite the eviews constant shock
    db['rpdi_eviews']                    = (1-(shock3a/100))* shock3 / input_db['hic']
    db['rpdi_eviews'][span_end]          = baseline_db['rpdi_eviews']


        # Exogenized variables
    db['ogi'][investment_span_1]     = input_db['ogi'] + shock1 * (shock1a/100) + shock4 * (shock4a/100)
    db['ogi'][span_end]              = input_db['ogi']

    db['exph'][investment_span_1]    = input_db['exph'] + shock2 * (shock2a/100)
    db['exph'][span_end]             = input_db['exph']

    db['expsp'][investment_span_1]   = input_db['expsp'] + shock3 * (shock3a/100)
    db['expsp'][span_end]            = input_db['expsp']

    # calculate efficiency shock
    db['eff'] = input_db['eff'].copy()
    
    for i in list(start_date1 >> start_date1 + 9):
        eff_lag         = db['eff'](i-1)
        eff_base        = input_db['eff'](i)
        eff_base_lag    = input_db['eff'](i-1)
        yen             = input_db['yen'](i)
        db['eff'][i] = (eff_lag) + (eff_base-eff_base_lag) + 0.01*(100*(shock1/yen)/0.62)

    for i in list(start_date1 + 9 + 1 >> end_sim):
        eff_lag         = db['eff'](i-1)
        eff_base        = input_db['eff'](i)
        eff_base_lag    = input_db['eff'](i-1)
        yen             = input_db['yen'](i)
        db['eff'][i] = (eff_lag) + (eff_base-eff_base_lag)

    # calculate skrat shock
    db['skrat'] = input_db['skrat'].copy()
    
    for i in list(ir.yy(2023)>>ir.yy(2023)+Y3-1):
        skrat_base        = input_db['skrat'](i)
        skrat_base_lag    = input_db['skrat'](i-1)
        db['skrat'][i] = (skrat_base_lag)*(skrat_base/skrat_base_lag)*(1+(educ_spending/Y3)/100)

    for i in list(ir.yy(2023)+Y3 >> end_sim):
        skrat_base        = input_db['skrat'](i)
        skrat_base_lag    = input_db['skrat'](i-1)
        db['skrat'][i] = (skrat_base_lag)*(skrat_base/skrat_base_lag)


    plan = ir.PlanSimulate(model, sim_span, )
    plan.swap(sim_span, ("ogi", "res_ogi"), )
    plan.swap(sim_span, ("exph", "res_exph"), )
    plan.swap(sim_span, ("expsp", "res_expsp"), )
    plan.swap(sim_span, ("eff", "res_eff"), )
    #plan.swap(sim_span, ("lrxf", "res_lrxf"), )   # it is here to check how irispie LRXF formula works
    plan.swap(sim_span, ("skrat", "res_skrat"), )

    sim_db, *_ = model.simulate(db, sim_span, method="period", plan=plan, )

    sim_db.to_sheet(
        OUTPUT_FILE_NAME,
        description_row=False,
    )

    return sim_db
