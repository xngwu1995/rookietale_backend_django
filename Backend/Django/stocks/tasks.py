import logging
from celery import shared_task
from utils.schedules import Schedules
from utils.strategy import VCP_Strategy


logger = logging.getLogger(__name__)


@shared_task
def get_latest_vcp_strategy():
    # is_holiday_result = Schedules.is_holiday()
    # is_weekend_result = Schedules.is_weekend()

    # if is_holiday_result or is_weekend_result:
    #     return
    logger.info("Starting get_latest_vcp_strategy task.")
    vcp_strategy = VCP_Strategy()
    vcp_strategy.execute()
    logger.info("Completed get_latest_vcp_strategy task.")
