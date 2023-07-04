# ads2bibtex
Make ADS style inputs into bibtex file, by querying to NASA ADS.

I created this script to reduce the time I waste on creating BibTeX files for multiple journals and my thesis.

## Purpose
I created this script to **run in the background** on my terminal while I crawl references on ADS. When I [add a paper to my library on ADS](http://adsabs.github.io/help/libraries/creating-libraries), this script automatically detects the change by checking the *last-modified timestamp* and updates the local BibTeX file accordingly.


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


## First Usage

Try:

    ads2bibtex -h

The simplest usage:

    ads2bibtex <library ID> -o ysBach_PhDT_SNU/references.bib

This downloads entry as bibtex, using ADS default format (bibtex). For different journals use `-f` (see `ads2bibtex -h`).

## Usage Tips
### "Additional" Entry
There are things that are **not registered to ADS**. If you have an additional file for them:

    ads2bibtex <library ID> -a bib_add.txt -o outputdir/references.bib

<details><summary>Contents of my <code>bib_add.txt</code> as an example (click)</summary>
<p>
I always use `-f bibtex` as default. Thus, my "additional file" is in BibTeX format:

```
% A part of my own bib_add.txt
@ARTICLE{2022_SAG_NICpolpy,
       author = {{Bach}, Yoonsoo P. and {Ishiguro}, Masateru and {Takahashi}, Jun and {Geem}, Jooyeon},
        title = "{Data Reduction Process and Pipeline for the NIC Polarimetry Mode in Python, NICpolpy}",
      journal = {Stars and Galaxies (arXiv:2212.14167)},
     keywords = {methods: data analysis, methods: observational, techniques: image processing, techniques: polarimetric},
         year = 2022,
        month = dec,
       volume = {5},
          eid = {4},
        pages = {4},
archivePrefix = {arXiv},
       eprint = {2212.14167},
 primaryClass = {astro-ph.IM},
       adsurl = {https://ui.adsabs.harvard.edu/abs/2022arXiv221214167B},
      adsnote = {}
}

@INPROCEEDINGS{gil-hutton-data,
title= {Catalogue of asteroid polarization curves},
author = {Gil-Hutton, R.},
year = {2017},
booktitle= {ACM (Asteroid, Comets, Meteors) 2017, Montevideo},
pages={Poster1.d.17},
URL= {http://gcpsj.sdf-eu.org/catalogo.html},
       adsurl = {},
      adsnote = {}
}
```

</p>
</details>

* **Important Note**: `ads2bibtex` just copies and pastes the contents of the "additional file" (`-a`, `--additional-file`) at the end of the ADS-queried results. Thus, if you use `-f` option, you must have the "additional file" written in **that specific format**.


### Journal Names
You want the **full name** of the journals? Use `-j full` to make ``\apj`` → ``Astrophysicial Journal``:

    ads2bibtex <library ID> -o outputdir/references.bib -j full

You want **ISO4 style**? You need to install `nltk` and use `-j iso4` to make ``\apj`` → ``Astrophys. J.``:

    ads2bibtex <library ID> -o outputdir/references.bib -j iso4

These are useful for, e.g., non-astronomy specific journals like Nature/Science (or even thesis).


### Less Useful Functionalities
Some tips for other arguments (use ``ads2bibtex -h`` for full help)
* ``-n`` (``-num-iter``): number of iterations (default=500)
  * **Warning**: Although I could not find the description, ADS "**limits users to 5000 requests/day (on a rolling 24-hour window)**", and there is no way to circumvent this limit [Lockhart, K. 2023-03-07, priv. comm. via email through help desk].
* ``-t`` (``--dtime``): time between iterations (default=5s)
* ``-i`` (``--info-interval``): number of iterations between info prints (default=20)

<details><summary>For debugging purpose...</summary>
<p>

If you want to save a separate output as *ADS-Export* functionality as ``bib_raw.txt`` for some reason (for me, I made it purely for debugging purpose):

    ads2bibtex <library ID> -r bib_raw.txt -o outputdir/references.bib

Use ``-f`` or ``-F`` (``--format`` or ``--format-raw``) to set the save style of output file and raw file, respectively. By default, ``-f`` is ``"bibtex"`` and ``-F`` is ``%R  # %3h_%Y_%q_%V_%p %T`` (a random testing format I used for debugging).

    ads2bibtex <library ID> -r bib_raw.txt -o outputdir/references.bib -F "%R  # %10.5N_%Y_%q_%V_%p %T"

This is the same as ADS's "Export → Custom Format". See [this help page](http://adsabs.github.io/help/actions/export) of ADS.

</p>
</details>


## Requirements
- `regex` (also used in `nltk` https://pypi.org/project/regex/)
- `colorama` (for colorful output on terminal)

To use abbreviation of words (``-j iso4``), you need `nltk`.


## Other Notes

### `iso4`
The `iso4/` is directly adopted from [`adlpr/iso4`](https://github.com/adlpr/iso4), and underwent minor tweak to cope with the more recent LTWA version.

The Abbreviation file from LTWA (version 2021-07-02, retrieved 2022-12-27): http://www.issn.org/services/online-services/access-to-the-ltwa/

### Notes by ADS
ADS provides some example notes:
* [GitHub](https://github.com/adsabs/adsabs-dev-api)
* [nbviewer](https://nbviewer.jupyter.org/github/adsabs/adsabs-dev-api/tree/master/)

Explanations are scattered to many places, such as:
* [Full API Docs](https://ui.adsabs.harvard.edu/help/api/api-docs.html#auth)
* [Export API](https://nbviewer.jupyter.org/github/adsabs/adsabs-dev-api/blob/master/Export_API.ipynb)
* [Search API](https://nbviewer.jupyter.org/github/adsabs/adsabs-dev-api/blob/master/Search_API.ipynb): this explains most of the APIs I guess.

