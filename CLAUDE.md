# Mintlify Documentation

This directory contains the ChatAds documentation site powered by Mintlify. Changes pushed to this repo automatically deploy to [docs.getchatads.com](https://docs.getchatads.com).

## Tech Stack

- **Platform**: Mintlify
- **Content Format**: MDX (Markdown + JSX components)
- **API Docs**: Auto-generated from OpenAPI spec
- **Deployment**: Automatic on push to main

## Project Structure

```
/docs
├── docs.json              # Mintlify configuration (nav, theme, API settings)
├── index.mdx              # Homepage
├── quickstart.mdx         # Getting started guide
├── api-reference/
│   ├── introduction.mdx   # API overview
│   ├── messages.mdx       # POST /v1/chatads/messages endpoint
│   └── openapi.json       # OpenAPI spec (synced from API)
├── guides/
│   ├── authentication.mdx # API key setup and security
│   ├── rate-limits.mdx    # Quotas and limits
│   └── error-handling.mdx # Error codes and troubleshooting
├── sdks/
│   ├── typescript.mdx     # TypeScript SDK docs
│   ├── python.mdx         # Python SDK docs
│   └── mcp.mdx            # MCP wrapper docs
├── images/                # Documentation images
├── logo/                  # Logo files (light/dark)
└── snippets/              # Reusable content snippets
```

## Configuration (docs.json)

Key settings:
- **theme**: "mint" (Mintlify default)
- **colors**: Primary #6366F1 (indigo)
- **api.baseUrl**: Modal API endpoint
- **api.auth**: X-API-Key header authentication
- **openapi**: Points to `/api-reference/openapi.json`

## Writing Documentation

### MDX Components

Mintlify provides built-in components:

```mdx
<Note>Important information</Note>
<Warning>Caution about something</Warning>
<Tip>Helpful suggestion</Tip>

<CodeGroup>
```bash cURL
curl -X POST ...
```
```typescript TypeScript
const client = new ChatAdsClient();
```
</CodeGroup>

<ParamField body="message" type="string" required>
  Description of parameter
</ParamField>

<ResponseField name="success" type="boolean">
  Description of response field
</ResponseField>

<CardGroup cols={2}>
  <Card title="Title" icon="icon-name" href="/path">
    Card description
  </Card>
</CardGroup>
```

### API Reference Pages

For API endpoint documentation, use the format:

```mdx
---
title: "Endpoint Name"
api: "METHOD /path"
description: "Brief description"
---

Content...

<RequestExample>
```bash cURL
curl command here
```
</RequestExample>

<ResponseExample>
```json Success Response
{ ... }
```
</ResponseExample>
```

## OpenAPI Spec

The file `/api-reference/openapi.json` should be kept in sync with the live API.

To update:
```bash
curl -s https://chatads--chatads-api-fastapiserver-serve.modal.run/openapi.json > api-reference/openapi.json
```

This enables:
- Auto-generated parameter documentation
- "Try It" interactive API testing
- Accurate type information

## Development

### Local Preview

Mintlify doesn't require local setup - changes preview in PR deployments.

For local development (optional):
```bash
npm i -g mintlify
mintlify dev
```

### Making Changes

1. Edit MDX files directly
2. Push to main branch
3. Mintlify auto-deploys within ~2 minutes
4. Preview at docs.getchatads.com

## Navigation Structure

Navigation is defined in `docs.json` under `navigation.tabs`:

- **Documentation** tab: Getting Started, Guides, SDKs
- **API Reference** tab: Overview, Endpoints

To add a new page:
1. Create the `.mdx` file
2. Add to appropriate group in `docs.json` navigation

## Related Resources

- **API Implementation**: `/api/api/` (source of truth for OpenAPI spec)
- **SDK Source Code**: `/sdks/` (TypeScript, Python, MCP, n8n)
- **In-App Docs**: `/frontend/src/pages/Docs.tsx` (dashboard documentation)

## Key Documentation Areas

### Current Pages
- Getting Started (index, quickstart)
- Guides (authentication, rate-limits, error-handling)
- SDKs (typescript, python, mcp)
- API Reference (introduction, messages endpoint)

### Areas That Need Work (CHA-353)
- FAQ section (missing)
- n8n SDK documentation (missing)
- Complete error codes reference
- Intent scoring documentation
- `skip_message_analysis` parameter documentation
- Response schema completeness

## Support Docs Compilation

The `/docs` content is compiled into a single text file for use by the support chatbot.

### Script Location
`/docs/scripts/compile-support-docs.py`

### How to Run
```bash
cd /Users/chrisshuptrine/Downloads/github/docs/scripts
python compile-support-docs.py
```

### What It Does
1. Finds all `.mdx` files in `/docs` (excludes `/docs/snippets/`)
2. Extracts titles from YAML frontmatter
3. Strips frontmatter and MDX/JSX components (`<Card/>`, `<Warning>`, etc.)
4. Cleans whitespace while preserving code blocks
5. Outputs to `/marketing/support-docs.txt`

### Data Flow
```
/docs/**/*.mdx → compile-support-docs.py → /marketing/support-docs.txt
                                                    ↓
                                    https://www.getchatads.com/support-docs.txt
                                                    ↓
                                    support-chat edge function (fetches + caches)
```

### When to Run
Run this script manually after making changes to documentation that should be reflected in the support chatbot. The output file is committed to git and served publicly.

### Related Files
- **Script**: `/docs/scripts/compile-support-docs.py`
- **Output**: `/marketing/support-docs.txt` (~62KB)
- **Consumer**: `/supabase/functions/support-chat/index.ts`
