# -*- coding: utf-8 -*-
"""
Cached Agent Wrapper
Provides easy-to-use caching decorators and utilities for agents
"""

import functools
from typing import Callable, Any, Dict, Optional
from cache_manager import get_cache_manager


def cached_agent_run(agent_name: str, ttl_hours: int = 6, cache_params: Optional[Callable] = None):
    """
    Decorator to cache agent execution results
    
    Args:
        agent_name: Name of the agent (for cache key)
        ttl_hours: Time-to-live in hours
        cache_params: Optional function to extract cache parameters from function args
        
    Example:
        @cached_agent_run('news_agent', ttl_hours=6)
        def collect_news():
            # ... expensive operation
            return news_data
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            cache = get_cache_manager()
            
            # Extract cache parameters if provided
            params = None
            if cache_params:
                try:
                    params = cache_params(*args, **kwargs)
                except:
                    params = None
            
            # Try to get from cache
            cached_data = cache.get(agent_name, params=params, ttl_hours=ttl_hours)
            if cached_data is not None:
                print(f"💾 Using cached data for {agent_name}")
                return cached_data
            
            # Execute function
            print(f"🔄 No valid cache, executing {agent_name}...")
            result = func(*args, **kwargs)
            
            # Cache result
            if result is not None:
                cache.set(agent_name, result, params=params)
            
            return result
        
        return wrapper
    return decorator


class CachedAgentHelper:
    """Helper class for agents to use caching"""
    
    def __init__(self, agent_name: str, ttl_hours: int = 6):
        """
        Initialize cached agent helper
        
        Args:
            agent_name: Name of the agent
            ttl_hours: Default TTL in hours
        """
        self.agent_name = agent_name
        self.ttl_hours = ttl_hours
        self.cache = get_cache_manager()
    
    def get_cached_or_run(self, func: Callable, params: Dict = None, force_refresh: bool = False) -> Any:
        """
        Get cached data or run function
        
        Args:
            func: Function to execute if cache miss
            params: Optional parameters for cache key
            force_refresh: Force refresh even if cache exists
            
        Returns:
            Cached or fresh data
        """
        if force_refresh:
            print(f"🔄 Force refresh enabled, skipping cache for {self.agent_name}")
            result = func()
            if result is not None:
                self.cache.set(self.agent_name, result, params=params)
            return result
        
        # Try cache first
        cached_data = self.cache.get(self.agent_name, params=params, ttl_hours=self.ttl_hours)
        if cached_data is not None:
            print(f"💾 Using cached data for {self.agent_name}")
            return cached_data
        
        # Execute function
        print(f"🔄 No valid cache, executing {self.agent_name}...")
        result = func()
        
        # Cache result
        if result is not None:
            self.cache.set(self.agent_name, result, params=params)
        
        return result
    
    def invalidate(self, params: Dict = None):
        """Invalidate cache for this agent"""
        self.cache.invalidate(self.agent_name, params=params)
    
    def should_use_cache(self) -> bool:
        """Check if cache exists and is valid"""
        cached_data = self.cache.get(self.agent_name, ttl_hours=self.ttl_hours)
        return cached_data is not None


# Example usage functions

def example_news_agent_with_cache():
    """Example: News agent with caching"""
    
    @cached_agent_run('news_agent', ttl_hours=6)
    def collect_news():
        print("Collecting news from API...")
        # Expensive operation here
        return {"articles": [...]}
    
    # First call: executes function
    news = collect_news()
    
    # Second call within 6 hours: uses cache
    news = collect_news()


def example_social_agent_with_helper():
    """Example: Social agent with helper class"""
    
    helper = CachedAgentHelper('social_agent', ttl_hours=4)
    
    def collect_social_data():
        print("Collecting social media data...")
        # Expensive operation here
        return {"posts": [...]}
    
    # Get cached or run
    data = helper.get_cached_or_run(collect_social_data)
    
    # Force refresh
    data = helper.get_cached_or_run(collect_social_data, force_refresh=True)
    
    # Invalidate cache
    helper.invalidate()
