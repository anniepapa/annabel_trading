import subprocess
from apscheduler.schedulers.blocking import BlockingScheduler

from my_logger import logger


def run_docker_compose():
    try:
        completed_process = subprocess.run(
            ["docker-compose", "up", "-d"],
            check=True,
            capture_output=True,
            text=True,
        )
        logger.info(completed_process.stdout)
    except subprocess.CalledProcessError as e:
        logger.error(f"Command execution failed: {e.stderr}")
    except Exception as e:
        logger.exception(f"An error occurred💥💥💥: {str(e)}")


# Create a scheduler
scheduler = BlockingScheduler()

# Schedule the job to run every 1 minute
scheduler.add_job(run_docker_compose, "interval", seconds=90)

# Start the scheduler
scheduler.start()
