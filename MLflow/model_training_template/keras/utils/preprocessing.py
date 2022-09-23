import csv


def load_data(path):
    x = []
    with open(path, 'r', encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile, delimiter=' ')
        for row in reader:
            x.append(row[0])
    return x
