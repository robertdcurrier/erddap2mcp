# 📜 Bob's Requirements & Wisdom

**Every word from Bob is SACRED - These are direct quotes and requirements**

## 2024-01-15 Session

### On Tool Count
> "What are you talking about? List the tools in the local server..."
> "I think they must be wishful thinking..."

**Translation**: Bob identified that we had useless URL generator tools padding the count.

### On URL Generators
> "Do the url_generators actually get called and used in the code? Why does the remote version work perfectly even though it doesn't have these generators?"

**Result**: Discovered URL generators were completely unnecessary.

### On Who Added The Bloat
> "That 'someone' was you! LOL, busted."

**Action**: Immediately cleaned up all 6 unnecessary tools.

### On README Instructions
> "Under 'Quick Start' it says 2. Run the server: we don't need to run the server! Claude will take care of that when we start Claude Desktop. That's very confusing."

**Rule**: NEVER tell users to manually run servers.

### On Developer vs User Documentation
> "And under Option 2: Remote MCP Server we DO NOT WANT TO TELL USERS to install dependencies, run locally for testing or deploy to fly.io. That's for ME ONLY!!!!"

**Rule**: Strictly separate user instructions from developer documentation.

### On ERDDAP Server Limitations
> "OH! I remember now! I *did* have a download function, but I got yelled at by the ERDDAP team because the ERDDAP code isn't robust enough to handle big requests and they live in the 90s and want 'the client to deal with this' rather than making their server bulletproof!"

**Context**: Explains why download_file was neutered to just return URLs.

### On Deployment
> "Well, let's push this so we get the production code up and ready for people to use."
> "Push it."

**Action**: Always push clean, working code to production promptly.

### On Memory Bank
> "read ~/.claude/CLAUDE.md and set up a memory-bank for this project"

**Rule**: EVERY project MUST have a memory bank. NO EXCEPTIONS.

### On ERDDAP Server List
> "I have put a new file in this directory called erddaps.json. Let's remove the hardwired list of ERDDAP servers from the code, and load erddaps.json when we run. Erddaps.json will provide our list of servers from now on."

**Action**: Implemented dynamic loading from erddaps.json with 76 servers.

---

## Golden Bob Principles
1. **Clean code matters** - Remove unnecessary bloat
2. **User experience first** - Don't confuse users with developer tasks
3. **Push working code** - Get it to production
4. **Document everything** - Especially the painful lessons
5. **Memory is mandatory** - Never forget what we've learned

---

**Remember**: When Bob identifies a problem, FIX IT IMMEDIATELY.