---
title: "Vanadium Redox Flow Battery"
type: technology
status: active
tags: ["electrochemical", "flow", "long-duration", "grid-scale"]
energy_density_wh_kg: "15-25"
round_trip_efficiency_pct: "65-80"
typical_duration_hours: "4-12"
maturity: commercial
---

# Vanadium Redox Flow Battery

A flow battery that stores energy in two vanadium electrolyte solutions held in external tanks. During charge and discharge, electrolyte is pumped through a cell stack where electrochemical reactions occur across a membrane.
([Wikipedia](https://en.wikipedia.org/wiki/Vanadium_redox_battery))

## How it works

Unlike intercalation batteries (lithium-ion), energy is stored in dissolved vanadium ions in four oxidation states (V²⁺, V³⁺, VO²⁺, VO₂⁺) rather than in solid electrode materials. Power and energy are decoupled: power scales with cell stack size, energy scales with tank volume.

This decoupling makes VRFB particularly attractive for long-duration applications - you add more electrolyte without redesigning the power electronics.

## Key properties

- **Cycle life**: Effectively unlimited; vanadium electrolyte does not degrade, only the membrane and stack wear over time ([Wikipedia](https://en.wikipedia.org/wiki/Vanadium_redox_battery))
- **Calendar life**: 20+ years
- **No cross-contamination risk**: Both sides use vanadium, so mixing doesn't permanently damage the electrolyte - it can be remixed
- **State of charge visibility**: Can be measured accurately from electrolyte color and open-circuit voltage

## Economics

High capital cost compared to LFP at shorter durations; becomes competitive at 8+ hours. [Vanadium pentoxide traded at approximately $7-10/lb (~$15-22/kg) in 2024](https://www.vanadiumprice.com/), though prices are volatile - electrolyte represents roughly 40% of system cost. Some projects use electrolyte leasing to reduce upfront capital cost.

## Notable deployments

- [[dalian-flow-battery-station]] - 100 MW / 400 MWh (phase 1), world's largest VRFB when commissioned (2022)
- Rongke Power (Dalian) is the primary manufacturer at utility scale
- Invinity Energy Systems operates smaller projects in the UK and North America

## Sources

- [Wikipedia: Vanadium redox battery](https://en.wikipedia.org/wiki/Vanadium_redox_battery)

## Related

[[round-trip-efficiency]], [[energy-density]], [[dalian-flow-battery-station]]
