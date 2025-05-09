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
        Exclude ultra-premium services (e.g., 1dayAM, 2dayAM, First Overnight) from fastest calculation.
        
        Args:
            options: List of rate options from different carriers
            
        Returns:
            RateResponse containing cheapest and fastest options
        """
        if not options:
            raise ValueError("No rate options provided")

        # Cheapest: always the lowest cost
        sorted_by_cost = sorted(options, key=lambda x: x.cost)
        cheapest = sorted_by_cost[0]

        # Exclude ultra-premium services for fastest
        def is_ultra_premium(service_name: str) -> bool:
            name = service_name.lower()
            return ("am" in name) or ("first" in name)

        non_ultra_premium = [opt for opt in options if not is_ultra_premium(opt.service_name)]
        if not non_ultra_premium:
            # fallback: if all are ultra-premium, use all
            non_ultra_premium = options

        # Find soonest estimated_delivery among non-ultra-premium
        soonest_date = min(opt.estimated_delivery for opt in non_ultra_premium)
        soonest_options = [opt for opt in non_ultra_premium if opt.estimated_delivery == soonest_date]

        # If multiple, pick lowest cost among them
        fastest = min(soonest_options, key=lambda x: x.cost)

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
