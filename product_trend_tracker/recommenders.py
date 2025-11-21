# Wrapper module so tests can import the recommender classes.

from product_trend_tracker.recommender_api import (
    PopularityRecommender,
    ItemItemCF,
)

__all__ = [
    "PopularityRecommender",
    "ItemItemCF",
]
