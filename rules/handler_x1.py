import pandas as pd
from clean_x1 import clean_x1

pc_aliases = {
    "810g2": "810", "3626": "3113", "3249": "3113", "r7572": "i5420", "1229dx": "1016dx", "6787": "3435"}

cpu_model_aliases = {
    "hp": {"1st gen": "620m", "3540m": "3520m", "2nd gen": "2520m", "q720": "2800m", "m520": "520m",
           "3rd gen": "620m", "m640": "620m", "m620": "620m", "q820": "620m", "720qm": "620m", "640m": "620m",
           "880m": "620m"},
    "acer": {"1005m": "2020m"},
    "lenovo": {"e-300": "hd-6310", "3rd gen": "3320m", "sl9400": "l9400"},
    "asus": {},
    "dell": {}
}

model_2_pcname = {
    "1-6010": "15g070nr"
}

family_single = ["x200", "x200t", "x100"]

family_capacity = ["x220"]

pc_single = ["v5132", "8440p", "ux301la", "e5571", "15f009wm", "5742", "ux31a", "15g070nr",
             "e1731", "p3171", "v5123", "e1532", "v3772", "e1522", "e5531", "v5573", "e5521",
             "15r150nr", "15d090nr", "2339", "2320", "2338", "3448", "0622", "s7392", "v5122",
             "8770w", "5547", "15g012dx", "7537", "5735", "2560p", "3444", "8570p",
             "8730w", "8530p", "8530w", "2540p", "nc6400", "ux21e", "5620", "8470w",
             "2170p", "e1531", "2325", "as5552", "15p030nr", "2760p", "dv6000",
             "m731r", "i5420", "1016dx"]

model_single = ["3320m"]
pc_core = ["8560p", "m5481", "810", "e1572", "e1771", "v3111"]
pc_capacity = ["8540w", "8460p", "0611"]
pc_core_capacity = ["9470m", "8740w"]

solved_spec = []
unsolved_spec = []

instance_list = set()


def handle_x1(dataset: pd.DataFrame):

    dataset = clean_x1(dataset)

    for index, row in dataset.iterrows():
        instance_id = row['instance_id']
        brand = row['brand']
        cpu_core = row['cpu_core']
        cpu_model = row['cpu_model']
        cpu_frequency = row['cpu_frequency']
        pc_name = row['pc_name']
        capacity = row['ram_capacity']
        family = row['family']
        rest_info = row['rest_info']
        title = row['title']
        pc = {}

        if pc_name in pc_aliases.keys():
            pc_name = pc_aliases[pc_name]

        if (pc_name == '0') and (family in family_single):
            pc_name = family

        if cpu_model in model_2_pcname.keys():
            pc_name = model_2_pcname[cpu_model]

        if brand in cpu_model_aliases.keys():
            if cpu_model in cpu_model_aliases[brand].keys():
                cpu_model = cpu_model_aliases[brand][cpu_model]

        instance_list.add(instance_id)

        pc['id'] = instance_id
        pc['title'] = title
        pc['brand'] = brand
        pc['pc_name'] = pc_name
        pc['cpu_model'] = cpu_model
        pc['capacity'] = capacity
        pc['cpu_core'] = cpu_core
        pc['rest'] = rest_info

        if pc_name == "8460p" and cpu_model == "2450m":
            pc['identification'] = pc_name + ' ' + cpu_model
            solved_spec.append(pc)
        elif pc_name in pc_single or pc_name in family_single:
            pc['identification'] = pc_name
            solved_spec.append(pc)
        elif pc_name in pc_capacity and capacity != '0':
            pc['identification'] = pc_name + ' ' + capacity
            solved_spec.append(pc)
        elif cpu_model in model_single:
            pc['identification'] = cpu_model
            solved_spec.append(pc)
        elif pc_name in pc_core and cpu_core != '0':
            pc['identification'] = pc_name + ' ' + cpu_core
            solved_spec.append(pc)
        elif family in family_capacity and capacity != '0':
            pc['identification'] = family + ' ' + capacity
            solved_spec.append(pc)
        elif pc_name in pc_core_capacity and cpu_core != '0' and capacity != '0':
            pc['identification'] = pc_name + ' ' + cpu_core + ' ' + capacity
            solved_spec.append(pc)
        elif pc_name != '0' and cpu_model != '0':
            pc['identification'] = pc_name + ' ' + cpu_model
            solved_spec.append(pc)
        elif pc_name != '0' and cpu_core != '0':
            pc['identification'] = pc_name + ' ' + cpu_core
            solved_spec.append(pc)
        elif pc_name != '0' and cpu_frequency != '0':
            pc['identification'] = pc_name + ' ' + cpu_frequency
            solved_spec.append(pc)
        elif rest_info != '0':
            pc['identification'] = rest_info
            solved_spec.append(pc)
        else:
            unsolved_spec.append(pc)

    clusters = dict()

    for s in solved_spec:
        if s['identification'] in clusters.keys():
            clusters[s['identification']].append(s['id'])
        else:
            clusters.update({s['identification']: [s['id']]})

    for u in unsolved_spec:
        identification = u['brand'] + ' ' + u['pc_name'] + ' ' + u['cpu_model'] + ' ' + u['capacity'] + ' ' + \
                         u['cpu_core']
        if identification in clusters.keys():
            clusters[identification].append(u['id'])
        else:
            clusters.update({identification: [u['id']]})

    couples = set()
    for c in clusters.keys():
        if len(clusters[c]) > 1:
            for i in clusters[c]:
                for j in clusters[c]:
                    if i < j:
                        couples.add((i, j, 1))
                    if i > j:
                        couples.add((j, i, 1))

    output = couples
    output = pd.DataFrame(
        output,
        columns=[
            'lid',
            'rid',
            'label'])
    output.drop(columns=['label'], inplace=True)

    return output