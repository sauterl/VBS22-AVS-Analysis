--- Counts for each team/task/item combination the number of incorrect AVS submissions before the first correct one
SELECT task, avg(errors) AS average, max(errors) AS maximum
FROM (SELECT s.team, s.task, s.item, count(*) AS errors
      FROM submission s
               LEFT OUTER JOIN
           (SELECT team, task, item, min(time) AS time
            FROM submission
            WHERE status = 'CORRECT'
            GROUP BY team, task, item) fc
           ON s.team = fc.team AND s.task = fc.task AND s.item = fc.item
      WHERE s.time < fc.time OR fc.time IS NULL
      GROUP BY s.team, s.task, s.item)
GROUP BY task;