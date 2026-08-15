# Human decisions required

Every unresolved question across Section A, in one place. 131 inline markers in
the nine pages collapse to the 34 distinct decisions below.

Nothing here has been decided on the committee's behalf. Where a common practice
exists elsewhere in the sport it is offered as an option, clearly labelled.

Regenerate the marker list at any time:

```bash
python docs/audits/check.py
```

Last compiled: 2026-08-15

## How to use this

1. Work top down. `BLOCKING` items stop pages from publishing.
2. Record the decision in [EVENT_FACTS.md](../EVENT_FACTS.md), not in a page.
3. Replace the markers in the affected pages, then update `status` in the front
   matter and in [manifest.yaml](../manifest.yaml).
4. Re-run `check.py`.

---

# BLOCKING

These stop a page from being published at all.

| # | Decision | Affects | Why it matters | Options |
|---|---|---|---|---|
| B1 | Maze cell size, grid size and overall footprint | A3 3.3.1, A2, B kit docs | Every navigation algorithm and the venue floor plan depend on it | Classic 16x16 at 18 cm cells, half size 32x32 at 9 cm, or a reduced custom grid to fit six hours |
| B2 | Wall height, wall thickness and post size, with tolerance | A3 3.3.2 | Sensor choice and wall following are calibrated against it | Follow the international convention, or match whatever the built mazes actually are |
| B3 | Start cell position and orientation | A3 3.3.3, 3.4 | Where the mouse is placed and which way it faces at the signal | Corner cell facing along the wall is conventional |
| B4 | Goal area size and position | A3 3.3.4, 3.5, 3.8 | Defines what "reached the maze centre" means | 2x2 centre area is conventional; a single centre cell is stricter |
| B5 | Maximum micromouse footprint and any height limit | A3 3.2.1, A8 | A mouse that will not fit must be caught before it runs, not during | Must fit within one cell is the usual test |
| B6 | Number of runs permitted per team, total maze time, and timeout per run | A3 3.5.1 to 3.5.3, A2 running order | Team strategy for the whole day, and the schedule capacity of the event | A fixed time slot per team is simpler to run than a run count |
| B7 | Whether exploration run time is counted, weighted or ignored | A3 3.5.5, 3.8 | Decides whether teams explore fully or dash | Ignore it, or apply a small weighting as some contests do |
| B8 | Timing method and who operates it | A3 3.5.6, 3.8, 3.11 | Defines what "verified" means for the main award | Gate sensors, or a named judge with a stopwatch |
| B9 | Handling and touch penalties, and whether a touched run still scores | A3 3.6.2, 3.6.3 | The single most argued rule at any Micromouse event | Touch ends the run, or a time penalty per touch |
| B10 | Scoring formula for the main award | A3 3.8.1 | The award itself cannot be given without it | Fastest single speed run is the simplest defensible rule |
| B11 | Tie breakers | A3 3.8.4 | Two identical times is a real outcome, not a hypothetical | Second best run, then fewer touches, then judges' decision |
| B12 | Design and reliability award criteria, and the judging panel | A3 3.9.2, 3.9.3, A2, A4 | Teams cannot aim at an undefined target | Publish two or three criteria per award |
| B13 | Disqualification grounds and who may impose one | A3 3.10.2 | Due process, and consistency between judges | |
| B14 | Appeals route, time limit and final arbiter | A3 3.11.1 | Disputes have to end somewhere | Head judge decision is final, appeals within 15 minutes |
| B15 | Named code of conduct contacts and the reporting channel | A9 | A code of conduct with no named contact does not function | At least two named people, ideally not all the same gender, plus a monitored channel |
| B16 | Which UCD policy the Open formally sits under | A9 | Determines the escalation path for a serious report | UCD Student Code of Conduct and the Societies Council Code of Practice are the candidates |
| B17 | Whether Anthropic credits go to all teams or the winning team only | A7, A2, A4, A5 | The public event page says "for the winning team". If competitors expect credits on the day, that must be stated separately | |
| B18 | Anthropic credits redemption mechanism, value, expiry and eligibility | A7, A3 3.9.4 | Redemption instructions must not be guessed. A wrong instruction on the day wastes build time | Confirm with the sponsor contact |
| B19 | Battery handling, charging and fault procedure | A3 3.12.2, A8, A9 | Safety of the venue and of competitors, and a venue condition | |

---

# SOON

Needed before registration opens or before competitors travel.

