import json
import re

import requests

__all__ = ["_check_token", "change_journal_name",
           "read_sort_bib_ads", "read_bib_add", "query_ads",
           "query_lib", "make_rawfile", "extract_cite_keys"]


# Journal name abbreviations used in ADS
# I have no idea why ADS failed to give full list properly... I had to combine
# their website and style files manually, and expand the abbreviations to full
# names. See https://ui.adsabs.harvard.edu/help/actions/journal-macros
# NOTE: apjl/apjs must preceed apj, otherwise apjl will be replaced by, e.g.,
#   "Astrophysical Journall" (double l at the end). Same for aapr/aaps & aap,
#   nar/nat & na
JOURNAL_MACRO = {
    "aas": "American Astronomical Society Meeting Abstracts",
    "aj": "Astronomical Journal",
    "actaa": "Acta Astronomica",
    "araa": "Annual Review of Astron and Astrophysis",
    "apjl": "Astrophysical Journal, Letters",
    "apjs": "Astrophysical Journal, Supplement",
    "apj": "Astrophysical Journal",
    "ao": "Applied Optics",
    "apss": "Astrophysics and Space Science",
    "aapr": "Astronomy and Astrophysics Reviews",
    "aaps": "Astronomy and Astrophysics, Supplement",
    "aap": "Astronomy and Astrophysics",
    "aplett": "Astrophysics Letters",
    "apspr": "Astrophysics Space Physics Research",
    "azh": "Astronomicheskii Zhurnal",
    "baas": "Bulletin of the American Astronomical Society",
    "bac": "Bulletin of the Astronomical Institutes of Czechoslovakia",
    "bain": "Bulletin Astronomical Institute of the Netherlands",
    "caa": "Chinese Astronomy and Astrophysics",
    "cjaa": "Chinese Journal of Astronomy and Astrophysics",
    "dps": "American Astronomical Society/Division for Planetary Sciences Meeting Abstracts",
    "fcp": "Fundamental Cosmic Physics",
    "gca": "Geochimica Cosmochimica Acta",
    "grl": "Geophysics Research Letters",
    "iaucirc": "International Astronomical Union Cirulars",
    "icarus": "Icarus",
    "jaavso": "Journal of the American Association of Variable Star Observers",
    "jcap": "Journal of Cosmology and Astroparticle Physics",
    "jcp": "Journal of Chemical Physics",
    "jgr": "Journal of Geophysics Research",
    "jqsrt": "Journal of Quantitiative Spectroscopy and Radiative Transfer",
    "jrasc": "Journal of the Royal Astronomical Society of Canada",
    "maps": "Meteoritics and Planetary Science",
    "memras": "Memoirs of the Royal Astronomical Society",
    "memsai": "Mem. Societa Astronomica Italiana",
    "mnras": "Monthly Notices of the Royal Astronomical Society",
    "nat": "Nature",
    "nar": "New Astronomy Review",
    "na": "New Astronomy",
    "nphysa": "Nuclear Physics A",
    "pasa": "Publications of the Astronomical Society of Australia",
    "pasp": "Publications of the Astronomical Society of the Pacific",
    "pasj": "Publications of the Astronomical Society of Japan",
    "physrep": "Physics Reports",
    "physscr": "Physica Scripta",
    "planss": "Planetary Space Science",
    "pra": "Physical Review A",  # I removed ": General Physics"
    "prb": "Physical Review B",  # I removed ": Solid State"
    "prc": "Physical Review C",
    "prd": "Physical Review D",
    "pre": "Physical Review E",
    "prl": "Physical Review Letters",
    "procspie": "Proceedings of the Society of Photo-Optical Instrumentation Engineers",
    "psj": "Planetary Science Journal",
    "qjras": "Quarterly Journal of the Royal Astronomical Society",
    "rmxaa": "Revista Mexicana de Astronomia y Astrofisica",
    "skytel": "Sky and Telescope",
    "solphys": "Solar Physics",
    "sovast": "Soviet Astronomy",
    "ssr": "Space Science Reviews",
    "zap": "Zeitschrift fuer Astrophysik"
}


