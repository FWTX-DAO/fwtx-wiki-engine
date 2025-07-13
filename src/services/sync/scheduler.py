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
from src.services.sync.data_loader import DataLoader, load_and_sync_all_data
from src.services.sync.top_loader import TOPDataLoader
from src.services.agent.researcher import FortWorthResearchWorkflow

logger = logging.getLogger(__name__)


class DataSyncScheduler:
    """Manages scheduled data synchronization tasks."""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.sync_service = FortWorthDataSync(graphiti)
        self.research_workflow = FortWorthResearchWorkflow(graphiti)
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
        """Run daily incremental sync with live data."""
        logger.info("Starting daily live data sync...")
        try:
            # First ensure TOP base data is present
            top_loader = TOPDataLoader(graphiti)
            await top_loader.sync_to_graphiti()
            
            # Then sync from all sources
            await load_and_sync_all_data(graphiti)
                    
            logger.info("Daily sync completed successfully")
        except Exception as e:
            logger.error(f"Daily sync failed: {e}")
    
    async def _run_weekly_full_sync(self):
        """Run weekly full sync with comprehensive research."""
        logger.info("Starting weekly full sync...")
        try:
            # Get all data fetch tasks
            fetch_tasks = await self.sync_service.run_live_data_fetch()
            
            # Add additional comprehensive research tasks
            comprehensive_tasks = [
                {
                    "name": "Recent City Council Meetings",
                    "config": {
                        "search_queries": [
                            "Fort Worth city council meeting minutes 2024",
                            "Fort Worth city council agenda recent",
                            "Fort Worth city council decisions ordinances"
                        ],
                        "data_needed": [
                            "recent_decisions",
                            "new_ordinances",
                            "policy_changes",
                            "budget_amendments"
                        ]
                    }
                },
                {
                    "name": "City Projects and Initiatives",
                    "config": {
                        "search_queries": [
                            "Fort Worth capital projects 2024",
                            "Fort Worth city initiatives programs",
                            "Fort Worth infrastructure improvements"
                        ],
                        "data_needed": [
                            "project_names",
                            "project_budgets",
                            "timelines",
                            "responsible_departments"
                        ]
                    }
                }
            ]
            
            all_tasks = fetch_tasks + comprehensive_tasks
            
            # Process all tasks with research workflow
            episodes = await self.research_workflow.research_all_tasks(all_tasks)
            
            if episodes:
                await self.graphiti.add_episode_bulk(episodes)
                logger.info(f"Added {len(episodes)} episodes from comprehensive research")
                    
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
                await self._run_weekly_full_sync()
            elif sync_type == "services":
                await load_and_sync_all_data(graphiti)
            elif sync_type == "governance":
                await load_and_sync_all_data(graphiti)
            else:
                # Default incremental sync
                await load_and_sync_all_data(graphiti)
                
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