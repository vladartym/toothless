import os
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from claude_agent_sdk import query, ClaudeAgentOptions
from asgiref.sync import async_to_sync
import asyncio


@require_http_methods(["GET"])
async def get_data(request, action):
    """Handle dynamic GET requests from HTMX - generates pages based on action"""

    # Get additional context from hx-vals if provided
    page_description = request.GET.get('description', '')
    context = request.GET.get('context', '')

    print(f"\n{'='*60}")
    print(f"🔗 Dynamic navigation request received")
    print(f"   Action: {action}")
    print(f"   Description: {page_description}")
    print(f"   Context: {context}")
    print(f"{'='*60}\n")

    try:
        # Set API key from environment
        api_key = os.getenv('ANTHROPIC_API_KEY')
        print(f"🔑 API Key loaded: {'Yes' if api_key else 'No'}")
        os.environ['ANTHROPIC_API_KEY'] = api_key

        # Build context-aware prompt with additional details
        context_info = ""
        if page_description:
            context_info += f"\n\nPage Description: {page_description}"
        if context:
            context_info += f"\nAdditional Context: {context}"

        # Create context-aware prompt based on action
        prompt = f"""The user clicked on an element with the action: "{action}"{context_info}

Based on this action and context, generate a complete, full-page styled HTML that responds to what the user wants to see.

Analyze the action description and infer the user's intent. For example:
- "7-day-forecast-Toronto" with description "Show detailed 7-day weather forecast with daily highs, lows, and conditions"
- "temperature-details-Miami" with description "Display temperature trends, feels like, and heat index information"
- "back-to-weather-Boston" with description "Return to main weather dashboard overview"

The HTML should:
- Match the existing Airbnb-style design (clean, minimal, modern)
- Use inline styles with the color scheme: #222 for text, #717171 for secondary text, #f7f7f7 for backgrounds
- Use the font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif
- Include realistic, detailed data relevant to the action
- Be responsive and well-formatted with good padding and spacing
- Follow the page description guidance if provided

**CRITICAL: Add HTMX attributes to ALL interactive elements with hx-vals for context:**
- Use hx-get="/api/get/{{descriptive-action}}" on buttons, cards, links, sections
- Use hx-vals='json:{{"description": "detailed description of what this page should show", "context": "additional context"}}' to provide guidance for next page generation
- Use hx-target="#main-content" on all HTMX elements
- Use hx-swap="innerHTML" on all HTMX elements
- Make the action descriptions semantic and descriptive
- The description in hx-vals should explain what data/layout the next page needs

Examples of HTMX attributes to include:
- <button hx-get="/api/get/back-to-main-weather-Toronto" hx-vals='json:{{"description": "Main weather dashboard with current conditions, forecast cards, and quick stats", "context": "navigation-back"}}' hx-target="#main-content" hx-swap="innerHTML">Back</button>
- <div hx-get="/api/get/detailed-temperature-analysis-Toronto" hx-vals='json:{{"description": "Temperature chart showing hourly trends, high/low analysis, and historical comparison", "context": "temperature-deep-dive"}}' hx-target="#main-content" hx-swap="innerHTML" style="cursor: pointer;">
- <a hx-get="/api/get/wind-speed-details-Toronto" hx-vals='json:{{"description": "Wind data with speed, direction, gusts, and wind chill information", "context": "wind-details"}}' hx-target="#main-content" hx-swap="innerHTML">View Wind Details</a>

Return ONLY the HTML code, no markdown or explanations."""

        print(f"📝 Prompt created ({len(prompt)} chars)")

        # Configure Claude Agent SDK options
        options = ClaudeAgentOptions(
            model="claude-sonnet-4-5",
            max_turns=1
        )

        print(f"⚙️  Options configured: model={options.model}")
        print(f"🚀 Querying Claude Agent SDK...")

        # Query Claude for HTML generation
        generated_html = ""
        message_count = 0
        async for message in query(prompt=prompt, options=options):
            message_count += 1
            print(f"📨 Received message #{message_count}: {type(message).__name__}")

            # Extract text content from the response
            if hasattr(message, 'content'):
                print(f"   Content blocks: {len(message.content)}")
                for i, block in enumerate(message.content):
                    if hasattr(block, 'text'):
                        text_preview = block.text[:100] + "..." if len(block.text) > 100 else block.text
                        print(f"   Block {i+1}: {len(block.text)} chars - {text_preview}")
                        generated_html += block.text

        print(f"\n✅ Generated HTML: {len(generated_html)} chars")

        # Return generated HTML
        if generated_html:
            print(f"✨ Returning generated HTML to client\n")
            return HttpResponse(generated_html)
        else:
            print(f"⚠️  No HTML generated\n")
            return HttpResponse('<div style="color: #e61e4d;">Failed to generate content</div>')

    except Exception as e:
        print(f"\n❌ Error occurred: {str(e)}")
        print(f"   Type: {type(e).__name__}\n")
        import traceback
        traceback.print_exc()
        return HttpResponse(f'<div style="color: #e61e4d;">Error: {str(e)}</div>')


