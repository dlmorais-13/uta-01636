if __name__ == "__main__":
    from src.settings import settings

    if settings.job_manager_id is not None:
        from src.jobs.job_manager import JobManager

        jobManager = JobManager()
        jobManager.run()
    else:
        from src.webapp import app
        import uvicorn

        uvicorn.run(app, host="0.0.0.0", port=8000)
