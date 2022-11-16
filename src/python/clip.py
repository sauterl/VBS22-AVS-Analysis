
class CLIP:
    MARGIN_IN_MILLISECOND = 0

    def __init__(self, video_id, start_time_in_millisecond, end_time_in_millisecond):
        self.video_id = video_id
        self.start_time = start_time_in_millisecond
        self.end_time = end_time_in_millisecond

    def __eq__(self, other):
        if self.video_id != other.video_id:
            return False
        no_overlap = self.start_time >= (other.end_time + CLIP.MARGIN_IN_MILLISECOND) or \
            self.end_time <= (other.start_time - CLIP.MARGIN_IN_MILLISECOND)
        return not no_overlap

    def __str__(self):
        return "(%d: %d, %d)" % (self.video_id, self.start_time, self.end_time)


if __name__ == "__main__":
    a = CLIP(1, 3000, 5000)

    b1 = CLIP(1, 1000, 3000)
    b2 = CLIP(1, 1000, 3100)
    c1 = CLIP(1, 5000, 6000)
    c2 = CLIP(1, 4500, 6000)

    d1 = CLIP(1, 3500, 4500)
    d2 = CLIP(1, 2500, 5500)

    submissions = [a, b1, b2, c1, c2, d1, d2]
    print("Submissions:", [str(i) for i in submissions])

    unique_submission = []
    for i in submissions:
        if i in unique_submission:
            continue
        unique_submission.append(i)
    print("Unique Submissions:", [str(i) for i in unique_submission])
