# Shopify Meta Product Feeds

Public Meta/Facebook/Instagram catalog feed generated from ReefnaFood's public Shopify catalog.

- Feed: `reefna-meta-product-feed.xml`
- Source: `https://reefnafood.com/products.json?limit=250`
- Refresh: every 6 hours via GitHub Actions
- Currency: EGP
- Granularity: one item per Shopify variant

The feed is public because Meta Commerce Manager must be able to fetch it without authentication.

## Doctor Ponino

- Feed: `doctor-ponino-meta-product-feed.xml`
- Source: `https://www.doctorponino.com/products.json?limit=250`
- Refresh: every 6 hours via GitHub Actions
- Currency: EGP
- Granularity: one item per Shopify variant
