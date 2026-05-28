# TODO

- [x] FIX 1: Update `scraper/sources/gleaner.py` URL, headers, and status-code handling (return `[]` + log on non-200)
- [x] FIX 2: Update `scraper/sources/goj.py` URL, timeout to 30s, and timeout/error handling (return `[]`)
- [x] FIX 3: Update `scraper/sources/remote_co.py` URL, timeout to 30s, retry (3x with 5s delay), graceful failure to `[]`
- [x] FIX 4: Replace `scraper/sources/facebook_ads.py` Playwright logic with requests-based approach to Facebook endpoint; graceful failure + exact warning log
- [x] FIX 5: Update `scraper/sources/caribbeanjobs.py` URL, full headers, timeout to 30s, blocked/empty handling to return `[]`
- [ ] FIX 6: Run scraper once (`python scraper/main.py --run-now`)
- [ ] FIX 6: Commit and push with message `Fix scraper URLs, timeouts and error handling`