def _check_token():
    try:
        with open(".ads-token", "r") as ff:
            token = ff.read().strip()
    except FileNotFoundError:
        token = input(
            "\n\nGet your ADS API token: https://ui.adsabs.harvard.edu/user/settings/token"
            + "\nPaste your token (needed only for the first time within this directory): "
        )
        with open(".ads-token", "w") as ff:
            ff.write(token)
        print("Token saved in file `.ads-token`\n\n")
    return token


def _iso4fy_journals(raw_bibtex_text):
    try:
        from .iso4 import abbreviate
    except ImportError:
        raise ImportError(
            "Please install `nltk` package to use `iso4` journalname formatter."
        )
    # Expand all macros first
    lines = raw_bibtex_text.split("\n")
    for i, line in enumerate(lines):
        if line.strip().startswith("journal"):
            fullname = line.strip().split("{")[1].split("}")[0]
            abbrname = abbreviate(fullname, periods=True)
            lines[i] = line.replace(fullname, abbrname)
            # FIXME: When "Exception: Ambiguous word in title:" happens, we need to
            #   put, e.g., disambiguation_langs=['eng']. However, after updating to
            #   2021-07-02 LTWA version, I cannot see this exception happening.
    return "\n".join(lines)


def _expand_macros(raw_bibtex_text):
    for k, v in JOURNAL_MACRO.items():
        raw_bibtex_text = re.sub(r"\\{}".format(k), v, raw_bibtex_text)
    return raw_bibtex_text


def change_journal_name(raw_bibtex_text, journalname="ads"):
    if journalname == "ads":
        return raw_bibtex_text
    elif journalname == "full":
        return _expand_macros(raw_bibtex_text)
    elif journalname == "iso4":
        return _iso4fy_journals(_expand_macros(raw_bibtex_text))
    else:
        raise ValueError("Unknown journalname formatter: {}".format(journalname))


def read_sort_bib_ads(fname, sort=False):
    """Reads and sorts bibcodes from ADS format text.

    Parameters
    ----------
    sort : bool, optional.
        Whether to sort the bibcodes, by default False, because the inputs will
        be sorted by ADS in `query_ads` depending on `options`.

    Returns
    -------
    _bibs : list of str
        Sorted bibcodes in list.
    """
    try:
        with open(fname, 'r') as ff:
            _bibs = ff.read()
        _bibs += '\n'  # Add a new line at the end in case if not there.
        # First, ignore all comment (# or %) parts
        _bibs = re.sub(r"\s?[#%](.)*\s?\n", "\n", _bibs)
        # Second, split if more than 2 are in one line (comma-separated)
        _bibs = re.sub('\s?,\s?', '\n', _bibs)
        # Third, remove trailing white space (not necessary but...)
        _bibs = re.sub(r"\s?\n", "\n", _bibs)
        _bibs.replace(' ', '')
        # Finally convert to list, remove null string.
        _bibs = _bibs.split("\n")
        _bibs = list(filter(lambda a: a != '', _bibs))
        if sort:
            _bibs.sort()
    except (IndexError, TypeError, FileNotFoundError):
        _bibs = []
    return _bibs


def read_bib_add(fname):
    """Reads raw additional bibtex entries and extract citation keys.

    Returns:
        _adds: str
            The raw file content, which will only be used to check if there is
            any change in the file. If no file is found, returns empty str.
        _adds2: list of str
            The list of citation keys. If no file is found, returns empty list.
    """
    try:
        with open(fname, 'r') as ff:
            _adds = ff.read()
        _adds = str(_adds)
        # First, ignore all comment parts
        _adds2 = re.sub(r"\s?[#%](.)*\s?\n", "\n", _adds)
        _adds2 = _adds2.split("\n")
        _adds2 = list(filter(lambda a: a != '', _adds2))
        _adds2 = re.findall(r"@\w+{(.+),", _adds)
    except (TypeError, FileNotFoundError):
        _adds = ""
        _adds2 = []
    return _adds, _adds2