| # | Decision | Affects | Why it matters | Options |
|---|---|---|---|---|
| S1 | Team size, minimum and maximum | A2, A3 3.1.3, A5 | Judges cannot rule on an oversized team at the maze, and it sets kit quantities | |
| S2 | Registration mechanism, opening date, closing date and fee | A2, A5 | Nothing else in A5 can be published without it | |
| S3 | Eligibility beyond "undergraduates and anyone else", plus minimum age and any under 18 rules | A3 3.1.4, A5 | Entry disputes at sign-in, and a safeguarding question if minors attend | |
| S4 | Whether solo entries are accepted and whether the organisers run team matching | A5 | A large share of sign-ups at events like this arrive alone | |
| S5 | Whether ElecSoc membership is required | A5 | Changes the sign-up flow | |
| S6 | Whether walk-up entry on the day is allowed | A5 | Affects kit ordering | |
| S7 | Total number of team places | A5 | Sets the cap and the waiting list | |
| S8 | Whether teams may bring their own components or tools | A2, A3 3.2.3, A5, A8 | Parity between teams is the core fairness claim of the format | Kit only, or kit plus a published allowed list |
| S9 | Whether pre-event code is permitted, and any starter repository URL | A3 3.7.4, A4, A2, A6 | Determines what teams may legitimately prepare in advance | |
| S10 | Exact room within UCD Village, and the building | A2, A5, A8 | Competitors cannot find the event without it, and the route map cannot be drawn | |
| S11 | Start and finish times, and the hour by hour running order | A2, A5, A8 | Travel planning, catering times, and the whole day timeline | |
| S12 | Catering: whether food is provided, to whom, meal times, dietary request process and allergen labelling | A2, A5, A8 | People with allergies need this before they commit to a six hour day | |
| S13 | Accessibility: step-free route, lift access, accessible toilets, quiet space, access request process and deadline, named accessibility contact | A5, A8 | Competitors with access needs must not have to ask in order to know | |
| S14 | Filming and photography arrangements and the opt-out | A5, A8, A9 | A consent question, not a nice to have | |
| S15 | On-the-day emergency contact number and campus security number | A5, A8, A9 | Required for a live event with soldering and batteries | |
| S16 | Exact ESP32 board model shipped in the kit | A6, B kit docs | A6 is written for the ESP32-C6 with arduino-esp32 core 3.0.0 or later. A different board changes the install steps | |
| S17 | Shared tools provided, whether soldering happens on the day and who does it, and the replacement policy for broken components | A2, A8 | Determines what competitors must bring and what the venue must permit | |
| S18 | Prohibited items in the room | A8 | A venue condition that competitors must know before they pack | |
| S19 | Whether the diagonal mini maze is used for scored runs or practice only | A3 3.3.6, A2 | Decides whether teams should optimise for diagonals | |
| S20 | Permitted contents of the start cell and any pre-run alignment aids | A3 3.4.4 | Consistency of start conditions between teams | |
| S21 | Remaining sponsor slots and the exact wording the UCD School wishes to be credited with | A7 | Two technical partner slots remain open | |
| S22 | Prize list beyond the Anthropic credits package | A2, A3 3.9.4, A5 | Prize claims made in public must be accurate | |

---

# OPTIONAL

Improves the documentation but nothing is blocked on it.

| # | Decision | Affects | Why it matters |
|---|---|---|---|
| O1 | Whether teams keep the kit after the event or return it | A5 | A common question, and it affects kit budget |
| O2 | Whether results and team names are published afterwards | A5 | A data protection courtesy |
| O3 | Whether the Open becomes an annual competition | A5 | Recruitment and sponsor conversations |
| O4 | Sockets per team, tables and bench space, bag and coat storage | A8 | Practical, but competitors can cope without knowing |
| O5 | Wi-Fi arrangement for non-UCD competitors | A8 | AI coding agents need a network. Worth confirming early |
| O6 | Cycle compound access for visitors on a Saturday, and event parking | A8 | UCD pay and display is documented as weekday only, so a Saturday check is needed |
| O7 | Whether the house safety wiki pages will be published under `00_MustKnow` | A9 | A9 currently links to a placeholder index |
| O8 | Whether a carer may attend without registering as a competitor | A8 | Should be yes, but it needs stating |

---

[Documentation home](../index.md) · [Section A audit](A_SECTION_AUDIT.md) · [Competitor docs](../competitor/index.md)
