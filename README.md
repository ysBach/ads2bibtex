# ads2bibtex
Make ADS style inputs into bibtex file, by querying to NASA ADS.

**Warning**: Although I could not find the description, ADS ``limits users to 5000 requests/day (on a rolling 24-hour window)`` [Lockhart, K. 2023-03-07, priv. comm.].

# Usage
Please note that this repo is under a heavy development for my personal use. Currently, the following will work:

    # Simply download entry as bibtex
    ads2bibtex <library ID> -o outputdir/ref.bib

    # If you have "additional" entry that is not registered to ADS
    ads2bibtex <library ID> -a bib_add.txt -o outputdir/ref.bib

    # If you want ISO4 style journal names (e.g., \apj --> Astrophys. J.)
    #   use `-j full` for the full journal name
    ads2bibtex <library ID> -o outputdir/ref.bib -j iso4

    # If you want to save the raw bibcodes as bib_raw.txt
    ads2bibtex <library ID> -r bib_raw.txt -o outputdir/ref.bib

    # If you want to save the raw bibcodes as bib_raw.txt
    #   use -F (--format-raw) to set the save style
    ads2bibtex <library ID> -r bib_raw.txt -o outputdir/ref.bib


# Requirements
- `nltk` (for abbreviation of words)
- `regex` (also used in `nltk` https://pypi.org/project/regex/)
- `colorama` (for colorful output on terminal)

The `iso4/` is directly adopted from [`adlpr/iso4`](https://github.com/adlpr/iso4), and underwent minor tweak to cope with the more recent LTWA version

ADS provides some example notes ([GitHub](https://github.com/adsabs/adsabs-dev-api), [nbviewer](https://nbviewer.jupyter.org/github/adsabs/adsabs-dev-api/tree/master/)).

Explanations are scattered to many places, such as
* [Full API Docs](https://ui.adsabs.harvard.edu/help/api/api-docs.html#auth)
* [Export API](https://nbviewer.jupyter.org/github/adsabs/adsabs-dev-api/blob/master/Export_API.ipynb)
* [Search API](https://nbviewer.jupyter.org/github/adsabs/adsabs-dev-api/blob/master/Search_API.ipynb): this explains most of the APIs I guess.

Abbreviation file from LTWA (version 2021-07-02, retrieved 2022-12-27) from: http://www.issn.org/services/online-services/access-to-the-ltwa/