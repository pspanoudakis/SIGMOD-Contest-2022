import pandas as pd
from handler_X1 import handle_x1

Flag = True

if __name__ == '__main__':
    couples = []
    for file_name in ['/home/theodora/Documents/SigmodContest/sigmodContest2022/rules/X1.csv']:
        data = pd.read_csv(file_name)
        if 'name' not in data.columns:
            couples.extend(handle_x1(data))
        else:
            if Flag:
                couples.extend([(0,0)]*0)
            else:
                couples.extend([(0,0)]*2000000)

    output = pd.DataFrame(
                couples,
                columns=[
                    'left_instance_id',
                    'right_instance_id'])
    output.to_csv(
            "output.csv",
            index=False)

    """ if Flag:
        output.to_csv("../datasets/output.csv", sep=',', encoding='utf-8', index=False)
        Flag = False
    else:
        output.to_csv(
            "output.csv",
            mode='a',
            sep=',',
            encoding='utf-8',
            index=False,
            header=None) """