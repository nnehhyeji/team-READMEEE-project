import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management import call_command
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # 00:00에 실행될 작업 정의
        @util.close_old_connections
        def generate_daily_question():
            call_command('generate_question')


        # 작업을 스케줄러에 추가 (매일 00:00)
        scheduler.add_job(
            generate_daily_question,
            trigger=CronTrigger(hour="00", minute="00"), 
            id="generate_daily_question", 
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'generate_daily_question'.")

        try:
            logger.info("Starting scheduler...")

            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
