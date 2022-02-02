import pandas as pd
rater1=pd.read_csv(\
	'subject8_referringexpressions_Abhinav.csv',sep='\t',\
		skiprows=1,header=None,\
			names=['referencetype','referenceid','referencevistargets'])
rater1_targets=rater1['referencevistargets']

rater2=pd.read_csv(\
	'subject8_referringexpressions_Jillian.csv',sep='\t',\
		skiprows=1,header=None,\
			names=['referencetype','referenceid','referencevistargets'])
rater2_targets=rater2['referencevistargets']

print("Rater 1",list(rater1_targets))
print("Rater 2",list(rater2_targets))

from sklearn.metrics import cohen_kappa_score
print("Agreement score",cohen_kappa_score(rater1_targets,rater2_targets))
