# Scenario 2_2 runner: Education investment scenario


import irispie as ir
import os


OUTPUT_FILE_NAME = os.path.join(
    "scenario_data_files", "scenario_2_2.csv",
)


def run(model, input_db, sim_span, _, baseline_db, ):

    # Import the raw database and residuals from the baseline scenario
    db = input_db.copy()
    res_names = (n for n in model.get_names() if n.startswith("res_"))
    for n in res_names:
         db[n] = baseline_db[n]


    #
    # Scenario 2_2 tunes
    #
    
    start_sim = sim_span.start_date
    end_sim = sim_span.end_date

    # Assumptions to set
    # Set the size of additional education spending per year (as bln LCY)
    shock1  = 159108
    
    # Set if additional spending is from debt (True) or from reallocation (False)
    shock1a = True  
    
    # Set the year when the shock is first introduced
    YR1     = 2023 # shock is starting later than usual sim period.
    
    # Enter number of years over which to spread the education investment shock
    Y3      = 8
    
    # Calculatethe overall education spending as % of GDP (take 2026 as a base to get roughly and avergae 5% extra spending)
    educ_spending = 100*shock1 * Y3 / input_db['yen'][ir.yy(2026)].get_data()


    # Create the investment periods:
        
        # 1st investment period
    start_date1          = ir.yy(YR1)
    end_date1            = ir.yy(YR1)+Y3-1
    investment_span_1    = start_date1 >> end_date1
       
        # end: after investment period
    span_end             = end_date1+1 >> end_sim

    # Scenario 2_2 tunes:
        # Add shocks
    
    # technology shock
    db['res_techl'][investment_span_1]                     = baseline_db['res_techl'] \
        + input_db['techl_eviews'] + 0.001*shock1/input_db['yen']*100
    
    db['res_techl'][span_end]                              = baseline_db['res_techl'] \
        + input_db['techl_eviews']
   
    db['techl_eviews'][start_date1 >> end_sim]            = 0

    # inequality shock
    db['res_gini_disp'][start_date1 >> end_date1 + 1 + 25] = baseline_db['res_gini_disp'] \
        + input_db['gini_disp_eviews'] - 0.006*(shock1)/input_db['yen']*100
   
    db['gini_disp_eviews'][start_date1 >> end_sim]        = 0

        # Exogenize additional variables
    plan = ir.PlanSimulate(model, sim_span, )
    
    if shock1a: # extra investment in educ from debt
        db['ogc'][investment_span_1] = input_db['ogc'] + shock1
        
        db['ogc'][span_end]          = input_db['ogc']
        
        plan.swap(start_date1 >> end_sim, ("ogc", "res_ogc"), )
    
    else: # extra investment in educ from reallocation of other investment
        db['ogc'][investment_span_1] = input_db['ogc'] + shock1
        
        db['ogc'][span_end]          = input_db['ogc']
        
        db['ogi'][investment_span_1] = input_db['ogi'] - shock1
        
        db['ogi'][span_end]          = input_db['ogi']
        
        plan.swap(start_date1 >> end_sim, ("ogi", "res_ogi"), )
        plan.swap(start_date1 >> end_sim, ("ogc", "res_ogc"), )

        # calculate skrat shock
        
    db['skrat'] = input_db['skrat'].copy()
    
    for i in list(ir.yy(2023)>>ir.yy(2023)+Y3-1):
        skrat_lag         = db['skrat'](i-1)
        skrat_base        = input_db['skrat'](i)       
        skrat_base_lag    = input_db['skrat'](i-1)       
        db['skrat'][i] = (skrat_lag)*(skrat_base/skrat_base_lag)*(1+(educ_spending/Y3)/100)

    for i in list(ir.yy(2023)+Y3 >> end_sim):
        skrat_lag         = db['skrat'](i-1)
        skrat_base        = input_db['skrat'](i)
        skrat_base_lag    = input_db['skrat'](i-1)
        db['skrat'][i] = (skrat_lag)*(skrat_base/skrat_base_lag)

    #plan.swap(sim_span, ("lrxf", "res_lrxf"), )   # it is here to check how irispie LRXF formula works
    plan.swap(sim_span, ("skrat", "res_skrat"), )

    sim_db, *_ = model.simulate(db, sim_span, method="period", plan=plan, )

    sim_db.to_sheet(
        OUTPUT_FILE_NAME,
        description_row=False,
    )

    return sim_db

