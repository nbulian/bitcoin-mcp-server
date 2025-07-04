"""Market data and price information tools."""

from typing import Dict, Any, Optional
import httpx
from ..utils.errors import ValidationError

class MarketTools:
    """Bitcoin market data tools."""
    
    def __init__(self):
        self.external_client = httpx.AsyncClient(timeout=30.0)
        self.coingecko_api = "https://api.coingecko.com/api/v3"
    
    async def get_current_price(self, currency: str = "usd") -> Dict[str, Any]:
        """
        Get current Bitcoin price in specified currency.
        
        Args:
            currency: Target currency (usd, eur, btc, etc.)
            
        Returns:
            Dict containing current price information
        """
        try:
            url = f"{self.coingecko_api}/simple/price"
            params = {
                "ids": "bitcoin",
                "vs_currencies": currency.lower(),
                "include_market_cap": "true",
                "include_24hr_vol": "true",
                "include_24hr_change": "true",
                "include_last_updated_at": "true"
            }
            
            response = await self.external_client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            bitcoin_data = data.get("bitcoin", {})
            currency_upper = currency.upper()
            
            return {
                "currency": currency_upper,
                "price": bitcoin_data.get(currency.lower()),
                "market_cap": bitcoin_data.get(f"usd_market_cap"),
                "volume_24h": bitcoin_data.get(f"usd_24h_vol"),
                "change_24h": bitcoin_data.get(f"usd_24h_change"),
                "last_updated": bitcoin_data.get("last_updated_at")
            }
        except httpx.HTTPError as e:
            raise ValidationError(f"Failed to fetch Bitcoin price: {str(e)}")
        except Exception as e:
            raise ValidationError(f"Error getting market data: {str(e)}")
    
    async def get_price_history(self, days: int = 7, currency: str = "usd") -> Dict[str, Any]:
        """
        Get Bitcoin price history for specified period.
        
        Args:
            days: Number of days of history (max 365)
            currency: Target currency
            
        Returns:
            Dict containing price history
        """
        if days <= 0 or days > 365:
            raise ValidationError("Days must be between 1 and 365", "days")
        
        try:
            url = f"{self.coingecko_api}/coins/bitcoin/market_chart"
            params = {
                "vs_currency": currency.lower(),
                "days": days,
                "interval": "daily" if days > 30 else "hourly"
            }
            
            response = await self.external_client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            prices = data.get("prices", [])
            market_caps = data.get("market_caps", [])
            volumes = data.get("total_volumes", [])
            
            # Format data points
            history = []
            for i, price_point in enumerate(prices):
                history.append({
                    "timestamp": price_point[0],
                    "price": price_point[1],
                    "market_cap": market_caps[i][1] if i < len(market_caps) else None,
                    "volume": volumes[i][1] if i < len(volumes) else None
                })
            
            return {
                "currency": currency.upper(),
                "period_days": days,
                "data_points": len(history),
                "price_history": history,
                "summary": {
                    "start_price": history[0]["price"] if history else None,
                    "end_price": history[-1]["price"] if history else None,
                    "min_price": min(point["price"] for point in history) if history else None,
                    "max_price": max(point["price"] for point in history) if history else None,
                    "avg_price": sum(point["price"] for point in history) / len(history) if history else None
                }
            }
        except httpx.HTTPError as e:
            raise ValidationError(f"Failed to fetch Bitcoin price history: {str(e)}")
        except Exception as e:
            raise ValidationError(f"Error getting price history: {str(e)}")
    
    async def get_market_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive Bitcoin market statistics.
        
        Returns:
            Dict containing market statistics
        """
        try:
            url = f"{self.coingecko_api}/coins/bitcoin"
            params = {
                "localization": "false",
                "tickers": "false",
                "market_data": "true",
                "community_data": "false",
                "developer_data": "false",
                "sparkline": "false"
            }
            
            response = await self.external_client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            market_data = data.get("market_data", {})
            
            return {
                "basic_info": {
                    "name": data.get("name"),
                    "symbol": data.get("symbol"),
                    "rank": data.get("market_cap_rank"),
                    "last_updated": data.get("last_updated")
                },
                "price_data": {
                    "current_price_usd": market_data.get("current_price", {}).get("usd"),
                    "market_cap_usd": market_data.get("market_cap", {}).get("usd"),
                    "total_volume_usd": market_data.get("total_volume", {}).get("usd"),
                    "high_24h_usd": market_data.get("high_24h", {}).get("usd"),
                    "low_24h_usd": market_data.get("low_24h", {}).get("usd"),
                    "price_change_24h": market_data.get("price_change_24h"),
                    "price_change_percentage_24h": market_data.get("price_change_percentage_24h"),
                    "price_change_percentage_7d": market_data.get("price_change_percentage_7d"),
                    "price_change_percentage_30d": market_data.get("price_change_percentage_30d"),
                    "price_change_percentage_1y": market_data.get("price_change_percentage_1y")
                },
                "supply_data": {
                    "circulating_supply": market_data.get("circulating_supply"),
                    "total_supply": market_data.get("total_supply"),
                    "max_supply": market_data.get("max_supply")
                },
                "all_time": {
                    "ath": market_data.get("ath", {}).get("usd"),
                    "ath_date": market_data.get("ath_date", {}).get("usd"),
                    "ath_change_percentage": market_data.get("ath_change_percentage", {}).get("usd"),
                    "atl": market_data.get("atl", {}).get("usd"),
                    "atl_date": market_data.get("atl_date", {}).get("usd"),
                    "atl_change_percentage": market_data.get("atl_change_percentage", {}).get("usd")
                }
            }
        except httpx.HTTPError as e:
            raise ValidationError(f"Failed to fetch Bitcoin market stats: {str(e)}")
        except Exception as e:
            raise ValidationError(f"Error getting market stats: {str(e)}")
    
    async def get_fear_greed_index(self) -> Dict[str, Any]:
        """
        Get Bitcoin Fear & Greed Index.
        
        Returns:
            Dict containing fear & greed index data
        """
        try:
            url = "https://api.alternative.me/fng/?limit=30"
            
            response = await self.external_client.get(url)
            response.raise_for_status()
            data = response.json()
            
            current = data.get("data", [{}])[0]
            historical = data.get("data", [])
            
            return {
                "current": {
                    "value": current.get("value"),
                    "value_classification": current.get("value_classification"),
                    "timestamp": current.get("timestamp"),
                    "time_until_update": current.get("time_until_update")
                },
                "historical": [
                    {
                        "value": item.get("value"),
                        "classification": item.get("value_classification"),
                        "timestamp": item.get("timestamp")
                    }
                    for item in historical[:10]  # Last 10 days
                ],
                "metadata": data.get("metadata", {})
            }
        except httpx.HTTPError as e:
            raise ValidationError(f"Failed to fetch Fear & Greed Index: {str(e)}")
        except Exception as e:
            raise ValidationError(f"Error getting Fear & Greed Index: {str(e)}")
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if hasattr(self, 'external_client'):
            await self.external_client.aclose()