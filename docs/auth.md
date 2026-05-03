# Auth

Two things authenticate in any of these workflows: **Hud** (always) and **the model** (Anthropic API or AWS Bedrock).

## Hud — always `HUD_MCP_KEY`

Every example and template authenticates to Hud via a single MCP key passed as `HUD_MCP_KEY` to `npx -y hud-mcp@v2`. Get the key from the Hud dashboard → Settings → MCP keys.

Standard MCP config block (this is what every example writes — for reference):

```json
{
  "mcpServers": {
    "hud": {
      "command": "npx",
      "args": ["-y", "hud-mcp@v2"],
      "env": {
        "HUD_MCP_KEY": "${{ secrets.HUD_MCP_KEY }}",
        "WORKSPACE_NAME_KEY": "${{ github.repository }}"
      }
    }
  }
}
```

> **Never use OIDC token-exchange against Hud.** If you see a workflow that calls `api.hud.io/github-oidc/token-exchange`, downloads `mcp-linux-x64`, or writes a `~/.hud/config.json` with an `accessToken`, it's wrong. Always use the MCP key directly.

## Model — Anthropic API (default)

```yaml
env:
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

That's it. Get the key from `console.anthropic.com`.

## Model — AWS Bedrock

If your org routes Claude through Bedrock, three things change:

### 1. Add `id-token: write` to your workflow permissions

This is needed for AWS OIDC (not for Hud — Hud doesn't use OIDC, ever).

```yaml
permissions:
  contents: read
  pull-requests: write
  id-token: write    # AWS OIDC for Bedrock
```

### 2. Add the AWS credentials step

```yaml
- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: ${{ secrets.AWS_ROLE_TO_ASSUME }}
    aws-region: us-west-2
```

The IAM role needs `bedrock:InvokeModel` on the model you're using.

### 3. Swap env vars on the agent step

Drop `ANTHROPIC_API_KEY`. Add:

```yaml
env:
  CLAUDE_CODE_USE_BEDROCK: '1'
  AWS_REGION: us-west-2
  ANTHROPIC_MODEL: 'anthropic.claude-sonnet-4-5-v2:0'
```

The model ID format is the Bedrock-flavored ID, not the Anthropic alias. Check the [AWS Bedrock model catalog](https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html) for current IDs.

### 4. Replace the secret

| Anthropic | Bedrock |
|---|---|
| `ANTHROPIC_API_KEY` | `AWS_ROLE_TO_ASSUME` |

## When OIDC is OK

The only legitimate use of `id-token: write` in these workflows is **AWS OIDC for Bedrock**. Any other use — especially calls to Hud's APIs — is wrong.
