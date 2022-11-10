import csv
import sqlite3


def main():
    db_con = sqlite3.connect('../../data/submissions.sqlite3')

    cursor = db_con.cursor()

    cursor.execute('CREATE TABLE submission ('
                   'team TEXT, '
                   'task TEXT, '
                   'item INTEGER, '
                   'time INTEGER, '
                   'status TEXT'
                   ')')

    db_con.commit()

    with open('../../data/avs-submissions.csv') as f:
        csv_reader = csv.reader(f)
        next(csv_reader)
        for row in csv_reader:
            task = row[2]
            time = int(row[4])
            team = row[5]
            item = int(row[7])
            status = row[10]

            cursor.execute('INSERT INTO submission (task, time, team, item, status) VALUES (?, ?, ?, ?, ?)',
                           (task, time, team, item, status))

    db_con.commit()


if __name__ == '__main__':
    main()