@require_http_methods(["POST"])
async def post_data(request):
    """Handle weather requests from HTMX using Claude Agent SDK"""
    city = request.POST.get('city', '').strip()

    print(f"\n{'='*60}")
    print(f"🌤️  Weather request received for: {city}")
    print(f"{'='*60}\n")

    if not city:
        print("❌ No city provided")
        html = '<div style="color: #e61e4d;">Please enter a city name</div>'
        return HttpResponse(html)

    try:
        # Set API key from environment
        api_key = os.getenv('ANTHROPIC_API_KEY')
        print(f"🔑 API Key loaded: {'Yes' if api_key else 'No'}")
        os.environ['ANTHROPIC_API_KEY'] = api_key

        # Create prompt with form context
        prompt = f"""The user submitted a form with the label "Get the weather for:" and entered the city name "{city}".

Generate a complete, full-page styled HTML for a weather page for {city}. The HTML should:
- Match the existing Airbnb-style design (clean, minimal, modern)
- Include realistic weather data (temperature, conditions, humidity, wind speed, forecast)
- Use inline styles with the color scheme: #222 for text, #717171 for secondary text, #f7f7f7 for backgrounds
- Include weather emoji/icons
- Be responsive and well-formatted
- Use the font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif
- Make it a full, beautiful weather dashboard that takes up the entire content area
- Include padding and margins for good spacing

**CRITICAL: Add HTMX attributes to ALL interactive elements with hx-vals for context:**
- Use hx-get="/api/get/{{descriptive-action}}" on buttons, cards, links, sections
- Use hx-vals='json:{{"description": "detailed description of what this page should show", "context": "additional context"}}' to provide guidance for next page generation
- Use hx-target="#main-content" on all HTMX elements
- Use hx-swap="innerHTML" on all HTMX elements
- Make the action descriptions semantic and descriptive (e.g., "view-7-day-forecast-{city}", "hourly-breakdown-{city}", "temperature-details-{city}")
- The description in hx-vals should explain what data/layout the next page needs
- Add multiple clickable elements: forecast cards, data sections, "view details" buttons
- Make sections/cards clickable for drill-down details

Examples of HTMX attributes to include:
- <div hx-get="/api/get/7-day-forecast-{city}" hx-vals='json:{{"description": "Detailed 7-day forecast with daily high/low temperatures, weather conditions, precipitation chance, and weather icons for each day", "context": "forecast-view"}}' hx-target="#main-content" hx-swap="innerHTML" style="cursor: pointer; padding: 20px; background: #f7f7f7; border-radius: 12px; margin: 10px 0;">
- <button hx-get="/api/get/hourly-breakdown-{city}" hx-vals='json:{{"description": "Hour-by-hour weather breakdown for the next 24 hours showing temperature, conditions, and precipitation", "context": "hourly-forecast"}}' hx-target="#main-content" hx-swap="innerHTML" style="...">View Hourly Forecast</button>
- <a hx-get="/api/get/temperature-analysis-{city}" hx-vals='json:{{"description": "Temperature trends with graphs, feels-like temperature, heat index, and historical comparison", "context": "temperature-details"}}' hx-target="#main-content" hx-swap="innerHTML">Detailed Temperature</a>

Return ONLY the HTML code, no markdown or explanations."""

        print(f"📝 Prompt created ({len(prompt)} chars)")

        # Configure Claude Agent SDK options
        options = ClaudeAgentOptions(
            model="claude-sonnet-4-5",
            max_turns=1
        )

        print(f"⚙️  Options configured: model={options.model}")
        print(f"🚀 Querying Claude Agent SDK...")

        # Query Claude for HTML generation
        generated_html = ""
        message_count = 0
        async for message in query(prompt=prompt, options=options):
            message_count += 1
            print(f"📨 Received message #{message_count}: {type(message).__name__}")

            # Extract text content from the response
            if hasattr(message, 'content'):
                print(f"   Content blocks: {len(message.content)}")
                for i, block in enumerate(message.content):
                    if hasattr(block, 'text'):
                        text_preview = block.text[:100] + "..." if len(block.text) > 100 else block.text
                        print(f"   Block {i+1}: {len(block.text)} chars - {text_preview}")
                        generated_html += block.text

        print(f"\n✅ Generated HTML: {len(generated_html)} chars")

        # Return generated HTML
        if generated_html:
            print(f"✨ Returning generated HTML to client\n")
            return HttpResponse(generated_html)
        else:
            print(f"⚠️  No HTML generated\n")
            return HttpResponse('<div style="color: #e61e4d;">Failed to generate weather data</div>')

    except Exception as e:
        print(f"\n❌ Error occurred: {str(e)}")
        print(f"   Type: {type(e).__name__}\n")
        import traceback
        traceback.print_exc()
        return HttpResponse(f'<div style="color: #e61e4d;">Error: {str(e)}</div>')
