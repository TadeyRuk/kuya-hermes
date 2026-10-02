# Kuya Hermes 🏪

A Telegram assistant that keeps the books for a Filipino **sari-sari store**. The owner chats in quick, messy Taglish:

> *"kumuha si Aling Nena ng 3 canton, ilista mo"*

The bot reads the message, records it in a Google Sheet, and replies:

> *"Nailista ✅ Aling Nena: 3 Pancit Canton (₱54). Utang niya ngayon: ₱54."*

Built on [Hermes Agent](https://hermes-agent.nousresearch.com/docs) by Nous Research.

## What it does

| Owner says | Bot does |
|---|---|
| `bumili si Mang Jose ng 2 kopiko, ilista` | Logs **utang** (credit), shows his new balance |
| `cash, 2 sardinas at 1 coke` | Logs **sales**, shows how much stock is left |
| `nagbayad si Aling Nena ng 30` | Logs a **bayad** (payment) against her utang |
| `dumating 20 kopiko` | Logs a **restock** |
| `sino may utang?` / `ano paubos na?` | Reads balances and low-stock items |
| *(every 9 PM)* | Sends a nightly recap to the owner's Telegram |

## How it works

```
Telegram ──► Hermes gateway ──► LLM + Kuya Hermes persona (SOUL.md)
                                   │
                                   └─► sari-sari-store skill ──► store.py ──► Google Sheet
                                                                             ├─ Inventory   (live stock formulas)
                                                                             ├─ Transactions (append-only ledger)
                                                                             └─ Utang       (live balances)
```

- **`persona/SOUL.md`**: the Kuya Hermes personality. Taglish, short replies, keeps customer balances private.
- **`skill/sari-sari-store/SKILL.md`**: teaches the agent how to read Taglish (`ilista`, `bayad`, `dumating`, item nicknames, number words) and which command to run.
- **`skill/sari-sari-store/scripts/store.py`**: a small CLI (`inventory`, `log`, `utang`, `summary`, `undo`) that reads and writes the Sheet and prints JSON. Stock and balances come from Sheet formulas, never from the model.
- **`setup/create_sheet.py`**: creates the Sheet with demo inventory.
- **`setup/install.ps1`**: installs everything into a local Hermes.

## Setup (Windows)

### 1. Hermes Agent
Install Hermes, run `hermes setup`, then `hermes model` to choose an LLM provider. Check with `hermes chat -q "hi"`.

### 2. Telegram bot
1. In Telegram, message **@BotFather** and send `/newbot` to get a bot token. **Never share or commit it.**
2. Message **@userinfobot** to get your numeric user ID.
3. Run `hermes gateway setup`, choose Telegram, paste the token, and allow only your user ID.

### 3. Google access
Hermes's built-in `google-workspace` skill needs a Google Cloud OAuth client:
1. Enable the Gmail, Calendar, Drive, Sheets, Docs and People APIs ([one-click link](https://console.cloud.google.com/flows/enableapi?apiid=gmail.googleapis.com,calendar-json.googleapis.com,drive.googleapis.com,sheets.googleapis.com,docs.googleapis.com,people.googleapis.com)).
2. Set up the OAuth consent screen as **External** and add yourself under **Test users**.
3. Create an OAuth client of type **Desktop app** and download the JSON.
4. Authorize (with `$env:HERMES_HOME` pointing to `%LOCALAPPDATA%\hermes`):
   ```powershell
   $py = "$env:LOCALAPPDATA\hermes\hermes-agent\venv\Scripts\python.exe"
   $g  = "$env:LOCALAPPDATA\hermes\skills\productivity\google-workspace\scripts\setup.py"
   & $py $g --client-secret "C:\path\to\client_secret.json"
   & $py $g --auth-url        # open the link, approve, copy the localhost:1 URL
   & $py $g --auth-code "<paste the whole localhost:1 URL>"
   & $py $g --check           # should print AUTHENTICATED
   ```

### 4. Install Kuya Hermes
```powershell
git clone https://github.com/polsalarm/kuya-hermes.git
cd kuya-hermes
powershell -ExecutionPolicy Bypass -File setup\install.ps1 -TelegramChatId <your-telegram-user-id>
hermes gateway restart
```
Then send `/new` to your bot in Telegram.

The installer flags:
- `-SheetId <id>`: reuse an existing Sheet instead of creating a new one.
- `-SkipPersona`: keep your current `SOUL.md`. Otherwise the old one is backed up before it's replaced.
- Leave out `-TelegramChatId` to skip the nightly report.

## Customizing

- **Products and prices:** edit the **Inventory** tab. To add a product, copy a full existing row so the formula columns (Restocked, Sold, On hand, Status) come along.
- **Personality:** edit `persona/SOUL.md` and re-run the installer, or edit `%LOCALAPPDATA%\hermes\SOUL.md` directly.
- **Report time:** `hermes cron list`, then `hermes cron edit <id>`.
- **After any change:** send `/new` in Telegram, because each conversation keeps the persona it started with.

## Demo tips

- Put the Google Sheet on the projector next to Telegram, so each message shows up as a new row.
- Send `/new` right before presenting.
- Pick a fast model that's good at tool calls (`hermes model`). Turn off MCP servers you don't use (`hermes mcp list`); every extra tool slows down replies.

## Security

- Never commit `.env`, `google_token.json`, `google_client_secret.json`, `mcp-tokens/`, or any bot token or API key. `.gitignore` covers the common ones.
- Keep the Telegram bot locked to the owner's user ID. Anyone who can message an unlocked bot can run commands on the host PC.
