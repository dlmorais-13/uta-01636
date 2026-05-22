
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'job':
        from src.jobs.job_manager import JobManager
        from src.apis.agol_api import AgolAPI
        jobManager = JobManager(AgolAPI())
        jobManager.run()
    else:
        from src.webapp import app
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)
