import numpy as np
from collections import Counter
from load import load_judgement
from matplotlib import pyplot as plt
from time import strftime
from time import gmtime
import math
import matplotlib.dates as md


def get_task_team_submission(unique=False, correct=False, sort_by_time=False):
    ju = load_judgement()
    team_ids = set(ju["steam"].values.tolist())
    task_ids = sorted(set(ju["stask"].values.tolist()))
    team_submission_timestamp = {task_id: {team_id: {"clip": [], "time": []} for team_id in team_ids} for task_id in task_ids}

    for index, row in ju.iterrows():
        if correct and row["sstatus"] != "CORRECT":
            continue
        _task_id, _team_id, _clip_id, _time = row["stask"], row["steam"], (row["sitem"], row["sstart"], row["sending"]), row["stime"]
        team_submission_timestamp[_task_id][_team_id]["clip"].append(_clip_id)
        team_submission_timestamp[_task_id][_team_id]["time"].append(_time)

    if unique:  # consider unique submissions only
        for _task_id in task_ids:
            for _team_id in team_ids:
                _clip_ids_sorted, _times_sorted = [], []
                for _clip_id, _time in zip(team_submission_timestamp[_task_id][_team_id]["clip"], team_submission_timestamp[_task_id][_team_id]["time"]):
                    if _clip_id in _clip_ids_sorted:
                        continue
                    _clip_ids_sorted.append(_clip_id)
                    _times_sorted.append(_time)

                del team_submission_timestamp[_task_id][_team_id]["clip"]
                del team_submission_timestamp[_task_id][_team_id]["time"]
                team_submission_timestamp[_task_id][_team_id]["clip"] = _clip_ids_sorted
                team_submission_timestamp[_task_id][_team_id]["time"] = _times_sorted

    if sort_by_time:  # consider unique submissions only
        for _task_id in task_ids:
            for _team_id in team_ids:
                if not team_submission_timestamp[_task_id][_team_id]["clip"]:
                    continue

                _clip_time_pair = [(_clip_id, _time) for _clip_id, _time in zip(team_submission_timestamp[_task_id][_team_id]["clip"],
                                                                                team_submission_timestamp[_task_id][_team_id]["time"])]
                _clip_time_pair_sorted = sorted(_clip_time_pair, key=lambda x: x[1])
                _clip_ids_sorted, _times_sorted = zip(*_clip_time_pair_sorted)

                del team_submission_timestamp[_task_id][_team_id]["clip"]
                del team_submission_timestamp[_task_id][_team_id]["time"]
                team_submission_timestamp[_task_id][_team_id]["clip"] = _clip_ids_sorted
                team_submission_timestamp[_task_id][_team_id]["time"] = _times_sorted

    return team_submission_timestamp


def accumulative_correct_submission(unique=False, by_task=True):
    """
    :param unique: only count unique submissions if set to True
    :param by_task: calculate by avs task if set to Ture, otherwise, calculate by team
    :return:
    """
    task_team_correct_timestamp = get_task_team_submission(unique=unique, correct=True, sort_by_time=False)

    if by_task:
        for _task_id in task_team_correct_timestamp:
            intervals = [i*20000 for i in range(1, 16)]
            time_stamps = []
            for _team_id in task_team_correct_timestamp[_task_id]:
                time_stamps += task_team_correct_timestamp[_task_id][_team_id]["time"]
            samples = np.searchsorted(intervals, time_stamps).tolist()
            freq_count = Counter(samples)

            freq_acc = []
            _freq = 0
            for i in range(16):
                _freq += freq_count[i]
                freq_acc.append(_freq if _freq else 1)

            _label = f"a{int(_task_id[-2:])}"
            plt.plot(list(range(15)), freq_acc[:15], label=_label)
            print(f"{_label}: {freq_acc[0]}")

        plt.xticks(list(range(0, 15)), [strftime("%M:%S", gmtime(i*20)) for i in range(1, 16)], rotation=90)
        plt.yscale('log')
        plt.legend(bbox_to_anchor=(1, 0.5), loc="center left")
        unique_tag = "unique_" if unique else ""
        fig_name = f"../../plots/accumulative_correct_{unique_tag}submission.png"
        plt.savefig(fig_name, bbox_inches='tight')
        print("Saved:", fig_name)
        plt.clf()
    else:
        raise NotImplementedError

    return task_team_correct_timestamp


