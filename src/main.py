if __name__ == "__main__":
    from src.settings import settings
    from src.jobs.job_manager import JobManager

    jobManager = JobManager()
    jobManager.run()
