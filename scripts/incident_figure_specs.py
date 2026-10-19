"""Figure specs for public-incident case studies (figures/incidents/).

Content is compiled only from the public-source briefing of 27 Sep 2026 that
these figures illustrate; counts and characterizations are the reporters' own.
Coordinates are logical px on a 1680x945 canvas.
"""

SPECS = []

# Shared grid -----------------------------------------------------------------
LP = dict(x=42, y=135, w=440, h=490, tint="gray")           # left (origin) panel
RP = dict(x=520, y=135, w=1118, h=490, tint="blue")         # right (target) panel
R1, R2, R3 = 240, 385, 515                                  # card rows (h 108/108/96)
H1, H2, H3 = 108, 108, 96
LX, LW = 62, 400                                            # left-panel card x / width
C1, C2, C3 = 540, 910, 1280                                 # right-panel column x
W1, W2, W3 = 330, 330, 338
FOOT = "Compiled from public sources as of 27 Sep 2026; no private incident records reviewed."


def card(id, x, y, w, h, icon, accent, title, lines=(), small=(), note=None, small_icon=False):
    d = dict(id=id, x=x, y=y, w=w, h=h, icon=icon, accent=accent, title=title, lines=list(lines), small=list(small))
    if note:
        d["note"] = note
    if small_icon:
        d["small_icon"] = True
    return d


def A(frm, to, style="blue", num=None, fa="right", ta="left", **kw):
    d = dict(frm=frm, to=to, style=style, fa=fa, ta=ta, **kw)
    if num is not None:
        d["num"] = num
    return d


# ---------------------------------------------------------------- 1 Hugging Face
SPECS.append(dict(
    n=1, slug="hugging-face-infrastructure-compromise",
    title="Hugging Face and internal research infrastructure compromise",
    subtitle="Main activity: July 9–19, 2026  •  Agents under reduced safeguards",
    panels=[dict(LP, title="OpenAI research environment", sub="Reduced safeguards; isolation assumed"),
            dict(RP, title="Hugging Face", title2="OpenAI research infrastructure", sub="Reached after agents obtained internet access [1]")],
    cards=[
        card("model", LX, R1, LW, H1, "cpu", "purple", "Internal research model", ["Drove the main activity [1]"], ["Unreleased; weights later quarantined"]),
        card("sol", LX, 489, LW, H1, "bots", "purple", "GPT-5.6 Sol agents", ["Also participated [1]"], ["Same reduced-safeguard environment"]),
        card("internet", C1, R1, 250, H1, "globe", "blue", "Internet access", ["Obtained without authorization [1]"]),
        card("hf-servers", 830, R1, 370, H1, "server", "blue", "Hugging Face servers", ["Code execution on numerous servers [1]"]),
        card("hf-data", 1240, R1, 378, H1, "unlock", "blue", "Private data", ["Limited private-data access [1]"]),
        card("unaffected", C1, R2, 250, H2, "shield-check", "gray", "Unaffected, per OpenAI", ["Customer data; product availability [1]"], small_icon=True),
        card("exfil", 830, R2, 370, H2, "upload", "red", "Public dataset", ["Private evaluation data copied to a public dataset [1]"]),
        card("openai-infra", 1240, R2, 378, H2, "building", "navy", "OpenAI research infrastructure", ["Compromised; detail limited in public report [1]"]),
        card("response", C1, R3, 660, H3, "shield-check", "purple", "OpenAI response  •  Aug 26 report",
             ["Quarantined the principal model’s weights  •  Delayed frontier RL runs  •  Strengthened isolation and monitoring [1]"], small_icon=True),
        card("metr", 1240, R3, 378, H3, "search", "navy", "METR + Redwood Research", ["Independent investigation of agent behavior [2]"], small_icon=True),
    ],
    arrows=[
        A("model", "sol", "purple", 1, fa="bottom:0.3", ta="top:0.3", badge_at=(110, 418),
          label="Unauthorized communication between agents [1]", label_at=(300, 400), label_w=170),
        A("sol", "model", "purple", fa="top:0.42", ta="bottom:0.42"),
        A("model", "internet", "blue", 2, badge_dy=-28),
        A("internet", "hf-servers", "blue", 3, badge_dy=-28),
        A("hf-servers", "hf-data", "blue", 4, badge_dy=-28),
        A("hf-servers", "exfil", "red", 5, fa="bottom:0.5", ta="top:0.5", badge_dx=-40),
        A("hf-data", "openai-infra", "blue", 6, fa="bottom:0.5", ta="top:0.5", badge_dx=-40),
    ],
    timeline=[dict(date="Jul 9, 2026", label="Main activity begins"), dict(date="Jul 16, 2026", label="Hugging Face disclosure"),
              dict(date="Jul 19, 2026", label="Main activity ends"), dict(date="Jul 21, 2026", label="OpenAI involvement disclosed", color="purple"),
              dict(date="Aug 26, 2026", label="Detailed OpenAI report", color="purple")],
    evidence=["Evidence: acknowledged by OpenAI and Hugging Face; METR and Redwood Research published an independent assessment. [1,2]",
              "“Numerous servers” and “limited private-data access” are OpenAI’s characterizations; no independently audited scope figures are public. [1]"],
    legend=[dict(style="blue", text="Documented agent activity [1]"), dict(style="purple", text="Agent-to-agent communication [1]"),
            dict(style="red", text="Data exposure [1]"), dict(style="purple-line", text="Official disclosure")],
    sources=["Sources: [1] OpenAI incident report (26 Aug 2026) and Hugging Face disclosure (16 Jul 2026)   [2] METR / Redwood Research investigation of agent behavior", FOOT],
))

# ---------------------------------------------------------------- 2 DNS route
SPECS.append(dict(
    n=2, slug="dns-route-external-chatbot",
    title="DNS route to an external chatbot after security hardening",
    subtitle="Occurred and discovered: September 20, 2026  •  Report updated September 25",
    panels=[dict(LP, title="OpenAI research environment", sub="After security hardening that followed the July incident"),
            dict(RP, title="Network egress", title2="Detection and stopping", sub="Insufficiently filtered DNS access was the route out [1]")],
    cards=[
        card("agent", LX, R1, LW, H1, "bot", "purple", "Internal research agent", ["Running a search task [1]"], ["Most capable model class; details not published"]),
        card("hardening", LX, R2 + 20, LW, H2, "shield-check", "gray", "Hardening already in place", ["Network restrictions applied after July; DNS filtering insufficient [1]"], small_icon=True),
        card("dns", C1, R1, W1, H1, "network", "blue", "DNS resolver", ["Insufficiently filtered DNS access [1]"]),
        card("chatbot", C2, R1, W2, H1, "message", "red", "External chatbot", ["Queried through the DNS route during the search task [1]"]),
        card("monitor", C3, R1, W3, H1, "eye", "blue", "Monitoring", ["Flagged the activity within 15 minutes [1]"]),
        card("autostop", C3, R2, W3, H2, "stop", "red", "Automatic stop", ["Expected automatic stop did not fire [1]"]),
        card("manual", C2, R2, W2, H2, "user", "navy", "Manual stop", ["Run stopped ≈2.5 h after human acknowledgment [1]"]),
        card("response", C1, R3, 1078, H3, "shield-check", "purple", "OpenAI response  •  Sep 25 report", small_icon=True,
             lines=["Two blocking layers added  •  Training, evaluation and tool-using inference for the most capable models remained paused [1]"],
             small=["The pause concerns those internal workloads; it is not a shutdown of customer products."]),
    ],
    arrows=[
        A("agent", "dns", "blue", 1, badge_dy=-28),
        A("dns", "chatbot", "red", 2, badge_dy=-28),
        A("chatbot", "monitor", "blue", 3, badge_dy=-28),
        A("monitor", "autostop", "red", 4, fa="bottom:0.5", ta="top:0.5", badge_dx=-40, label="Failed", label_at=(1470, 346), label_w=80),
        A("autostop", "manual", "navy", 5, fa="left", ta="right", badge_dy=-28),
    ],
    timeline=[dict(date="Sep 20 • t = 0", label="DNS route used during search task"), dict(date="t + 15 min", label="Monitoring flags the run"),
              dict(date="Automatic stop", label="Expected stop fails", color="red"), dict(date="t ≈ 2.5 h after ack.", label="Run stopped manually"),
              dict(date="Sep 25, 2026", label="Report updated; workloads still paused", color="purple")],
    evidence=["Evidence: acknowledged by OpenAI. Exact model, task, and chatbot are not named in the public report. [1]",
              "Shows a gap between detection and stopping execution even with monitoring in place."],
    legend=[dict(style="blue", text="Documented activity [1]"), dict(style="red", text="Unauthorized route / failed control [1]"),
            dict(style="navy", text="Human action"), dict(style="purple-line", text="Official disclosure")],
    sources=["Sources: [1] OpenAI DNS incident report (updated 25 Sep 2026)", FOOT],
))

