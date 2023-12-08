# Scenario 1_1 runner: Renewable energy investment scenario


import irispie as ir
import os


OUTPUT_FILE_NAME = os.path.join(
    "scenario_data_files", "scenario_1_1.csv",
)


def run(model, input_db, sim_span, _, baseline_db, ):

    # Import the raw database and residuals from the baseline scenario
    db = input_db.copy()
    res_names = (n for n in model.get_names() if n.startswith("res_"))
    for n in res_names:
         db[n] = baseline_db[n]


    #
    # Scenario 1 tunes
    #

    start_sim = sim_span.start_date
    end_sim = sim_span.end_date


    # Set the size of investment in renewables per year until 2030 (bln USD)
    shock1 = 13.5

    # Set the size of investment in renewables per year from 2030 until 2050 (bln USD)"
    shock2 = 23

    # Initial Renewable Energy capacity
    initial_rc = input_db["rc"](start_sim)

    # Set the size of the renewable energy capacity in 2030 (Exojoules)
    shock3 = 1.26

    # Set the size of the renewable energy capacity in 2050 (Exojoules)
    shock4 = 6.5

    # Set share of renewable investment financed by the government
    shock5 = 100

    # Set the year when the shock is first introduced
    #YR1 = 2021

    # Enter number of years over which to spread the investment shock first period
    Y3 = 9

    # Enter number of years over which to spread the investment shock second period
    Y4 = 20

    # Create the investment periods:

    # 1st investment period
    start_date1 = start_sim #ir.yy(YR1)
    end_date1 = start_sim + Y3 #ir.yy(YR1)+Y3
    investment_span_1 = start_date1 >> end_date1

    # 2nd investment period
    start_date2 = start_sim + Y3 + 1
    end_date2 = start_sim + Y3 + Y4
    investment_span_2 = start_date2 >> end_date2

        # end: after investment period - not needed, this investment scenario is running until end_sim

    # Scenario 1 tunes:
        # Add shocks
    
    # private investment shock
    db["res_ipr"][investment_span_1] = \
        baseline_db["res_ipr"] \
        + input_db["ipr_eviews"] \
        + 0.18*((1-shock5/100)*shock1)/input_db["yen_S"]*input_db["yer"]/input_db["ipr"]

    db["res_ipr"][investment_span_2] = \
        baseline_db["res_ipr"] \
        + input_db["ipr_eviews"] \
        + 0.05 * ((1-shock5/100)*shock2) / input_db["yen_S"] * input_db["yer"] / input_db["ipr"]

    db["ipr_eviews"] = 0

    # renewable energy shock
    db["res_rc"][investment_span_1] = \
        baseline_db["res_rc"] + input_db["rc_eviews"] + 0.3*(ir.log(shock3) - ir.log(initial_rc))/Y3

    db["res_rc"][investment_span_2] = \
        baseline_db["res_rc"] + input_db["rc_eviews"] + 1.1*(ir.log(shock4) - ir.log(shock3))/Y4

    db["rc_eviews"] = 0

        # Exogenized variables
    # add extra government investment
    db["ogi"][investment_span_1] = input_db["ogi"] + input_db["exr"] * shock1 * shock5/100

    db["ogi"][investment_span_2] = input_db["ogi"] + input_db["exr"] * shock2 * shock5/100

    # change renewable energy price
    db["pr"] = input_db["pr"].copy()

        # Gross rate of change in pr
    input_db["roc_pr"] = ir.roc(input_db["pr"])

    for t in investment_span_1:
        db["pr"][t] = db["pr"](t-1) * input_db["roc_pr"](t) - 0.2*(shock1 / input_db["yen_S"](t))

    for t in investment_span_2:
        db["pr"][t] = db["pr"](t-1) * input_db["roc_pr"](t) - 0.2*(shock2 / input_db["yen_S"](t))

    plan = ir.PlanSimulate(model, sim_span, )
    plan.swap(sim_span, ("ogi", "res_ogi"), )
    plan.swap(sim_span, ("pr", "res_pr"), )
    # plan.swap(sim_span, ("lrxf", "res_lrxf"), )   # it is here to check how irispie LRXF formula works

    sim_db, *_ = model.simulate(db, sim_span, method="period", plan=plan, )

    sim_db.to_sheet(
        OUTPUT_FILE_NAME,
        description_row=False,
    )

    return sim_db

