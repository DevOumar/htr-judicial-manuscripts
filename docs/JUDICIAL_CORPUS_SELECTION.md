# Judicial corpus selection

The technical development corpus remains `CATMuS/medieval` and `CATMuS/medieval-segmentation`.
The final domain demonstration uses French legal manuscript pages from Gallica.

## Compared sources

| Source | URL | Institution | Period | Image quality | Transcriptions | Legal relevance | Assessment |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Copie de registres du Parlement de Paris, Francais 21256 | https://gallica.bnf.fr/ark:/12148/btv1b9062074w | BnF / Gallica | 1643-1644 | Full-page IIIF images, suitable for Kraken | Not available in machine-readable form | Very high: Parlement de Paris register copies | Selected for the final demo |
| Registre du Parlement tenu a Pontoise | https://gallica.bnf.fr/ark:/12148/btv1b9063861b | BnF / Gallica | 1652 | Full-page IIIF images expected | Not available in machine-readable form | High: parlementary register | Good fallback corpus |
| Collection de copies et extraits des registres du Parlement de Paris, principaux proces criminels | https://gallica.bnf.fr/ark:/12148/btv1b525273066 | BnF / Gallica | 17th-18th c. compilation | Full-page Gallica images | Not available in machine-readable form | High: criminal proceedings and parlementary extracts | Relevant but more heterogeneous |
| Registres des bannieres du Chatelet de Paris, serie Y | Archives nationales, e.g. Y//9 referenced in secondary sources | Archives nationales | 1515-1546 for cited volume | Digitized access not confirmed for automated download | Not available in machine-readable form | Very high: Chatelet legal publication register | Strong subject match, but not selected because automated image access was not confirmed |
| Inventaire du greffe de la maison consulaire de Montpellier | Municipal archives of Montpellier, manuscript II 10/II 11 | Archives municipales de Montpellier | 1662-1663 | Online full-page image access not confirmed | Later printed partial edition exists | Medium-high: greffe/administrative legal archive | Good contextual source, but not selected for reproducible download |

## Recommended corpus

The selected corpus is BnF Francais 21256:

- Title: Copie de registres du Parlement de Paris, years 1643-1644.
- ARK: `btv1b9062074w`.
- Institution: Bibliotheque nationale de France, Gallica.
- Access: IIIF manifest at `https://gallica.bnf.fr/iiif/ark:/12148/btv1b9062074w/manifest.json`.
- Rationale: legal domain, French manuscript pages, 17th century, full-page IIIF access, reproducible download.

The current demonstration downloads 5 page images and runs:

```text
full judicial page
-> Kraken segmentation
-> line extraction
-> TrOCR transcription
-> PAGE XML
-> JSON
```
