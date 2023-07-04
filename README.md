# ads2bibtex
Make ADS style inputs into bibtex file, by querying to NASA ADS.

**Warning**: Although I could not find the description, ADS ``limits users to 5000 requests/day (on a rolling 24-hour window)`` [Lockhart, K. 2023-03-07, priv. comm.].

# Basic Usage
## First Step (One Time)

<details><summary>API Token (click)</summary>

**Get your own token**

* Go to [NASA ADS](https://ui.adsabs.harvard.edu/)
* Top right: `Log In`. After logging in...
* Top right: `Account` → `Settings`
* Left: `API Token`

Do **NOT** click `Generate a new key` unless you really need it!!
</details>

<details><summary>Make a Library (click)</summary>

**Make a Library you will use**

* Top right: `Account` → `ADS Libraries`
* Left: `ADD A LIBRARY` → Set the name of the library (e.g., "PhDT", "everything", "Bach+2023AJ").
* Select `Manage Access` Tab → copy <Library ID>: ``https://ui.adsabs.harvard.edu/public-libraries/<Library ID>``

</p>
</details>

Simply download entry as bibtex

    ads2bibtex <library ID> -o outputdir/ref.bib

## "Additional" Entry
(If you have a bibtex for things that are not registered to ADS)

    ads2bibtex <library ID> -a bib_add.txt -o outputdir/ref.bib

## ISO4
If you want ISO4 style journal names (e.g., not ``\apj`` but ``Astrophys. J.``).

    ads2bibtex <library ID> -o outputdir/ref.bib -j iso4

You may use use `-j full` for the full journal name (``Astrophysicial Journal``):

    ads2bibtex <library ID> -o outputdir/ref.bib -j full

These are useful for, e.g., non-astronomy specific journals (or even thesis).


## Less Useful Functionalities

If you want to save the raw bibcodes as bib_raw.txt

    ads2bibtex <library ID> -r bib_raw.txt -o outputdir/ref.bib

If you want to save the raw bibcodes as bib_raw.txt

    ads2bibtex <library ID> -r bib_raw.txt -o outputdir/ref.bib

Use ``-F`` (``--format-raw``) to set the save style.



# Requirements
- `regex` (also used in `nltk` https://pypi.org/project/regex/)
- `colorama` (for colorful output on terminal)

To use abbreviation of words (``-j iso4``), you need `nltk`.

## `iso4`
The `iso4/` is directly adopted from [`adlpr/iso4`](https://github.com/adlpr/iso4), and underwent minor tweak to cope with the more recent LTWA version


# Other Notes
ADS provides some example notes:
* [GitHub](https://github.com/adsabs/adsabs-dev-api)
* [nbviewer](https://nbviewer.jupyter.org/github/adsabs/adsabs-dev-api/tree/master/)

Explanations are scattered to many places, such as:
* [Full API Docs](https://ui.adsabs.harvard.edu/help/api/api-docs.html#auth)
* [Export API](https://nbviewer.jupyter.org/github/adsabs/adsabs-dev-api/blob/master/Export_API.ipynb)
* [Search API](https://nbviewer.jupyter.org/github/adsabs/adsabs-dev-api/blob/master/Search_API.ipynb): this explains most of the APIs I guess.

Abbreviation file from LTWA (version 2021-07-02, retrieved 2022-12-27) from: http://www.issn.org/services/online-services/access-to-the-ltwa/