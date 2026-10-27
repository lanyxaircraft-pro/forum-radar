# Technical addendum for the existing access-request thread

Use this as a reply in the original ticket after verifying its recipient and ticket identifier. Do not submit another request for the same use case. Replace this document link with an immutable commit link when replying. This is a prepared addendum, not a statement that a reply has been sent or accepted.

---

I would appreciate clarification and, if eligible, reconsideration of my existing Forum Radar access request. I am following up in the original thread, not opening another application. I understand approval is discretionary and that personal use does not itself confer API eligibility.

My original submission was insufficiently concrete about data removal and the Devvit deployment question. It also described features broader than the minimum reading workflow. I have revised the implementation and published reproducible review evidence:

- Source: https://github.com/lanyxaircraft-pro/forum-radar
- Evidence and exact endpoint inventory: https://github.com/lanyxaircraft-pro/forum-radar/blob/main/docs/REVIEW.md
- Data practices and limitations: https://github.com/lanyxaircraft-pro/forum-radar/blob/main/docs/PRIVACY.md
- Offline safeguard tests: https://github.com/lanyxaircraft-pro/forum-radar/blob/main/tests/test_reddit_safeguards.py

**Narrow pilot request.** One personal operator, with at most five manually selected public discussion threads within r/flying, r/aviationmaintenance and r/avionics, only as permitted by Reddit. I read aviation discussions and want a small reminder that a selected conversation has changed so I can return to the original Reddit page. I am not requesting user-history monitoring, subreddit-wide feeds, broad keyword discovery, a historical archive or a service for other customers. The live Reddit adapter now rejects those broader modes. Author/keyword filtering is limited to the selected thread. The app does not link authors across platforms or infer personal characteristics. No moderator role or community endorsement is claimed.

**Minimum access.** The intended scope is read-only OAuth `read`. The only requested endpoints are a selected thread's comments and `/api/info` for revalidating known post/comment IDs. Polling is at most hourly, with a hard aggregate maximum of 200 Reddit requests/day, including deletion checks, or any lower approved limit. Client identification includes the platform, app/version and configured Reddit contact. 401/403 stop further calls using that credential; rate-limit responses trigger cooldown. No credentials have been obtained through an unapproved path, no Reddit data has been collected, and no bypass or third-party data vendor is used.

**Implemented data minimization.** The local Reddit cache now has a 24-hour TTL rather than the previously proposed seven days; unchanged reads do not extend it. Known items are rechecked before generating or sending notifications. Deleted, removed, unavailable or author-deleted items are purged conservatively, including associated pending updates and local derived digest copies. If a check fails, Reddit notification is blocked. This is a polling implementation, not a real-time delete-event subscription; if that is insufficient, I will not activate it until a supported solution is implemented. A computer that is off cannot perform cleanup; cleanup runs on restart before serving cached state. OS backups and already delivered messages are outside the app's deletion control.

**Restricted notifications and no AI.** The Reddit path sends only an operator-selected label, an update count and an original permalink to my own Apple Messages address. It does not export copied Reddit titles, bodies, author lists or summaries. All Reddit items are excluded from both external and local AI processing in code, regardless of UI switches. There is no model training, advertising, monetization, sale or redistribution to other users. Other forum connectors are separate and do not expand this Reddit request.

**Devvit and the long-term path.** I have now reviewed the documentation for scheduling, deletion triggers, HTTP Fetch and External Endpoints. My initial claim was a deployment mismatch, not proof that Devvit cannot support notifications. The existing prototype is a loopback-only Mac application without a cloud callback service. A supported Devvit design may be possible with separately approved external endpoints and an appropriate installation/permission model; I have not implemented or obtained approval for that design and do not claim moderator installation rights. I also recognize the announced January/March 2027 API migration milestones and am not requesting an assumed permanent exemption.

Could you please identify which of the following applies?

1. This personal selected-thread reminder is ineligible even with the restricted scope and safeguards above.
2. The use is potentially eligible, but specific evidence, data-handling controls, app/developer registration or deployment changes remain necessary.
3. Devvit is the required route; if so, which supported installation/access model and external-endpoint process should I use for this workflow?

If the Data API route is eligible, please specify the required controls and permitted scope before any collection begins. I am requesting only a zero-cost path; if none is available, I will leave the Reddit connector disabled rather than activate paid access or an unauthorized alternative. I can provide additional source/test details in this thread.

Thank you for reviewing the clarification.
