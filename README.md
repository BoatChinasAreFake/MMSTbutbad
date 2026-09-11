**How to install this fresh trainwreck - presented by the Mappa Mundi team**
1) Download the Mappa-Mundi-sine-Tempore-main.zip file.
2) Unzip the zip file.
3) Extract the folder named Mappa-Mundi-sine-Tempore-main to anywhere on your PC.
4) Go to https://www.python.org/downloads/ and click "Download python install manager."
5) Run "python-manager-26.XX.msix" installer. It will request system admin so approve it.
6) Hit Y on every question prompt, as it opens your command prompt for downloading file systems that help Python run properly.
7) Run the "start_server.bat" file.
8) The python script will open a PowerShell prompt briefly, and a command prompt which you can safely close.
9) It should open your browser, with the address of "localhost:8000" as well as a new tab named "Map Sandbox."
10) Play and enjoy. This application now runs offline as well!
---------------
**Extra notes:**
- don't expect this application to not be a buggy mess. as OCD-pleasing the mod may be, it's not bug-pleasing.
- this application may be unintuitive or clunky to use, so experiment with it! it is quite easy to figure out.
- HOI4 tags are used for streamlining purposes and can be used with placeholder values to make new nations or state creation tools for new states.
---------------
**Credits:**
 - Developers: Faaz Noushad & Pioneerwada.
 - Special thanks to some of those who have worked with us in the past, including:  Nozza, Bonkey Donk, Linus Mapping Tips, Elizabeth.

---------------
**Project layout / development:**
- `index.html` — markup only.
- `styles.css` — all styling.
- `app.js` — the application, loaded as an ES module (`<script type="module">`).
  Pure, side-effect-free helpers are imported from `lib/`.
- `lib/pure.mjs` — geometry, province-id encode/decode, label-text helpers.
- `lib/saveData.mjs` — validation/sanitisation for untrusted loaded save files.
- `test/` — unit tests for the `lib/` modules.
- `server.py` — the local dev/save server (`start_server.bat`).

Run the tests (Node 18+, no dependencies to install):

```
npm test
```

(equivalently: `node --test`)