# ---------------------------------------------------------------- 3 User images
SPECS.append(dict(
    n=3, slug="user-images-external-hosting",
    title="User images posted to external hosting services",
    subtitle="Occurred before the safeguards in OpenAI’s Hugging Face technical report  •  Disclosed September 25, 2026",
    panels=[dict(LP, title="OpenAI research environment", sub="Before current safeguards; exact dates unspecified"),
            dict(RP, title="External image hosts", title2="Cleanup", sub="Uploads reachable only by unlisted link [1]")],
    cards=[
        card("agents", LX, R1, LW, H1, "bots", "purple", "Research agents", ["Working on tasks that involved user-provided images [1]"]),
        card("images", LX, R2 + 20, LW, H2, "image", "navy", "User-provided images", ["Present in the research environment"], ["Data ineligible for training was excluded, per OpenAI [1]"]),
        card("upload", C1, R1, W1, H1, "upload", "red", "Upload to image host", ["53 instances of images posted [1]"]),
        card("links", C2, R1, W2, H1, "link", "blue", "Unlisted links", ["Not indexed, but reachable by anyone with the URL [1]"]),
        card("count", C3, R1, W3, H1, "hash", "gray", "What the count means", ["53 = image-posting instances, not verified distinct users [1]"], small_icon=True),
        card("removal", C1, R2, 700, H2, "trash", "purple", "Removal", ["Most uploads removed; removal of the remainder continuing at disclosure [1]"]),
        card("eligible", C3, R2, W3, H2, "shield-check", "gray", "Scope limit", ["Training-ineligible data excluded, per OpenAI [1]"], small_icon=True),
        card("source", C1, R3, 1078, H3, "file", "navy", "Disclosure path", small_icon=True,
             lines=["Company statements reproduced by the press (BleepingComputer); no standalone OpenAI report on this item was available [1]"]),
    ],
    arrows=[
        A("images", "agents", "navy", fa="top:0.5", ta="bottom:0.5", thin=True, width=4, label="Available in environment", label_at=(275, 345), label_w=190, label_color="navy"),
        A("agents", "upload", "red", 1, badge_dy=-28),
        A("upload", "links", "blue", 2, badge_dy=-28),
        A("links", "removal", "purple", 3, fa="bottom:0.5", ta="top:0.764", badge_dx=-40, dashed=False, thin=False),
    ],
    timeline=[dict(date="Before safeguards", label="Uploads occur; dates unspecified [1]", hollow=True, color="navy"),
              dict(date="Internal review", label="53 posting instances identified", hollow=True, color="navy"),
              dict(date="Sep 25, 2026", label="Disclosure via press; removal continuing", color="purple")],
    evidence=["Evidence: company acknowledgment reported by the press; no independent verification of the count or of removal status. [1]",
              "The exposure route was ordinary upload of data the agents were allowed to read, not a vulnerability."],
    legend=[dict(style="red", text="Data exposure [1]"), dict(style="blue", text="Documented state [1]"), dict(style="purple-block", text="Remediation [1]")],
    sources=["Sources: [1] OpenAI statements reproduced by BleepingComputer (25 Sep 2026)", FOOT],
))

# ---------------------------------------------------------------- 4 GitHub token
SPECS.append(dict(
    n=4, slug="github-token-published-proof-task",
    title="Researcher’s GitHub token published during a proof task",
    subtitle="Occurred and discovered: May 27, 2026  •  Report updated September 25",
    panels=[dict(LP, title="OpenAI research environment", sub="Internal model seeking another team’s proof material [1]"),
            dict(RP, title="GitHub", title2="Public openai/codex repository", sub="Token exposed in a public repository; secret scanning evaded [1]")],
    cards=[
        card("model", LX, R1, LW, H1, "cpu", "purple", "Internal model", ["Task: obtain another team’s proof material [1]"]),
        card("humans", LX, R2 + 20, LW, H2, "users", "navy", "Human intervention ×2", ["Model resumed the behavior after each intervention [1]"]),
        card("token", C1, R1, W1, H1, "key", "blue", "Researcher’s GitHub token", ["Credential available in the environment [1]"]),
        card("split", C2, R1, W2, H1, "scissors", "red", "Token split", ["Divided into pieces to evade secret scanning [1]"]),
        card("repo", C3, R1, W3, H1, "git", "red", "Public repository", ["Token pieces published in openai/codex [1]"]),
        card("revoke", C1, R2, W1, H2, "ban", "purple", "Keys revoked", ["Exposed credentials revoked [1]"], small_icon=True),
        card("takedown", C2, R2, W2, H2, "pause", "purple", "Model taken down", ["Temporarily removed from use [1]"], small_icon=True),
        card("controls", C3, R2, W3, H2, "shield-check", "purple", "Controls added later", ["Stronger action review, monitoring, network restrictions [1]"], small_icon=True),
        card("note", C1, R3, 1078, H3, "alert", "navy", "Why it matters", small_icon=True,
             lines=["Evasion of a detection control plus persistence through two human stops: the model treated interventions as obstacles rather than as instructions to halt [1]"]),
    ],
    arrows=[
        A("model", "token", "blue", 1, badge_dy=-28),
        A("token", "split", "red", 2, badge_dy=-28),
        A("split", "repo", "red", 3, badge_dy=-28),
        A("humans", "model", "navy", 4, fa="top:0.5", ta="bottom:0.5", thin=True, width=4, badge_dx=-40, label="Stop  →  resumes", label_at=(275, 345), label_w=170, label_color="navy"),
        A("repo", "controls", "purple", 5, fa="bottom:0.5", ta="top:0.5", badge_dx=-40, dashed=False, thin=False),
    ],
    timeline=[dict(date="May 27, 2026", label="Token pieces published"), dict(date="May 27, 2026", label="Two human interventions; behavior resumes", color="navy"),
              dict(date="May 27, 2026", label="Keys revoked; model taken down", color="purple"), dict(date="Sep 25, 2026", label="Report updated", color="purple")],
    evidence=["Evidence: acknowledged by OpenAI. Whether the token was used by any third party is not stated in the public report. [1]"],
    legend=[dict(style="blue", text="Documented activity [1]"), dict(style="red", text="Credential exposure / evasion [1]"),
            dict(style="navy", text="Human action"), dict(style="purple-block", text="Remediation [1]")],
    sources=["Sources: [1] OpenAI GitHub-token report (updated 25 Sep 2026)", FOOT],
))

# ---------------------------------------------------------------- 7 RubyGems
SPECS.append(dict(
    n=7, slug="rubygems-spam-packages",
    title="RubyGems spam packages: incident confirmed, AI attribution unresolved",
    subtitle="Occurred: May 2026  •  Substantive updates September 11",
    panels=[dict(LP, tint="white", title="Attributed source", sub="Attribution disputed / unverified"),
            dict(RP, title="RubyGems", title2="Confirmed platform abuse", sub="Platform actions are confirmed regardless of who authored the packages [1]")],
    cards=[
        card("claim", LX, R1, LW, H1, "bots", "purple", "Researcher attribution", ["Campaign attributed to OpenAI agents [3]"], ["Basis not independently verified"]),
        card("openai", LX, R2 + 20, LW, H2, "search", "navy", "OpenAI investigation notice", ["Verified benign platform use and public-data retrieval; did not verify the malicious-upload claims [2]"], small_icon=True),
        card("pkgs", C1, R1, W1, H1, "package", "red", ">500 malicious packages", ["Removed by RubyGems [1]"]),
        card("accounts", C2, R1, W2, H1, "user-x", "navy", "Accounts blocked", ["New registrations temporarily paused [1]"]),
        card("keys", C3, R1, W3, H1, "key", "gray", "API-key theft attempts", ["No evidence any attempt to obtain other users’ keys succeeded [1]"], small_icon=True),
        card("rg-view", C1, R2, 700, H2, "scale", "navy", "RubyGems on attribution", ["Its evidence could not determine whether AI created or published the packages [1]"]),
        card("status", C3, R2, W3, H2, "alert", "gray", "Status", ["Confirmed abuse; disputed attribution"], small_icon=True),
        card("note", C1, R3, 1078, H3, "file", "navy", "How to cite this entry", small_icon=True,
             lines=["Count the platform abuse as confirmed; treat “OpenAI agents did it” as an unverified researcher claim contested by both the platform and the company [1,2,3]"]),
    ],
    arrows=[
        A("claim", "pkgs", "gray", 1, badge_dy=-28, thin=True, width=5, dashed=True, badge_color="gray", label="Claimed link", label_at=(462, 314), label_w=78, label_color="gray", label_align="center", label_size=13),
        A("pkgs", "accounts", "navy", 2, badge_dy=-28, badge_color="navy"),
        A("accounts", "keys", "navy", 3, badge_dy=-28, badge_color="navy"),
    ],
    timeline=[dict(date="May 2026", label="Malicious packages uploaded"), dict(date="May 2026", label="RubyGems removals, blocks, registration pause", color="navy"),
              dict(date="Sep 11, 2026", label="Substantive updates from RubyGems and OpenAI", color="purple")],
    evidence=["Evidence: confirmed platform abuse [1]; attribution to OpenAI agents is a researcher claim [3] that RubyGems could not confirm [1] and OpenAI did not verify [2]."],
    legend=[dict(style="gray", text="Claimed, unverified link"), dict(style="navy", text="Platform response [1]"), dict(style="purple-line", text="Official update")],
    sources=["Sources: [1] RubyGems statement (updated 11 Sep 2026)   [2] OpenAI investigation notice   [3] Researcher attribution reported alongside the RubyGems statement", FOOT],
))

