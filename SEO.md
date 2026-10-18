# SEO & Setup Checklist — enigmuz/enigmuz

GitHub strips `<meta>` tags, CSS and scripts from READMEs, so text that is truly hidden can't be done, and search engines ignore it anyway. What actually ranks a GitHub profile is below. The README already handles the in-file parts (keyword-rich headings, descriptive `alt` text on every image, a collapsible `index --about` block, and a keyword comment at the top for anyone reading the source).

## 1. Publish the profile README
1. Create a **public** repo named exactly **`enigmuz`** (it has to match your username).
2. Push everything in this folder to the `main` branch.
3. Go to **Settings → Actions → General → Workflow permissions** and choose **Read and write permissions**.
4. Open **Actions**, run **🐍 Generate Contribution Snake** once by hand. It creates the `output` branch that holds the snake SVGs, then refreshes every 12 hours.

## 2. Profile fields (these carry the most SEO weight)
| Field | Suggested value |
|---|---|
| **Name** | `Nimantha Perera (Enigmuz)`: Google indexes the display name in the page title |
| **Bio** | `DevSecOps Engineer · Agentic AI Security · Security Automation · Threat Hunting` |
| **Website** | Your LinkedIn or portfolio URL |
| **Social accounts** | Add LinkedIn and X/Twitter. Cross-links help Google tie the identities together |
| **Pinned repos** | PhantomEye, nexo-sentinel-V1, ThreatScry, plus your strongest agentic AI repo |

## 3. Repo-level SEO (do this for every pinned repo)
- **Description:** one plain-English sentence with the main keyword, e.g. *"AI-powered domain-squatting detection and takedown framework"*.
- **Topics** (up to 20): `cybersecurity`, `devsecops`, `threat-intelligence`, `security-automation`, `soar`, `siem`, `threat-hunting`, `agentic-ai`, `ai-security`, `mcp`, `red-teaming`, `brand-protection`, `phishing-detection`, `python`, `fastapi`.
- **Social preview image:** Settings → Social preview. Upload a 1280×640 banner.
- Each repo needs its own README whose first heading uses the project name and its keyword.

## 4. Off-GitHub signals
- Link `github.com/enigmuz` from LinkedIn, your CV and any write-ups. Backlinks are what move ranking.
- Use the same handle, **Enigmuz**, everywhere so search engines merge the identities.

## Regenerating the ASCII terminal
```bash
pip install pillow
python scripts/generate_terminal.py --image assets/avatar.png --out assets/terminal.svg --cols 52
```
If you swap `assets/avatar.png` (a square image works best), the **🖥️ Rebuild ASCII Terminal** workflow rebuilds the SVG on push.
