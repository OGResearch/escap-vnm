# Master file for running ESCAP scenarios

import irispie as ir

import sys

import scenario_baseline
import scenario_1_1
import scenario_1_2
import scenario_2_1
import scenario_2_2
import scenario_3

import utils
import chartpacks


ir.min_irispie_version_required("0.28.0", )


# Setup which scenarios to run
scenarios_to_run = (
    "baseline",
    "scenario_1_1",
    "scenario_1_2",
    "scenario_2_1",
    "scenario_2_2",
    "scenario_3",
)

show_charts = True
# show_charts = False


#
# Set up dates
#

start_sim = ir.yy(2021)
end_hist = start_sim - 1
end_sim = ir.yy(2050)
end_short_tune = ir.yy(2026)
sim_span = start_sim >> end_sim
short_tune_span = start_sim >> end_short_tune

chart_span = start_sim - 5 >> end_sim
highlight_span = chart_span.start_date >> start_sim - 1


#
# Read the basic chartpack
#

basic_chartpack = chartpacks.basic_chartpack
basic_chartpack.span = chart_span
basic_chartpack.highlight = highlight_span
basic_chartpack.show_charts = show_charts


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
# Create model object
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


#==============================================================================
# Baseline
#==============================================================================


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


#==============================================================================
# Scenario 1_1: Renewable energy investment scenario
#==============================================================================


if "scenario_1_1" in scenarios_to_run:

    sim_db_1_1 = scenario_1_1.run(
        model, input_db,
        sim_span, short_tune_span, sim_db_baseline,
    )

    chart_db = sim_db_1_1.copy()
    chart_db.merge(sim_db_baseline,  )

    ch = basic_chartpack.copy()
    ch.format_figure_titles(SCENARIO_NAME=scenario_1_1.SCENARIO_NAME, )
    ch.plot(chart_db, )


#===============================================================================
# Scenario 1_2: Carbon Tax scenario
#===============================================================================


if "scenario_1_2" in scenarios_to_run:

    sim_db_1_2 = scenario_1_2.run(
        model, input_db,
        sim_span, short_tune_span, sim_db_baseline,
    )

    chart_db = sim_db_1_2.copy()
    chart_db.merge(sim_db_baseline,  )

    ch = basic_chartpack.copy()
    ch.format_figure_titles(SCENARIO_NAME=scenario_1_2.SCENARIO_NAME, )
    ch.plot(chart_db, )


#===============================================================================
# Scenario 2_1: National Target Program scenario
#===============================================================================


if "scenario_2_1" in scenarios_to_run:

    sim_db_2_1 = scenario_2_1.run(
        model, input_db,
        sim_span, short_tune_span, sim_db_baseline,
    )

    chart_db = sim_db_2_1.copy()
    chart_db.merge(sim_db_baseline,  )

    ch = basic_chartpack.copy()
    ch.format_figure_titles(SCENARIO_NAME=scenario_2_1.SCENARIO_NAME, )
    ch.plot(chart_db, )


#===============================================================================
# Scenario 2_2: Education investment scenario
#===============================================================================


if "scenario_2_2" in scenarios_to_run:

    sim_db_2_2 = scenario_2_2.run(
        model, input_db,
        sim_span, short_tune_span, sim_db_baseline,
    )

    chart_db = sim_db_2_2.copy()
    chart_db.merge(sim_db_baseline,  )

    ch = basic_chartpack.copy()
    ch.format_figure_titles(SCENARIO_NAME=scenario_2_2.SCENARIO_NAME, )
    ch.plot(chart_db, )


#===============================================================================
# Scenario 3: ICT investment scenario
#===============================================================================


if "scenario_3" in scenarios_to_run:

    sim_db_3 = scenario_3.run(
        model, input_db,
        sim_span, short_tune_span, sim_db_baseline,
    )

    chart_db = sim_db_3.copy()
    chart_db.merge(sim_db_baseline,  )

    ch = basic_chartpack.copy()
    ch.format_figure_titles(SCENARIO_NAME=scenario_3.SCENARIO_NAME, )
    ch.plot(chart_db, )


