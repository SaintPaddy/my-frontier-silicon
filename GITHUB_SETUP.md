# GitHub Setup Guide

## Publishing Your Integration to GitHub

Follow these steps to share your integration with the world!

## Prerequisites

- GitHub account
- Git installed on your computer
- This integration folder

## Step 1: Create GitHub Repository

### Via GitHub Website

1. Go to https://github.com
2. Click the **+** icon (top right) → **New repository**
3. Repository name: `my-frontier-silicon` (or your choice)
4. Description: `Advanced Home Assistant integration for Frontier Silicon radios`
5. Choose **Public** (required for HACS)
6. ✅ Add a README file
7. Choose license: **MIT License**
8. Click **Create repository**

## Step 2: Prepare Your Files

### Update These Files First

Before uploading, update your username in these files:

**1. manifest.json**
```json
{
  "codeowners": ["@SaintPaddy"],  // ← Change this
  "documentation": "https://github.com/SaintPaddy/my-frontier-silicon",  // ← Change this
  "issue_tracker": "https://github.com/SaintPaddy/my-frontier-silicon/issues"  // ← Change this
}
```

**2. README.md**
- Replace all instances of `SaintPaddy` with your GitHub username

**3. INSTALL.md**
- Replace repository URL with your actual URL

**4. info.md**
- Replace repository links with your actual links

## Step 3: Upload to GitHub

### Method 1: GitHub Web Interface (Easiest)

1. In your repository, click **Add file** → **Upload files**
2. Drag and drop the entire `my-frontier-silicon` folder
3. Or click **choose your files** and select all files
4. Scroll down to **Commit changes**
5. Commit message: `Initial release v1.0.0`
6. Click **Commit changes**

### Method 2: Git Command Line

```bash
# Navigate to your integration folder
cd /path/to/homerton_hacs_integration

# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial release v1.0.0"

# Add remote (replace YOURUSERNAME)
git remote add origin https://github.com/YOURUSERNAME/my-frontier-silicon.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 4: Create a Release

Releases are required for HACS!

### Via GitHub Website

1. Go to your repository
2. Click **Releases** (right sidebar)
3. Click **Create a new release**
4. Tag version: `v1.0.0` (must start with 'v')
5. Release title: `v1.0.0 - Initial Release`
6. Description:
```markdown
## 🎉 Initial Release

First public release of My Frontier Silicon integration!

### Features
- ✅ Full media player control
- ✅ Preset/station selection dropdown
- ✅ Mode switching
- ✅ Rich sensors
- ✅ Easy UI-based setup

### Tested Devices
- Majority Homerton 2
- Should work with all Frontier Silicon radios

See [CHANGELOG.md](./CHANGELOG.md) for full details.
```
7. Click **Publish release**

## Step 5: Make HACS-Compatible

### Verify Required Files

Your repository must have:
- ✅ `custom_components/my_frontier_silicon/` folder
- ✅ `manifest.json` in component folder
- ✅ `hacs.json` in repository root
- ✅ `README.md` in repository root
- ✅ At least one release tag

### File Structure Should Be:

```
my-frontier-silicon/
├── custom_components/
│   └── my_frontier_silicon/
│       ├── __init__.py
│       ├── api.py
│       ├── button.py
│       ├── config_flow.py
│       ├── const.py
│       ├── coordinator.py
│       ├── manifest.json
│       ├── media_player.py
│       ├── select.py
│       ├── sensor.py
│       ├── strings.json
│       └── translations/
│           └── en.json
├── hacs.json
├── README.md
├── CHANGELOG.md
├── INSTALL.md
├── info.md
└── LICENSE
```

## Step 6: Test HACS Installation

Before sharing publicly, test it yourself!

### Add as Custom Repository

1. Open your Home Assistant
2. Go to HACS → Integrations
3. Click ⋮ (menu) → Custom repositories
4. URL: `https://github.com/YOURUSERNAME/my-frontier-silicon`
5. Category: **Integration**
6. Click **Add**

### Install and Test

1. Find your integration in HACS
2. Install it
3. Restart HA
4. Add the integration via UI
5. Test all features

## Step 7: Share with the Community

### Option 1: Submit to HACS Default Repository (Recommended)

Once tested and stable:

1. Go to https://github.com/hacs/default
2. Fork the repository
3. Add your integration to `integration` file
4. Create pull request
5. Wait for review and approval

After approval, everyone can find your integration in HACS without adding custom repository!

### Option 2: Share Link Directly

Share your repository URL on:
- Home Assistant Community Forums
- Reddit r/homeassistant
- Discord servers
- Social media

## Step 8: Maintenance

### Updating Your Integration

When you make changes:

```bash
# Make your changes
# ...

# Commit changes
git add .
git commit -m "Fix: Description of fix"
git push

# Create new release
# Go to GitHub → Releases → Draft a new release
# Tag: v1.0.1 (increment version)
# Describe changes
# Publish
```

### Version Numbering

Follow semantic versioning:
- `v1.0.1` - Bug fixes
- `v1.1.0` - New features
- `v2.0.0` - Breaking changes

Update version in:
- manifest.json
- Release tag
- CHANGELOG.md

## Troubleshooting

### HACS Can't Find Integration

**Check:**
- Repository is public
- At least one release exists
- hacs.json is in root
- custom_components folder structure is correct

### Installation Fails

**Check:**
- manifest.json is valid JSON
- All required files present
- No syntax errors in Python files

### Integration Won't Load

**Check Home Assistant Logs:**
```
Settings → System → Logs
Search for your integration name
```

**Common Issues:**
- Import errors (missing files)
- Invalid manifest
- Python syntax errors

## Security

### Before Publishing

**Review for sensitive data:**
- Remove any hardcoded IPs
- Remove any personal information
- Remove test credentials
- Check logs for exposed secrets

### .gitignore

Create `.gitignore` file:
```
__pycache__/
*.py[cod]
*$py.class
*.so
.DS_Store
*.log
```

## Legal

### License

Include MIT license (already done) or your choice of open-source license.

### Attribution

Give credit to:
- Original Frontier Silicon API documentation
- Home Assistant team
- Contributors

## Promotion

### Write About It

**Home Assistant Community:**
1. Create post in "Share Your Projects"
2. Include screenshots
3. Explain features
4. Link to GitHub

**README Should Have:**
- Clear description
- Installation instructions
- Usage examples
- Screenshots/GIFs
- Troubleshooting
- Contributing guidelines

### Quality Indicators

Add badges to README:

```markdown
![GitHub release](https://img.shields.io/github/release/YOURUSERNAME/my-frontier-silicon.svg)
![GitHub](https://img.shields.io/github/license/YOURUSERNAME/my-frontier-silicon.svg)
![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)
```

## Getting Help

**Resources:**
- HACS documentation: https://hacs.xyz/
- HA Developer Docs: https://developers.home-assistant.io/
- HA Discord: https://discord.gg/home-assistant

**Questions?**
- Open an issue on GitHub
- Ask in HA Community forums
- Join HACS Discord

## Success Checklist

Before going public:

- [ ] All files uploaded to GitHub
- [ ] Repository is public
- [ ] At least one release created
- [ ] Tested installation via HACS
- [ ] All features working
- [ ] README is complete
- [ ] License is included
- [ ] No sensitive data in code
- [ ] Documentation is clear
- [ ] CHANGELOG is up to date

## Your Repository is Ready! 🎉

You can now share this link with anyone:
```
https://github.com/YOURUSERNAME/my-frontier-silicon
```

They can add it as a custom repository in HACS!

---

**Good luck with your first integration! 🚀**
