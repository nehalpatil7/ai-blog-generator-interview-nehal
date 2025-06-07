import os
from openai import (
    OpenAI,
)
from dotenv import load_dotenv
import seo_fetcher

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_SECRET")

if not OPENROUTER_API_KEY:
    print(
        "Warning: OPENROUTER_API_KEY not found in .env file or environment variables. AI generation will fail."
    )
    client = None
else:
    try:
        client = OpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "http://localhost:5001/",
                "X-Title": "AI Blog Generator"
            }
        )
    except Exception as e:
        print(f"Error initializing OpenAI client: {e}")
        client = None


def generate_blog_post(
    keyword: str, seo_data: dict, output_format: str = "markdown"
) -> str:
    """
    Generates a draft blog post using the OpenAI API based on a keyword and combined SEO data.
    """
    if not client:
        return "Error: OpenAI client is not initialized. Please check your API key."

    trends = seo_data.get("trends", {})
    relative_interest_score = trends.get("relative_interest_score", "N/A")

    related_queries_list = trends.get("related_queries", [])
    formatted_related_queries = "N/A"
    if related_queries_list:
        # Assuming related_queries are list of dicts like {'query': '...', 'value': ...}
        query_texts = [q["query"] for q in related_queries_list if "query" in q]
        if query_texts:
            formatted_related_queries = ", ".join(
                query_texts[:5]
            )  # Limit to top 5 for brevity in prompt

    prompt_template = f"""
    You are an expert SEO content writer and blog post strategist.
    Your task is to generate a compelling, well-structured, and engaging draft blog post.

    **Keyword Focus:** "{keyword}"

    **Target SEO Insights & Trends (use these to guide tone and depth):**
    - Estimated Search Volume: {seo_data.get('search_volume', 'N/A')} (from general market data)
    - Keyword Difficulty: {seo_data.get('keyword_difficulty', 'N/A')} (from general market data)
    - Average CPC: ${seo_data.get('avg_cpc', 'N/A')} (from general market data)
    - **Google Trends - Relative Interest Score (last 12 months)**: {relative_interest_score} (0-100, higher indicates more search interest/popularity over time).
    - **Google Trends - Top Related Queries**: {formatted_related_queries} (These are popular searches related to the keyword. Consider these for sub-sections, FAQs, or to broaden the content's scope.)
    - Strategic Notes: {seo_data.get('notes', 'Focus on providing unique value and practical insights.')}

    **Blog Post Structure Requirements:**
    1.  **Catchy Title:** Create an H1-level title that is engaging and includes the keyword "{keyword}".
    2.  **Introduction (approx. 100-150 words):**
        * Hook the reader immediately.
        * Briefly introduce the keyword "{keyword}" and its importance or relevance.
        * State what the reader will learn or gain from this post.
    3.  **Main Section 1 (H2-level heading, approx. 200-300 words):**
        * Discuss a key aspect, benefit, or sub-topic related to "{keyword}".
        * Incorporate insights from the related queries if applicable.
        * Provide valuable information, practical tips, or unique insights.
        * Naturally integrate the placeholder `{{AFF_LINK_1}}` where relevant (e.g., recommending a related product or service).
    4.  **Main Section 2 (H2-level heading, approx. 200-300 words):**
        * Explore another significant aspect of "{keyword}".
        * Leverage related queries for deeper content.
        * Offer different perspectives or solutions.
        * Naturally integrate the placeholder `{{AFF_LINK_2}}` where relevant.
    5.  **(Optional) Main Section 3 (H2-level heading, approx. 150-250 words):**
        * If applicable, add another section for more depth or a related topic, possibly based on related queries.
        * If used, integrate `{{AFF_LINK_3}}`.
    6.  **Conclusion (approx. 100-150 words):**
        * Summarize the main takeaways.
        * Offer a final thought or a call to action (e.g., encourage comments, share the post, or check out a related resource).

    **Output Format:** Please generate the entire blog post strictly in **{output_format}** format.
    - If HTML: Use appropriate tags like `<h1>`, `<h2>`, `<p>`, `<ul>`, `<li>`, `<strong>`, `<em>`, and `<a>` for links. Ensure valid HTML structure.
    - If Markdown: Use standard Markdown syntax, including `#` for H1, `##` for H2, `*` or `-` for lists, `**bold**`, `*italic*`, etc.

    **Affiliate Links:**
    - Use the exact placeholders `{{AFF_LINK_1}}`, `{{AFF_LINK_2}}`, and `{{AFF_LINK_3}}` (if Section 3 is used).
    - These will be replaced programmatically later. Integrate them naturally into the text.

    **Tone and Style:**
    - Informative, engaging, and authoritative yet accessible.
    - Write for an audience interested in "{keyword}".
    - Avoid jargon where possible, or explain it clearly.

    **IMPORTANT:** Directly output the blog post content. Do not include any conversational preamble or postamble like "Okay, here's your blog post..." or "I hope this helps!". Just the raw {output_format} content.
    """

    try:
        completion = client.chat.completions.create(
            model="openai/gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful blog post writing assistant specialized in SEO content.",
                },
                {"role": "user", "content": prompt_template},
            ],
            temperature=0.7,
            max_tokens=1500,
        )

        generated_text = completion.choices[0].message.content.strip()

        dummy_affiliate_links = {
            "{{AFF_LINK_1}}": "https://amzn.to/dummy-link-123",
            "{{AFF_LINK_2}}": "https://shareasale.com/r.cfm?b=000001&u=000002&m=00003&urllink=&afftrack=",
            "{{AFF_LINK_3}}": "https://clk.tradedoubler.com/click?p=001&a=002&g=003",
        }

        for placeholder, actual_link in dummy_affiliate_links.items():
            if output_format == "html":
                # For HTML, wrap the link in an <a> tag
                link_text = f"Check out this recommended product {placeholder.split('_')[-1].replace('}}','')}"
                generated_text = generated_text.replace(
                    placeholder,
                    f'<a href="{actual_link}" target="_blank" rel="noopener noreferrer">{link_text}</a>',
                )
            else:  # Markdown
                link_text = (
                    f"Recommended Product {placeholder.split('_')[-1].replace('}}','')}"
                )
                generated_text = generated_text.replace(
                    placeholder, f"[{link_text}]({actual_link})"
                )

        return generated_text

    except Exception as e:
        error_message = f"Error calling OpenAI API or processing response: {e}"
        print(error_message)
        if output_format == "html":
            return (
                f"<p><strong>Error generating blog post:</strong> {error_message}</p>"
            )
        else:
            return f"**Error generating blog post:** {error_message}"


if __name__ == "__main__":
    if not client:
        print(
            "Skipping ai_generator.py test as OpenAI client is not initialized (check API key)."
        )
    else:
        print("Testing ai_generator.py...")
        sample_keyword = "best wireless earbuds for running"
        sample_seo_data = seo_fetcher.get_seo_data(
            sample_keyword
        )

        if "error" in sample_seo_data:
            print(f"Could not fetch SEO data for '{sample_keyword}'. Aborting test.")
        else:
            print(f"\n--- Generating Markdown for: '{sample_keyword}' ---")
            markdown_post = generate_blog_post(
                sample_keyword, sample_seo_data, output_format="markdown"
            )
            print(markdown_post)

            print(f"\n--- Generating HTML for: '{sample_keyword}' ---")
            html_post = generate_blog_post(
                sample_keyword, sample_seo_data, output_format="html"
            )
            print(html_post)
