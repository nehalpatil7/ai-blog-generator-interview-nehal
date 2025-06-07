# AI-Powered Blog Post Generator

This Python/Flask application generates draft blog posts based on a given keyword. It performs mock "SEO research" and uses the OpenAI API to create content. It also includes a scheduler to automatically generate a new post daily for a predefined keyword.

This project was created as part of an interview exercise.

## Features

- **On-demand Blog Post Generation**: Via a REST API endpoint (`/generate?keyword=<your_keyword>`).
- **Mock SEO Data**: Uses a local JSON file (`mock_seo_data.json`) to simulate keyword metrics (search volume, difficulty, CPC).
- **OpenAI Integration**: Calls the OpenAI API (GPT-3.5 Turbo or newer) to generate blog post content.
- **Structured Output**: Generates posts in Markdown or HTML format with a basic structure (Title, Intro, Sections, Conclusion).
- **Placeholder Affiliate Links**: Includes `{{AFF_LINK_n}}` placeholders in the prompt, which are then replaced with dummy URLs in the generated content.
- **Daily Automated Generation**: Uses APScheduler to generate a blog post for a predefined keyword once a day and saves it locally.

## Project Structure
```txt
ai-blog-generator-interview/
├── app.py                    # Main Flask application, API endpoint, scheduler setup
├── ai_generator.py           # Module for OpenAI API calls and prompt engineering
├── seo_fetcher.py            # Module for fetching mock SEO data
├── mock_seo_data.json        # JSON file with mock SEO metrics
├── daily_generated_posts/    # Directory where daily scheduled posts are saved (created automatically)
├── requirements.txt          # Python package dependencies
├── .env                      # Environment file (format given below, fill it in similarly)
├── .gitignore                # Specifies intentionally untracked files
└── README.md                 # This file
```

### .env file
```txt
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_SECRET = "YOUR_OPENROUTER_KEY_HERE"

DAILY_KEYWORD="YOUR_KEYWORD"
DAILY_OUTPUT_DIR="DIR_BLOG_POSTS"
DAILY_FORMAT="markdown/html"
DAILY_CRON_HOUR="UTC_TIME_HERE"
DAILY_CRON_MINUTE="0"

FLASK_APP="app.py"
FLASK_ENV="development/production"
FLASK_DEBUG=(1 for hot reload, 2 for normal)
```

## Prerequisites

-   Python 3.8 or higher
-   `pip` (Python package installer)
-   An OpenAI API Key

## Setup and Installation

1.  **Clone the Repository**:
    ```bash
    git clone [https://github.com/](https://github.com/)nehalpatil7/ai-blog-generator-interview-nehal.git
    cd ai-blog-generator-interview-nehal
    ```

2.  **Create a Virtual Environment** (recommended):
    ```bash
    python -m venv venv
    ```
    Activate the virtual environment:
    -   On macOS and Linux:
        ```bash
        source venv/bin/activate
        ```
    -   On Windows:
        ```bash
        .\venv\Scripts\activate
        ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up Environment Variables**:
    -   Copy the example environment file:
        ```bash
        cp .env.example .env
        ```
    -   Open the `.env` file in a text editor and add your OpenAI API key:
        ```
        OPENAI_API_KEY="sk-YourActualOpenAIAPIKeyHere"

        # Optional: Customize daily generation settings
        DAILY_KEYWORD="your favorite daily keyword" # Default: "sustainable living tips"
        DAILY_OUTPUT_DIR="my_daily_posts"          # Default: "daily_generated_posts"
        DAILY_FORMAT="html"                        # Default: "markdown" (can be "markdown" or "html")
        DAILY_CRON_HOUR="4"                        # Default: "3" (UTC hour for daily job, 0-23)
        DAILY_CRON_MINUTE="30"                     # Default: "0" (UTC minute for daily job, 0-59)
        ```
    -   **Important**: Ensure your OpenAI account has sufficient credits/quota.

## Running the Application

1.  **Start the Flask Development Server**:
    ```bash
    python app.py
    ```
    The application will typically start on `http://localhost:5000` or `http://0.0.0.0:5000`. Check the console output for the exact address.