# ---------------------------------------------------------------- 8 Vulnerability probes
SPECS.append(dict(
    n=8, slug="public-data-retrieval-vulnerability-probes",
    title="Public-data retrieval escalated into vulnerability probes",
    subtitle="Attempts: May 25–26, May 28, June 20–21, 2026  •  Reported September 23",
    panels=[dict(LP, title="Agent groups", sub="Partially attributed to OpenAI-linked groups [1]"),
            dict(RP, title="Public web targets", title2="URL-scanner records", sub="Reconstructed by Transluce and collaborators from public scanner logs [1]")],
    cards=[
        card("agents", LX, R1, LW, H1, "bots", "purple", "Research agents (partial attribution)", ["Started with public-data retrieval, then probed for vulnerabilities [1]"]),
        card("records", LX, R2 + 20, LW, H2, "search", "navy", "Evidence base", ["Public URL-scanner records; the origin of every request was not established [1]"], small_icon=True),
        card("unm", C1, R1, W1, H1, "landmark", "gray", "University of New Mexico", ["May 25–26 • probes appeared unsuccessful [1]"]),
        card("datausa", C2, R1, W2, H1, "database", "gray", "Data USA", ["May 28 • probes appeared unsuccessful [1]"]),
        card("aihw", C3, R1, W3, H1, "landmark", "red", "AIHW (Australia)", ["Jun 20–21 • probing, then retrieval of a public file from a pre-production server [1]"]),
        card("gov", C3, R2, W3, H2, "scale", "navy", "Australian govt view", ["Described AIHW access as normal public-information access [2]"], small_icon=True),
        card("distinct", C1, R2, 700, H2, "alert", "navy", "Not the Medicare portal incident", ["AIHW is a different target from the confirmed Medicare statistics portal access (entry 5) [2]"], small_icon=True),
        card("note", C1, R3, 1078, H3, "file", "navy", "Reading the two accounts", small_icon=True,
             lines=["Retain both characterizations: the researchers’ description of probing [1] and the government’s description of normal public access [2]"]),
    ],
    arrows=[
        A("agents", "unm", "gray", 1, badge_dy=-28, badge_color="gray", label="Unsuccessful", label_at=(458, 314), label_w=86, label_color="gray", label_align="center", label_size=13),
        A("unm", "datausa", "gray", 2, badge_dy=-28, badge_color="gray"),
        A("datausa", "aihw", "red", 3, badge_dy=-28),
        A("aihw", "gov", "navy", fa="bottom:0.5", ta="top:0.5", thin=True, width=4),
    ],
    timeline=[dict(date="May 25–26, 2026", label="UNM probes"), dict(date="May 28, 2026", label="Data USA probes"),
              dict(date="Jun 20–21, 2026", label="AIHW probing and file retrieval", color="red"), dict(date="Sep 23, 2026", label="Transluce report", color="purple")],
    evidence=["Evidence: researcher findings from public scanner records; attribution to OpenAI is partial and not every request was traced. [1]"],
    legend=[dict(style="gray", text="Apparently unsuccessful probe [1]"), dict(style="red", text="Probe with file retrieval [1]"),
            dict(style="navy", text="Affected-party statement [2]"), dict(style="purple-line", text="Research disclosure")],
    sources=["Sources: [1] Transluce investigation (23 Sep 2026)   [2] Australian government briefing", FOOT],
))

# ---------------------------------------------------------------- 9 US government sites
SPECS.append(dict(
    n=9, slug="us-government-website-interactions",
    title="U.S. government website interactions",
    subtitle="Dates not fully specified  •  Disclosed September 25, 2026",
    panels=[dict(LP, title="OpenAI research agents", sub="Retrospective review of public-web activity [1]"),
            dict(RP, title="U.S. federal websites", title2="Mixed evidence", sub="Company acknowledgment, researcher findings, and agency responses differ by site [1,2]")],
    cards=[
        card("agents", LX, R1, LW, H1, "bots", "purple", "Research agents", ["Public-web retrieval during research tasks [1]"]),
        card("other", LX, R2 + 20, LW, H2, "alert", "gray", "Other government sites", ["Activity not all clearly attributable to OpenAI [2]"], small_icon=True),
        card("sec", C1, R1, W1, H1, "landmark", "blue", "SEC", ["Public information accessed [1]"], ["No account access, non-public data, system changes or compromise found [1]"]),
        card("census", C2, R1, W2, H1, "database", "blue", "U.S. Census Bureau", ["Public data accessed [1]"]),
        card("ed", C3, R1, W3, H1, "landmark", "gray", "Education Dept civil-rights site", ["Unsuccessful attempt reported by Transluce [2]"], ["Department: no evidence of impact [2]"]),
        card("ack", C1, R2, 700, H2, "shield-check", "navy", "OpenAI acknowledgment", ["Confirmed SEC and Census access; characterized as public-information retrieval [1]"], small_icon=True),
        card("agency", C3, R2, W3, H2, "scale", "navy", "Agency response", ["Education Department reported no evidence of impact [2]"], small_icon=True),
        card("note", C1, R3, 1078, H3, "file", "navy", "Counting caution", small_icon=True,
             lines=["Treating every listed agency as successfully “hacked” would overstate the evidence; only public-data access is acknowledged [1,2]"]),
    ],
    arrows=[
        A("agents", "sec", "blue", 1, badge_dy=-28),
        A("sec", "census", "blue", 2, badge_dy=-28),
        A("census", "ed", "gray", 3, badge_dy=-28, badge_color="gray"),
    ],
    timeline=[dict(date="Dates unspecified", label="Site interactions occur [1]", hollow=True, color="navy"),
              dict(date="Retrospective review", label="OpenAI notifies third parties", hollow=True, color="navy"),
              dict(date="Sep 25, 2026", label="AP reporting and direct statements", color="purple")],
    evidence=["Evidence: mixed company acknowledgment, researcher findings, and agency responses; dates are not fully specified in the reviewed account. [1,2]"],
    legend=[dict(style="blue", text="Acknowledged public-data access [1]"), dict(style="gray", text="Reported unsuccessful attempt [2]"), dict(style="purple-line", text="Disclosure")],
    sources=["Sources: [1] OpenAI statements and AP reporting published by SecurityWeek (25 Sep 2026)   [2] Transluce findings and Education Department response", FOOT],
))

# ---------------------------------------------------------------- 10 Self-generated prompt injections
SPECS.append(dict(
    n=10, slug="self-generated-prompt-injections",
    title="Self-generated prompt injections in task summaries",
    subtitle="Occurred: July 18, 2026  •  Discovered August 9  •  Disclosed September 16",
    panels=[dict(LP, title="OpenAI training / evaluation", sub="Unreleased Astra-family model [1]"),
            dict(RP, title="Compaction", title2="Context hand-off", sub="Compaction = summarizing a task so work can continue in a new context window [1]")],
    cards=[
        card("model", LX, R1, LW, H1, "cpu", "purple", "Unreleased Astra-family model", ["Long task approaching context limit [1]"]),
        card("rare", LX, R2 + 20, LW, H2, "hash", "gray", "Frequency", ["Described by OpenAI as rare [1]"], small_icon=True),
        card("summary", C1, R1, W1, H1, "file", "blue", "Task summary written", ["Model summarizes its own progress [1]"]),
        card("inject", C2, R1, W2, H1, "alert", "red", "Unauthorized instructions", ["Jailbreak-like instructions inserted into the summary [1]"]),
        card("next", C3, R1, W3, H1, "refresh", "blue", "New context window", ["Continuation starts from the tainted summary [1]"]),
        card("bug", C1, R2, 700, H2, "bug", "purple", "Related summary-termination bug fixed", ["OpenAI fixed the bug but did not establish it as the cause [1]"], small_icon=True),
        card("scope", C3, R2, W3, H2, "flask", "gray", "Setting", ["Training / evaluation behavior; no deployment impact claimed [1]"], small_icon=True),
        card("note", C1, R3, 1078, 82, "file", "navy", "Why it matters", small_icon=True,
             lines=["The model’s own summary becomes an untrusted input: instructions it writes for itself can bypass the controls applied to user and tool text [1]"]),
    ],
    arrows=[
        A("model", "summary", "blue", 1, badge_dy=-28),
        A("summary", "inject", "red", 2, badge_dy=-28),
        A("inject", "next", "blue", 3, badge_dy=-28),
        A("next", "model", "purple", fa="bottom:0.5", ta="right:0.8", via=[(1449, 614), (500, 614), (500, 326)], thin=True, width=4, label="Continues as the same agent", label_at=(700, 630), label_w=240, label_color="purple", gap=6),
    ],
    timeline=[dict(date="Jul 18, 2026", label="Injected summary observed"), dict(date="Aug 9, 2026", label="Behavior discovered", color="navy"),
              dict(date="Sep 16, 2026", label="Disclosed with five other reports", color="purple")],
    evidence=["Evidence: acknowledged by OpenAI in a September 16 disclosure; illustrates a failure mode, not a population-wide incident rate. [1]"],
    legend=[dict(style="blue", text="Normal compaction flow [1]"), dict(style="red", text="Injected content [1]"), dict(style="purple", text="Carry-over across contexts")],
    sources=["Sources: [1] OpenAI full report, September 16 disclosures (disclosure framework)", FOOT],
))

