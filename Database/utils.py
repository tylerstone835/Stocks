import pandas as pd


def natural_join(left: pd.DataFrame,
                 right: pd.DataFrame,
                 how: str = 'inner'
                 ) -> pd.DataFrame | None:
    """
    Merges two pd.DataFrame objects based on overlapping column labels.
        :param left: Left pd.DataFrame in the join.
        :param right: Right pd.DataFrame in the join.
        :param how: Join type to be performed (e.g., inner, left, right, outer, cross)
        :return: Joined pd.DataFrame object.
    """
    columns_list = list(left.columns) + list(right.columns)

    dupe_labels_df = (pd.Series(columns_list)
                      .value_counts()
                      .reset_index()
                      )
    dupe_labels_list = dupe_labels_df.loc[dupe_labels_df['count'] > 1]['index'].to_list()

    if not dupe_labels_list:
        return

    return pd.merge(left=left, right=right, how=how, on=dupe_labels_list)
