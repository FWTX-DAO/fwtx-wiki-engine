"""
Scheduled sync job mechanism for Fort Worth data.

This module provides scheduled synchronization of Fort Worth municipal data
using background tasks and periodic updates.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from src.services.graphiti.index import graphiti
from src.services.sync.fort_worth_data import FortWorthDataSync

logger = logging.getLogger(__name__)


class DataSyncScheduler:
    """Manages scheduled data synchronization tasks."""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.sync_service = FortWorthDataSync(graphiti)
        self.is_running = False
        
    def start(self):
        """Start the scheduler with configured jobs."""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
            
        try:
            # Daily sync at 2 AM
            self.scheduler.add_job(
                self._run_daily_sync,
                CronTrigger(hour=2, minute=0),
                id='daily_sync',
                name='Daily Fort Worth Data Sync',
                replace_existing=True
            )
            
            # Weekly full sync on Sundays at 3 AM
            self.scheduler.add_job(
                self._run_weekly_full_sync,
                CronTrigger(day_of_week='sun', hour=3, minute=0),
                id='weekly_full_sync',
                name='Weekly Full Data Sync',
                replace_existing=True
            )
            
            # Hourly check for urgent updates
            self.scheduler.add_job(
                self._check_urgent_updates,
                CronTrigger(minute=0),  # Every hour
                id='hourly_check',
                name='Hourly Urgent Update Check',
                replace_existing=True
            )
            
            self.scheduler.start()
            self.is_running = True
            logger.info("Data sync scheduler started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
            raise
    
    def stop(self):
        """Stop the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Data sync scheduler stopped")
    
    async def _run_daily_sync(self):
        """Run daily incremental sync."""
        logger.info("Starting daily data sync...")
        try:
            # Sync only recent updates
            await self.sync_service.sync_from_fwtx_json()
            logger.info("Daily sync completed successfully")
        except Exception as e:
            logger.error(f"Daily sync failed: {e}")
    
    async def _run_weekly_full_sync(self):
        """Run weekly full sync."""
        logger.info("Starting weekly full sync...")
        try:
            await self.sync_service.run_full_sync()
            logger.info("Weekly full sync completed successfully")
        except Exception as e:
            logger.error(f"Weekly full sync failed: {e}")
    
    async def _check_urgent_updates(self):
        """Check for urgent updates that need immediate sync."""
        # This would check for critical updates like emergency ordinances
        # For now, it's a placeholder
        logger.debug("Checking for urgent updates...")
    
    async def trigger_manual_sync(self, sync_type: str = "incremental"):
        """Manually trigger a sync operation."""
        logger.info(f"Manual {sync_type} sync triggered")
        
        try:
            if sync_type == "full":
                await self.sync_service.run_full_sync()
            elif sync_type == "services":
                await self.sync_service.sync_from_fwtx_json()
            elif sync_type == "governance":
                await self.sync_service.sync_governance_structure()
            else:
                # Default incremental sync
                await self.sync_service.sync_from_fwtx_json()
                
            logger.info(f"Manual {sync_type} sync completed")
            return {"status": "success", "sync_type": sync_type, "timestamp": datetime.now().isoformat()}
            
        except Exception as e:
            logger.error(f"Manual sync failed: {e}")
            return {"status": "error", "sync_type": sync_type, "error": str(e)}
    
    def get_job_status(self):
        """Get status of all scheduled jobs."""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
        
        return {
            "scheduler_running": self.is_running,
            "jobs": jobs
        }


# Global scheduler instance
scheduler = DataSyncScheduler()


def start_sync_scheduler():
    """Start the global sync scheduler."""
    scheduler.start()


def stop_sync_scheduler():
    """Stop the global sync scheduler."""
    scheduler.stop()


async def manual_sync(sync_type: str = "incremental"):
    """Trigger a manual sync."""
    return await scheduler.trigger_manual_sync(sync_type)


def get_scheduler_status():
    """Get scheduler status."""
    return scheduler.get_job_status()