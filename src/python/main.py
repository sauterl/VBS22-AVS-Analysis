import numpy as np
from collections import Counter
from load import load_judgement
from load import load_submission
from matplotlib import pyplot as plt
from time import strftime
from time import gmtime
from utils import bar_plot
from clip import CLIP
NOT_FOUND_TIME = 1e10
TEAM_NUMBER = 10


def get_task_team_submission(correct=False, sort_by_time=False):
    sub = load_submission()
    team_ids = set(sub["team"].values.tolist())
    task_ids = sorted(set(sub["task"].values.tolist()))
    team_submission_timestamp = {task_id: {team_id: {"clip": [], "time": [], "status": []} for team_id in team_ids} for task_id in task_ids}

    for index, row in sub.iterrows():
        _status = row["status"]
        if correct and _status != "CORRECT":
            continue
        _task_id, _team_id, _time = row["task"], row["team"], row["time"]
        _clip_id = (row["item"], row["start"]//1000, row["ending"]//1000)  # id of a unique clip
        team_submission_timestamp[_task_id][_team_id]["clip"].append(_clip_id)
        team_submission_timestamp[_task_id][_team_id]["time"].append(_time)
        team_submission_timestamp[_task_id][_team_id]["status"].append(_status)

    # team-level unique: The same submissions from the same team will be considered as 1
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


def test_repetitive_judgements():
    ju = load_judgement()

    clips = []
    for index, row in ju.iterrows():
        _status = row["sstatus"]
        # _clip_id = (row["sitem"], row["sstart"]//1000, row["sending"]//1000)  # id of a unique clip
        _clip = CLIP(row["sitem"], row["sstart"], row["sending"])
        clips.append(_clip)

    unique_clips = []
    for _clip in clips:
        if _clip in unique_clips:
            continue
        unique_clips.append(_clip)
    print("Deduplicated: %d -> %d = %d" % (len(clips), len(unique_clips), (len(clips)-len(unique_clips))))
    print()


def test_repetitive_submissions():
    sub = load_submission()
    clips = []
    for index, row in sub.iterrows():
        if row["task"] != "vbs22-avs-02":
            continue
        _status = row["status"]
        _clip = CLIP(row["item"], row["start"], row["ending"])
        clips.append(_clip)

    unique_clips = []
    for _clip in clips:
        if _clip in unique_clips:
            continue
        unique_clips.append(_clip)
    print("Deduplicated: %d -> %d = %d" % (len(clips), len(unique_clips), (len(clips)-len(unique_clips))))
    print()


def plot_submission_video_dist():
    sub = load_submission()

    interval_num = 17
    intervals = [i*1000 for i in range(1, interval_num+1)]
    teams = ["VIREO", "vibro", "CVHunter", "VISIONE"]
    team_video_ids = {_team_id: [] for _team_id in teams}

    for index, row in sub.iterrows():
        _team_id = row["team"]
        if _team_id not in teams:
            continue
        _video_id = row["item"]
        team_video_ids[_team_id].append(_video_id)

    team_submission_dist = {}
    for _team_id in teams:
        _search_slots = np.searchsorted(intervals, team_video_ids[_team_id]).tolist()
        _counter = Counter(_search_slots)
        team_submission_dist[_team_id] = [_counter[i] for i in range(interval_num+1)]

    fig, ax_bar = plt.subplots()
    bar_plot(ax_bar, team_submission_dist, total_width=.8, single_width=.9)
    x_pos = list(range(interval_num))
    x_ticks = ["%d" % (i*1000) for i in range(1, interval_num+1)]
    plt.xticks(x_pos, x_ticks, rotation=45)
    ax_bar.set_ylabel("Number of submissions")
    ax_bar.set_xlabel("Video Range")

    fig_name = f"../../plots/submission_video_distribution.pdf"
    plt.savefig(fig_name, bbox_inches='tight')
    print("Saved:", fig_name)


def plot_submission_duration():
    sub = load_submission()

    clip_durations = []
    for index, row in sub.iterrows():
        du = row["ending"] - row["start"]
        clip_durations.append((du+500)//1000)

    fig, ax_bar = plt.subplots()
    ax_bar.hist(clip_durations)
    ax_bar.set_ylabel("Number of submissions")
    ax_bar.set_xlabel("Clip duration")
    fig_name = f"../../plots/submission_duration_distribution.pdf"
    plt.savefig(fig_name)
    print("Saved:", fig_name)


# Figure 10
def plot_number_of_submissions_overtime(unique=False, accumulative=True, correct=True):
    """
    :param unique: same submissions from N teams are counted as 1 if set to True
    :param accumulative:
    :param correct:
    :return:
    """

    # interval_len, interval_num = 20000, 15
    interval_len, interval_num = 10000, 30

    task_team_correct_timestamp = get_task_team_submission(correct=correct, sort_by_time=False)

    for _task_id in task_team_correct_timestamp:
        intervals = [i*interval_len for i in range(1, interval_num+1)]
        time_stamps = []
        unique_clips = []  # task-level unique clip id
        c_skipped = 0
        for _team_id in task_team_correct_timestamp[_task_id]:
            if unique:  # filter the repeated submissions
                _clips = task_team_correct_timestamp[_task_id][_team_id]["clip"]
                _times = task_team_correct_timestamp[_task_id][_team_id]["time"]
                for _clip, _time in zip(_clips, _times):
                    if _clip in unique_clips:  # skip repeated submissions
                        c_skipped += 1
                        continue
                    unique_clips.append(_clip)
                    time_stamps.append(_time)
            else:
                time_stamps += task_team_correct_timestamp[_task_id][_team_id]["time"]
        samples = np.searchsorted(intervals, time_stamps).tolist()
        freq_count = Counter(samples)

        freq_accu = []
        _freq = 0
        for i in range(interval_num+1):
            if accumulative:
                _freq += freq_count[i]
            else:
                _freq = freq_count[i]  # if freq_count[i] < 60 else 60
            freq_accu.append(_freq if _freq else 1)

        _label = f"a{int(_task_id[-2:])}"
        plt.plot(list(range(interval_num)), freq_accu[:interval_num], label=_label)
        print("%3s Freq@1: %3d" % (_label, freq_accu[0]), end=" | ")
        print("#time stamps: %4d | #unique clip: %4d | #skipped: %3d" % (len(time_stamps), len(unique_clips), c_skipped))

    # plt.xticks(list(range(0, 15)), [strftime("%M:%S", gmtime(i*20)) for i in range(1, 16)], rotation=90)
    plt.xticks(list(range(0, interval_num)),
               [strftime("%M:%S", gmtime(i*interval_len/1000)) if (i*interval_len) % 20000 == 0 else "" for i in range(1, interval_num+1)],
               rotation=90)
    if accumulative:
        plt.yscale('log')
    plt.legend(bbox_to_anchor=(1, 0.5), loc="center left")
    unique_tag = "unique_" if unique else ""
    accumulative_tag = "accumulative_" if accumulative else ""
    fig_name = f"../../plots/avs_{accumulative_tag}correct_{unique_tag}submission.pdf"
    plt.savefig(fig_name, bbox_inches='tight')
    print("Saved:", fig_name)
    plt.clf()

    return task_team_correct_timestamp


# Figure 11
def plot_number_of_submissions(unique=False, correct=False):
    """
    :param unique: same submissions from N teams are counted as 1 if set to True
    :param correct: only consider 'correct' submissions if set to True
    :return:
    """

    def __time_by_half_teams__(timestamps, team_num):
        # TODO: return the longest time if less than 50% of teams submit (correct) results
        timestamps_sorted = sorted(timestamps)
        time = timestamps_sorted[team_num // 2]
        if time == NOT_FOUND_TIME:
            time = max([i for i in timestamps_sorted if i != NOT_FOUND_TIME])
        return time

    task_team_timestamp = get_task_team_submission(correct=correct, sort_by_time=True)
    task_info = {_task_id: {"submission_num": 0, "time_to_1": 0, "time_to_1_by_50%": 0, "time_to_10_by_50%": 0} for _task_id in task_team_timestamp}

    for _task_id in task_team_timestamp:
        _time_to_1, _time_to_10 = [], []
        _clips_unique = []
        for _team_id in task_team_timestamp[_task_id]:
            if unique:
                _times_with_repeat = task_team_timestamp[_task_id][_team_id]["time"]
                _clips_with_repeat = task_team_timestamp[_task_id][_team_id]["clip"]
                _times_unique = []
                for _clip, _time in zip(_clips_with_repeat, _times_with_repeat):
                    if _clip in _clips_unique:
                        continue
                    _clips_unique.append(_clip)
                    _times_unique.append(_time)
                _times = _times_unique
            else:
                _times = task_team_timestamp[_task_id][_team_id]["time"]

            task_info[_task_id]["submission_num"] += len(_times)
            if not _times:
                continue
            time_1st = _times[0] if len(_times) >= 1 else NOT_FOUND_TIME  # submission time of the 1st team
            time_10th = _times[9] if len(_times) >= 10 else NOT_FOUND_TIME  # submission time of the 10th team
            _time_to_1.append(time_1st)
            _time_to_10.append(time_10th)

        num_of_teams = len(task_team_timestamp[_task_id])
        task_info[_task_id]["time_to_1"] = min(_time_to_1)
        task_info[_task_id]["time_to_1_by_50%"] = __time_by_half_teams__(_time_to_1, num_of_teams)
        task_info[_task_id]["time_to_10_by_50%"] = __time_by_half_teams__(_time_to_10, num_of_teams)

    # collect data
    task_ids = list(task_info.keys())
    submission_nums = [task_info[_task_id]["submission_num"] for _task_id in task_ids]
    time_to_1 = [task_info[_task_id]["time_to_1"] // 1000 for _task_id in task_ids]
    time_to_1_by_50p = [task_info[_task_id]["time_to_1_by_50%"] // 1000 for _task_id in task_ids]
    time_to_10_by_50p = [task_info[_task_id]["time_to_10_by_50%"] // 1000 for _task_id in task_ids]

    # plot bar chart
    fig, ax_bar = plt.subplots()
    x_ticks = [f"a{int(_task_id[-2:])}" for _task_id in task_ids]
    ax_bar.bar(x_ticks, submission_nums, color="pink")
    ax_bar.set_xlabel("Task")
    ax_bar.set_ylabel("Number of submissions")

    # plot scatter chart
    x_pos = list(range(len(task_ids)))
    ax_scatter = ax_bar.twinx()
    ax_scatter.set_ylabel('Time')
    correct_tag = "correct " if correct else ""
    print("x_ticks", x_ticks)
    print("time_to_1", time_to_1)
    print("time_to_1_by_50p", time_to_1_by_50p)
    print("time_to_10_by_50p", time_to_10_by_50p)
    ax_scatter.scatter(x_pos, time_to_1, marker="v", color="turquoise", label=f"Time until first {correct_tag}submission")
    ax_scatter.scatter(x_pos, time_to_1_by_50p, marker="d", color="silver", label=f"Time to first {correct_tag}by 50% of teams")
    ax_scatter.scatter(x_pos, time_to_10_by_50p, marker="^", color="cornflowerblue", label=f"Time to 10 {correct_tag}by 50% of teams")
    ax_scatter.invert_yaxis()

    plt.xticks(x_pos, x_ticks, rotation=90)
    plt.legend(bbox_to_anchor=(0, -0.35), loc="lower left")
    correct_tag = "correct_" if correct else ""
    unique_tag = "unique_" if unique else ""
    fig_name = f"../../plots/avs_num_and_time_of_{correct_tag}{unique_tag}submission.pdf"
    plt.savefig(fig_name, bbox_inches='tight')
    print("Saved:", fig_name)
    plt.clf()


# Table
def tab_number_of_correct_submission():
    # Number of teams in agreement/disagreement with judges
    task_team_timestamp = get_task_team_submission(sort_by_time=False)

    column_num = 11
    print("\\begin{table*}[tb]")
    print("\\centering")
    print("\t\\begin{tabular}{%s}" % ("l" * (column_num+1)))
    print("\t\\toprule")
    print("\t& \\multicolumn{%d}{l}{Number of teams in agreement/disagreement with judges} \\\\" % column_num)
    print("\t\\cmidrule{2-%d}" % (column_num+1))
    print("\tTask &", end="")
    for i in range(column_num):
        end = "&" if i < (column_num - 1) else "\\\\"
        print("%d %s" % (i+1, end), end=" ")
    print("\t\\toprule")

    for _task_id in task_team_timestamp:
        clip_disagreement_count = {}
        clip_agreement_count = {}
        _label = f"a-{int(_task_id[-2:])}"
        print("\t%3s" % _label, end=" & ")
        for _team_id in task_team_timestamp[_task_id]:
            _clips = task_team_timestamp[_task_id][_team_id]["clip"]
            _statuses = task_team_timestamp[_task_id][_team_id]["status"]
            for _clip, _status in zip(_clips, _statuses):
                _disagreement_count = int(_status == "WRONG")
                if _clip not in clip_disagreement_count:
                    clip_disagreement_count[_clip] = 0
                clip_disagreement_count[_clip] += _disagreement_count

                _agreement_count = int(_status == "CORRECT")
                if _clip not in clip_agreement_count:
                    clip_agreement_count[_clip] = 0
                clip_agreement_count[_clip] += _agreement_count

        disagreement_numbers = Counter(list(clip_disagreement_count.values()))
        agreement_numbers = Counter(list(clip_agreement_count.values()))
        for _count in range(column_num):
            _end = "&" if _count < (column_num-1) else "\\\\"
            _count += 1
            if agreement_numbers[_count] == 0 and disagreement_numbers[_count] == 0:
                _value = "-"
            else:
                _value = "%d/%d" % (agreement_numbers[_count], disagreement_numbers[_count])

            is_bold = agreement_numbers[_count] < disagreement_numbers[_count]
            if is_bold:
                _value = "\\textbf{%s}" % _value
            print(_value, end=" %s " % _end)
        print()
    print("\t\\bottomrule")
    print("\t\\multicolumn{%d}{l}{Bold font highlights cases where the fraction is lower or equal to one (i.e., $\\frac{\\#agreement}{\\#disagreement} \\leq 1$)}" % (column_num+1))
    print("\t\\end{tabular}")
    print("\\end{table*}")


if __name__ == "__main__":
    print("Hello world")
    for _unique in [True, False]:
        for _correct in [True, False]:
            for _accumulative in [True, False]:
                plot_number_of_submissions_overtime(unique=_unique, accumulative=_accumulative, correct=_correct)

    for _unique in [True, False]:
        plot_number_of_submissions(unique=_unique, correct=True)  # correct

    tab_number_of_correct_submission()

    # plot_submission_video_dist()
    # plot_submission_duration()
    # test_repetitive_judgements()
    # test_repetitive_submissions()
