"""
Job storage implementations for stateless operation
"""

import json
import asyncio
from typing import Optional, Dict
from uuid import UUID
from datetime import datetime, timedelta
import logging

from src.core.interfaces import IJobStorage
from src.api.schemas_v2 import RawDataResponse

logger = logging.getLogger(__name__)


class InMemoryJobStorage(IJobStorage):
    """
    In-memory job storage with TTL support.
    Suitable for single-instance deployments or development.
    For production multi-instance deployments, use RedisJobStorage.
    """
    
    def __init__(self):
        self._storage: Dict[str, Dict] = {}
        self._cleanup_interval = 300  # 5 minutes
        self._last_cleanup = datetime.now()
        self.logger = logging.getLogger(__name__)
    
    async def store_job_result(self, job_id: UUID, result: RawDataResponse, ttl_seconds: int = 3600) -> bool:
        """Store job result with time-to-live"""
        try:
            expiry_time = datetime.now() + timedelta(seconds=ttl_seconds)
            
            self._storage[str(job_id)] = {
                'data': result.dict(),
                'expires_at': expiry_time,
                'created_at': datetime.now()
            }
            
            # Periodic cleanup
            await self._cleanup_expired()
            
            self.logger.debug(f"Stored job result for {job_id} with TTL {ttl_seconds}s")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store job result for {job_id}: {str(e)}")
            return False
    
    async def get_job_result(self, job_id: UUID) -> Optional[RawDataResponse]:
        """Retrieve job result by ID"""
        try:
            job_key = str(job_id)
            
            if job_key not in self._storage:
                return None
            
            job_data = self._storage[job_key]
            
            # Check if expired
            if datetime.now() > job_data['expires_at']:
                del self._storage[job_key]
                self.logger.debug(f"Job {job_id} expired, removed from storage")
                return None
            
            # Reconstruct response object
            return RawDataResponse(**job_data['data'])
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve job result for {job_id}: {str(e)}")
            return None
    
    async def delete_job_result(self, job_id: UUID) -> bool:
        """Delete job result"""
        try:
            job_key = str(job_id)
            
            if job_key in self._storage:
                del self._storage[job_key]
                self.logger.debug(f"Deleted job result for {job_id}")
                return True
            
            return True  # Consider non-existent as successfully deleted
            
        except Exception as e:
            self.logger.error(f"Failed to delete job result for {job_id}: {str(e)}")
            return False
    
    async def _cleanup_expired(self):
        """Remove expired job results"""
        try:
            now = datetime.now()
            
            # Only cleanup periodically to avoid overhead
            if (now - self._last_cleanup).seconds < self._cleanup_interval:
                return
            
            expired_keys = []
            for job_key, job_data in self._storage.items():
                if now > job_data['expires_at']:
                    expired_keys.append(job_key)
            
            for key in expired_keys:
                del self._storage[key]
            
            if expired_keys:
                self.logger.info(f"Cleaned up {len(expired_keys)} expired job results")
            
            self._last_cleanup = now
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup expired jobs: {str(e)}")
    
    def get_storage_stats(self) -> Dict:
        """Get storage statistics for monitoring"""
        return {
            'total_jobs': len(self._storage),
            'last_cleanup': self._last_cleanup.isoformat(),
            'oldest_job': min([job['created_at'] for job in self._storage.values()]).isoformat() if self._storage else None
        }


# Future Redis implementation for production use
class RedisJobStorage(IJobStorage):
    """
    Redis-based job storage for production multi-instance deployments.
    Provides true stateless operation with shared storage.
    """
    
    def __init__(self, redis_client=None):
        self.redis = redis_client
        self.logger = logging.getLogger(__name__)
        
        if not self.redis:
            self.logger.warning("Redis client not provided - falling back to in-memory storage")
            self._fallback = InMemoryJobStorage()
    
    async def store_job_result(self, job_id: UUID, result: RawDataResponse, ttl_seconds: int = 3600) -> bool:
        """Store job result with time-to-live in Redis"""
        if not self.redis:
            return await self._fallback.store_job_result(job_id, result, ttl_seconds)
        
        try:
            job_key = f"atlas:job:{job_id}"
            job_data = result.json()
            
            # Store with TTL
            await self.redis.setex(job_key, ttl_seconds, job_data)
            
            self.logger.debug(f"Stored job result for {job_id} in Redis with TTL {ttl_seconds}s")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store job result in Redis for {job_id}: {str(e)}")
            return False
    
    async def get_job_result(self, job_id: UUID) -> Optional[RawDataResponse]:
        """Retrieve job result by ID from Redis"""
        if not self.redis:
            return await self._fallback.get_job_result(job_id)
        
        try:
            job_key = f"atlas:job:{job_id}"
            job_data = await self.redis.get(job_key)
            
            if job_data is None:
                return None
            
            # Parse JSON data
            return RawDataResponse.parse_raw(job_data)
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve job result from Redis for {job_id}: {str(e)}")
            return None
    
    async def delete_job_result(self, job_id: UUID) -> bool:
        """Delete job result from Redis"""
        if not self.redis:
            return await self._fallback.delete_job_result(job_id)
        
        try:
            job_key = f"atlas:job:{job_id}"
            await self.redis.delete(job_key)
            
            self.logger.debug(f"Deleted job result from Redis for {job_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete job result from Redis for {job_id}: {str(e)}")
            return False