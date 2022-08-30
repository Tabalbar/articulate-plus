import itertools
from statsmodels.stats.multicomp import MultiComparison
import scipy.stats as stats
import pickle


class ANOVA:
    @staticmethod
    def get(model_names, model_results):
        names = list(
            itertools.chain(*[
                [model_name] * len(model_results[0]) for model_name in model_names
            ])
        )
        groups = list(model_results)
        metrics = list(itertools.chain(*groups))

        one_way_anova_p_value = stats.f_oneway(*groups)[1]
        tukey = MultiComparison(metrics, names).tukeyhsd()

        return one_way_anova_p_value, tukey

    @staticmethod
    def write_as_csv(model_names, model_results, alpha=0.05, output_file_name='anova_tukey.csv'):
        one_way_anova_p_value, tukey = ANOVA.get(model_names=model_names, model_results=model_results)

        if one_way_anova_p_value > alpha:
            with open(output_file_name, 'w') as f:
                f.write('insignificant one_way_anova_p_value: ' + str(one_way_anova_p_value) + ',' +
                        tukey.summary().as_csv())
        else:
            with open(output_file_name, 'w') as f:
                f.write('significant one_way_anova_p_value: ' + str(one_way_anova_p_value) + ',' +
                        tukey.summary().as_csv())