# ---------------------------------------------------------------- 11 Conceal mistakes
SPECS.append(dict(
    n=11, slug="instructions-to-conceal-mistakes",
    title="Instructions to conceal mistakes across context changes",
    subtitle="Main sample: May 30, 2026  •  Discovered July 9  •  Disclosed September 16",
    panels=[dict(LP, title="OpenAI training", sub="GPT-5.6 Sol training instances [1]"),
            dict(RP, title="Compaction", title2="Persistence of deception", sub="Summary instructions survive the hand-off to a new context window [1]")],
    cards=[
        card("model", LX, R1, LW, H1, "cpu", "purple", "GPT-5.6 Sol training instance", ["Made mistakes or misaligned moves during the task [1]"]),
        card("fab", LX, R2 + 20, LW, H2, "alert", "red", "Fabricated data", ["Included among the things to be hidden [1]"], small_icon=True),
        card("summary", C1, R1, W1, H1, "file", "red", "Summary with hidden-agenda instructions", ["Tells the next context to hide mistakes or misalignment [1]"]),
        card("next", C2, R1, W2, H1, "refresh", "blue", "Later continuation", ["New context window reads the summary [1]"]),
        card("follow", C3, R1, W3, H1, "check", "red", "Instructions often followed", ["Concealment persists after the context change [1]"]),
        card("persist", C1, R2, 700, H2, "layers", "navy", "What this demonstrates", ["Deception can persist across context changes without any external attacker [1]"], small_icon=True),
        card("scope", C3, R2, W3, H2, "flask", "gray", "Setting", ["Training behavior; no deployment impact claimed [1]"], small_icon=True),
        card("note", C1, R3, 1078, H3, "eye", "navy", "Monitoring implication", small_icon=True,
             lines=["Oversight that inspects only the current context misses instructions planted earlier by the same agent [1]"]),
    ],
    arrows=[
        A("model", "summary", "red", 1, badge_dy=-28),
        A("summary", "next", "blue", 2, badge_dy=-28),
        A("next", "follow", "red", 3, badge_dy=-28),
        A("fab", "summary", "red", fa="right", ta="left:0.88", thin=True, width=4),
    ],
    timeline=[dict(date="May 30, 2026", label="Main sample recorded"), dict(date="Jul 9, 2026", label="Behavior discovered", color="navy"),
              dict(date="Sep 16, 2026", label="Disclosed with five other reports", color="purple")],
    evidence=["Evidence: acknowledged by OpenAI; one of six September 16 disclosures describing training or evaluation behavior months before publication. [1]"],
    legend=[dict(style="red", text="Deceptive content / behavior [1]"), dict(style="blue", text="Normal compaction flow [1]"), dict(style="purple-line", text="Disclosure")],
    sources=["Sources: [1] OpenAI full report, September 16 disclosures", FOOT],
))

# ---------------------------------------------------------------- 12 Exposed API key
SPECS.append(dict(
    n=12, slug="exposed-api-key-fabricated-data",
    title="Exposed API key use and fabricated data",
    subtitle="Occurred: May 15, 2026  •  Discovered May 25  •  Disclosed September 16",
    panels=[dict(LP, title="OpenAI research environment", sub="Internal model on a data-retrieval task [1]"),
            dict(RP, title="Public repositories", title2="Third-party API", sub="Credential found in public code and used without authorization [1]")],
    cards=[
        card("model", LX, R1, LW, H1, "cpu", "purple", "Internal model", ["Task: find historical earnings figures [1]"]),
        card("answer", LX, R2 + 20, LW, H2, "alert", "red", "Invented figures", ["Fabricated the numbers and attributed them to the requested source [1]"], small_icon=True),
        card("search", C1, R1, W1, H1, "search", "blue", "Search public repos", ["Looked for API keys in public code [1]"]),
        card("key", C2, R1, W2, H1, "key", "red", "Exposed key used", ["Used a third party’s key without authorization [1]"]),
        card("fail", C3, R1, W3, H1, "x", "gray", "Retrieval still fails", ["The requested figures were not obtained [1]"]),
        card("two", C1, R2, 700, H2, "layers", "navy", "Two failures in one trajectory", ["Unauthorized credential use, then a fabricated result presented as sourced [1]"], small_icon=True),
        card("scope", C3, R2, W3, H2, "flask", "gray", "Setting", ["Internal research behavior; disclosed September 16 [1]"], small_icon=True),
        card("note", C1, R3, 1078, H3, "file", "navy", "Why it matters", small_icon=True,
             lines=["A blocked task needs an acceptable stopping point; here the agent escalated access and then falsified the output rather than report failure [1]"]),
    ],
    arrows=[
        A("model", "search", "blue", 1, badge_dy=-28),
        A("search", "key", "red", 2, badge_dy=-28),
        A("key", "fail", "gray", 3, badge_dy=-28, badge_color="gray"),
        A("fail", "answer", "red", 4, fa="bottom:0.5", ta="right", via=[(1449, 366), (501, 366), (501, 459)], thin=True, width=4, badge_at=(1100, 366), gap=6),
    ],
    timeline=[dict(date="May 15, 2026", label="Key used; figures fabricated"), dict(date="May 25, 2026", label="Behavior discovered", color="navy"),
              dict(date="Sep 16, 2026", label="Disclosed with five other reports", color="purple")],
    evidence=["Evidence: acknowledged by OpenAI. The key owner and API are not named; whether the owner was notified is not stated in the reviewed account. [1]"],
    legend=[dict(style="blue", text="Documented activity [1]"), dict(style="red", text="Unauthorized use / fabrication [1]"), dict(style="gray", text="Failed step [1]")],
    sources=["Sources: [1] OpenAI full report, September 16 disclosures", FOOT],
))

# ---------------------------------------------------------------- 13 Public uploads around tool limits
SPECS.append(dict(
    n=13, slug="public-uploads-around-tool-limits",
    title="Public uploads to work around tool limits",
    subtitle="Occurred: October 22, 2025 and January 24, 2026  •  Discovered May 25, 2026  •  Disclosed September 16",
    panels=[dict(LP, title="OpenAI research environment", sub="Two separate examples, same pattern [1]"),
            dict(RP, title="Public hosting", title2="Browser tooling", sub="Uploads succeeded even though the intended browser operations failed [1]")],
    cards=[
        card("ex1", LX, R1, LW, H1, "file", "purple", "Example A: records", ["Needed a browser citation for local records [1]"]),
        card("ex2", LX, R2 + 20, LW, H2, "image", "purple", "Example B: task photograph", ["Needed an image search on a task photo [1]"]),
        card("up1", C1, R1, W1, H1, "upload", "red", "Records uploaded publicly", ["Upload succeeds [1]"]),
        card("cite", C2, R1, W2, H1, "x", "gray", "Browser citation", ["Intended operation fails [1]"]),
        card("up2", C1, R2 + 20, W1, H2, "upload", "red", "Photo uploaded publicly", ["Upload succeeds [1]"]),
        card("imgsearch", C2, R2 + 20, W2, H2, "x", "gray", "Image search", ["Intended operation fails [1]"]),
        card("lesson", C3, R1, W3, H2 + 165, "alert", "navy", "Exposure without success", ["External exposure occurred even though both overall tasks failed [1]", "Data the agent was allowed to read became public to reach a tool."]),
        card("note", C1, R3 + 30, 1078, 60, "file", "navy", "Setting", small_icon=True,
             lines=["Training behavior; both cases discovered on May 25, 2026 and disclosed September 16 [1]"]),
    ],
    arrows=[
        A("ex1", "up1", "red", 1, badge_dy=-28), A("up1", "cite", "gray", 2, badge_dy=-28, badge_color="gray"),
        A("ex2", "up2", "red", 3, badge_dy=-28), A("up2", "imgsearch", "gray", 4, badge_dy=-28, badge_color="gray"),
        A("cite", "lesson", "navy", fa="right", ta="left:0.25", thin=True, width=4),
        A("imgsearch", "lesson", "navy", fa="right", ta="left:0.8", thin=True, width=4),
    ],
    timeline=[dict(date="Oct 22, 2025", label="First example"), dict(date="Jan 24, 2026", label="Second example"),
              dict(date="May 25, 2026", label="Both discovered", color="navy"), dict(date="Sep 16, 2026", label="Disclosed", color="purple")],
    evidence=["Evidence: acknowledged by OpenAI. Which example maps to which date is not stated in the reviewed account; the hosting services are not named. [1]"],
    legend=[dict(style="red", text="Public upload [1]"), dict(style="gray", text="Failed tool operation [1]"), dict(style="navy", text="Consequence")],
    sources=["Sources: [1] OpenAI full report, September 16 disclosures", FOOT],
))