def query_ads(bibcodes, token, options=dict(sort="date asc"), fmt="bibtex",
              journalname="ads", url="https://api.adsabs.harvard.edu/v1/export/"):
    """Query ADS API and return the response.

    Parameters
    ----------
    bibcodes : list of str
        List of ADS stule bibcodes to query (e.g., output of
        `read_sort_bib_ads`).
    token : str
        ADS API token.
    options : dict, optional
        Options for ADS API, by default ``dict(sort="date asc")``
    fmt : str, optional
        Format of the response, by default ``"bibtex"``. Options are tagged
        formats (``{"ads", "bibtex", "bibtexabs", "endnote", "medlars",
        "procite", "refworks", "ris"}``), LaTeX formats (``{"aastex", "icarus",
        "mnras", "soph"}``), and XML formats (``{"dcxml", "refxml",
        "refabsxml", "rss", "votable"}``). Any other string will be understood
        as "custom" formatting. See ADS API documentation for details.
    url : str, optional
        ADS API URL, by default
        ``"https://api.adsabs.harvard.edu/v1/export/"``.
    journalname : str, optional
        Journal name to be used. Default ``"ads"``, which uses the raw output
        of ADS (e.g., r"\aj" for the "Astronomical Journal"). Other options
        implemented are "full", which uses the full journal name (e.g.,
        "Astronomical Journal").

    Returns
    -------
    response : dict
        Response from ADS API.
    """
    # Duplicated bibs will automatically be removed by ADS..! Wow!
    options.update({"bibcode": bibcodes})

    if fmt not in ["ads", "bibtex", "bibtexabs", "endnote", "medlars",
                   "procite", "refworks", "ris", "aastex", "icarus", "mnras",
                   "soph", "dcxml", "refxml", "refabsxml", "rss", "votable"]:
        options.update({"format": fmt})
        fmt = "custom"

    r = requests.post(
        str(url) + str(fmt),
        headers={"Authorization": "Bearer " + token,
                 "Content-type": "application/json"},
        data=json.dumps(options)
    )
    try:
        raw = r.json()["export"]
    except KeyError:
        raise ValueError("Error in ADS API query. Check your token..? See:", r.json())

    return change_journal_name(raw, journalname=journalname)


def query_lib(library_id, token, url="https://api.adsabs.harvard.edu/v1/biblib/libraries/"):
    """Query ADS Library contents (upto 10000 rows hard-coded)

    Parameters
    ----------
    library_id : str
        The library id to query.
    token : str
        ADS API token.
    url : str, optional
        ADS API URL, by default
        ``"https://api.adsabs.harvard.edu/v1/biblib/libraries/"``.

    Returns
    -------
    documents : list of bibcode(str)
        Response from ADS API.
    """
    r = requests.get(
        str(url) + library_id + "?rows=10000",
        headers={"Authorization": "Bearer " + token,
                 "Content-type": "application/json"},
    )
    try:
        _res = r.json()
        meta = _res["metadata"]
        return (_res["documents"], meta["date_last_modified"],
                "ADS Library: " + meta["name"])
    except KeyError:
        raise ValueError("Error in ADS API query. Check your token..? See:", r.json())


def make_rawfile(bibtex_ads, rawfile):
    bibs = []
    auths = []
    tits = []
    for line in bibtex_ads.split("\n"):
        line = line.strip()
        if line.startswith("@"):
            bib = line.split("{")[1].split(",")[0]
            if len(bib) == 19:
                bibs.append(bib)
        elif line.startswith("author ="):
            line = line.split(" = {")[1][:-2]
            lasts = re.findall("[^{}]*(?=\})", line)
            lasts = [l for l in lasts if l]
            if len(lasts) > 3:
                auths.append(lasts[0] + f"+{len(lasts) - 1}")
            elif len(lasts) > 1:  # 2 or 3
                auths.append("+".join(lasts))
            else:  # 1
                auths.append(lasts[0])
        elif line.startswith("title ="):
            tits.append(line.split("{")[1][:-3])

    with open(rawfile, "w+") as ff:
        for bib, auth, tit in zip(bibs, auths, tits):
            ff.write(f"{bib}  # {auth} || {tit}\n")


def extract_cite_keys(texfile):
    with open(texfile, "r") as ff:
        contents = "".join(ff.readlines())

    rx = re.compile(r'''(?<!\\)%.+|(\\(?:no)?citep?\{((?!\*)[^{}]+)\})''')
    keys = []
    for _m in rx.finditer(contents):
        if _m.group(2):
            _keys = _m.group(2).split(",")
            for _key in _keys:
                _key = _key.strip()
                if _key[:4].isdigit() and len(_key) == 19:
                    keys.append(_key)

    return keys
