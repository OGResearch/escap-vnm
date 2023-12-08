# Scenario 1_2 runner: Carbon Tax scenario


import irispie as ir
import os


OUTPUT_FILE_NAME = os.path.join(
    "scenario_data_files", "scenario_1_2.csv",
)


def run(model, input_db, sim_span, _, baseline_db, ):

    # Import the raw database and residuals from the baseline scenario
    db = input_db.copy()
    res_names = (n for n in model.get_names() if n.startswith("res_"))
    for n in res_names:
         db[n] = baseline_db[n]

    #
    # Scenario 3 tunes
    #
    
    start_sim = sim_span.start_date
    end_sim = sim_span.end_date

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
    db['gcarbr'][ir.yy(2021)] = - shock0
 
    db['gcarbr'][ir.yy(2022)] = \
        db['gcarbr'](ir.yy(2021)) + shock0/Y2 + shock1
    
    db['gcarbr'][ir.yy(2023)] = \
        db['gcarbr'](ir.yy(2022)) + shock0/Y2 + (shock2-shock1)
    
    for i in list(ir.yy(2024) >> end_date1):
        db['gcarbr'][i] = db['gcarbr'](i-1) + (shock3-shock2)/Y1
   
    db['gcarbr'][span_end] = shock3
  
    # generate tax revenue spending shocks
    db['sharesp'][tax_span]    = shock4/100 
    db['shareh'][tax_span]     = shock5/100
    db['sharee'][tax_span]     = shock6/100
    db['sharex'][tax_span]     = shock7/100

    plan = ir.PlanSimulate(model, sim_span, )
    plan.swap(sim_span, ("gcarbr", "res_gcarbr"), )
    plan.swap(sim_span, ("sharee", "res_sharee"), )
    plan.swap(sim_span, ("sharesp", "res_sharesp"), )
    plan.swap(sim_span, ("shareh", "res_shareh"), )
    plan.swap(sim_span, ("sharex", "res_sharex"), )
    #plan.swap(sim_span, ("lrxf", "res_lrxf"), )   # it is here to check how irispie LRXF formula works


    sim_db, *_ = model.simulate(db, sim_span, method="period", plan=plan, )

    sim_db.to_sheet(
        OUTPUT_FILE_NAME,
        description_row=False,
    )

    return sim_db

