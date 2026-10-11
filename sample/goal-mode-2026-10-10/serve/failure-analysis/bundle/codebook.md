# Codebook

A run moves around one cycle. What an agent knows and has done (K) is posted to the board (L). The board delivers posts into what each other agent has received (L^i): a turn is handed the posts up to its `through`, and posts that arrive during a turn are not seen unless the agent reads the board again. Each agent reads what it received into its picture of who does what (G^i), and acts on the shared workspace (X).

A failure is a point where two of these states stop agreeing. Class it by asking these questions in order; the first answered 'no' is its class, and you do not go further:

1. **unsaid**: Did what another agent's work needs reach the board, in time?
2. **unreceived**: Had the acting agent received the relevant post when it acted?
3. **misread**: Did its reading keep what the posts clearly established, and add nothing they did not?
4. **disagreement**: Where the posts left room, did the agents read them the same way?
5. **ungrounded**: Is what the readings record as done, delivered, reviewed, or true what the workspace holds?
6. **stalled**: Did the work keep moving, and close at the right time?

If all six hold and the work is still poor, it is not a communication failure: it is the agents' capability, a collective judgement, the task's data, the harness, or the grader. Record a failure caused by the harness (for example the runner ending a run on a post that withheld DONE) as an incident with source "harness".

## Severity: what happened to the team's work, read from the trace

- **1 Negligible**: caught and resolved within the next exchange; nothing redone or lost
- **2 Friction**: time, tokens, or posts spent on the repair; the work is unchanged
- **3 Waste**: a substantial piece of work duplicated, discarded, or overwritten, or the product left inconsistent; every required part still delivered
- **4 Damage**: a required part of the deliverable missing, wrong, or unreviewed because of it
- **5 Breakdown**: the core result not delivered, or delivered invalid or self-contradictory, or the run derailed

## Classes and patterns

### unsaid (K → L; disclosure)
Something an agent knows or did, which another agent's work needs, never reaches the board, or reaches it too late.
- `withheld_information` Withheld information: An agent knows something another agent's work needs, from its own work or its instructions, and never posts it. Example: D measured that the page is slow only above 10,000 rows and never says so; B tests on a small table.
- `unannounced_delivery` Unannounced delivery: An agent finishes a piece of work in the workspace and never says so on the board. Example: B's fix is in the workspace but B never posts it; C waits to review it, and D starts the same fix.
- `unasked_question` Unasked question: An agent cannot tell from the board what it should do, and guesses instead of asking. Example: B cannot tell whether the slow page is the list or the detail page, and picks one without asking.
- `late_disclosure` Late disclosure: Information another agent needed is posted only after that agent has acted without it. Example: D posts the 10,000-row finding after B's patch is reviewed and closed.

### unreceived (L → Lⁱ; C0 currency)
A post is on the board, or meant to be, but not in what the acting agent had received when it acted.
- `silent_drop` Silent drop: An agent believes it posted, but the post never reached the board. Example: B's "Patch ready" fails to send; B waits for a review that nobody knows to do.
- `misrouted_post` Misrouted post: A post lands somewhere other than intended: on another board, or under another seat. Example: B posts "Patch ready" to another team's board.
- `missed_post` Missed post: A post reached the board, but the agent it concerns was never handed it. Example: A's listener skips the post that moves the query to D, and A goes on as before.
- `crossed_posts` Crossed posts: Two agents post conflicting acts at nearly the same time, each without having seen the other's. Example: B and D both post "I'll take the query" within the same two seconds.
- `stale_act` Stale act: An agent acts on a post that a later post had already changed, because it had not yet received the change. Example: A changes the task to "look at the index, not the query" while B is mid-turn; B finishes and posts a query patch.
- `premature_final` Premature final: A post declares a decision final before its author has read the posts that change it. Example: A posts "Final plan: fix the query" while C's post arguing for the index is still unread.
- `stale_review` Stale review: A review concerns an earlier version of a result than the one now delivered. Example: C reviews B's first patch after B has posted a second.
- `duplicate_delivery` Duplicate delivery: The same post is delivered, or acted on, twice. Example: A retry delivers "run the benchmark" twice, and B runs it twice.

### misread (Lⁱ → Gⁱ; C1 retention, both directions)
An agent received the posts, but its reading drops what they established or adds what they did not.
- `R1` Open-set decay: The post claims or redoes an item that an earlier post already settled: delivered, or held by another seat. Example: Long after B delivered the query fix and C reviewed it, D posts "I'll take the query."
- `R2` Replacement re-does work: A seat that joined late claims or redoes work the log already holds. Example: D replaces an agent that stopped, reads only the last posts, and rewrites the query fix B already delivered.
- `over_reading` Over-reading: An agent reads more into a post than it says: a suggestion as an order, an offer as a commitment. Example: C writes "I could profile it later"; A records C as the profiler.
- `buried_signal` Buried signal: A post that changes the work is lost among many posts that do not, and nobody acts on it. Example: A's post moving the query to D sits between twenty status posts, and nobody acts on it.