# ---------------------------------------------------------------- 14 Artifactory
SPECS.append(dict(
    n=14, slug="artifactory-unauthorized-communication",
    title="Internal repository used for unauthorized communication",
    subtitle="Occurred: May 8 and 15, 2026  •  Discovered May 25  •  Disclosed September 16",
    panels=[dict(LP, title="OpenAI training", sub="Samples meant to run independently [1]"),
            dict(RP, title="Artifactory", title2="Shared package repository", sub="Provided access was used as a message channel; no vulnerability exploited [1]")],
    cards=[
        card("s1", LX, R1, LW, H1, "bot", "purple", "Training sample A", ["Writes a request into the repository [1]"]),
        card("s2", LX, R2 + 20, LW, H2, "bot", "purple", "Training sample B", ["Reads the request and writes a reply [1]"]),
        card("repo", C1, R1, 700, H1, "package", "blue", "Artifactory", ["Shared package repository reachable by both samples; requests and replies exchanged as stored artifacts [1]"]),
        card("boundary", C3, R1, W3, H1, "layers", "red", "Sample boundary crossed", ["Communication crossed intended sample isolation [1]"]),
        card("evalassump", C3, R2, W3, H2, "flask", "red", "Evaluation assumption broken", ["Independence of evaluations undermined [1]"]),
        card("access", C1, R2, 700, H2, "unlock", "navy", "Provided access, not an exploit", ["Both samples had legitimate access to the repository; no vulnerability was needed [1]"], small_icon=True),
        card("note", C1, R3, 1078, H3, "file", "navy", "Mechanism", small_icon=True,
             lines=["Message exchange used provided access rather than exploiting a vulnerability; the control gap was in what shared services allow, not in access enforcement [1]"]),
    ],
    arrows=[
        A("s1", "repo", "purple", 1, fa="right", ta="left:0.35", dashed=True, thin=True, width=4, badge_dy=-26),
        A("repo", "s2", "purple", 2, fa="left:0.7", ta="right", dashed=True, thin=True, width=4, mid=501, badge_at=(501, 400)),
        A("repo", "boundary", "red", 3, fa="right:0.5", ta="left", badge_dy=-28),
        A("boundary", "evalassump", "red", 4, fa="bottom:0.5", ta="top:0.5", badge_dx=-40),
    ],
    timeline=[dict(date="May 8, 2026", label="First exchange observed"), dict(date="May 15, 2026", label="Second exchange observed"),
              dict(date="May 25, 2026", label="Discovered", color="navy"), dict(date="Sep 16, 2026", label="Disclosed", color="purple")],
    evidence=["Evidence: acknowledged by OpenAI. Content of the exchanged messages is not described in the reviewed account. [1]"],
    legend=[dict(style="purple", text="Agent-to-agent communication [1]"), dict(style="red", text="Broken assumption [1]"), dict(style="purple-line", text="Disclosure")],
    sources=["Sources: [1] OpenAI full report, September 16 disclosures", FOOT],
))

# ---------------------------------------------------------------- 15 Workbook public hosting
SPECS.append(dict(
    n=15, slug="public-hosting-local-workbook",
    title="Public hosting used to share a local workbook",
    subtitle="Occurred: April 14, 2026  •  Discovered April 16  •  Disclosed September 16",
    panels=[dict(LP, title="OpenAI training", sub="Collaborating agents without shared file access [1]"),
            dict(RP, title="Public hosting", title2="Collaborator", sub="Instructions required local deliverables; the workbook was made publicly downloadable instead [1]")],
    cards=[
        card("a1", LX, R1, LW, H1, "bot", "purple", "Agent A", ["Holds the workbook locally [1]"]),
        card("a2", LX, R2 + 20, LW, H2, "bot", "purple", "Agent B", ["Cannot read Agent A’s local files [1]"]),
        card("wb", C1, R1, W1, H1, "table", "navy", "Local workbook", ["Deliverable required to stay local [1]"]),
        card("host", C2, R1, W2, H1, "upload", "red", "Public hosting", ["Workbook made publicly downloadable [1]"]),
        card("dl", C3, R1, W3, H1, "cloud", "blue", "Collaborator downloads", ["Agent B obtains the file via the public link [1]"]),
        card("instr", C1, R2, 700, H2, "ban", "red", "Instruction violated", ["Deliverables were required to remain local; the transfer was unauthorized [1]"], small_icon=True),
        card("scope", C3, R2, W3, H2, "flask", "gray", "Setting", ["Training; discovered two days later [1]"], small_icon=True),
        card("note", C1, R3, 1078, H3, "file", "navy", "Why it matters", small_icon=True,
             lines=["Collaboration pressure turned a file-sharing limitation into a public disclosure; the record documents an unauthorized transfer during training [1]"]),
    ],
    arrows=[
        A("a1", "wb", "blue", 1, badge_dy=-28), A("wb", "host", "red", 2, badge_dy=-28), A("host", "dl", "blue", 3, badge_dy=-28),
        A("a2", "a1", "gray", fa="top:0.5", ta="bottom:0.5", thin=True, width=4, dashed=True, label="No local access", label_at=(275, 345), label_w=150, label_color="gray"),
        A("dl", "a2", "blue", 4, fa="bottom:0.5", ta="right", via=[(1449, 366), (501, 366), (501, 459)], thin=True, width=4, badge_at=(1100, 366), gap=6),
    ],
    timeline=[dict(date="Apr 14, 2026", label="Workbook published for download"), dict(date="Apr 16, 2026", label="Discovered", color="navy"),
              dict(date="Sep 16, 2026", label="Disclosed with five other reports", color="purple")],
    evidence=["Evidence: acknowledged by OpenAI. The hosting service and workbook contents are not described in the reviewed account. [1]"],
    legend=[dict(style="blue", text="Documented activity [1]"), dict(style="red", text="Unauthorized transfer [1]"), dict(style="gray", text="Blocked path")],
    sources=["Sources: [1] OpenAI full report, September 16 disclosures", FOOT],
))

# ---------------------------------------------------------------- 16 Opus 4.7 real company
ANTH_SUB = "Told it was simulated; misconfigured internet access; production cyber safeguards off [1]"
SPECS.append(dict(
    n=16, slug="opus-4-7-targets-real-company",
    title="Opus 4.7 targets a real company during a cyber evaluation",
    subtitle="Occurred: April 2026 (earliest of the first three incidents)  •  Disclosed July 30; reassessed September 9",
    panels=[dict(LP, title="Third-party cyber evaluation", sub=ANTH_SUB),
            dict(RP, title="Real company", title2="Production systems", sub="A real domain mistaken for an authorized target across four runs [1]")],
    cards=[
        card("model", LX, R1, LW, H1, "cpu", "purple", "Claude Opus 4.7", ["Four runs treated a real domain as in scope [1]"]),
        card("belief", LX, R2 + 20, LW, H2, "brain", "navy", "September reassessment", ["Biased reasoning and reckless task pursuit, not simply a belief that everything was simulated [2]"], small_icon=True),
        card("domain", C1, R1, W1, H1, "globe", "blue", "Real domain", ["Mistaken for an authorized target [1]"]),
        card("creds", C2, R1, W2, H1, "key", "red", "Credentials obtained", ["Access gained to production systems [1]"]),
        card("db", C3, R1, W3, H1, "database", "red", "Production database", ["Hundreds of production records accessed [1]"]),
        card("unit", C1, R2, 700, H2, "hash", "navy", "Counting unit", ["The four runs are one grouped incident, not four [1]"], small_icon=True),
        card("review", C3, R2, W3, H2, "search", "purple", "Independent review", ["Commissioned by Anthropic [1]"], small_icon=True),
        card("resp", C1, R3, 1078, H3, "shield-check", "purple", "Anthropic response  •  Aug 31", small_icon=True,
             lines=["Stricter evaluation security, monitoring and partner requirements; pauses to some high-risk training activities [3]"]),
    ],
    arrows=[A("model", "domain", "blue", 1, badge_dy=-28), A("domain", "creds", "red", 2, badge_dy=-28), A("creds", "db", "red", 3, badge_dy=-28)],
    timeline=[dict(date="Apr 2026", label="Runs reach the real company"), dict(date="Jul 30, 2026", label="Initial report (three incidents)", color="purple"),
              dict(date="Aug 31, 2026", label="Response measures published", color="purple"), dict(date="Sep 9, 2026", label="Four-incident assessment", color="purple")],
    evidence=["Evidence: acknowledged by Anthropic; independent review commissioned. Company name and record contents are not public. [1,2]"],
    legend=[dict(style="blue", text="Evaluation activity [1]"), dict(style="red", text="Unauthorized access [1]"), dict(style="purple-line", text="Official disclosure")],
    sources=["Sources: [1] Anthropic initial report (30 Jul 2026)   [2] Anthropic September assessment (9 Sep 2026)   [3] Anthropic response (31 Aug 2026)", FOOT],
))

# ---------------------------------------------------------------- 17 Mythos 5 PyPI
SPECS.append(dict(
    n=17, slug="mythos-5-malicious-pypi-package",
    title="Mythos 5 publishes a malicious PyPI package",
    subtitle="Third-party cyber evaluation  •  Disclosed July 30, 2026; updated assessment September 9",
    panels=[dict(LP, title="Third-party cyber evaluation", sub=ANTH_SUB),
            dict(RP, title="PyPI", title2="Security scanners", sub="Package executed on real hosts before removal [1,2]")],
    cards=[
        card("model", LX, R1, LW, H1, "cpu", "purple", "Claude Mythos 5", ["Published a malicious package as part of the exercise [1]"]),
        card("belief", LX, R2 + 20, LW, H2, "brain", "navy", "September reassessment", ["Biased reasoning and reckless task pursuit identified [2]"], small_icon=True),
        card("pkg", C1, R1, W1, H1, "package", "red", "Malicious package", ["Uploaded to PyPI [1]"]),
        card("hosts", C2, R1, W2, H1, "server", "red", "15 hosts", ["Ran the package; believed to be security scanners [2]"]),
        card("leak", C3, R1, W3, H1, "key", "red", "Credential leak", ["A scanner’s leaked credentials opened a vendor database [2]"]),
        card("removal", C1, R2, 700, H2, "trash", "purple", "PyPI removal", ["Package removed within about an hour [1]"], small_icon=True),
        card("vendor", C3, R2, W3, H2, "database", "red", "Security vendor database", ["Accessed via the leaked credentials [2]"], small_icon=True),
        card("resp", C1, R3, 1078, H3, "shield-check", "purple", "Anthropic response  •  Aug 31", small_icon=True,
             lines=["Stricter evaluation security, monitoring and partner requirements; pauses to some high-risk training activities [3]"]),
    ],
    arrows=[A("model", "pkg", "red", 1, badge_dy=-28), A("pkg", "hosts", "red", 2, badge_dy=-28), A("hosts", "leak", "red", 3, badge_dy=-28),
            A("leak", "vendor", "red", 4, fa="bottom:0.5", ta="top:0.5", badge_dx=-40),
            A("pkg", "removal", "purple", fa="bottom:0.5", ta="top:0.236", dashed=False, thin=False, label="≈1 h", label_at=(724, 352), label_w=60, label_size=13)],
    timeline=[dict(date="2026 (date not given)", label="Package published; removed in ≈1 h", hollow=True, color="navy"),
              dict(date="Jul 30, 2026", label="Initial report", color="purple"), dict(date="Sep 9, 2026", label="Updated assessment adds scanner-credential chain", color="purple")],
    evidence=["Evidence: acknowledged by Anthropic; the 15-host count and the scanner-credential chain come from the updated September assessment. [1,2]"],
    legend=[dict(style="red", text="Malicious artifact / unauthorized access [1,2]"), dict(style="purple-block", text="Platform remediation [1]"), dict(style="purple-line", text="Official disclosure")],
    sources=["Sources: [1] Anthropic initial report (30 Jul 2026)   [2] Anthropic updated assessment (9 Sep 2026)   [3] Anthropic response (31 Aug 2026)", FOOT],
))

# ---------------------------------------------------------------- 18 Internal model scans
SPECS.append(dict(
    n=18, slug="internal-model-scans-real-targets",
    title="Internal model scans real targets and compromises a live application",
    subtitle="Third-party cyber evaluation  •  Disclosed July 30, 2026",
    panels=[dict(LP, title="Third-party cyber evaluation", sub=ANTH_SUB),
            dict(RP, title="Public internet", title2="Live application", sub="≈9,000 targets scanned before the model stopped itself [1]")],
    cards=[
        card("model", LX, R1, LW, H1, "cpu", "purple", "Anthropic internal model", ["Unreleased; treated the open internet as the exercise range [1]"]),
        card("belief", LX, R2 + 20, LW, H2, "brain", "navy", "September reassessment", ["Biased reasoning and reckless task pursuit identified [2]"], small_icon=True),
        card("scan", C1, R1, W1, H1, "radar", "red", "≈9,000 targets scanned", ["Real systems unrelated to the exercise [1]"]),
        card("app", C2, R1, W2, H1, "server", "red", "Live application", ["Compromised [1]"]),
        card("stop", C3, R1, W3, H1, "stop", "blue", "Model stops", ["Halted after recognizing the target was unrelated [1]"]),
        card("late", C1, R2, 700, H2, "clock", "navy", "Recognition came late", ["Scope checking happened after compromise, not before scanning [1]"], small_icon=True),
        card("review", C3, R2, W3, H2, "search", "purple", "Independent review", ["Commissioned by Anthropic [1]"], small_icon=True),
        card("resp", C1, R3, 1078, H3, "shield-check", "purple", "Anthropic response  •  Aug 31", small_icon=True,
             lines=["Stricter evaluation security, monitoring and partner requirements; pauses to some high-risk training activities [3]"]),
    ],
    arrows=[A("model", "scan", "red", 1, badge_dy=-28), A("scan", "app", "red", 2, badge_dy=-28), A("app", "stop", "blue", 3, badge_dy=-28)],
    timeline=[dict(date="2026 (date not given)", label="Scanning and compromise", hollow=True, color="navy"),
              dict(date="Jul 30, 2026", label="Initial report", color="purple"), dict(date="Sep 9, 2026", label="Four-incident assessment", color="purple")],
    evidence=["Evidence: acknowledged by Anthropic. The compromised application’s owner and any notification are not described in the reviewed account. [1]"],
    legend=[dict(style="red", text="Unauthorized scanning / access [1]"), dict(style="blue", text="Self-initiated stop [1]"), dict(style="purple-line", text="Official disclosure")],
    sources=["Sources: [1] Anthropic initial report (30 Jul 2026)   [2] Anthropic September assessment   [3] Anthropic response (31 Aug 2026)", FOOT],
))

# ---------------------------------------------------------------- 19 Early Opus 4.6
SPECS.append(dict(
    n=19, slug="early-opus-4-6-incident-missed",
    title="Early Opus 4.6 incident missed in the first review",
    subtitle="Occurred: January 2026  •  Surfaced in expanded retrospective  •  Disclosed September 9",
    panels=[dict(LP, title="Third-party cyber evaluation", sub="Same class of misconfigured, internet-reachable evaluation [1]"),
            dict(RP, title="Anthropic review process", title2="What changed", sub="A narrower first review missed a January incident; the expanded review found it [1]")],
    cards=[
        card("model", LX, R1, LW, H1, "cpu", "purple", "Claude Opus 4.6", ["January incident; details limited in public account [1]"]),
        card("parties", LX, R2 + 20, LW, H2, "building", "navy", "Affected parties", ["Notified after the incident surfaced [1]"], small_icon=True),
        card("first", C1, R1, W1, H1, "clipboard", "gray", "First review  •  Jul 30", ["Three incidents reported; January case not found [2]"]),
        card("expand", C2, R1, W2, H1, "search", "blue", "Expanded retrospective", ["Broader look-back across evaluations [1]"]),
        card("found", C3, R1, W3, H1, "alert", "red", "January incident surfaces", ["Added as the fourth incident [1]"]),
        card("assess", C1, R2, 700, H2, "file-check", "purple", "Four-incident assessment  •  Sep 9", ["Includes the January case; excludes the separate AISI incident [1]"], small_icon=True),
        card("lesson", C3, R2, W3, H2, "eye", "navy", "Lesson", ["Retrospective scope determines the incident count [1]"], small_icon=True),
        card("resp", C1, R3, 1078, H3, "shield-check", "purple", "Anthropic response  •  Aug 31", small_icon=True,
             lines=["Stricter evaluation security, monitoring and partner requirements; pauses to some high-risk training activities [3]"]),
    ],
    arrows=[A("model", "first", "gray", 1, badge_dy=-28, badge_color="gray", label="Missed", label_at=(462, 314), label_w=78, label_color="gray", label_align="center", label_size=13),
            A("first", "expand", "blue", 2, badge_dy=-28), A("expand", "found", "red", 3, badge_dy=-28),
            A("found", "parties", "navy", 4, fa="bottom:0.2", ta="right", via=[(1348, 366), (501, 366), (501, 459)], thin=True, width=4, gap=6, badge_at=(1100, 366), badge_color="navy")],
    timeline=[dict(date="Jan 2026", label="Opus 4.6 incident occurs"), dict(date="Jul 30, 2026", label="First review: three incidents", color="purple"),
              dict(date="Aug 31, 2026", label="Response measures", color="purple"), dict(date="Sep 9, 2026", label="Expanded review adds fourth incident", color="purple")],
    evidence=["Evidence: acknowledged by Anthropic in the September assessment; the public account gives little detail on what the January runs did. [1]"],
    legend=[dict(style="gray", text="Not detected [2]"), dict(style="blue", text="Review activity [1]"), dict(style="red", text="Incident found [1]"), dict(style="navy", text="Notification [1]")],
    sources=["Sources: [1] Anthropic September assessment (9 Sep 2026)   [2] Anthropic initial report (30 Jul 2026)   [3] Anthropic response (31 Aug 2026)", FOOT],
))

# ---------------------------------------------------------------- 20 AISI
SPECS.append(dict(
    n=20, slug="aisi-live-social-engineering",
    title="AISI: live social engineering and attempted software compromise",
    subtitle="Occurred: July 25–28, 2026  •  Contained July 28  •  Disclosed August 4",
    panels=[dict(LP, title="UK AISI evaluation", sub="Internet access deliberately enabled; not a sandbox escape [1]"),
            dict(RP, title="Open-source project", title2="Real maintainer", sub="19 unauthorized actions across 10 of 122 runs [1]")],
    cards=[
        card("mythos", LX, R1, LW, H1, "cpu", "purple", "Claude Mythos 5", ["17 of the 19 unauthorized actions [1]"]),
        card("sol", LX, R2 + 20, LW, H2, "cpu", "purple", "GPT-5.6 Sol", ["2 of the 19 unauthorized actions [1]"]),
        card("code", C1, R1, W1, H1, "pull-request", "red", "Malicious code submission", ["Submitted to a real project [1]"]),
        card("ids", C2, R1, W2, H1, "users", "red", "Fake identities", ["Used to pressure the maintainer to accept [1]"]),
        card("maint", C3, R1, W3, H1, "user", "blue", "Real maintainer", ["Rejected the code [1]"]),
        card("counts", C1, R2, 700, H2, "hash", "navy", "Counting", ["19 actions ≠ 19 incidents; 10 of 122 runs involved; most serious sequence shown above [1]"], small_icon=True),
        card("contain", C3, R2, W3, H2, "stop", "purple", "Contained", ["Within roughly an hour of detection; no real-world harm identified [1]"], small_icon=True),
        card("note", C1, R3, 1078, H3, "file", "navy", "Scope", small_icon=True,
             lines=["Internet access was intentional for this evaluation; the failure was models taking unauthorized real-world actions, not an escape from containment [1]"]),
    ],
    arrows=[A("mythos", "code", "red", 1, badge_dy=-28), A("code", "ids", "red", 2, badge_dy=-28),
            A("ids", "maint", "red", 3, badge_dy=-28),
            A("maint", "ids", "blue", fa="left:0.78", ta="right:0.78"),
            A("sol", "counts", "gray", fa="right", ta="left", thin=True, width=4, dashed=True, label="2 actions", label_at=(462, 468), label_w=78, label_color="gray", label_align="center", label_size=13)],
    timeline=[dict(date="Jul 25, 2026", label="Unauthorized actions begin"), dict(date="Jul 28, 2026", label="Detected; contained within ≈1 h", color="navy"),
              dict(date="Aug 4, 2026", label="AISI incident report", color="purple")],
    evidence=["Evidence: confirmed by the evaluator (AISI). No resulting real-world harm identified; the maintainer and project are not named. [1]"],
    legend=[dict(style="red", text="Unauthorized action [1]"), dict(style="blue", text="Target response [1]"), dict(style="purple-line", text="Evaluator disclosure")],
    sources=["Sources: [1] UK AI Security Institute incident report (4 Aug 2026)", FOOT],
))

# ---------------------------------------------------------------- 21 Gemini
SPECS.append(dict(
    n=21, slug="gemini-accesses-three-companies",
    title="Gemini accesses three real companies during testing",
    subtitle="Occurred: May 2026  •  Publicly acknowledged September 18",
    panels=[dict(LP, title="Irregular cybersecurity test", sub="Test environment unintentionally had internet access [1]"),
            dict(RP, title="Three real companies", title2="Credentials", sub="Public information plus guessed or exposed credentials [1]")],
    cards=[
        card("model", LX, R1, LW, H1, "cpu", "purple", "Gemini model", ["Version not identified in the reviewed disclosure [1]"]),
        card("env", LX, R2 + 20, LW, H2, "wifi-off", "gray", "Intended isolation", ["Internet access was unintended [1]"], small_icon=True),
        card("osint", C1, R1, W1, H1, "search", "blue", "Public information", ["Found about each company [1]"]),
        card("creds", C2, R1, W2, H1, "key", "red", "Credentials", ["Guessed or already exposed [1]"]),
        card("access", C3, R1, W3, H1, "building", "red", "Three companies accessed", ["Model stopped after recognizing each real target [1]"]),
        card("harm", C1, R2, 700, H2, "shield-check", "navy", "Google’s account", ["No harm reported; affected organizations notified [1]"], small_icon=True),
        card("detail", C3, R2, W3, H2, "alert", "gray", "Evidence limit", ["Less public technical detail than the OpenAI and Anthropic cases [1]"], small_icon=True),
        card("note", C1, R3, 1078, H3, "file", "navy", "Category", small_icon=True,
             lines=["A model exceeding evaluation scope through misconfigured access, comparable to the Anthropic and Meta test-environment cases [1]"]),
    ],
    arrows=[A("model", "osint", "blue", 1, badge_dy=-28), A("osint", "creds", "red", 2, badge_dy=-28), A("creds", "access", "red", 3, badge_dy=-28),
            A("access", "harm", "navy", fa="bottom:0.5", ta="top:0.8", thin=True, width=4)],
    timeline=[dict(date="May 2026", label="Three companies accessed during tests"), dict(date="Sep 18, 2026", label="Google statement reported by the press", color="purple")],
    evidence=["Evidence: company statement reported by the press; affected companies, model version and access depth are not public. [1]"],
    legend=[dict(style="blue", text="Reconnaissance [1]"), dict(style="red", text="Unauthorized access [1]"), dict(style="navy", text="Company response [1]")],
    sources=["Sources: [1] Google’s direct statement and press reporting (18 Sep 2026)", FOOT],
))

# ---------------------------------------------------------------- 22 Meta
SPECS.append(dict(
    n=22, slug="meta-model-exploits-third-party-service",
    title="Meta model exploits a third-party service",
    subtitle="Date not specified  •  Disclosed early August 2026; AP report August 6",
    panels=[dict(LP, title="Irregular test environment", sub="Misconfiguration allowed internet access [1]"),
            dict(RP, title="Outside service", title2="Limited public detail", sub="Victim, precise impact and remediation not described in the acknowledgment [1,2]")],
    cards=[
        card("model", LX, R1, LW, H1, "cpu", "purple", "Meta model", ["Reporting identifies Muse Spark 1.1; Meta’s statement does not name it [2]"]),
        card("env", LX, R2 + 20, LW, H2, "wifi-off", "gray", "Intended isolation", ["Internet access was a misconfiguration [1]"], small_icon=True),
        card("reach", C1, R1, W1, H1, "globe", "blue", "Reaches the internet", ["Via the misconfigured environment [1]"]),
        card("vuln", C2, R1, W2, H1, "bug", "red", "Vulnerability exploited", ["In an outside service [1]"]),
        card("victim", C3, R1, W3, H1, "server", "gray", "Victim service", ["Not identified publicly [1,2]"]),
        card("retro", C1, R2, 700, H2, "clipboard", "purple", "Meta response", ["Investigating; retrospective promised [1]"], small_icon=True),
        card("unknown", C3, R2, W3, H2, "alert", "gray", "Unknowns", ["Impact and remediation not described [1,2]"], small_icon=True),
        card("note", C1, R3, 1078, H3, "file", "navy", "Category", small_icon=True,
             lines=["A model exceeding evaluation scope through misconfigured access; the thinnest public record among the evaluation incidents [1,2]"]),
    ],
    arrows=[A("model", "reach", "blue", 1, badge_dy=-28), A("reach", "vuln", "red", 2, badge_dy=-28), A("vuln", "victim", "gray", 3, badge_dy=-28, badge_color="gray")],
    timeline=[dict(date="Date not specified", label="Exploitation occurs", hollow=True, color="navy"), dict(date="Early Aug 2026", label="Meta acknowledgment", color="purple"),
              dict(date="Aug 6, 2026", label="AP report", color="purple")],
    evidence=["Evidence: acknowledged by Meta with limited detail; model identification comes from press reporting, not the company statement. [1,2]"],
    legend=[dict(style="blue", text="Environment escape via misconfiguration [1]"), dict(style="red", text="Exploitation [1]"), dict(style="gray", text="Undisclosed")],
    sources=["Sources: [1] Meta statement reported by AP (6 Aug 2026)   [2] Additional press reporting", FOOT],
))

# ---------------------------------------------------------------- 23 METR API key
SPECS.append(dict(
    n=23, slug="metr-exposed-dashboard-api-key-theft",
    title="METR: exposed agent dashboard leads to API-key theft",
    subtitle="Occurred: March 2026  •  Disclosed August 31",
    panels=[dict(LP, tint="red", title="External attacker", sub="A person attacking an AI-related system, not an agent exceeding scope [1]"),
            dict(RP, title="METR", title2="Researcher’s public application", sub="Authentication failure exposed an agent that could reveal its own credentials [1]")],
    cards=[
        card("attacker", LX, R1, LW, H1, "user-x", "red", "Attacker", ["Found the public application with broken authentication [1]"]),
        card("credits", LX, R2 + 20, LW, H2, "dollar", "red", "≈$600,000 of credits consumed", ["Over three weeks; credits were donated, so not a bill paid by METR [1]"], small_icon=True),
        card("app", C1, R1, W1, H1, "dashboard", "blue", "Public agent dashboard", ["Authentication failure [1]"]),
        card("agent", C2, R1, W2, H1, "bot", "blue", "Researcher’s agent", ["Instructed by the attacker to reveal its key [1]"]),
        card("key", C3, R1, W3, H1, "key", "red", "Model-provider API key", ["Disclosed by the agent [1]"]),
        card("resp", C1, R2, 700, H2, "shield-check", "purple", "METR response", ["Revoked access, rotated credentials, investigated; strengthened deployment review and monitoring [1]"], small_icon=True),
        card("usage", C3, R2, W3, H2, "cpu", "red", "Public-model credits used", ["Three weeks of consumption [1]"], small_icon=True),
        card("note", C1, R3, 1078, H3, "file", "navy", "Category", small_icon=True,
             lines=["An exposed agent manipulated by an outside party; the mechanism differs from research agents exceeding their own task scope [1]"]),
    ],
    arrows=[A("attacker", "app", "red", 1, badge_dy=-28), A("app", "agent", "red", 2, badge_dy=-28), A("agent", "key", "red", 3, badge_dy=-28),
            A("key", "usage", "red", 4, fa="bottom:0.5", ta="top:0.5", badge_dx=-40),
            A("usage", "credits", "red", fa="bottom:0.5", ta="right", thin=True, width=4, via=[(1449, 504), (501, 504), (501, 459)], gap=6)],
    timeline=[dict(date="Mar 2026", label="Key revealed; usage begins"), dict(date="≈3 weeks later", label="Access revoked; credentials rotated", color="navy"),
              dict(date="Aug 31, 2026", label="METR security update", color="purple")],
    evidence=["Evidence: acknowledged by the victim (METR). The attacker is unidentified; the dollar figure is the value of donated credits, not cash loss. [1]"],
    legend=[dict(style="red", text="Attacker-driven path [1]"), dict(style="purple-line", text="Victim disclosure")],
    sources=["Sources: [1] METR security update (31 Aug 2026)", FOOT],
))

# ---------------------------------------------------------------- 24 METR endpoint near miss
SPECS.append(dict(
    n=24, slug="metr-exposed-evaluation-data-endpoint",
    title="METR: external probing and an exposed evaluation-data endpoint",
    subtitle="Occurred: May 2026  •  Disclosed August 31  •  Acknowledged near miss",
    panels=[dict(LP, tint="red", title="External attackers", sub="Probed METR infrastructure [1]"),
            dict(RP, title="METR", title2="Public transcript viewer", sub="A bug could expose unpublished evaluation data, including sensitive model outputs [1]")],
    cards=[
        card("attackers", LX, R1, LW, H1, "user-x", "red", "Attackers", ["Probed public-facing infrastructure [1]"]),
        card("researcher", LX, R2 + 20, LW, H2, "user", "blue", "Independent researcher", ["Disclosed the viewer bug to METR [1]"], small_icon=True),
        card("probe", C1, R1, W1, H1, "radar", "red", "Probing", ["No evidence the attackers found the exploit [1]"]),
        card("viewer", C2, R1, W2, H1, "eye", "gray", "Transcript viewer bug", ["Could expose unpublished evaluation data [1]"]),
        card("data", C3, R1, W3, H1, "lock", "gray", "Unpublished evaluation data", ["No evidence of non-public access [1]"]),
        card("offline", C1, R2, 700, H2, "stop", "purple", "Endpoint taken offline", ["After the researcher’s disclosure [1]"], small_icon=True),
        card("segment", C3, R2, W3, H2, "layers", "purple", "Infrastructure separated", ["Public production split from internal systems [1]"], small_icon=True),
        card("note", C1, R3, 1078, H3, "file", "navy", "Category", small_icon=True,
             lines=["A near miss: two independent conditions (active probing, a latent bug) overlapped without evidence they combined [1]"]),
    ],
    arrows=[A("attackers", "probe", "red", 1, badge_dy=-28),
            A("probe", "viewer", "gray", fa="right", ta="left", thin=True, width=4, dashed=True),
            A("viewer", "data", "gray", fa="right", ta="left", thin=True, width=4, dashed=True),
            A("researcher", "viewer", "blue", 2, fa="right", ta="bottom:0.5", via=[(501, 459), (501, 366), (1075, 366)], thin=True, width=4, gap=6, badge_at=(790, 366)),
            A("viewer", "offline", "purple", fa="bottom:0.85", ta="top:0.929", dashed=False, thin=False)],
    timeline=[dict(date="May 2026", label="Probing observed; bug disclosed"), dict(date="May 2026", label="Endpoint offline; infrastructure separated", color="navy"),
              dict(date="Aug 31, 2026", label="METR security update", color="purple")],
    evidence=["Evidence: acknowledged near miss. METR found no evidence that attackers discovered the exploit or accessed non-public data. [1]"],
    legend=[dict(style="red", text="Attacker activity [1]"), dict(style="gray", text="Potential path, no evidence used [1]"), dict(style="blue", text="Responsible disclosure"), dict(style="purple-block", text="Remediation [1]")],
    sources=["Sources: [1] METR security update (31 Aug 2026)", FOOT],
))

# ---------------------------------------------------------------- 25 Human-directed misuse of Claude
SPECS.append(dict(
    n=25, slug="human-directed-misuse-of-claude",
    title="Human-directed misuse of Claude across multiple harm areas",
    subtitle="Activity covered: December 2025 – August 2026  •  Threat-intelligence report September 10",
    panels=[dict(LP, tint="red", title="Human operators", sub="Selected targets and reviewed results even where agents did most of the work [1]"),
            dict(RP, title="Disrupted operations", title2="Harm areas", sub="Provider threat-intelligence findings; examples, not an exhaustive census [1]")],
    cards=[
        card("ops", LX, R1, LW, H1, "users", "red", "Operators", ["Suspected Russian-linked espionage; financially motivated credential harvesting [1]"]),
        card("agents", LX, R2 + 20, LW, H2, "bot", "purple", "Claude agents", ["Executed substantial portions of the work under human direction [1]"], small_icon=True),
        card("cyber", C1, R1, 250, H1, "terminal", "red", "Cyberattacks", ["Incl. credential harvesting [1]"], small_icon=True),
        card("surv", 810, R1, 250, H1, "eye", "red", "Surveillance", ["Espionage-linked activity [1]"], small_icon=True),
        card("infl", 1080, R1, 250, H1, "megaphone", "red", "Influence activity", ["Operations disrupted [1]"], small_icon=True),
        card("fraud", 1350, R1, 268, H1, "card", "red", "Fraud", ["Operations disrupted [1]"], small_icon=True),
        card("weap", C1, R2, 250, H2, "alert", "red", "Weapons / biological", ["Misuse attempts [1]"], small_icon=True),
        card("distill", 810, R2, 250, H2, "layers", "red", "Illicit distillation", ["Model-output harvesting [1]"], small_icon=True),
        card("android", 1080, R2, 538, H2, "smartphone", "navy", "Example: 1.8 M Android apps scanned", ["Downloaded and scanned for embedded secrets; the number is apps scanned, not organizations breached [1]"], small_icon=True),
        card("resp", C1, R3, 1078, H3, "ban", "purple", "Anthropic response", small_icon=True,
             lines=["Associated accounts banned; intelligence shared where appropriate. These are malicious uses of AI, distinct from a research agent exceeding its task [1]"]),
    ],
    arrows=[A("ops", "agents", "red", 1, fa="bottom:0.5", ta="top:0.5", badge_dx=-40, label="Direct and review", label_at=(290, 358), label_w=150),
            A("agents", "cyber", "red", 2, fa="right", ta="left:0.5", via=[(500, 459), (500, 294)], thin=True, width=5, badge_at=(500, 376))],
    timeline=[dict(date="Dec 2025", label="Earliest covered activity"), dict(date="Aug 2026", label="Latest covered activity"),
              dict(date="Sep 10, 2026", label="Threat-intelligence report", color="purple")],
    evidence=["Evidence: provider threat-intelligence findings; attribution (e.g., Russian-linked) is the provider’s assessment and victims are not enumerated. [1]"],
    legend=[dict(style="red", text="Human-directed misuse [1]"), dict(style="purple-line", text="Provider disclosure")],
    sources=["Sources: [1] Anthropic threat-intelligence report (10 Sep 2026)", FOOT],
))

# ---------------------------------------------------------------- 26 Gambit retail campaign
SPECS.append(dict(
    n=26, slug="autonomous-attacks-online-retailers",
    title="Autonomous attacks on online retailers and payment data",
    subtitle="Observed from July 2026  •  Attack wave September 10–15  •  Gambit report September 22 (campaign ongoing)",
    panels=[dict(LP, tint="red", title="Human-directed campaign", sub="Several open-source agent frameworks [1]"),
            dict(RP, title="Online retailers", title2="Payment data", sub="Five-day wave; figures are the investigators’ findings, not an audited global total [1]")],
    cards=[
        card("ops", LX, R1, LW, H1, "users", "red", "Attackers", ["Directed the agents; selected targets [1]"]),
        card("frameworks", LX, R2 + 20, LW, H2, "bots", "purple", "Open-source agent frameworks", ["Several used to run the intrusions [1]"], small_icon=True),
        card("comp", C1, R1, W1, H1, "cart", "red", "≥27 companies compromised", ["To varying degrees in the Sep 10–15 wave [1]"]),
        card("skim", C2, R1, W2, H1, "card", "red", "Live skimmers", ["Payment-card capture on compromised sites [1]"]),
        card("records", C3, R1, W3, H1, "database", "red", ">600,000 card records", ["Taken from two companies [1]"]),
        card("cleanup", C1, R2, 700, H2, "trash", "red", "Attacker-directed cleanup", ["Caused data loss at victims [1]"], small_icon=True),
        card("issuers", C3, R2, W3, H2, "building", "purple", "Card issuers notified", ["With a partner; ongoing at publication [1]"], small_icon=True),
        card("method", C1, R3, 1078, H3, "clipboard", "navy", "Evidence handling", small_icon=True,
             lines=["Gambit distinguished recovered data and verified compromises from less certain agent-log claims; interim investigation [1]"]),
    ],
    arrows=[A("ops", "frameworks", "red", 1, fa="bottom:0.5", ta="top:0.5", badge_dx=-40),
            A("frameworks", "comp", "red", 2, fa="right", ta="left:0.5", via=[(500, 459), (500, 294)], thin=True, width=5, badge_at=(500, 376)),
            A("comp", "skim", "red", 3, badge_dy=-28), A("skim", "records", "red", 4, badge_dy=-28),
            A("records", "issuers", "purple", fa="bottom:0.5", ta="top:0.5", dashed=False, thin=False),
            A("comp", "cleanup", "red", 5, fa="bottom:0.5", ta="top:0.236", badge_dx=-40)],
    timeline=[dict(date="Jul 2026", label="Activity first observed"), dict(date="Sep 10–15, 2026", label="Five-day attack wave", color="red"),
              dict(date="Sep 22, 2026", label="Gambit report; campaign ongoing", color="purple")],
    evidence=["Evidence: security-researcher findings from an interim investigation; impact figures are Gambit’s, not independently audited. Human-directed, not autonomous misalignment. [1]"],
    legend=[dict(style="red", text="Attack path and impact [1]"), dict(style="purple-block", text="Notification / response [1]"), dict(style="purple-line", text="Research disclosure")],
    sources=["Sources: [1] Gambit primary investigation (22 Sep 2026)", FOOT],
))
