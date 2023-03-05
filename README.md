# ads2bibtex
Make ADS style inputs into bibtex file, by querying to NASA ADS.


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