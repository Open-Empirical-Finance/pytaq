# Overview of pyTAQ

pyTAQ is a Python package for processing and analyzing TAQ data. It is designed to be used in conjunction with the TAQ data provided by the [Wharton Research Data Services](https://wrds-www.wharton.upenn.edu/). pyTAQ currently only supports the Daily TAQ format.

pyTAQ was originally developed while working on [Grégoire & Martineau (2022)](https://doi.org/10.1111/1475-679X.12394) and as also been used in [Akey, Grégoire & Martineau (2022)](https://doi.org/10.1016/j.jfineco.2021.12.006).

## Main features

- Replicates the cleaning procedure of [Holden and Jacobsen (2014)](https://doi.org/10.1111/jofi.12127) by default.
- Allows for a great deal of flexibility in the cleaning procedure.
- Multiple signing conventions for the trade sign:
    - Tick rule
    - LR: [Lee and Ready (1991)](https://doi.org/10.1111/j.1540-6261.1991.tb02683.x)
    - EMO: [Ellis, Michaely, O'Hara (2000)](https://doi.org/10.2307/2676254)
    - CLNV: [Chakrabarty, Li, Nguyen & Van Ness (2007)](https://doi.org/10.1016/j.jbankfin.2007.03.003)
- Indentify and sign retail trades:
    - BJZ: [Boehmer, Jones & Zhang (2021)](https://doi.org/10.1111/jofi.13033)
- Multiple efficiency and liquidity metrics:
    - Time-weighted average quoted spread
    - Effective spread, realized spread, and price impact:
      - Simple average, share-weighted average, and dollar-weighted average
      - Flexible to allow for grouping based on trade characteristics


## Installation

pyTAQ is available on PyPI and can be installed with pip or poetry.

=== pip

```bash
pip install pytaq
```

=== poetry

```bash
poetry add pytaq
```

## Aknowledgements

TODO!!!

The package was developed by Vincent Grégoire while working at HEC Montréal on projects funded by SSHRC (grants #mj and ##) and IVADO (grant ##).

I would like to thank Charles Martineau for his help in the development of the package, and Mohammad Ebrahimi for his help in the development of the documentation and on the review of the code.

## References

> Holden, C. W., & Jacobsen, S. (2014). Liquidity measurement problems in fast, competitive markets: Expensive and cheap solutions. _The Journal of Finance_, _69_(4), 1747-1785.

> Lee, C. M., & Ready, M. J. (1991). Inferring trade direction from intraday data. _The Journal of Finance_, _46_(2), 733-746.

> Chakrabarty, B., Li, B., Nguyen, V., & Van Ness, R. A. (2007). Trade classification algorithms for electronic communications network trades. Journal of Banking & Finance, 31(12), 3806-3821.

> Boehmer, E., Jones, C. M., Zhang, X., & Zhang, X. (2021). Tracking retail investor activity. The Journal of Finance, 76(5), 2249-2305.

> Ellis, K., Michaely, R., & O'Hara, M. (2000). The accuracy of trade classification rules: Evidence from Nasdaq. Journal of financial and Quantitative Analysis, 35(4), 529-551.

> Akey, P., Grégoire, V., & Martineau, C. (2022). Price revelation from insider trading: Evidence from hacked earnings news. Journal of Financial Economics, 143(3), 1162-1184.

> Gregoire, V., & Martineau, C. (2022). How is Earnings News Transmitted to Stock Prices?. Journal of Accounting Research, 60(1), 261-297.