### disagreement (Gⁱ ≠ Gʲ; C2 agreement)
Agents that received the same posts read different coordination from them: who owns what, what the work is, what was decided.
- `B1` Belief without commitment: A hedged claim that is never made firm, or an ask addressed to a seat that nobody answers. Example: B answers "Looking now." A reads an acceptance; C reads a glance and takes the query too.
- `B2` Identity drift: Who speaks or who leads changes under one handle: the post speaks for another seat, or a second seat claims a role already held. Example: A session posts from C's seat, and readers credit C with a review C never wrote.
- `ambiguous_reference` Ambiguous reference: A post names a piece of work in a way that fits more than one, and readers pick different ones. Example: B writes "I'll fix the slow query" while two queries are slow; A records the list query, B fixes the detail query.
- `status_word_mismatch` Status-word mismatch: Agents use the same status word (done, ready, final) to mean different things. Example: B's "done" means the patch is written; A's "done" means it passed the benchmark.
- `divergent_assumptions` Divergent assumptions: The posts leave a detail of the work open, and agents fill it in differently. Example: Nobody says what "fast" means; B aims for under one second, C for under two.
- `term_drift` Term drift: A name for a piece of work changes meaning during the run, and agents use it in different senses. Example: "The fix" first means the query rewrite and later the cache; D reviews "the fix" and means the query.
- `conflicting_authority` Conflicting authority: Two agents give incompatible instructions, and the board does not say whose holds. Example: A tells B to fix the query; C tells B to leave it and add an index.
- `undeclared_decision` Undeclared decision: A discussion reaches a decision that nobody states, and agents leave it with different conclusions. Example: After a long thread on query versus index, A thinks query and D thinks index; nobody wrote the outcome down.

### ungrounded (Gⁱ ≠ X; C3 grounding)
What the readings record as done, delivered, reviewed or true is not what the workspace holds.
- `D1` Unattested action: The post claims an action (pushed, uploaded, paid, tests pass) that nothing on the board attests. Example: B posts "Patch applied, the page is fast now" without having run the benchmark.
- `D2` Review of nothing: The post passes a review of an item whose result was never delivered. Example: C posts "Reviewed, looks good" before B has posted a patch.
- `off_spec_delivery` Off-spec delivery: The delivered work is not the work that was agreed, though it is reported as that work. Example: B was to rewrite the query, adds a cache instead, and posts "query fixed".
- `workspace_race` Workspace race: An agent reads or checks the shared workspace while another agent is still changing it. Example: C runs the benchmark while B is half-way through the patch, and reports a failure.
- `error_cascade` Error cascade: A claim about the work is taken as true without a check, and other agents build on it. Example: B says "the query returns 50 rows"; C and D both design around 50 rows; it returns 5,000.
- `overwrite` Overwrite: Two agents change the same part of the workspace, and one silently undoes the other's delivered work. Example: D's edit to the query file reverts B's reviewed patch.

### stalled (G over time; progress and closure)
Every reading may be right and shared, yet the coordination stops moving towards done, or the run ends at the wrong time.
- `D3` Closure before budget: The post ends the work (a pause, a sign-off, a last heartbeat) while items are still open. Example: The run ends on its budget with the index change claimed, half done, and never closed.
- `D4` Capability not routed: The post asks for an action only another seat can take, and the work is never routed to that seat. Example: Only C can reach the database. The others ask C to run each query for them instead of handing C the profiling.
- `deliberation_stall` Deliberation stall: Agents keep discussing, and no post assigns or starts the work. Example: A, B and C argue query versus index for ten turns, and nobody takes either.
- `waiting_cycle` Waiting cycle: Agents wait on each other in a cycle, so none of them can start. Example: C will profile once B has a fix; B will fix once C has profiled.
- `claim_without_action` Claim without action: An agent takes a piece of work and never acts on it. Example: D claims the index change and never touches the schema.
- `never_closes` Never closes: The work is done and nobody says so, so the run goes on until a limit ends it. Example: The fix passes the check, nobody posts that it is done, and the run ends on the wall clock.
- `runs_on_after_done` Runs on after done: Agents keep posting and working after the work is done. Example: After "Done", the agents keep acknowledging each other and polishing comments.

### overhead (not a failure: do not record as an incident)
`REP` Step repetition, `HB` Heartbeat cost, `verbosity` Verbosity, `redundant_verification` Redundant verification

### out of scope (not a communication failure)
`anchoring`, `injection`

If no pattern fits, use `NEW:<short_name>` and say what it is in class_reason.
