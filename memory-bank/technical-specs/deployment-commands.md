# 🚀 Deployment Commands for fly.io

## Quick Deploy (What Bob Needs)

```bash
# From the erddap2mcp directory, just run:
fly deploy

# That's it! fly.toml handles everything
```

## Full Process (If Starting Fresh)

```bash
# 1. Login to fly.io (only needed once)
fly auth login

# 2. Deploy the app (uses Dockerfile and fly.toml)
fly deploy

# 3. Check deployment status
fly status -a erddap2mcp

# 4. Monitor logs
fly logs -a erddap2mcp

# 5. If something goes wrong, check the app
fly apps list
```

## What Gets Deployed

The `fly deploy` command:
1. Builds the Docker image using the Dockerfile
2. Pushes it to fly.io registry
3. Deploys to https://erddap2mcp.fly.dev/
4. Auto-configures SSL/HTTPS
5. Sets up auto-scaling based on fly.toml

## Files Used

- **Dockerfile** - Defines the container
- **fly.toml** - Configuration for fly.io
- **requirements.txt** - Python dependencies
- **erddap_remote_mcp_oauth.py** - The actual server

## Important Notes

- The app name is `erddap2mcp` (defined in fly.toml)
- Region is `mia` (Miami)
- Auto-starts and stops based on traffic
- 1GB RAM, 1 shared CPU

## Testing After Deployment

```bash
# Test the remote server
curl https://erddap2mcp.fly.dev/

# Test with mcp-remote
npx mcp-remote https://erddap2mcp.fly.dev/ --test
```

---

**Last Updated**: 2024-01-15
**Note**: Bob keeps forgetting this, so we wrote it down! 🚀