#!/usr/bin/env python3
import sys
import csv
import numpy as np
import pylab as pl
from scipy.stats import norm
from dateutil import parser
from ftf_utilities import log, Mode


records = []


class Record:
    def __init__(self,
                 date,
                 in_time,
                 out_time,
                 tutor,
                 shadow,
                 student,
                 class_id,
                 comments):
        self.date = parser.parse(date)
        self.in_time = parser.parse(date + " " + in_time)
        self.out_time = parser.parse(date + " " + out_time)
        self.tutor = tutor.title()
        self.shadow = shadow.title()
        self.student = student.title()
        self.class_id = class_id
        self.comments = []

        for e in comments:
            if e != '' and e is not None:
                self.comments.append(e)


def load_file(path):
    skip = 2
    file = open(path)
    reader = csv.reader(file, quotechar='|')

    records = []
    for row in reader:
        if(skip > 0):
            skip -= 1
        else:
            records.append(Record(row[0],
                                  row[5],
                                  row[6],
                                  row[1],
                                  row[2],
                                  row[3],
                                  row[4],
                                  row[8:]))
    file.close()
    return records


def get_uniques(field):
    global records
    uniques = []
    res = list(set(map(lambda x: getattr(x, field), records)))
    for r in res:
        if(r != '' and r is not None):
            uniques.append(r)
    return sorted(uniques)


def draw_help_time(records):
    name = records[0].tutor
    in_times = list(map(lambda x: getattr(x, 'in_time'), records))
    out_times = list(map(lambda x: getattr(x, 'out_time'), records))

    elapsed = []
    for i, o in zip(in_times, out_times):
        elapsed.append((o - i).total_seconds() / 60)
    elapsed = sorted(elapsed)

    mu = np.mean(elapsed)
    sigma = np.std(elapsed)

    fit = norm.pdf(elapsed, mu, sigma)
    pl.title(name + "'s Distribution (" + str(len(records)) + ")")
    pl.xlabel("Time Spent (minutes)")
    pl.ylabel("Frequency Coefficient")
    pl.plot(elapsed, fit, '-o')
    pl.savefig('data/' + name.replace(' ', '_').lower() + '_distribution.png')
    pl.show()

    return mu, sigma


def draw_count_per_day(records):
    pl.title('Help per day')
    pl.xlabel('Date')
    pl.ylabel('Number of Students')

    count = list(map(lambda x: records[x], records))
    min_c = min(count)
    max_c = max(count)

    log(Mode.INFO, "Min: " + str(min_c) + ", Max: " + str(max_c))

    pl.hist(list(records), weights=3.0, bins=len(records), color='red', rwidth=0.5)
    pl.axis([None, None, 0, max_c])
    pl.show()


def select_by(field, value):
    global records
    results = []

    if(type(value) is str):
        value = value.title()

    for record in records:
        row_value = getattr(record, field)
        if(type(value) is str and value in row_value):
            results.append(record)
        elif(row_value == value):
            results.append(record)
    return results


def main(args):
    global records
    if(len(args) == 0):
        log(Mode.ERROR, "Path to records file not provided!")
        sys.exit(-1)

    path = args[0]
    records = load_file(path)

    tutors = get_uniques('tutor')
    log(Mode.INFO, "Tutors(" + str(len(tutors)) + "): " + str(tutors))

    dates = get_uniques('date')
    date_count = {}
    for date in dates:
        results = select_by('date', date)
        date_count[date] = len(results)

    log(Mode.INFO, "Date: " + str(date_count))
    draw_count_per_day(date_count)

    # for tutor in tutors:
    #     results = select_by('tutor', tutor)
    #
    #     if(len(results) > 1):
    #         mu, sigma = draw_help_time(results)
    #         log(Mode.INFO, tutor
    #             + " helped " + str(len(results))
    #             + " people.\n\t\t"
    #             + "(mu: " + str(mu) + ","
    #             + " sigma: " + str(sigma) + ")")
    #     else:
    #         log(Mode.WARN, tutor
    #             + " didn't have enough entries to create a distribution plot.")


if __name__ == "__main__":
    main(sys.argv[1:])
