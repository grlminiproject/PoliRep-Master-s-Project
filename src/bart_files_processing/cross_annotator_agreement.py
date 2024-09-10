import bratiaa as biaa

project = '../data/annotations/phase2_original'

# instance-level agreement
f1_agreement = biaa.compute_f1_agreement(project)

# print agreement report to stdout
biaa.iaa_report(f1_agreement)