def number_of_submissions(unique=False, correct=False):
    """
    :param unique: only consider 'unique' submissions if set to True
    :param correct: only consider 'correct' submissions if set to True
    :return:
    """
    task_team_timestamp = get_task_team_submission(unique=unique, correct=correct, sort_by_time=True)
    task_info = {_task_id: {"submission_num": 0, "time_to_1": 0, "time_to_1_by_50%": 0, "time_to_10_by_50%": 0} for _task_id in task_team_timestamp}

    for _task_id in task_team_timestamp:
        _time_to_1, _time_to_10 = [], []
        for _team_id in task_team_timestamp[_task_id]:
            task_info[_task_id]["submission_num"] += len(task_team_timestamp[_task_id][_team_id]["time"])
            _times = task_team_timestamp[_task_id][_team_id]["time"]
            if not _times:
                continue
            time_1st = _times[0] if len(_times) >= 1 else 1e5
            time_10th = _times[9] if len(_times) >= 10 else 1e5
            _time_to_1.append(time_1st)
            _time_to_10.append(time_10th)

        num_of_teams = len(task_team_timestamp[_task_id])
        task_info[_task_id]["time_to_1"] = min(_time_to_1)
        task_info[_task_id]["time_to_1_by_50%"] = sorted(_time_to_1)[num_of_teams//2]
        task_info[_task_id]["time_to_10_by_50%"] = sorted(_time_to_10)[num_of_teams//2]

    # collect data
    task_ids = list(task_info.keys())
    submission_nums = [task_info[_task_id]["submission_num"] for _task_id in task_ids]
    time_to_1 = [task_info[_task_id]["time_to_1"] // 1000 for _task_id in task_ids]
    time_to_1_by_50p = [task_info[_task_id]["time_to_1_by_50%"] // 1000 for _task_id in task_ids]
    time_to_10_by_50p = [task_info[_task_id]["time_to_10_by_50%"] // 1000 for _task_id in task_ids]

    # plot bar chart
    fig, ax_bar = plt.subplots()
    x_ticks = [f"a{int(_task_id[-2:])}" for _task_id in task_ids]
    ax_bar.bar(x_ticks, submission_nums)
    ax_bar.set_xlabel("Task")
    ax_bar.set_ylabel("Number of submissions")

    # plot scatter chart
    x_pos = list(range(len(task_ids)))
    ax_scatter = ax_bar.twinx()
    ax_scatter.set_ylabel('time')
    correct_tag = "correct " if correct else ""
    print(time_to_1)
    print(time_to_1_by_50p)
    print(time_to_10_by_50p)
    ax_scatter.scatter(x_pos, time_to_1, marker="^", color="blue", label=f"Time until first {correct_tag}submission")
    ax_scatter.scatter(x_pos, time_to_1_by_50p, marker="d", color="red", label=f"Time to first {correct_tag}by 50% of teams")
    ax_scatter.scatter(x_pos, time_to_10_by_50p, marker="^", color="yellow", label=f"Time to 10 {correct_tag}by 50% of teams")
    ax_scatter.invert_yaxis()
    # ax_scatter.yaxis.set_major_formatter(strftime("%M:%S"))

    plt.xticks(x_pos, x_ticks, rotation=90)
    plt.legend(bbox_to_anchor=(0, -0.35), loc="lower left")
    correct_tag = "correct_" if correct else ""
    unique_tag = "unique_" if unique else ""
    fig_name = f"../../plots/num_and_time_of_{correct_tag}{unique_tag}submission.png"
    plt.savefig(fig_name, bbox_inches='tight')
    print("Saved:", fig_name)
    plt.clf()


if __name__ == "__main__":
    print("Hello world")
    # accumulative_correct_submission(unique=False)
    number_of_submissions(unique=False, correct=False)
