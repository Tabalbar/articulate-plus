import numpy as np
import json

file_name='results/dialogue_act_model_evaluation.json'
levels=['top_level','bottom_level','two_level']
with open(file_name, 'r') as f:
    results=json.load(f)

all_experiments=[]
for level in levels:
    experiments=[]
    for model in results.keys():
        if level in model:
            metrics=[metric['F1'] for metric in results[model]]
            experiments.append((model, np.mean(metrics)))
    experiments.sort(reverse=True, key=lambda x: x[1])
    all_experiments.append(experiments)

print(file_name)
for exp in all_experiments:
    for e in exp:
        print(e)

print("\n\n")
file_name='results/text_segmentation_model_evaluation.json'
with open(file_name,'r') as f:
    results = json.load(f)

for metric_name in ['full_misses', 'near_misses', 'pk', 'f1', 'window_diff', 'boundary_matches', 'boundaries']:
    print(metric_name)
    all_experiments=[]
    for model, metrics in results.items():
        totals = [metric[metric_name] for metric in metrics]

        if metric_name in ['pk', 'window_diff', 'f1']:
            all_experiments.append((model, np.mean(totals)))
        else:
            all_experiments.append((model, np.sum(totals)))

    all_experiments.sort(reverse=False, key=lambda x: x[1])
    print(file_name)
    for exp in all_experiments:
        print(exp)

print("\n\n")
file_name='results/referring_expression_extraction_model_evaluation.json'
with open(file_name, 'r') as f:
    results = json.load(f)

all_experiments=[]
for model, metrics in results.items():
    avg_pk = np.mean([metric['F1'] for metric in metrics])
    all_experiments.append((model, avg_pk))

all_experiments.sort(reverse=True, key=lambda x: x[1])
print(file_name)
for exp in all_experiments:
    print(exp)