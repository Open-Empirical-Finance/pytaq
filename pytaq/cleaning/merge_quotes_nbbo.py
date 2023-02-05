import pandas as pd


def merge_quotes_nbbo(
    nbbo: pd.DataFrame, quote: pd.DataFrame, keep_changes_only: bool = True
) -> pd.DataFrame:
    """Merges the NBBO and Quote dataframes to create the official complte NBBO.

    With default options used to clean the input dataframes, this function should
    yield the same results as the official complete NBBO table in WRDS.

    Args:
        nbbo (pd.DataFrame): NBBO quotes
        quote (pd.DataFrame): Quotes.
        keep_changes_only (bool, optional): Only keep the last observation for each timestamp. Defaults to True.

    Returns:
        pd.DaraFrame: Official complete NBBO
    """

    df = nbbo.append(quote).sort_values(["symbol", "timestamp", "qu_seqnum"])

    # Remove duplicate quotes at same microsecond (keep last one based
    # on sequence number)

    if keep_changes_only:
        df = df.groupby(["symbol", "timestamp"]).last().reset_index()

    # # Drop obs with no change in obs.
    # df = df.groupby(['symbol', 'best_bid', 'best_bidsizeshares',
    #                  'best_bidex', 'best_ask', 'best_asksizeshares',
    #                  'best_askex']).first().reset_index()

    return df
