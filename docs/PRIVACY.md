# Forum Radar: data practices for the review prototype

This single-user prototype runs locally. No Reddit access has been approved and no live collection is claimed. These are current implementation facts, not a substitute for Reddit approval or legal advice.

## Inputs and local storage

The operator explicitly selects a permitted discussion and may enter a local label, author/keyword filters, timing and expiration. Subject to approval, the prototype processes the public title, text, author name, subreddit, item IDs, parent relationships, timestamps and permalink returned for that discussion. Those fields support matching, change detection and revalidation; it does not collect email addresses, private messages, real-world identities, avatars or inferred sensitive traits.

Data is stored in a local SQLite database under the app's private data directory. The HTTP interface listens on 127.0.0.1. Credential values come from environment variables and are not returned to the interface or placed in source control. Local operating-system permissions and backups remain the operator's responsibility.

## Retention and removal

Reddit cache entries expire after at most 24 hours while the app is running. Unchanged reads do not extend that TTL. Editing a source creates a new version with its own retention period. Cleanup also removes linked pending notifications and replaces affected local digests with a removal notice. SQLite secure_delete is enabled; forensic erasure of OS backups or storage media is not promised. If the app is off, cleanup runs on restart before the UI serves state or a digest is prepared.

The app revalidates known IDs before generating or sending Reddit notifications. Deleted, removed, missing or author-deleted items are purged conservatively. Source edits invalidate old cached content when detected. If revalidation fails, notification of Reddit items is blocked. This is polling, not a real-time deletion-event subscription; that limitation must be evaluated by Reddit before activation.

## Outputs and third parties

Reddit notifications contain only a user-entered label, update count and original link. Source titles, bodies and author lists are not copied to Apple Messages. Apple processes messages under the operator's Apple account; this app cannot retract delivered messages. The operator must not copy source text into a custom label. Links already delivered may later point to unavailable content.

All Reddit items are excluded from AI processing, including locally hosted models. No model training, profiling, identity matching, data sale, advertising or multi-user feed service is supported. Other forum connectors and their separately configured optional AI processing are outside the Reddit pilot and subject to those sources' permissions.

## Controls and questions

The operator can pause/stop/expire watches and stop the local process. Pausing discards queued updates and cancels affected unsent previews; cached data still undergoes removal/expiration. There is no public hosted instance or customer account system.

Implementation questions can be raised through this repository's Issues page without posting private credentials or forum content. Reddit account/content requests should use Reddit's official support channels. Additional retention, security and incident-response requirements imposed during review must be implemented before activation.
