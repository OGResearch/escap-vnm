# Master file for running ESCAP scenarios

import irispie as ir

import utils
import sys

import scenario_baseline
import scenario_1_1
import scenario_1_2
import scenario_2_1
import scenario_2_2
import scenario_3


ir.min_irispie_version_required("0.25.0", )


# Setup which scenarios to run
scenarios_to_run = (
    "baseline",
    #"scenario_1_1",
    "scenario_1_2",
    #"scenario_2_1",
    #"scenario_2_2",
    #"scenario_3",
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
# Scenario 1_1: Renewable energy investment scenario
#

if "scenario_1_1" in scenarios_to_run:

    sim_db_1_1 = scenario_1_1.run(
        model, input_db,
        sim_span, short_tune_span, sim_db_baseline,
    )

#
# Scenario 1_2: Carbon Tax scenario
#

if "scenario_1_2" in scenarios_to_run:

    sim_db_1_2 = scenario_1_2.run(
        model, input_db,
        sim_span, short_tune_span, sim_db_baseline,
    )

#
# Scenario 2_1: National Target Program scenario
#

if "scenario_2_1" in scenarios_to_run:

    sim_db_2_1 = scenario_2_1.run(
        model, input_db,
        sim_span, short_tune_span, sim_db_baseline,
    )

#
# Scenario 2_2: Education investment scenario
#

if "scenario_2_2" in scenarios_to_run:

    sim_db_2_2 = scenario_2_2.run(
        model, input_db,
        sim_span, short_tune_span, sim_db_baseline,
    )


#
# Scenario 3: ICT investment scenario
#

if "scenario_3" in scenarios_to_run:

    sim_db_3 = scenario_3.run(
        model, input_db,
        sim_span, short_tune_span, sim_db_baseline,
    )
    

sys.exit()


#
# Compare scenarios
#

if "compare" in scenarios_to_run:

    scenario  = sim_db_3 # replace me with the scenario
    reference = sim_db_baseline # replace me with the reference databox
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

