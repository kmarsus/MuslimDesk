# Prompt for Claude Code on another PC

I'm continuing work on MuslimDesk, an open-source Windows desktop app:
https://github.com/kmarsus/MuslimDesk

On my main PC, I built and released v1.0.4, but when I click the download
link below, it asks me to log in to GitHub — which shouldn't happen for a
public repo's release asset:

https://github.com/kmarsus/MuslimDesk/releases/download/v1.0.4/MuslimDesk.exe

Please investigate from this machine (a genuinely independent test, not
logged into my GitHub account):

1. Open that exact URL in a normal (not incognito) browser here, where I'm
   not logged into GitHub at all, and tell me exactly what happens — does
   it download directly, show a GitHub login page, show a "this file may
   be unsafe" warning, or something else? Screenshot if possible.
2. Also check the release page itself:
   https://github.com/kmarsus/MuslimDesk/releases/tag/v1.0.4
   and the releases list: https://github.com/kmarsus/MuslimDesk/releases
3. If it does download, try running MuslimDesk.exe and confirm Windows
   SmartScreen behavior (should show "unrecognized publisher" — that part
   is expected and fine).
4. Report back exactly what you see at each step, in detail — I need the
   real symptom, not a guess, since my own environment can't reproduce
   this cleanly (I get a generic anti-bot block from GitHub, which is a
   different, known issue).

Don't change any code yet — this is purely a diagnostic pass from a truly
independent, logged-out vantage point. Once we know the real cause
(private/draft release, GitHub malware-scan gate, or something else),
we'll fix it from there.
