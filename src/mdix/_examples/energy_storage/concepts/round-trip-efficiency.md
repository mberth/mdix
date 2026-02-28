---
title: "Round-Trip Efficiency"
type: concept
status: active
tags: ["performance", "economics", "fundamental"]
---

# Round-Trip Efficiency

Round-trip efficiency (RTE) is the ratio of energy delivered on discharge to energy consumed on charge, expressed as a percentage. It is one of the most important metrics for comparing storage technologies and evaluating the economics of energy arbitrage.
([Wikipedia](https://en.wikipedia.org/wiki/Pumped-storage_hydroelectricity#Efficiency))

## Definition

```
RTE = (Energy out on discharge) / (Energy in on charge) × 100%
```

A system with 90% RTE returns 90 kWh for every 100 kWh charged. The remaining 10% is lost to heat, parasitic loads (pumps, thermal management, power electronics), and internal resistance.

## Values by technology

| Technology | Typical RTE |
|---|---|
| Lithium-ion (LFP) | 90-95% |
| Lithium-ion (NMC) | 88-93% |
| Vanadium flow battery | 65-80% |
| Pumped hydro | 70-85% |
| Compressed air (CAES) | 40-70% |
| Iron-air battery | 40-50% |
| Hydrogen (P2G2P) | 25-40% |

(Sources: [Wikipedia: Comparison of commercial battery types](https://en.wikipedia.org/wiki/Comparison_of_commercial_battery_types), [IEA: Energy Storage](https://www.iea.org/reports/grid-scale-storage))

## Why it matters for economics

RTE directly affects the cost of stored energy. To deliver 1 MWh from a 90% RTE system, you must buy 1.11 MWh of electricity. From a 45% RTE system, you must buy 2.22 MWh. If electricity costs $50/MWh:

- 90% RTE system: $55.6 input cost per MWh delivered
- 45% RTE system: $111 input cost per MWh delivered

This makes low-RTE systems economically viable only when the input electricity is very cheap (abundant solar/wind curtailment) or when duration value is high enough to compensate.

## RTE vs. duration trade-off

Higher duration technologies tend to have lower RTE:
- Short-duration (1-4 hrs): lithium-ion dominates with high RTE
- Medium-duration (4-12 hrs): flow batteries accept lower RTE for longer duration
- Long-duration (100+ hrs): iron-air accepts ~45% RTE for multi-day capability at very low capital cost per kWh

This is not purely a thermodynamic constraint - it also reflects where R&D investment has gone and which parasitic loads matter at each timescale.

## Sources

- [Wikipedia: Pumped-storage hydroelectricity (efficiency section)](https://en.wikipedia.org/wiki/Pumped-storage_hydroelectricity#Efficiency)
- [Wikipedia: Comparison of commercial battery types](https://en.wikipedia.org/wiki/Comparison_of_commercial_battery_types)
- [IEA: Grid-Scale Storage](https://www.iea.org/reports/grid-scale-storage)

## Related

[[energy-density]], [[depth-of-discharge]], [[lithium-ion-battery]], [[vanadium-flow-battery]], [[pumped-hydro-storage]], [[iron-air-battery]]
