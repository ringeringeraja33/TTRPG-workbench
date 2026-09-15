# Tower manual command audit

斯塔尼亚, 塔骰用户手册, 7.16.13.15.12Stable, 2020-09-02

All129 numbered entries are accounted for. Status is implementation routing, not a claim that every syntax/example has passed. No row claims exact Tower compatibility. See [local workflow](dice-local.md).

| ID | Command | PDF page | Status | Implementation / remaining difference |
|---|---|---|---|---|
| 1 | `.r` | 7 | local-with-differences | Strict bounded arithmetic, rational division, k/q and repeats; malformed input rejected. |
| 2 | `.rd` | 7 | local-with-differences | Default die shorthand via .rd; see r limits. |
| 3 | `.rh` | 7 | local-with-differences | Expression-only hidden roll to private file; no QQ private message or hidden skill shorthand. |
| 4 | `.ra` | 7 | local-with-differences | Explicit tower-house profile; explicit supplied thresholds take priority, unlike the historical forced-card behavior. |
| 5 | `.rc` | 7 | local-with-differences | Explicit CoC7 core profile; targets1..100; does not inherit the last ra/rc setting. |
| 6 | `.set` | 7 | local-with-differences | Keeper changes table default die; no cloud synchronization. |
| 7 | `.rb` | 8 | local-with-differences | Core maximum2 extra dice; explicit core profile. |
| 8 | `.rp` | 8 | local-with-differences | Core maximum2 extra dice; no repeat# variant. |
| 9 | `.sc` | 8 | local-with-differences | Current-card core SAN, nonnegative loss, fumble maximum, daily thresholds and bout suppression; no negative-loss recovery or named-card shorthand. |
| 10 | `.ti` | 8 | requires-data | Requires user-supplied source-checked ti deck; does not apply duration/control. |
| 11 | `.li` | 8 | requires-data | Requires user-supplied source-checked li deck; does not apply duration/control. |
| 12 | `.en` | 8 | local-with-differences | Recorded skill only; Keeper-approved mark via .mark; no attribute development or automatic90% milestone award. |
| 13 | `.rav` | 9 | local-with-differences | General opposition, rank then skill; no combat tie rules and no Tower actual-die tie-break. |
| 14 | `.rcv` | 9 | local-with-differences | General opposition, rank then skill; no combat tie rules and no Tower actual-die tie-break. |
| 15 | `.hiy` | 9 | local-with-differences | Actor/table history of ra/rc/rb/rp only; no shared cloud history. |
| 16 | `.ral` | 9 | local-with-differences | Numeric target and count1..100. |
| 17 | `.rcl` | 9 | local-with-differences | Numeric target and count1..100. |
| 18 | `.crule get` | 9 | local-with-differences | Explicit local house range. |
| 19 | `.crule set` | 9 | local-with-differences | Keeper-only range1..5. |
| 20 | `.algo get` | 9 | local-with-differences | Reports OS-secrets RNG. |
| 21 | `.algo set` | 10 | not-implemented | Historical Tower algorithm switching not implemented; OS RNG fixed. |
| 22 | `.bg` | 10 | requires-data | Requires supplied bg deck; no core-book table included. |
| 23 | `.gas` | 10 | requires-data | Requires supplied gas deck with sixth-edition attribution. |
| 24 | `.coc` | 10 | local-with-differences | CoC7 base batches .coc/.coc5; not Tower .coc6/.coc7 syntax or full age processing. |
| 25 | `.tz` | 10 | requires-data | Requires supplied tz deck identified as nonofficial. |
| 26 | `.name` | 10 | local-with-differences | Small original en/ch/jp name banks; no large historical dataset. |
| 27 | `.nn` | 10 | local-with-differences | Explicit name creates/selects a persistent local card; no unnamed auto-name or shared temporary slot. |
| 28 | `.st` | 10 | local-with-differences | Local names, aliases and bounded numeric expressions; no cloud or all template variables. |
| 29 | `.st list` | 10 | local-with-differences | Actor/table cards. |
| 30 | `.st rm` | 10 | local-with-differences | Cannot delete active or team-bound card. |
| 31 | `.st clr` | 11 | local-with-differences | Resets local temporary slot, preserving other cards. |
| 32 | `.st get` | 11 | local-with-differences | Returns stored values; no omission by official template defaults. |
| 33 | `.st show` | 11 | local-with-differences | Whole card or one canonical stat; absent defaults stay absent. |
| 34 | `.st lock` | 11 | local-with-differences | Table isolation is permanent; no cross-table global-card lock. |
| 35 | `.st rename` | 11 | local-with-differences | Renames ID and updates bound team references. |
| 36 | `.st cp` | 11 | local-with-differences | Local actor copy; target collisions refused; no live user message. |
| 37 | `.kp` | 11 | local-with-differences | First explicit local Keeper; no QQ registration. |
| 38 | `.team` | 11 | local-with-differences | Keeper view of recorded member stats ordered by DEX; derived values are not inferred. |
| 39 | `.team set` | 11 | local-with-differences | Explicit local actor IDs, bound to current cards. |
| 40 | `.team lock` | 11 | local-with-differences | Stable team binding; cross-table global sharing not implemented. |
| 41 | `.team desc` | 12 | local-with-differences | Keeper-private JSON/file; no QQ delivery. |
| 42 | `.team en` | 12 | local-with-differences | Development candidates for bound team cards; not automatic rule eligibility. |
| 43 | `.team hp` | 12 | local-with-differences | Atomic member HP updates, separate actual dice per member; negative resulting HP fails instead of clamping. |
| 44 | `.team san` | 12 | local-with-differences | Atomic member core SAN checks or numeric recovery; no implicit house/profile switching. |
| 45 | `.team rm` | 12 | local-with-differences | Explicit team-member removal. |
| 46 | `.team rename` | 12 | local-with-differences | Local binding preview only; no QQ nickname changes. |
| 47 | `.team clr` | 12 | local-with-differences | Keeper clears team bindings only. |
| 48 | `.team call` | 12 | local-with-differences | Local member preview only; no outgoing mentions. |
| 49 | `.npc` | 12 | local-with-differences | Keeper-private local names. |
| 50 | `.npc st` | 12 | local-with-differences | Keeper local numeric NPC registration. |
| 51 | `.npc rm` | 12 | local-with-differences | Keeper deletes named local NPC. |
| 52 | `.npc clr` | 12 | local-with-differences | Keeper clears NPC store. |
| 53 | `.npc make` | 12 | local-with-differences | Original name/goal seed only; no complete generated statblock. |
| 54 | `.monster` | 13 | local-with-differences | Keeper-private local names. |
| 55 | `.monster st` | 13 | local-with-differences | Keeper local numeric monster registration. |
| 56 | `.monster rm` | 13 | local-with-differences | Keeper deletes named local monster. |
| 57 | `.monster clr` | 13 | local-with-differences | Keeper clears monster store. |
| 58 | `.log` | 13 | local-with-differences | Explicit local submitted messages; no background chat capture. |
| 59 | `.log on` | 13 | local-with-differences | Append/reopen named log, one active per table. |
| 60 | `.log off` | 13 | local-with-differences | Close active log with optional matching name. |
| 61 | `.log list` | 13 | local-with-differences | Names within current table. |
| 62 | `.log get` | 13 | local-with-differences | Audience-filtered entries; CLI exports txt/clean-txt/html/json/docx, no email. |
| 63 | `.log rm` | 14 | local-with-differences | Keeper deletes closed log from active state; audit requests/backups retained. |
| 64 | `.log group get` | 14 | local-with-differences | Explicit local scopes, membership and audience checks; returns JSON entries, no email. |
| 65 | `.log group list` | 14 | local-with-differences | Lists only local scopes with actor membership and that log. |
| 66 | `.ob` | 14 | local-with-differences | Keeper explicitly assigns local observers; not unrestricted self-join. |
| 67 | `.clue` | 14 | local-with-differences | Stores public clue text with stable ID. |
| 68 | `.clue show` | 14 | local-with-differences | Public clue store only; GM evidence uses separate skill workflow. |
| 69 | `.clue rm` | 14 | local-with-differences | Owner or Keeper removes by stable ID, not historical timestamp. |
| 70 | `.clue clr` | 14 | local-with-differences | Keeper clears public clues. |
| 71 | `.dnd` | 14 | local-with-differences | Six unassigned4d6k3 scores per candidate; edition and allocation still required. |
| 72 | `.ri` | 14 | local-with-differences | Explicit d20 base, no table-default-die bug; duplicate initiative refused. |
| 73 | `.init` | 14 | local-with-differences | Sorted local initiative. |
| 74 | `.init clr` | 14 | local-with-differences | Keeper clears initiative. |
| 75 | `.init rm` | 14 | local-with-differences | Keeper removes exact name. |
| 76 | `.init set` | 14 | local-with-differences | Keeper sets explicit manual value; marks it manual. |
| 77 | `.magic` | 15 | requires-data | Requires imported dnd5e-2014/dnd3r source dataset; .magic5e/.magic3r; no bundled full spell database. |
| 78 | `.con` | 15 | requires-data | Requires imported edition-specific dataset. |
| 79 | `.3ry` | 15 | requires-data | Requires imported dnd3r dataset. |
| 80 | `.5ey` | 15 | requires-data | Requires imported dnd5e-2014 dataset; not2024. |
| 81 | `.dr` | 15 | requires-data | Requires supplied dnd5e-dr-a..i decks. |
| 82 | `.rule` | 15 | requires-data | Requires supplied coc7 lookup dataset or skill rule lookup workflow. |
| 83 | `.getbook card` | 15 | local-with-differences | Public character-sheet source pointer only; no historical Tower spreadsheet. |
| 84 | `.getbook make` | 15 | local-with-differences | Bundled creation procedure pointer. |
| 85 | `.getbook kp` | 15 | local-with-differences | Publisher pointer only; no full licensed book redistribution. |
| 86 | `.getbook rp` | 15 | local-with-differences | Bundled character workflow pointer; no RP360 text supplied. |
| 87 | `.w` | 15 | local-with-differences | Bounded local exploding pool; explicit defaults and full evidence differ from Tower terse output. |
| 88 | `.ww` | 16 | local-with-differences | Bounded local exploding pool; no private split at51 dice. |
| 89 | `.ws` | 16 | local-with-differences | Same local detailed pool response; not historical summary-only output. |
| 90 | `.rf` | 16 | local-with-differences | Four Fudge dice with actual raw results. |
| 91 | `.dw` | 16 | requires-data | Requires imported deathwatch lookup dataset. |
| 92 | `.dw card` | 16 | not-implemented | No supplied Deathwatch character-generation package. |
| 93 | `.pfy` | 16 | requires-data | Requires imported pf1 dataset; not PF2. |
| 94 | `.ban` | 16 | external-service | Tower cloud blacklist/API not connected. |
| 95 | `.ban list` | 16 | external-service | Tower cloud blacklist/API not connected. |
| 96 | `.white` | 16 | external-service | Tower per-owner cloud whitelist not connected. |
| 97 | `.white list` | 17 | external-service | Tower per-owner cloud whitelist not connected. |
| 98 | `.admin` | 17 | local-with-differences | Only local configuration .admin setting=value; no QQ on/off/exit/ban. |
| 99 | `.group list` | 17 | external-service | No QQ group inventory. |
| 100 | `.group search` | 17 | external-service | No QQ group lookup. |
| 101 | `.group clean` | 17 | external-service | No QQ group cleanup. |
| 102 | `.dice list` | 17 | external-service | No Tower heartbeat service. |
| 103 | `.system update` | 17 | external-service | No automatic binary download/restart. |
| 104 | `.system restart` | 17 | external-service | No host process management. |
| 105 | `.deck list` | 17 | local-with-differences | Installed local decks only; no Tower market. |
| 106 | `.group` | 17 | local-with-differences | Local simple/secret/jrrp/deck/ob switches only. |
| 107 | `.rank` | 18 | external-service | No cross-bot leader election; one SQLite transactional local store. |
| 108 | `.group secret` | 18 | local-with-differences | Local dice responses have private recipients/files; no QQ delivery. |
| 109 | `.welcome` | 18 | local-with-differences | Local .join events return and log welcome text; duplicate joins suppressed until .leave. No QQ join-event connection or external delivery. |
| 110 | `.fire` | 18 | not-implemented | No licensed solo scenario data or original Tower fire engine supplied. |
| 111 | `.cnmods` | 18 | external-service | No authenticated/verified current CNMods service adapter. |
| 112 | `.custom` | 18 | local-with-differences | Actor/table private custom data; no global Tower approval. |
| 113 | `.custom input` | 18 | local-with-differences | Local .custom input key / text, no shared moderation queue. |
| 114 | `.send` | 19 | external-service | No outgoing messages or Tower feedback channel. |
| 115 | `.answer` | 19 | external-service | No outgoing messages or Tower feedback channel. |
| 116 | `.jrrp` | 19 | local-with-differences | Local actor/table daily UTC value; no cloud synchronization. |
| 117 | `.deck` | 19 | local-with-differences | Flat arrays and attributed weighted/nested JSON decks; full draw-path receipts and transactional retries. No native Tower/Dice deck language, Dxml or executable scripts; bounded with-replacement draws. |
| 118 | `.deck help` | 19 | local-with-differences | Installed local deck names. |
| 119 | `.clock` | 19 | local-with-differences | Owner-private durable timers; list/poll, acknowledgement/cancel and bounded --wait-timers foreground delivery. Stopped processes do not notify; pending timers survive restart. External delivery is not exactly-once. |
| 120 | `.notice input` | 19 | local-with-differences | Local title / body draft only; no QQ announcement. |
| 121 | `.notice show` | 19 | local-with-differences | Keeper-private local notice states. |
| 122 | `.notice agree` | 19 | local-with-differences | Local Keeper approval status only; no independent second admin or publication. |
| 123 | `.notice refuse` | 19 | local-with-differences | Local rejection status only; no external mutation. |
| 124 | `.des` | 19 | local-with-differences | Actor/table private scene lookup. |
| 125 | `.des list` | 19 | local-with-differences | Actor/table scene names. |
| 126 | `.des set` | 19 | local-with-differences | Local .des set name / text. |
| 127 | `.reply` | 20 | local-with-differences | Opt-in actor-private exact-match replies; Keeper may publish an explicit shared snapshot. Submitted local plain messages only; no regex, scripts, background chat capture or marketplace. |
| 128 | `.reply list` | 20 | local-with-differences | Local actor/table reply keys. |
| 129 | `.monster get` | 20 | local-with-differences | Keeper-private recorded monster JSON/file; no QQ message. |
