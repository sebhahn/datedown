# The MIT License (MIT)
#
# Copyright (c) 2016,Christoph Paulik
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

'''
Interface for the package.
'''

from datetime import datetime
from datedown.down import check_downloaded
import warnings
import sys
import argparse


def download_by_dt(dts, url_create_fn,
                   fpath_create_fn, download_fn,
                   passes=3):
    """
    Download data for datetimes. If files are missing try
    again passes times.

    Parameters
    ----------
    dts: list
        list of datetime.datetime objects
    url_create_fn: function
        function that creates an URL from a datetime object
    fpath_create_fn: function
        function that creates a filename from a datetime object
    download_fn: function
        function that transfers data from a list
        of URLs to a list of filenames.
        Takes two arguments (url_list, fname_list)
    passes: int, optional
        if files are missing then try again passes times
    """
    urls = map(url_create_fn, dts)
    fnames = map(fpath_create_fn, dts)
    for p in range(passes):
        download_fn(urls, fnames)
        no_urls, no_fnames = check_downloaded(urls, fnames)
        urls = no_urls
        fnames = no_fnames
        if len(no_urls) == 0:
            break

    if len(urls) != 0:
        warnings.warn("Not all URL's were downloaded.")
        warnings.warn("\n".join(urls))


def mkdate(datestring):
    if len(datestring) == 10:
        return datetime.strptime(datestring, '%Y-%m-%d')
    if len(datestring) == 16:
        return datetime.strptime(datestring, '%Y-%m-%dT%H:%M')


def n_hours(intervalstring):
    """
    Convert an interval string like 1D, 6H etc. to the
    number of hours it represents.
    """
    multid = {'H': 1,
              'D': 24}
    multi = multid[intervalstring[-1].upper()]
    hours = multi * int(intervalstring[:-1])
    return hours


def parse_args(args):
    """
    Parse command line parameters

    :param args: command line parameters as list of strings
    :return: command line parameters as :obj:`argparse.Namespace`
    """
    parser = argparse.ArgumentParser(
        description="Download data in parallel using wget. Based on datetimes.")
    parser.add_argument("start", type=mkdate,
                        help="Startdate. Either in format YYYY-MM-DD or YYYY-MM-DDTHH:MM.")
    parser.add_argument("end", type=mkdate,
                        help="Enddate. Either in format YYYY-MM-DD or YYYY-MM-DDTHH:MM.")
    parser.add_argument("urlroot",
                        help='Root of URL of the remote dataset.')
    parser.add_argument("urlfname",
                        help='Filenames of the remote dataset.')
    parser.add_argument("localroot",
                        help='Root of local filesystem.')
    parser.add_argument("--urlsubdirs", nargs='+',
                        help=('Subdirectories to put between urlroot and urlfname.',
                              'This can be a list of directories that can contain date string templates.',
                              'e.g. --urlsubdirs %Y %m would look for files in urlroot/YYYY/MM/urlfname.'))
    parser.add_argument("--localfname",
                        help=('Filenames of the local dataset. ',
                              'If not given the filenames of the remote dataset are used.'))
    parser.add_argument("--localsubdirs", nargs='+',
                        help=('Subdirectories to put between localroot and localfname.',
                              'This can be a list of directories that can contain date string templates.',
                              'e.g. --localsubdirs %Y %m would look for files in localroot/YYYY/MM/localfname.',
                              'If not given then the urlsubdirs are used.'))
    parser.add_argument("--interval", type=n_hours, default='1D',
                        help=('Interval of datetimes between the start and end. ',
                              'Supported types are e.g. 6H for 6 hourly or 2D for 2 daily.'))
    return parser.parse_args(args)


def main(args):
    args = parse_args(args)


def run():
    main(sys.argv[1:])