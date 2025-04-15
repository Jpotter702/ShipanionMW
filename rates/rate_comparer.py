# Rate Comparer
# TODO: Implement this module

from typing import List
from models.rate_response import RateOption, RateResponse
from utils.service_normalizer import ServiceTier

class RateComparer:
    def __init__(self):
        self._reasonable_price_multiplier = 1.5  # Consider options up to 50% more expensive than cheapest

    def compare_rates(self, options: List[RateOption]) -> RateResponse:
        """
        Compare shipping rates and return the cheapest and fastest options.
        
        Args:
            options: List of rate options from different carriers
            
        Returns:
            RateResponse containing cheapest and fastest options
        """
        if not options:
            raise ValueError("No rate options provided")

        # Sort options by cost
        sorted_by_cost = sorted(options, key=lambda x: x.cost)
        cheapest = sorted_by_cost[0]

        # Find fastest reasonably priced option
        fastest = None
        for option in sorted(options, key=lambda x: x.transit_days):
            if option.cost <= cheapest.cost * self._reasonable_price_multiplier:
                fastest = option
                break

        return RateResponse(
            cheapest_option=cheapest,
            fastest_option=fastest,
            all_options=options
        )

    def filter_by_service_tier(self, options: List[RateOption], tier: ServiceTier) -> List[RateOption]:
        """
        Filter rate options by service tier.
        
        Args:
            options: List of rate options
            tier: Service tier to filter by
            
        Returns:
            Filtered list of rate options
        """
        return [option for option in options if option.service_tier == tier]
