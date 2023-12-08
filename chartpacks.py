
import irispie as ir


def _pct_diff(x, ):
    return 100*(x[:,0]/x[:,1] - 1)


def _diff(x, ):
    return x[:,0] - x[:,1]


def _diff_pct(x, ):
    return _diff(ir.pct(x, ))


chartpack_transforms = {
    "pct_diff": _pct_diff,
    "diff": _diff,
    "diff_pct": _diff_pct,
}


basic_chartpack = ir.Chartpack(
    transforms=chartpack_transforms,
    tiles=(3, 2),
)

basic_chartpack.add_figure("{SCENARIO_NAME}: Real economic activity", )

basic_chartpack.add_charts(
    "Real GDP, % dev from baseline: yer [pct_diff]",
    "Real investment, % diff from baseline: itr [pct_diff]",
    "Inflation, PP diff from baseline: hic [diff_pct]",
    "Employment, % diff from baseline: lnn [pct_diff]",
    "Real disposable income, % diff from baseline: rpdi [pct_diff]",
)


basic_chartpack.add_figure("{SCENARIO_NAME}: Environmental variables", )

basic_chartpack.add_charts(
    "CO2 emissions, % diff from baseline: co2 [pct_diff]",
    "Pollution (PM2.5), % diff from baseline: pm25 [pct_diff]",
    "Energy efficiency index, % diff from baseline: eff [pct_diff]",
    "Energy consumption, % diff from baseline: ec [pct_diff]",
    "Renewable energy consumption, % diff from baseline: rc [pct_diff]",
    "Coal consumption, % diff from baseline: coalc [pct_diff]",
)


basic_chartpack.add_figure("{SCENARIO_NAME}: Fiscal and social", )

basic_chartpack.add_charts(
    "Fiscal balance (% of GDP), compared to baseline: glnratio",
    "Public debt (% of GDP), compared to baseline: gdnratio",
    "Government expenditure, % diff from baseline: exp [pct_diff]",
    "Government revenue, % diff from baseline: rev [pct_diff]",
    "Gini coefficient, diff from baseline: gini_disp [diff]",
    "Poverty headcount ratio (% of population), diff from baseline: head55 [diff]",
)

