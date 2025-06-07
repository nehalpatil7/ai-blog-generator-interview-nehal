import os
import datetime
import logging

from flask import Flask, request, jsonify
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

import seo_fetcher
import ai_generator

load_dotenv()

app = Flask(__name__)

# --- Configuration ---
DAILY_GENERATION_KEYWORD = os.getenv("DAILY_KEYWORD", "sustainable living tips")
DAILY_GENERATION_OUTPUT_DIR = os.getenv("DAILY_OUTPUT_DIR", "daily_generated_posts")
DAILY_GENERATION_FORMAT = os.getenv("DAILY_FORMAT", "markdown").lower()
DAILY_CRON_HOUR = os.getenv("DAILY_CRON_HOUR", "3")
DAILY_CRON_MINUTE = os.getenv("DAILY_CRON_MINUTE", "0")


# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# --- Helper Functions ---
def _ensure_output_directory_exists():
    """Ensures the output directory for daily posts exists."""
    if not os.path.exists(DAILY_GENERATION_OUTPUT_DIR):
        try:
            os.makedirs(DAILY_GENERATION_OUTPUT_DIR)
            logger.info(
                f"Created directory for daily posts: {DAILY_GENERATION_OUTPUT_DIR}"
            )
        except OSError as e:
            logger.error(
                f"Could not create directory {DAILY_GENERATION_OUTPUT_DIR}: {e}"
            )
            return False
    return True


# --- Flask Routes ---
@app.route("/generate", methods=["GET"])
def generate_post_endpoint():
    """
    API endpoint to generate a blog post on demand.
    Query Parameters:
        - keyword (str, required): The keyword for the blog post.
        - format (str, optional): "markdown" or "html". Defaults to "markdown".
    """
    keyword = request.args.get("keyword")
    output_format = request.args.get("format", "markdown").lower()

    if not keyword:
        logger.warning("'/generate' endpoint called without keyword.")
        return jsonify({"error": "Keyword parameter is required"}), 400

    if output_format not in ["markdown", "html"]:
        logger.warning(
            f"'/generate' endpoint called with invalid format: {output_format}"
        )
        return (
            jsonify({"error": "Invalid format parameter. Use 'markdown' or 'html'."}),
            400,
        )

    logger.info(
        f"Received request to generate post for keyword: '{keyword}', format: {output_format}"
    )

    # 1. Fetch SEO data
    seo_data = seo_fetcher.get_seo_data(keyword)
    if seo_data.get("error"):
        logger.error(f"SEO data fetching failed for '{keyword}': {seo_data['error']}")
        return (
            jsonify(
                {
                    "error": f"Failed to fetch SEO data: {seo_data['error']}",
                    "keyword": keyword,
                }
            ),
            500,
        )

    # 2. Generate blog post
    if not ai_generator.client:
        logger.error(
            "OpenAI API key not configured or client failed to initialize. Cannot generate post."
        )
        return (
            jsonify(
                {
                    "error": "OpenAI API key is not configured or client initialization failed. Cannot generate post."
                }
            ),
            503,
        )  # Service Unavailable

    blog_post_content = ai_generator.generate_blog_post(
        keyword, seo_data, output_format=output_format
    )

    if (
        "Error generating blog post:" in blog_post_content
        or "OpenAI client is not initialized" in blog_post_content
    ):
        logger.error(
            f"Blog post generation failed for '{keyword}': {blog_post_content}"
        )
        return (
            jsonify(
                {
                    "error": "Blog post generation failed.",
                    "details": blog_post_content,
                    "keyword": keyword,
                    "seo_data": seo_data,
                }
            ),
            500,
        )

    logger.info(f"Successfully generated blog post for keyword: '{keyword}'")
    return jsonify(
        {
            "keyword": keyword,
            "seo_data": seo_data,
            "requested_format": output_format,
            "blog_post": blog_post_content,
        }
    )


