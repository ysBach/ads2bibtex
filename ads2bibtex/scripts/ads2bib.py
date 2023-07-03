import argparse
import time
from datetime import datetime
from pathlib import Path

from colorama import Back, Fore, Style
import json

from ads2bibtex import query_ads, query_lib, read_bib_add, make_rawfile, _check_token

DESCRIPTION = """
Accepts the ADS Library (recommended) or a text file with the ADS-style
bibcodes (deprecated), and optionally a text file with additional bibtex
entries (those that are not indexed to ADS). The bibtex or bibitem (etc) entry
is obtained by querying to ADS API. Then combine the queried results and the
additional entries (both could be optionally sorted) and save into an output
file.

To reset token, do
rm .ads-token
""".strip()


def print_infostr(fname, new, old):
    infostr = f" {fname} Changed "
    print(f"\n{infostr:=^80s}")
    print(Fore.WHITE, Back.BLACK, f"N_new = {len(new)}", Style.RESET_ALL)
    added = [x for x in new if x not in old]
    deled = [x for x in old if x not in new]
    if added:
        print(Fore.GREEN, Back.BLACK, " +{}: ".format(len(added)), Style.RESET_ALL, end="")
        for x in added[:-1]:
            print(Fore.BLACK, Back.GREEN, x, Style.RESET_ALL, end=", ")
        print(Fore.BLACK, Back.GREEN, added[-1], Style.RESET_ALL, end="\n")
    if deled:
        print(Fore.RED, Back.BLACK, " -{}: ".format(len(deled)), Style.RESET_ALL, end="")
        for x in deled[:-1]:
            print(Fore.BLACK, Back.RED, x, Style.RESET_ALL, end=", ")
        print(Fore.BLACK, Back.RED, deled[-1], Style.RESET_ALL)


def main(args=None):
    parser = argparse.ArgumentParser(
        description=DESCRIPTION,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("lib_or_file",
                        help="ADS Library ID (recommended) or ADS-style bibcodes file")
    parser.add_argument("-a", "--additional-file", default=None,  # nargs="+",
                        help="File with additional entries.")
    parser.add_argument("-o", "--output", default="references.bib",
                        help="Output file name. Default: `references.bib`")
    parser.add_argument("-r", "--rawfile", default="none",
                        help=("Filename to save bibcode and title info. "
                              + "Set to `none` to skip it. Default: `none`")
                        )
    parser.add_argument("-s", "--sort-option", default="date asc",
                        help="Sort option for ADS API. Default: `'date asc'`")
    parser.add_argument("-j", "--journal", default="ads", type=str,
                        help=("Journal name for the ADS API. One of [ads, full, iso4]. "
                              + "Default: `'ads'` (uses ADS macros, e.g., `\\apj`). "
                              + "`'full'` uses full journal names (e.g., `The "
                              + "Astrophysical Journal`). `'iso4'` uses ISO 4 journal "
                              + "names (e.g., `Astrophys. J.`)."
                              )
                        )
    parser.add_argument("-f", "--format", default="bibtex", type=str,
                        help=("The output format of the bibliography item. "
                              + "Options are tagged formats (ads, bibtex, bibtexabs, "
                              + "endnote, medlars, procite, refworks, ris), LaTeX formats "
                              + "(aastex, icarus, mnras, soph), and XML formats (dcxml, "
                              + "refxml, refabsxml, rss, votable). Any other string will "
                              + "be understood as `custom` formatting. For custom, see: "
                              + "http://adsabs.github.io/help/actions/export"
                              )
                        )
    parser.add_argument("-F", "--format-raw", type=str,
                        default='%R  # %3h_%Y_%q_%V_%p %T %ZAuthorSep:" " ',
                        help=("The output format for the raw file. ")
                        )
    parser.add_argument("-n", "--num-iter", default=500, type=int,
                        help="number of iterations (default=500)")
    parser.add_argument("-t", "--dtime", default=5, type=float,
                        help="time between iterations (default=5s)")
    parser.add_argument("-i", "--info-interval", default=20, type=int,
                        help="number of iterations between info prints (default=20)")

    print("1")
    args = parser.parse_args(args)
    print("2")
    token = _check_token()
    print("3")
    arg_ads = args.lib_or_file
    print("4")
    # if Path(arg_ads).exists():  # If you gave a file with ADS bibcodes
    #     bibs_old = read_sort_bib_ads(arg_ads)  # only the bibcodes

    # else:  # If it is library ID
    #   bibs, last_modified = query_lib(arg_ads, token=token)

    bibs_old, last_modified_old, name = query_lib(arg_ads, token=token)
    print("5")
    arg_add = args.additional_file
    adds_old, adds2_old = read_bib_add(arg_add)  # the raw file content & list of citekeys
    rawfile = None if args.rawfile == "none" else args.rawfile
    query_kw = dict(
        token=token,
        options=dict(sort=args.sort_option),
        fmt=args.format,
        journalname=args.journal,
    )
    if rawfile is not None:
        if args.format != "bibtex":
            raise ValueError("Currently rawfile is only supported for `-f bibtex`.")

        query_kw_raw = dict(
            token=token,
            options=dict(sort=args.sort_option),
            fmt=args.format_raw,
            journalname=args.journal,
        )

    bibtex_ads = query_ads(bibs_old, **query_kw)
    print("6")

    # if rawfile is not None:
    #     query_ads(bibs_old, **query_kw_raw)

    update = True
    for i in range(args.num_iter):
        adds, adds2 = read_bib_add(arg_add)
        if i != 0:
            try:
                bibs, last_modified, _ = query_lib(arg_ads, token=token)
                # only the bibcodes
            except json.JSONDecodeError:
                continue  # if the ADS API is down, just wait for the next iteration
            update = False
        else:
            last_modified = last_modified_old

        if last_modified != last_modified_old:
            update = True
            bibtex_ads = query_ads(bibs, **query_kw)
            print_infostr(name, bibs, bibs_old)
            bibs_old = bibs
            last_modified_old = last_modified

        if (adds != adds_old) or (adds2 != adds2_old):
            update = True
            print_infostr(arg_add, adds2, adds2_old)
            adds_old = adds
            adds2_old = adds2

        if update:
            with open(args.output, "w+") as ff:
                ff.writelines(bibtex_ads)
                try:
                    ff.writelines(adds)
                except FileNotFoundError:
                    pass
            print(f"Updated: {args.output} \n({datetime.now()})\n")

            if rawfile is not None:
                make_rawfile(bibtex_ads, rawfile)

        if (i > 0) and (i % args.info_interval == 0):
            pct = 100 * i / args.num_iter
            print(f"[INFORMATION] Iteration: {i} / {args.num_iter} ({pct:.1f} %) reached.")

        time.sleep(args.dtime)
