---
title: "Lithium-Ion Battery"
type: technology
status: active
tags: ["electrochemical", "mature", "grid-scale", "ev"]
energy_density_wh_kg: "150-300"
round_trip_efficiency_pct: "90-95"
typical_duration_hours: "1-8"
maturity: commercial
---

# Lithium-Ion Battery

The dominant electrochemical storage technology for both electric vehicles and grid-scale applications. Uses lithium ions moving between anode (typically graphite) and cathode through a liquid electrolyte during charge and discharge.
([Wikipedia](https://en.wikipedia.org/wiki/Lithium-ion_battery))

## Chemistry variants

Several cathode chemistries serve different use cases:

- **NMC (Nickel Manganese Cobalt)** - high energy density, common in EVs; typical capacity fade ~20% after 1,000 cycles
- **LFP (Lithium Iron Phosphate)** - lower energy density, longer cycle life (2,000-6,000+ cycles), no cobalt; dominant in stationary storage and increasingly in EVs
- **NCA (Nickel Cobalt Aluminium)** - high energy density; used in early Tesla Powerpack/Megapack units before LFP transition

([Wikipedia: Comparison of commercial battery types](https://en.wikipedia.org/wiki/Comparison_of_commercial_battery_types))

## Grid-scale deployment

Four-hour duration (power MW × 4 = energy MWh) is the standard BESS procurement block in most markets, driven by capacity market rules and PPA structures. Durations beyond 8 hours push economics toward longer-duration alternatives such as [[vanadium-flow-battery]] or [[iron-air-battery]].

## Cost trajectory

Utility-scale pack costs fell from [~$1,200/kWh in 2010 to below $150/kWh by 2023](https://about.bnef.com/blog/lithium-ion-battery-pack-prices-hit-record-low-of-139-kwh/) (BloombergNEF). LFP packs from Chinese manufacturers traded near [$80-100/kWh at the pack level in 2024](https://www.energy-storage.news/bnef-battery-pack-prices-fall-to-new-record-low-in-2024/).

## Limitations

- [[thermal-runaway]] risk requires fire suppression and thermal management systems (see [[moss-landing-energy-storage]] fire, January 2025)
- Calendar aging degrades capacity even without cycling
- Cobalt supply chain concerns for NMC/NCA (less relevant for LFP)
- Economic case weakens beyond 8-hour duration

## Key players

[[tesla-energy]], [[catl]], [[byd]], LG Energy Solution, Samsung SDI, Panasonic

## Sources

- [Wikipedia: Lithium-ion battery](https://en.wikipedia.org/wiki/Lithium-ion_battery)
- [Wikipedia: Comparison of commercial battery types](https://en.wikipedia.org/wiki/Comparison_of_commercial_battery_types)
- [BloombergNEF: Lithium-Ion Battery Pack Prices Hit Record Low](https://about.bnef.com/blog/lithium-ion-battery-pack-prices-hit-record-low-of-139-kwh/)
- [Energy-Storage.news: BNEF battery pack prices fall to new record low in 2024](https://www.energy-storage.news/bnef-battery-pack-prices-fall-to-new-record-low-in-2024/)
