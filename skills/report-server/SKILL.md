# Report Server

Publish HTML reports viewable from any device on the LAN at `10.0.0.46:3080`.

## When to use

When any agent generates a report, dashboard, or data visualization that Matthew should be able to view from his Surface tablet. Examples: Starscream engagement reports, Sky-Lynx weekly analysis, Galvatron pipeline health, IdeaForge status, Swindle listing previews.

## How to publish a report

1. Write the HTML file to `~/reports/` with a descriptive filename:
   ```
   ~/reports/starscream-engagement-2026-03-30.html
   ```

2. Write a metadata sidecar (optional but recommended):
   ```bash
   cat > ~/reports/starscream-engagement-2026-03-30.meta.json << 'EOF'
   {
     "title": "Starscream Engagement Report — March 30, 2026",
     "agent": "starscream",
     "created": "2026-03-30 22:00"
   }
   EOF
   ```

3. The report is immediately viewable at:
   ```
   http://10.0.0.46:3080/starscream-engagement-2026-03-30.html
   ```

4. The index at `http://10.0.0.46:3080/` lists all reports sorted by date.

## HTML style guide

Use dark theme to match the ST Metro aesthetic:
- Background: `#0d1117`
- Text: `#c9d1d9`
- Headers/accent: `#58a6ff`
- Secondary accent: `#bc8cff`
- Borders: `#30363d`
- Font: system stack (`-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif`)

Reports must be self-contained (inline CSS, no external deps). Include responsive `<meta viewport>` tag.

## Server management

```bash
# Start (PM2)
pm2 start ~/reports/server.py --name report-server --interpreter python3

# Check status
curl -s http://10.0.0.46:3080/ | head -5

# View from Surface
# http://10.0.0.46:3080/
```

## File conventions

- Filename: `{agent}-{report-type}-{YYYY-MM-DD}.html`
- Metadata: `{same-stem}.meta.json`
- All files in `~/reports/` (flat, no subdirectories)
- Server ignores non-HTML files in the directory listing

## NEVER

- Never use `localhost` — always `10.0.0.46:3080`
- Never use external CDNs or links — reports must work offline
- Never delete reports without asking — they're the historical record