2.  **Accessing the API Endpoint**:
    Open your web browser or use a tool like `curl` or Postman to send a GET request to the `/generate` endpoint.

    **Example using `curl`**:
    ```bash
    # Generate a post in Markdown (default)
    curl "http://localhost:5000/generate?keyword=best%20budget%20smartphone"

    # Generate a post in HTML
    curl "http://localhost:5000/generate?keyword=home%20office%20setup&format=html"
    ```

    **Expected JSON Response**:
    ```json
    {
      "keyword": "your_keyword",
      "seo_data": {
        "search_volume": 150000,
        "keyword_difficulty": 60,
        "avg_cpc": 1.75,
        "notes": "Target users looking for value, compare features and price."
      },
      "requested_format": "markdown", // or "html"
      "blog_post": "Generated blog post content here..." // Markdown or HTML string
    }
    ```

## Daily Scheduler

-   The application uses `APScheduler` to automatically generate a blog post once a day.
-   The default keyword is "sustainable living tips" and the default schedule is 3:00 AM UTC. These can be configured in the `.env` file (see `DAILY_KEYWORD`, `DAILY_CRON_HOUR`, `DAILY_CRON_MINUTE`).
-   Generated posts are saved in the `daily_generated_posts/` directory (or the directory specified by `DAILY_OUTPUT_DIR` in `.env`).
-   The filename includes a timestamp and the keyword (e.g., `2023-10-27_15-30-00_sustainable_living_tips.md`).
-   Scheduler logs and job execution information will be printed to the console where `app.py` is running.

## How the Daily Scheduler Works (APScheduler)

-   The `APScheduler` is configured in `app.py` to run as a `BackgroundScheduler`.
-   It calls the `scheduled_daily_post_generation_job` function based on the CRON schedule defined.
-   This job:
    1.  Fetches SEO data for the `DAILY_GENERATION_KEYWORD`.
    2.  Calls `ai_generator.generate_blog_post` to get the content.
    3.  Saves the generated content to a file in the specified output directory.
-   The scheduler is started when `app.py` runs, but only in the main Werkzeug process if Flask's debug reloader is active, to prevent multiple scheduler instances.

## Example Generated Blog Post

To see an example of a generated blog post:

1.  Run the application.
2.  Trigger the `/generate` endpoint with a keyword of your choice.
3.  Alternatively, wait for the daily scheduler to run (or adjust its schedule in `.env` for quicker testing, e.g., set it to run a few minutes from the current time for a one-off test).
4.  Check the `daily_generated_posts/` directory or the JSON response from the API.

*(You should include a sample generated file, e.g., `example_wireless_earbuds.md`, in your submission after running the app yourself.)*

## Technologies Used

-   **Python 3**
-   **Flask**: Micro web framework for the REST API.
-   **OpenAI Python Client**: For interacting with the OpenAI API.
-   **python-dotenv**: For managing environment variables (API keys).
-   **APScheduler**: For scheduling the daily post generation task.

## Further Improvements (Potential Next Steps)

-   **Real SEO Data**: Integrate with a live SEO API (e.g., Ahrefs, SEMrush, or a free alternative) instead of mock data.
-   **More Sophisticated Prompt Engineering**: Allow for more dynamic prompt customization.
-   **User Interface**: Build a simple frontend to interact with the API.
-   **Database Storage**: Store generated posts and SEO data in a database instead of local files.
-   **Error Handling & Resilience**: Implement more robust error handling, retries for API calls, and monitoring.
-   **Content Customization**: Allow users to specify post length, tone, style, or specific sections to include.
-   **Image Integration**: Add functionality to suggest or include relevant images (e.g., using stock photo APIs or AI image generation).
-   **Deployment**: Instructions for deploying to a cloud platform (e.g., Heroku, AWS, Google Cloud).
-   **Unit and Integration Tests**: Add automated tests for better reliability.

