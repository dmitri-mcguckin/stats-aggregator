import csv
import datetime
from dateutil import parser


class Tutor:
    def __init__(self, name):
        self.name = name
        self.people_helped = 0
        self.classes_tutored = []
        self.days_worked = []
        self.session_durations = []

    def append(self, date, duration, class_id):
        self.classes_tutored.append(class_id)
        if(date.date() not in self.days_worked):
            self.days_worked.append(date.date())
        self.session_durations.append(duration)
        self.people_helped += 1

    def average_session_length(self) -> datetime.timedelta:
        if(len(self.session_durations) > 0):
            return datetime.timedelta(seconds=sum(list(map(lambda x: x.total_seconds(), self.session_durations))) / len(self.session_durations))
        else:
            return datetime.timedelta(seconds=0)

    def average_class_tutored(self):
        if(len(self.classes_tutored) > 0):
            return max(set(self.classes_tutored), key=self.classes_tutored.count)
        else:
            return 'N/A'

    def __lt__(self, tutor):
        return self.name < tutor.name

    def __repr__(self):
        return "<Tutor: {} (people helped: {}) (days worked: {}) (avg help time: {}) (most tutored: {})>".format(self.name, self.people_helped, len(self.days_worked), self.average_session_length(), self.average_class_tutored())


class Record:
    def __init__(self,
                 date,
                 in_time,
                 out_time,
                 tutor,
                 shadow,
                 class_id,
                 comments,
                 line_no,
                 tutors_table):
        try:
            self.date = parser.parse(date)
        except Exception:
            raise ValueError('Invalid Date: \"{}\" on line {}\
                              \n\tWith data: \
                              \n\tIn Time: {} \
                              \n\tOut Time: {} \
                              \n\tTutor: {} \
                              \n\tShadow: {} \
                              \n\tClass: {} \
                              \n\tComments: {}\n'.format(date,
                                                         line_no,
                                                         in_time,
                                                         out_time,
                                                         tutor,
                                                         shadow,
                                                         class_id,
                                                         comments))
        try:
            self.in_time = parser.parse(date + " " + in_time)
        except Exception:
            raise ValueError('Invalid In Time: \"{}\" on line {}\
                              \n\tWith data: \
                              \n\tDate: {} \
                              \n\tOut Time: {} \
                              \n\tTutor: {} \
                              \n\tShadow: {} \
                              \n\tClass: {} \
                              \n\tComments: {}\n'.format(in_time,
                                                         line_no,
                                                         date,
                                                         out_time,
                                                         tutor,
                                                         shadow,
                                                         class_id,
                                                         comments))
        try:
            self.out_time = parser.parse(date + " " + out_time)
        except Exception:
            raise ValueError('Invalid Out Time: \"{}\" on line {}\
                              \n\tWith data: \
                              \n\tIn Time: {} \
                              \n\tDate: {} \
                              \n\tTutor: {} \
                              \n\tShadow: {} \
                              \n\tClass: {} \
                              \n\tComments: {}\n'.format(out_time,
                                                         line_no,
                                                         in_time,
                                                         date,
                                                         tutor,
                                                         shadow,
                                                         class_id,
                                                         comments))
        # Check if the tutor table has the tutor already, else generate it
        tutor_name = tutor.title().strip()

        if(tutor_name == '' or tutor_name is None):
            raise ValueError('Empty tutor name on line {}!'.format(line_no))

        tutor_table_entry = tutors_table.get(tutor_name)
        if(tutor_table_entry is None):
            self.tutor = Tutor(tutor_name)
            tutors_table[tutor_name] = self.tutor
        else:
            self.tutor = tutor_table_entry
        self.tutor.append(self.date, self.out_time - self.in_time, class_id)

        # Check if the tutor table has the shadow already, else generate it
        shadow_name = shadow.title().strip()
        shadow_table_entry = tutors_table.get(shadow_name)
        if(shadow_table_entry is None):
            self.shadow = Tutor(shadow_name)
            tutors_table[shadow_name] = self.shadow
        else:
            self.shadow = shadow_table_entry

        self.class_id = class_id
        self.comments = []

        # Join comments into one string
        for e in comments:
            if e != '' and e is not None:
                self.comments.append(e)


class RecordsSheet:
    def __init__(self, filename):
        skip = 2
        file = open(filename)
        reader = csv.reader(file, quotechar='\"')

        # Variables with state
        self.records = []
        self.tutors = {}
        self.students = []

        # Generate the records list
        for line_no, row in enumerate(reader):
            line_no += 1  # Offest the fact that file lines start at 1

            if(skip > 0):  # Determine if still in the header of the records
                skip -= 1
            elif(row != ''):  # Read in a record if it's not blank
                self.records.append(Record(row[0],
                                           row[5],
                                           row[6],
                                           row[1],
                                           row[2],
                                           row[4],
                                           row[8:],
                                           line_no,
                                           self.tutors))
                self.students.append(row[3].strip().replace(',', ''))
        self.students = len(set(self.students))
        self.tutors.pop('')  # Dunno where the empty tutor is coming from, but once records are done being populated, remove empty tutor

    def __repr__(self):
        return "<Records Sheet ({} entries) ({} unique tutors) ({} students)>" \
               .format(len(self.records), len(self.tutors), self.students)