# --- Scheduled Task ---
def scheduled_daily_post_generation_job():
    """
    This function is called by the APScheduler to generate a daily blog post
    for the predefined keyword and save it to a file.
    """
    logger.info(
        f"[{datetime.datetime.now()}] Starting scheduled daily post generation for keyword: '{DAILY_GENERATION_KEYWORD}'"
    )

    if not _ensure_output_directory_exists():
        logger.error(
            "Halting daily post generation as output directory could not be ensured."
        )
        return

    if not ai_generator.client:
        logger.error(
            f"[{datetime.datetime.now()}] OpenAI API key not configured or client failed. Skipping daily generation of '{DAILY_GENERATION_KEYWORD}'."
        )
        return

    seo_data = seo_fetcher.get_seo_data(DAILY_GENERATION_KEYWORD)
    if seo_data.get("error"):
        logger.error(
            f"[{datetime.datetime.now()}] Error fetching SEO data for daily keyword '{DAILY_GENERATION_KEYWORD}': {seo_data['error']}"
        )
        return

    blog_post_content = ai_generator.generate_blog_post(
        DAILY_GENERATION_KEYWORD, seo_data, output_format=DAILY_GENERATION_FORMAT
    )

    if (
        "Error generating blog post:" in blog_post_content
        or "OpenAI client is not initialized" in blog_post_content
    ):
        logger.error(
            f"[{datetime.datetime.now()}] Error generating daily post for '{DAILY_GENERATION_KEYWORD}': {blog_post_content}"
        )
    else:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        safe_filename_keyword = "".join(
            c if c.isalnum() else "_" for c in DAILY_GENERATION_KEYWORD.lower()
        )
        file_extension = "html" if DAILY_GENERATION_FORMAT == "html" else "md"
        filename = f"{timestamp}_{safe_filename_keyword}.{file_extension}"
        filepath = os.path.join(DAILY_GENERATION_OUTPUT_DIR, filename)

        try:
            content_to_write = blog_post_content.replace('\\n', '<br>') if '\\n' in blog_post_content else blog_post_content
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content_to_write)
            logger.info(
                f"[{datetime.datetime.now()}] Successfully generated and saved daily post to: {filepath}"
            )
        except IOError as e:
            logger.error(
                f"[{datetime.datetime.now()}] Error saving daily post to file {filepath}: {e}"
            )


# --- APScheduler Setup ---
# The scheduler should be initialized only once.
# When using Flask's reloader (debug=True), the main module can be executed twice.
# os.environ.get('WERKZEUG_RUN_MAIN') == 'true' ensures the scheduler starts only in the main Werkzeug process.
scheduler = BackgroundScheduler(
    daemon=True
)  # daemon=True allows app to exit even if scheduler thread is running

if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    if (
        scheduler.state == 0
    ):  # 0 means STATE_STOPPED (apscheduler.schedulers.base.STATE_STOPPED)
        try:
            cron_hour = int(DAILY_CRON_HOUR)
            cron_minute = int(DAILY_CRON_MINUTE)

            scheduler.add_job(
                func=scheduled_daily_post_generation_job,
                trigger=CronTrigger(
                    hour=cron_hour, minute=cron_minute, timezone="UTC"
                ),
                id="daily_post_job",
                name="Daily Blog Post Generation",
                replace_existing=True,
            )
            scheduler.start()
            logger.info(
                f"APScheduler started. Daily post generation scheduled for {cron_hour:02d}:{cron_minute:02d} UTC."
            )

            # For immediate testing of the scheduler logic (optional, uncomment if needed):
            # logger.info("Running an initial daily generation job for testing...")
            # scheduler.add_job(scheduled_daily_post_generation_job, 'date', run_date=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=5))

        except ValueError:
            logger.error(
                f"Invalid DAILY_CRON_HOUR ('{DAILY_CRON_HOUR}') or DAILY_CRON_MINUTE ('{DAILY_CRON_MINUTE}'). Please provide integers."
            )
        except Exception as e:
            logger.error(f"Error starting APScheduler or adding job: {e}")
    else:
        logger.info("APScheduler already running.")
else:
    logger.info(
        "APScheduler not started because Flask is in debug mode with reloader active (or not the main Werkzeug process)."
    )


@app.route("/scheduler/jobs", methods=["GET"])
def list_scheduled_jobs():
    jobs = scheduler.get_jobs()
    job_list = [
        {
            "id": job.id,
            "name": job.name,
            "next_run_time": str(job.next_run_time),
            "trigger": str(job.trigger),
        }
        for job in jobs
    ]
    return jsonify(job_list)


if __name__ == "__main__":
    _ensure_output_directory_exists()
    # For production, WSGI server: gunicorn -w 4 -b 0.0.0.0:5001 app:app
    app.run(debug=True, host="0.0.0.0", port=5001)
