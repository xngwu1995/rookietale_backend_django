import pandas as pd
from academicworld.models import Faculty


CLUSTERMAP = {
    'group1': 'Cognitive & Learning Processes',
    'group2': 'Medical Imaging & Diagnostics',
    'group3': 'Human-Computer Interaction',
    'group4': 'Parallel Computing & Systems',
    'group5': 'Language Processing & Understanding',
    'group6': 'Security, Privacy, & Cryptography',
}

def get_group_quantiles():
    # Fetch data from the Faculty model and store it in a list of dictionaries
    data = Faculty.objects.values('id', 'group1', 'group2', 'group3', 'group4', 'group5', 'group6')

    # Convert the data to a Pandas DataFrame
    df = pd.DataFrame.from_records(data)

    # Define the quantiles you want to calculate, e.g., 0.25, 0.5, 0.75
    quantiles = [0.2, 0.4, 0.6, 0.8]

    # Calculate the quantiles for each group
    group_quantiles = {}
    for group in range(1, 7):
        group_quantiles[f'group{group}'] = df[f'group{group}'].quantile(quantiles).to_dict()

    return group_quantiles

GROUPQUANTILES = get_group_quantiles()

def get_score_quantile(group, score):
    group_quantiles = GROUPQUANTILES[group]
    for key, value in group_quantiles.items():
        if score <= value:
            return key * 5
    return 5

