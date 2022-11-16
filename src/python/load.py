import pandas as pd
import os
data_root = "../../data"


def load_judgement():
    # csv head: jid, jvalidator, token, verdict, juser, jtimestamp
    # ptimestamp, stimestamp, pid, sid, staskId, stask
    # sgroup, stime, steam, smember, sitem, sstart, sending, sstatus
    """
    jtimestamp: time that a judge decide the correctness
    ptimestamp: time that a case comes into the pool
    stimestamp: time that a user submits a case
    :return:
    """

    judgement_path = os.path.join(data_root, "avs-submissions-judgements.csv")
    with open(judgement_path, "r") as f:
        judgement = pd.read_csv(f)
    return judgement


def load_submission():
    submission_path = os.path.join(data_root, "avs-submissions.csv")
    with open(submission_path, "r") as f:
        submission = pd.read_csv(f)
    return submission
