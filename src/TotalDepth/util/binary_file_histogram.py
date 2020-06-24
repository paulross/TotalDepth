import sys

from TotalDepth.util import Histogram


def add_file_to_histogram(path, histogram):
    with open(path, 'rb') as file:
        for b in file.read():
            histogram.add(b)


def main():
    histogram = Histogram.Histogram(pre_load=range(256))
    add_file_to_histogram(sys.argv[1], histogram)

    print(histogram.strRep(inclCount=True))

    return 0


if __name__ == '__main__':
    sys.exit(main())