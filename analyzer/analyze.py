import numpy as np
import pylab as pl
from scipy.stats import norm

records = []


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
