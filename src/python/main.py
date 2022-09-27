import numpy as np
from collections import Counter
from load import load_judgement
from matplotlib import pyplot as plt
from time import strftime
from time import gmtime
import math


def accumulative_correct_submission(unique=False, by_task=True):
    """
    :param unique: only count unique submissions if set to True
    :param by_task: calculate by avs task if set to Ture, otherwise, calculate by team
    :return:
    """
    ju = load_judgement()
    team_ids = set(ju["steam"].values.tolist())
    task_ids = sorted(set(ju["stask"].values.tolist()))
    team_correct_timestamp = {task_id: {team_id: {"clip": [], "time": []} for team_id in team_ids} for task_id in task_ids}

    for index, row in ju.iterrows():
        if row["sstatus"] != "CORRECT":
            continue
        _team_id = row["steam"]
        _task_id = row["stask"]
        _clip_id = (row["sitem"], row["sstart"], row["sending"])
        _time = row["stime"]
        team_correct_timestamp[_task_id][_team_id]["clip"].append(_clip_id)
        team_correct_timestamp[_task_id][_team_id]["time"].append(_time)

    if unique:  # consider unique submissions only
        for _task_id in task_ids:
            for _team_id in team_ids:
                _clip_ids_unique, _times_unique = [], []
                for _clip_id, _time in zip(team_correct_timestamp[_task_id][_team_id]["clip"], team_correct_timestamp[_task_id][_team_id]["time"]):
                    if _clip_id in _clip_ids_unique:
                        continue
                    _clip_ids_unique.append(_clip_id)
                    _times_unique.append(_time)
                team_correct_timestamp[_task_id][_team_id]["clip"] = _clip_ids_unique
                team_correct_timestamp[_task_id][_team_id]["time"] = _times_unique

    if by_task:
        for _task_id in task_ids:
            intervals = [i*20000 for i in range(1, 16)]
            time_stamps = []
            for _team_id in team_ids:
                time_stamps += team_correct_timestamp[_task_id][_team_id]["time"]
            samples = np.searchsorted(intervals, time_stamps).tolist()
            freq_count = Counter(samples)

            freq_acc = []
            _freq = 0
            for i in range(16):
                _freq += freq_count[i]
                freq_acc.append(_freq if _freq else 1)

            plt.xticks(rotation=90)
            _label = f"a{int(_task_id[-2:])}"
            plt.plot(list(range(15)), freq_acc[:15], label=_label)
            print(f"{_label}: {freq_acc[0]}")

        plt.xticks(list(range(0, 15)), [strftime("%M:%S", gmtime(i*20)) for i in range(1, 16)])
        plt.yscale('log')
        plt.legend(bbox_to_anchor=(1, 0.5), loc="center left")
        fig_name = f"../../plots/accumulative_correct_submission_unique_{unique}.png"
        plt.savefig(fig_name, bbox_inches='tight')
        print("Saved:", fig_name)
        plt.clf()
    else:
        raise NotImplementedError

    return team_correct_timestamp


if __name__ == "__main__":
    print("Hello world")
    accumulative_correct_submission(unique=True)
