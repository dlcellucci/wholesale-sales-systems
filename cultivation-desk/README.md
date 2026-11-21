# Cultivation Desk

A shared cultivation calendar for a small indoor grow, plus a morning Slack bot that tells each person what to do today.

## What it does

- **Month and week calendar** for every room: mothers, propagation, veg, flower 1, flower 2. Each day shows where every batch is ("Flower 1 · B19 · day 29").
- **Batches move when someone taps a button.** Rooted, Flip or Harvested saves the real date, and that becomes day 1 of the next stage.
- **A locked cycle plan.** "Flower day 29 = first defol" is set once. It lands on the right date for every batch, counted from that batch's real flip date.
- **IPM products with label rates.** Each product's rate per gallon shows on the task. A product with no rate shows up in red everywhere.
- **Planned time on every task.** Outcomes are done, not done (with why and how much longer), or not needed. Not-done work rolls to the next workday.
- **An Ops tab** that compares planned to actual time, shows not-done reasons, and shows real rooting and flower days by strain.
- **A morning bot.** `engine.js` works out each person's tasks, and the n8n workflow sends them as Slack DMs from a bot. People reply "1 done" or "2 not done, need 2h, short staffed," and the next run logs it.

## Files

- `index.html` is the desk page. It runs as a Claude artifact with a shared database. Only the owner and editors can create or change tasks.
- `engine.js` is the task math the morning run uses (the same math as the page). Try it: `node engine.js ../sample-data/cultivation 2026-11-20`
- `../workflows/cultivation-desk-bot.json` is the n8n bot workflow. It sends a DM, reads thread replies, and reads later DM messages. Set your own Slack bot credential and webhook path.
- `../sample-data/cultivation/` is made-up data.

## How it checks itself

- Day counts count the stage start date as day 1. The test: a batch flipped Oct 23 has to show "day 29" on Nov 20, and the day 29 defol has to land there.
- A task can't be marked done without minutes, or not done without a reason and the time still needed.
- A task someone moves keeps its new date. The plan never puts a second copy back on the old day.
- Products with no label rate are flagged instead of guessed.
- The Ops tab counts tasks marked done without minutes. It should stay at 0, or the labor numbers lie.
- Replies the bot can't understand are listed in the summary. It never guesses them.

## Where it breaks

- If the bot loses its `im:history` permission, it still sends messages but stops seeing replies, so logging quietly stops. Check the summary's "replies logged" count.
- "done" with no extra time is logged at the planned time, so a task that ran long but got marked plain "done" hides the overrun.
- Stage-length estimates are ranges you set, not predictions. Real dates come only from the taps.
- If nobody taps "Flipped," the flower calendar never starts for that batch.
