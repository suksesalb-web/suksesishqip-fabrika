# suksesishqip-fabrika

Automatic post factory for the Instagram page **@suksesishqip**.

## How it works
1. **Claude** writes the day's posts in Albanian into `queue/YYYY-MM-DD.json` and spellchecks them.
2. **Render action** (`.github/workflows/render.yml`) finds a photo for each post on Pixabay, renders the images into `out/YYYY-MM-DD/`, and commits them.
3. **Claude** looks at every image and writes `approved/YYYY-MM-DD.json` for the ones that pass.
4. **Publish action** (`.github/workflows/publish.yml`) sends approved posts to Buffer, scheduled at each post's time (Tirana). Buffer publishes them to Instagram. The log goes to `published/`.

What gets posted, and the rules for it, live in [GUIDE.md](GUIDE.md).

## Secrets (Settings → Secrets and variables → Actions)
- `PIXABAY_API_KEY` from pixabay.com/api/docs
- `BUFFER_API_KEY` from Buffer → profile icon → API (renew yearly)

## Folders
- `fabrika/` code, fonts, Albanian dictionary, logo
- `queue/` written posts · `out/` rendered images · `approved/` approvals · `published/` Buffer log
- `data/used_photos.txt` Pixabay photos already used (never reused)

Photos: [Pixabay](https://pixabay.com) Content License. Fonts: Inter and Source Serif 4 (SIL Open Font License). Dictionary: LibreOffice sq_AL (GPL).
