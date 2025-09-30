import os
from pathlib import Path
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from claude_agent_sdk import query, ClaudeAgentOptions
from asgiref.sync import async_to_sync
import asyncio


# Load system prompt once at module level
SYSTEM_PROMPT_PATH = Path(__file__).parent / 'system_prompt.md'
SYSTEM_PROMPT = ""
if SYSTEM_PROMPT_PATH.exists():
    with open(SYSTEM_PROMPT_PATH, 'r') as f:
        SYSTEM_PROMPT = f.read()


@require_http_methods(["GET"])
async def get_data(request, action):
    """Handle dynamic GET requests from HTMX - generates pages based on action"""

    # Get all context from hx-vals if provided
    description = request.GET.get('description', '')
    from_page = request.GET.get('from', '')
    to_page = request.GET.get('to', '')
    context = request.GET.get('context', '')

    # Get any additional context fields
    additional_context = {k: v for k, v in request.GET.items()
                         if k not in ['description', 'from', 'to', 'context']}

    print(f"\n{'='*80}")
    print(f"🎯 HTMX NAVIGATION CLICKED")
    print(f"{'='*80}")
    print(f"📍 Full Endpoint: /api/get/{action}/")
    print(f"🏷️  Action Parameter: {action}")
    print(f"{'─'*80}")
    print(f"📦 hx-vals Navigation Context:")
    print(f"   📝 description: {description or '❌ NOT PROVIDED'}")
    print(f"   ⬅️  from: {from_page or '❌ NOT PROVIDED'}")
    print(f"   ➡️  to: {to_page or '❌ NOT PROVIDED'}")
    if context:
        print(f"   🏷️  context: {context}")
    if additional_context:
        print(f"   ➕ Additional fields:")
        for key, value in additional_context.items():
            print(f"      • {key}: {value}")
    print(f"{'─'*80}")
    print(f"🔄 This context will guide Claude's page generation")
    print(f"{'='*80}\n")

    try:
        # Set API key from environment
        api_key = os.getenv('ANTHROPIC_API_KEY')
        print(f"🔑 API Key loaded: {'Yes' if api_key else 'No'}")
        os.environ['ANTHROPIC_API_KEY'] = api_key

        # Build context-aware prompt with navigation flow
        context_info = ""
        if description:
            context_info += f"\n\n📝 What to Generate: {description}"
        if from_page:
            context_info += f"\n⬅️  Coming From: {from_page}"
        if to_page:
            context_info += f"\n➡️  Going To: {to_page}"
        if context:
            context_info += f"\n🏷️  Context Type: {context}"
        if additional_context:
            context_info += f"\n➕ Additional Context: {additional_context}"

        # Create context-aware prompt based on action
        prompt = f"""{SYSTEM_PROMPT}

---

## Task
The user clicked on an element with the action: "{action}"{context_info}

Based on this navigation context, generate the appropriate page.

⚠️ **MANDATORY: Include 3-5 different clickable elements with COMPLETE hx-vals context**

EVERY clickable element needs all attributes INCLUDING rich hx-vals:
- hx-get="/api/get/{{action}}"
- hx-vals='json:{{"description":"detailed instructions for next page","from":"current-page-identifier","to":"destination-identifier"}}'
- hx-target="#main-content"
- hx-swap="innerHTML"

Example with PROPER navigation context:
<button hx-get="/api/get/back-Toronto" hx-vals='json:{{"description":"Main weather dashboard with current conditions and forecast cards","from":"forecast-details","to":"main-dashboard"}}' hx-target="#main-content" hx-swap="innerHTML" style="padding:14px 24px;background:#e61e4d;color:#fff;border:none;border-radius:8px;cursor:pointer;">← Back</button>

<div hx-get="/api/get/hourly-Toronto" hx-vals='json:{{"description":"Hour-by-hour breakdown for next 24 hours with temp and conditions","from":"main-dashboard","to":"hourly-view","city":"Toronto"}}' hx-target="#main-content" hx-swap="innerHTML" style="cursor:pointer;padding:20px;background:#f7f7f7;border-radius:12px;">
  <p style="font-size:18px;font-weight:600;">⏰ Hourly Forecast</p>
</div>

Return ONLY the HTML code, no markdown."""

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

        # Clean up markdown code blocks if present
        if generated_html:
            # Remove ```html and ``` markers
            generated_html = generated_html.strip()
            if generated_html.startswith('```html'):
                generated_html = generated_html[7:]  # Remove ```html
            elif generated_html.startswith('```'):
                generated_html = generated_html[3:]   # Remove ```
            if generated_html.endswith('```'):
                generated_html = generated_html[:-3]  # Remove trailing ```
            generated_html = generated_html.strip()
            print(f"🧹 Cleaned HTML: {len(generated_html)} chars")

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

    print(f"\n{'='*80}")
    print(f"📝 FORM SUBMISSION (Initial Request)")
    print(f"{'='*80}")
    print(f"📍 Endpoint: /api/post/")
    print(f"🏙️  City Submitted: {city}")
    print(f"{'─'*80}")
    print(f"🔄 This will generate the initial weather dashboard")
    print(f"{'='*80}\n")

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
        prompt = f"""{SYSTEM_PROMPT}

---

## Task
The user submitted a form with the label "Get the weather for:" and entered the city name "{city}".

Generate a minimal weather dashboard for {city} with:
- Current temperature and conditions (in a large centered display)
- 3-5 clickable sections/cards
- Key stats (humidity, wind)

⚠️ **MANDATORY: Create 3-5 different clickable elements with COMPLETE navigation context in hx-vals**

The dashboard MUST have these clickable sections:
1. Forecast card → detailed forecast view
2. Temperature section → temperature breakdown
3. Wind/humidity card → weather details
4. Additional stat sections as needed

EVERY clickable element needs rich hx-vals with navigation flow:
- hx-get="/api/get/{{action}}"
- hx-vals='json:{{"description":"detailed instructions","from":"main-dashboard","to":"destination-page"}}'
- hx-target="#main-content"
- hx-swap="innerHTML"
- style="cursor:pointer; ..." (make it look clickable)

Example elements with PROPER context:
<div hx-get="/api/get/forecast-{city}" hx-vals='json:{{"description":"5-day weather forecast with daily temps, conditions, and precipitation","from":"main-dashboard","to":"forecast-view","city":"{city}"}}' hx-target="#main-content" hx-swap="innerHTML" style="cursor:pointer;padding:20px;background:#f7f7f7;border-radius:12px;margin:10px 0;">
  <p style="font-size:18px;font-weight:600;margin:0 0 8px;">📅 Forecast</p>
  <p style="color:#717171;margin:0;">View 5-day forecast</p>
</div>

<div hx-get="/api/get/temperature-{city}" hx-vals='json:{{"description":"Temperature details with current, feels like, high/low, and hourly trend","from":"main-dashboard","to":"temperature-details","currentTemp":"72F"}}' hx-target="#main-content" hx-swap="innerHTML" style="cursor:pointer;padding:20px;background:#f7f7f7;border-radius:12px;margin:10px 0;">
  <p style="color:#717171;margin:0 0 4px;">Temperature</p>
  <p style="font-size:32px;font-weight:600;margin:0;">72°F</p>
</div>

<div hx-get="/api/get/wind-{city}" hx-vals='json:{{"description":"Wind speed, direction, gusts, and humidity information","from":"main-dashboard","to":"wind-details"}}' hx-target="#main-content" hx-swap="innerHTML" style="cursor:pointer;padding:16px;background:#f7f7f7;border-radius:8px;">💨 Wind Details →</div>

Return ONLY the HTML code, no markdown."""

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

        # Clean up markdown code blocks if present
        if generated_html:
            # Remove ```html and ``` markers
            generated_html = generated_html.strip()
            if generated_html.startswith('```html'):
                generated_html = generated_html[7:]  # Remove ```html
            elif generated_html.startswith('```'):
                generated_html = generated_html[3:]   # Remove ```
            if generated_html.endswith('```'):
                generated_html = generated_html[:-3]  # Remove trailing ```
            generated_html = generated_html.strip()
            print(f"🧹 Cleaned HTML: {len(generated_html)} chars")

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
