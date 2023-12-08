# Baseline scenario runner


import irispie as ir
import os


def run(model, input_db, sim_span, short_tune_span, ):

    db = input_db.copy()

    plan = ir.PlanSimulate(model, sim_span, )

    # Female LFPR block
    plan.swap(sim_span, ("popwaf", "res_popwaf"), ) # should be tuned until 2050
    # plan.swap(sim_span, ("lrxf", "res_lrxf"), ) # exogenized temporarily until FLFPR formula is ready
    plan.swap(sim_span, ("skrat", "res_skrat"), ) # education variable, should be exogenized always

    # GDP items
    plan.swap(short_tune_span, ("gcr", "res_gcr"), )
    plan.swap(short_tune_span, ("pcr", "res_pcr"), )
    #plan.swap(short_tune_span, ("itr", "res_ipr"), )
    plan.swap(short_tune_span, ("ipr", "res_ipr"), )
    plan.swap(short_tune_span, ("igr", "res_igr"), )
    plan.swap(short_tune_span, ("scr", "res_scr"), )
    plan.swap(short_tune_span, ("xtr", "res_xtr"), )
    plan.swap(short_tune_span, ("mtr", "res_mtr"), )
    # Budget expenditure items
    # plan.swap(sim_span, ("exp", "res_ogi"), ) # exp is an identity withouth shock, enrun_genizing one subitem of exp // might want to change this
    plan.swap(short_tune_span, ("expe", "res_expe"), )
    plan.swap(short_tune_span, ("exph", "res_exph"), )
    plan.swap(short_tune_span, ("expsp", "res_expsp"), )
    plan.swap(short_tune_span, ("ogc", "res_ogc"), )
    plan.swap(short_tune_span, ("ogi", "res_ogi"), )
    plan.swap(short_tune_span, ("gip", "res_gip"), )
    # Budget revenue items
    # plan.swap(sim_span, ("exp", "res_ogi"), ) # exp is an identity withouth shock, enrun_genizing one subitem of exp // might want to change this
    plan.swap(short_tune_span, ("tax", "res_taxr"), )
    plan.swap(short_tune_span, ("ctax", "res_ctaxr"), )
    plan.swap(short_tune_span, ("itax", "res_itaxr"), )
    plan.swap(short_tune_span, ("gtrade", "res_gtrader"), )
    #plan.swap(sim_span, ("revg", "res_revg"), ) this one we treat as fully exogenous
    plan.swap(short_tune_span, ("gcom", "res_gcom"), )
    plan.swap(short_tune_span, ("goth", "res_goth"), )

    # Other variables
    plan.swap(sim_span, ("eff", "res_eff"), ) # should be tuned until 2050
    plan.swap(sim_span, ("popt", "res_popt"), ) # should be tuned until 2050
    plan.swap(sim_span, ("popwa", "res_popwa"), ) # should be tuned until 2050
    plan.swap(short_tune_span, ("yed", "res_yed"), )
    plan.swap(short_tune_span, ("yft", "res_yft"), )
    plan.swap(short_tune_span, ("exr", "res_exr"), )
    plan.swap(short_tune_span, ("hic", "res_hic"), )
    plan.swap(short_tune_span, ("gdn", "res_gdn"), )
    plan.swap(short_tune_span, ("glnt", "res_glnt"), )

    # Exogenize these ranrun_m extra baseline variables
    plan.swap(sim_span, ("expeb", "res_expeb"), )
    plan.swap(sim_span, ("exphb", "res_exphb"), )
    plan.swap(sim_span, ("expspb", "res_expspb"), )
    plan.swap(sim_span, ("gcarbb", "res_gcarbb"), )

    sim_db, *_ = model.simulate(db, sim_span, method="period", plan=plan, )

    output_file_name = os.path.join("scenario_data_files", "scenario_baseline.csv", )
    sim_db.to_sheet(output_file_name, )

    return sim_db, output_file_name


