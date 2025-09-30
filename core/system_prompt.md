# System Instructions for HTML Generation

## Design Philosophy
- **Minimal & Simple**: Keep designs extremely clean and simple
- **Fast Loading**: Minimize HTML length to reduce loading times and token usage
- **Performance First**: Less is more - avoid excessive details or decorative elements

## HTML Requirements

### Length Constraints
- Target HTML length: **Under 3000 characters when possible**
- Remove unnecessary whitespace and comments
- Use concise inline styles
- Avoid repetitive code - use compact patterns

### Design System

#### Colors
- Primary text: `#222`
- Secondary text: `#717171`
- Background: `#f7f7f7`
- Accent: `#e61e4d` (Airbnb red - use sparingly)

#### Typography
- Font family: `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif`
- Keep font sizes consistent: 16px body, 24px-32px headings
- Font weights: 400 (normal), 600 (semibold)

#### Spacing
- Use multiples of 8px: 8px, 16px, 24px, 32px
- Max width: 580-800px for content areas
- Padding: 24px for sections, 16px for cards

#### Components
- Cards: `padding: 20px; background: #f7f7f7; border-radius: 12px;`
- Buttons: `padding: 14px 24px; border-radius: 8px; cursor: pointer;`
- Use `cursor: pointer` on all clickable elements

### Content Guidelines
- **Be Concise**: Show only essential data
- **Limit Items**: Show 3-5 key items per section, not exhaustive lists
- **Simple Layout**: Single column layouts preferred
- **No Fluff**: Skip unnecessary explanatory text
- **Fast to Scan**: Use clear hierarchy with whitespace

### HTMX Integration (CRITICAL - MANDATORY - DO NOT SKIP)

⚠️ **EVERY page MUST have 3-5 clickable elements with complete HTMX attributes.**

**ALL four attributes are REQUIRED on EVERY interactive element:**
1. `hx-get="/api/get/{descriptive-action}"`
2. `hx-vals='json:{"description":"what to generate next","from":"current page context","to":"destination page"}'`
3. `hx-target="#main-content"`
4. `hx-swap="innerHTML"`

**hx-vals MUST contain navigation context:**
- `description`: Detailed instructions for what the next page should contain
- `from`: Where user is coming from (e.g., "main-dashboard", "forecast-page", "temp-details")
- `to`: Where user is going (e.g., "detailed-forecast", "hourly-view", "back-to-dashboard")
- Additional context as needed (city, date, data point, etc.)

**What needs HTMX attributes:**
- ✅ ALL buttons (back, action, navigation)
- ✅ ALL cards showing data (weather cards, forecast cards, stat cards)
- ✅ ALL sections with information (make them clickable)
- ✅ ALL links
- ✅ ANY div displaying data users might want to explore

**Complete Examples:**

```html
<!-- Button with Navigation Context -->
<button hx-get="/api/get/back-Toronto" hx-vals='json:{"description":"Main weather dashboard with current conditions, forecast cards, humidity and wind stats","from":"forecast-details","to":"main-dashboard"}' hx-target="#main-content" hx-swap="innerHTML" style="padding:14px 24px;background:#e61e4d;color:#fff;border:none;border-radius:8px;cursor:pointer;">Back to Dashboard</button>

<!-- Clickable Card with Rich Context -->
<div hx-get="/api/get/forecast-Toronto" hx-vals='json:{"description":"5-day weather forecast showing daily high/low temps, conditions, precipitation chance for each day","from":"main-dashboard","to":"forecast-view","city":"Toronto"}' hx-target="#main-content" hx-swap="innerHTML" style="cursor:pointer;padding:20px;background:#f7f7f7;border-radius:12px;margin:10px 0;">
  <p style="font-size:18px;font-weight:600;margin:0 0 8px;">📅 Forecast</p>
  <p style="color:#717171;margin:0;">View 5-day forecast</p>
</div>

<!-- Clickable Data Section with Context -->
<div hx-get="/api/get/temp-details-Toronto" hx-vals='json:{"description":"Temperature breakdown with current temp, feels like, high/low for today, hourly trend","from":"main-dashboard","to":"temperature-details","currentTemp":"72F"}' hx-target="#main-content" hx-swap="innerHTML" style="cursor:pointer;padding:16px;background:#f7f7f7;border-radius:8px;">
  <p style="font-size:16px;margin:0 0 4px;color:#717171;">Temperature</p>
  <p style="font-size:32px;margin:0;font-weight:600;">72°F</p>
</div>

<!-- Link with Drill-down Context -->
<a hx-get="/api/get/hourly-Monday-Toronto" hx-vals='json:{"description":"Hourly weather breakdown for Monday showing temperature, conditions, and precipitation for each hour","from":"weekly-forecast","to":"hourly-breakdown","day":"Monday"}' hx-target="#main-content" hx-swap="innerHTML" style="color:#e61e4d;text-decoration:none;cursor:pointer;">View Monday Details →</a>
```

### Examples of Good vs Bad

#### ❌ BAD (Too Detailed, Too Long)
```html
<div style="padding: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);">
  <h2 style="font-size: 32px; font-weight: 700; margin-bottom: 20px;">Temperature Details</h2>
  <p style="font-size: 16px; line-height: 1.8; color: #666;">The current temperature is showing moderate conditions with a slight increase expected...</p>
  <!-- 15 more detailed items -->
</div>
```

#### ✅ GOOD (Minimal, Fast)
```html
<div style="padding: 20px; background: #f7f7f7; border-radius: 12px;">
  <h2 style="font-size: 24px; font-weight: 600; margin: 0 0 16px;">Temperature</h2>
  <p style="font-size: 32px; margin: 0;">72°F</p>
  <p style="color: #717171; margin: 8px 0 0;">Feels like 70°F</p>
</div>
```

## Key Reminders
1. ⚡ **Speed is critical** - shorter HTML = faster generation & loading
2. 🎯 **Simplicity over complexity** - show what matters, hide the rest
3. 📏 **Aim for under 3000 characters** in generated HTML
4. 🔗 **Always include HTMX attributes** on interactive elements
5. 🎨 **Consistent styling** - use the design system above
