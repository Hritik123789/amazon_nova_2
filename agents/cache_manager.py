# -*- coding: utf-8 -*-
"""
Cache Manager for CityPulse Agents
Implements intelligent caching to reduce costs for frequent runs
"""

import json
import os
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Any


class CacheManager:
    """Manages caching for agent data with TTL and invalidation"""
    
    def __init__(self, cache_dir: str = ".cache", default_ttl_hours: int = 6):
        """
        Initialize cache manager
        
        Args:
            cache_dir: Directory to store cache files
            default_ttl_hours: Default time-to-live for cache entries (hours)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.default_ttl = timedelta(hours=default_ttl_hours)
        
        # Cache metadata file
        self.metadata_file = self.cache_dir / "cache_metadata.json"
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict:
        """Load cache metadata"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_metadata(self):
        """Save cache metadata"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            print(f"⚠️  Failed to save cache metadata: {e}")
    
    def _generate_cache_key(self, agent_name: str, params: Dict = None) -> str:
        """
        Generate cache key from agent name and parameters
        
        Args:
            agent_name: Name of the agent
            params: Optional parameters that affect the output
            
        Returns:
            Cache key string
        """
        if params:
            # Sort params for consistent hashing
            param_str = json.dumps(params, sort_keys=True)
            param_hash = hashlib.md5(param_str.encode()).hexdigest()[:8]
            return f"{agent_name}_{param_hash}"
        return agent_name
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """Get file path for cache key"""
        return self.cache_dir / f"{cache_key}.json"
    
    def get(self, agent_name: str, params: Dict = None, ttl_hours: Optional[int] = None) -> Optional[Any]:
        """
        Get cached data if valid
        
        Args:
            agent_name: Name of the agent
            params: Optional parameters
            ttl_hours: Custom TTL in hours (overrides default)
            
        Returns:
            Cached data if valid, None otherwise
        """
        cache_key = self._generate_cache_key(agent_name, params)
        cache_path = self._get_cache_path(cache_key)
        
        # Check if cache exists
        if not cache_path.exists():
            return None
        
        # Check metadata
        if cache_key not in self.metadata:
            return None
        
        meta = self.metadata[cache_key]
        cached_at = datetime.fromisoformat(meta['cached_at'])
        
        # Check TTL
        ttl = timedelta(hours=ttl_hours) if ttl_hours else self.default_ttl
        if datetime.now() - cached_at > ttl:
            # Cache expired
            return None
        
        # Load cached data
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"✓ Cache hit for {agent_name} (age: {(datetime.now() - cached_at).seconds // 60} minutes)")
            return data
        except Exception as e:
            print(f"⚠️  Failed to load cache: {e}")
            return None
    
    def set(self, agent_name: str, data: Any, params: Dict = None, metadata: Dict = None):
        """
        Cache data
        
        Args:
            agent_name: Name of the agent
            data: Data to cache
            params: Optional parameters
            metadata: Optional metadata (cost, tokens, etc.)
        """
        cache_key = self._generate_cache_key(agent_name, params)
        cache_path = self._get_cache_path(cache_key)
        
        # Save data
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Update metadata
            self.metadata[cache_key] = {
                'agent_name': agent_name,
                'cached_at': datetime.now().isoformat(),
                'params': params,
                'metadata': metadata or {}
            }
            self._save_metadata()
            
            print(f"✓ Cached data for {agent_name}")
        except Exception as e:
            print(f"⚠️  Failed to cache data: {e}")
    
    def invalidate(self, agent_name: str, params: Dict = None):
        """
        Invalidate cache for specific agent
        
        Args:
            agent_name: Name of the agent
            params: Optional parameters
        """
        cache_key = self._generate_cache_key(agent_name, params)
        cache_path = self._get_cache_path(cache_key)
        
        # Remove cache file
        if cache_path.exists():
            cache_path.unlink()
        
        # Remove metadata
        if cache_key in self.metadata:
            del self.metadata[cache_key]
            self._save_metadata()
        
        print(f"✓ Invalidated cache for {agent_name}")
    
    def clear_all(self):
        """Clear all cached data"""
        for cache_file in self.cache_dir.glob("*.json"):
            if cache_file.name != "cache_metadata.json":
                cache_file.unlink()
        
        self.metadata = {}
        self._save_metadata()
        
        print("✓ Cleared all cache")
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        total_entries = len(self.metadata)
        valid_entries = 0
        expired_entries = 0
        total_size = 0
        
        for cache_key, meta in self.metadata.items():
            cache_path = self._get_cache_path(cache_key)
            
            if cache_path.exists():
                total_size += cache_path.stat().st_size
                
                cached_at = datetime.fromisoformat(meta['cached_at'])
                if datetime.now() - cached_at <= self.default_ttl:
                    valid_entries += 1
                else:
                    expired_entries += 1
        
        return {
            'total_entries': total_entries,
            'valid_entries': valid_entries,
            'expired_entries': expired_entries,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2)
        }
    
    def cleanup_expired(self):
        """Remove expired cache entries"""
        removed = 0
        
        for cache_key, meta in list(self.metadata.items()):
            cached_at = datetime.fromisoformat(meta['cached_at'])
            
            if datetime.now() - cached_at > self.default_ttl:
                cache_path = self._get_cache_path(cache_key)
                if cache_path.exists():
                    cache_path.unlink()
                
                del self.metadata[cache_key]
                removed += 1
        
        if removed > 0:
            self._save_metadata()
            print(f"✓ Removed {removed} expired cache entries")
        
        return removed


# Singleton instance
_cache_manager = None


def get_cache_manager() -> CacheManager:
    """Get global cache manager instance"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager
