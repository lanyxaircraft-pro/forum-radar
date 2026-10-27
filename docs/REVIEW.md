# Forum Radar: review evidence, v0.2

Status: review prototype; no API approval, production deployment or live Reddit collection is claimed. Local fixture tests are not a live integration test. This document is technical evidence, not a statement that Reddit has certified the app.

## Pilot scope

The Reddit adapter is now limited to at most five simultaneously active, explicitly selected threads in `flying`, `aviationmaintenance` and `avionics`. The user must specify the subreddit. Local author/keyword filtering within a selected thread is available. Reddit user-history retrieval, subreddit-wide discovery and flair discovery are disabled in the live adapter for this pilot. Other forums' selection features are independent.

No actual thread selections have been supplied by the operator yet. They will be chosen before activation and must remain within any scope Reddit approves. The pilot does not claim moderator status or moderator consent, and has not been installed in those communities.

## Implemented safeguards and evidence

| Control | Implementation | Offline evidence |
| --- | --- | --- |
| Approval before access | Watch approval flag, approval-reference environment setting, OAuth token and contact username are required. A local reference is a deployment gate, not proof that Reddit granted approval. | Missing approval prevents network access. |
| Narrow pilot | `reddit()` rejects non-thread modes, missing/unlisted subreddit and more than five active Reddit watches. | Broad discovery and unlisted subreddit rejection tests. |
| Limited load | Minimum interval 60 minutes; hard maximum 200 Reddit requests per UTC day, including deletion checks; configurable lower cap. | Interval and daily-use tests. |
| Transparent client | `macos:forum-radar:v0.2 (by /u/<configured-contact>)`; no disguise or unauthenticated scraping fallback. | Missing identity blocks access. |
| Stop on access rejection | 401/403 suspend further calls with the same credential; 429 honors numeric Retry-After or defaults to 15 minutes. Zero remaining quota triggers reset-based cooldown. | 403 stops the second network attempt. |
| No Reddit AI | Reddit items are excluded in `ai_summary()` irrespective of per-watch and global AI switches; applies to local and external models. | All AI switches on still results in zero AI calls for Reddit. |
| Link-only Reddit notifications | User-selected label, update count and original permalink; no copied Reddit title/body/author list or AI summary. | Notification test rejects fixture title, body and author. |
| Local cache TTL | Reddit content capped at 24 hours, unaffected by the longer retention setting for other forums; unchanged reads do not extend lifetime. Cleanup runs at startup/background cycles and before state/digest access. | 25-hour-old unchanged entry is purged. |
| Deletion/unavailability | Known IDs are revalidated via `/api/info` before preparing or sending a Reddit digest. Deleted, removed, missing or author-deleted items are conservatively purged, including linked pending events and local digest copies. | Missing/deleted-item and deleted-account tests. |
| Fail closed | If revalidation cannot finish, Reddit digest generation/sending is blocked; unrelated sources can continue. | Revalidation-failure test. |
| Local storage | Local-only listener; database permissions 600; secure_delete enabled; no contents or credentials in logs. | HTTP CSRF/Host controls and fixture workflow tests. |

Run `python3 -m unittest discover -s tests -v`. At this revision 28 offline tests pass. No test contacted Reddit or used real forum content.

## Exact requested API surface

- Read-only OAuth `read` scope; token issuance/refresh must follow Reddit's approved path.
- `GET /r/{approved_subreddit}/comments/{explicit_thread_id}`: selected thread and the returned comment tree, at most hourly.
- `GET /api/info?id={known_fullnames}`: batches of at most 100 known IDs for deletion/unavailability checks before notification.
- No user overview, search/new/hot feeds, posting, commenting, voting, private messages, moderator actions or third-party Reddit data vendors.

The adapter does not expand `more` nodes or promise complete pagination. It is a bounded change notifier, not a historical archive or a complete thread replica.

## Data handling and remaining limitations

See [PRIVACY.md](PRIVACY.md). A stopped computer cannot run background cleanup; on restart the app performs cleanup before exposing cached data. Database cleanup does not promise forensic erasure from an OS backup, SSD or external copy. Already delivered Apple Messages cannot be retracted by this app; Reddit notifications therefore contain links/counts, not copied source content. The user must not place copied source text into a custom watch label.

OAuth refresh, app/developer registration, live device testing and any Reddit-specific requirements remain activation prerequisites. There is no automatic workaround if access is denied. Future broader selection or model-processing features require separate review before being enabled for Reddit.

## Devvit assessment and migration question

The original application did not sufficiently analyze Devvit. The revised request should acknowledge that Devvit provides scheduling, deletion triggers and external integration capabilities; it is not accurate to claim that external notifications are categorically impossible.

The current app is a loopback-only, zero-cloud-service Mac process. Direct cloud-to-Mac callbacks are not available in that topology. Devvit HTTP Fetch permits reviewed HTTPS destinations, and personal domains normally require an exception. A Mac-polling alternative may be possible through Devvit External Endpoints, but the current documentation describes it as limited access; it requires a separate access decision and implementation.

The operator should ask Reddit whether a reviewed Devvit integration can cover this personal, manually selected reading use case and what installation/permission model is required for the selected communities. No moderator consent or external-endpoint access is claimed. If the local Data API design is ineligible, keep Reddit disabled and pursue only a supported design.

The app-registration page currently states that removals for unregistered/unengaged apps begin January 12, 2027 and remaining public API access ends in March 2027. This is not an application deadline or a guarantee of interim access. A permanent exception should not be assumed.

## Official references checked October 28, 2026

- https://support.reddithelp.com/hc/en-us/articles/42728983564564-Responsible-Builder-Policy
- https://support.reddithelp.com/hc/en-us/articles/16160319875092-Reddit-Data-API-Wiki
- https://developers.reddit.com/docs/capabilities/server/http-fetch
- https://developers.reddit.com/docs/capabilities/server/external-endpoints
- https://developers.reddit.com/app-registration

Reply to the existing application correspondence rather than opening another request for the same use case. Ask for the specific eligibility/detail gap and the supported route; do not claim approval or an exemption.
