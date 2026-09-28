# palousewaterpros.com

Static marketing site for Palouse Water Pros, an owner-operated water treatment
business in Moscow, Idaho. Plain HTML files at the repo root, no build step,
served by GitHub Pages at https://palousewaterpros.com/ (see `CNAME`).

## Check before pushing

```
python3 tools/validate.py
```

It checks every page for markup, metadata, JSON-LD, links, phone numbers,
banned claims, and template CSS, and checks the sitemap. Add any new page to
`FAMILY` in that script and to `sitemap.xml`, and list it in `llms.txt`.

## Page families

| Family | Template (copy its `<head>`, `<style>`, nav, footer verbatim) | Schema |
|---|---|---|
| Landing (town or service page) | `princeton-potlatch-water-treatment.html` | `Service` + `BreadcrumbList` |
| Article (long-form guide) | `palouse-well-water-guide.html` | `Article` + `BreadcrumbList` |
| FAQ | landing CSS plus its own `details` rules | `FAQPage` + `BreadcrumbList` |
| Home, quiz | their own CSS | `LocalBusiness` + `FAQPage` on home |

The `<style>` block of a landing or article page must be byte-identical to its
template. Change shared styling in the template and re-copy it to every page
in the family. Every page links to `index.html`, `index.html#contact`,
`palouse-well-water-guide.html`, and `water-quiz.html`, and to related pages.

Every page needs: title ≤ 70 characters ending in ` | Palouse Water Pros`
(home excepted), meta description 120–165 characters, canonical and `og:url`
equal to `https://palousewaterpros.com/<file>`, `og:image`, `og:locale`, and
the `prefers-reduced-motion` guard on `scroll-behavior`.

## Facts you may state

- Owner-operator: Trent. First-person voice. Based in Moscow, Idaho. Former
  general contractor who did a lot of plumbing.
- Call **(208) 883-4444** → `tel:+12088834444`. Text **(949) 456-6889** →
  `sms:+19494566889`. Email info@palousewaterpros.com. No other numbers.
- Service area: Latah County and the Idaho side of the Palouse only. Towns:
  Moscow, Viola, Troy, Deary, Bovill, Helmer, Genesee, Kendrick, Juliaetta,
  Princeton, Potlatch, Harvard. **Never claim Washington or Pullman.** The quiz
  offers a "Washington side" answer only to say it is outside the area.
- Process: short call or text → on-site visit of about 45–75 minutes with
  testing done in front of the customer → clear recommendation (one option or
  a couple) → written proposal → Trent builds and installs it himself.
- Equipment: industry-standard, serviceable components, no proprietary
  lock-in. Philosophy: "Never too much, never too little." Test first, design
  around the numbers, install clean, verify after.
- Regional chemistry (keep consistent with the guide): fractured basalt
  aquifers, low-oxygen groundwater dissolves iron and manganese, hardness
  rides along. Iron stains ≥ 0.3 mg/L; manganese stains ≥ 0.05 mg/L and
  0.3 mg/L is EPA health-advisory territory; 7+ gpg is hard; pH below ~6.8 or
  above ~8 complicates oxidation; tannins and coliform change the design.
  Highway 6 corridor runs heavier on manganese and tannins.

## Never state

Prices or dollar amounts, customer stories or road names that did not come
from Trent, testimonials, review counts, years in business, number of
installs, certifications, warranties, financing, whether the visit is free,
turnaround times, "same day", or "24/7". Verify geography and municipal water
facts against a public source before stating them, or leave them out.

## Style

Plain, direct, no hype, no exclamation points. Em dashes are fine. Homeowner
audience. Aim for 900–1,400 words on a landing page and 1,200–1,800 on an
article. One `.callout` per page with a practical "check at home" tip, not a
case study.
