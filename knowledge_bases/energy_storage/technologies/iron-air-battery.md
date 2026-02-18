---
title: "Iron-Air Battery"
type: technology
status: active
tags: ["electrochemical", "emerging", "long-duration", "grid-scale"]
energy_density_wh_kg: "20-30"
round_trip_efficiency_pct: "40-50"
typical_duration_hours: "100+"
maturity: pilot
---

# Iron-Air Battery

A metal-air battery chemistry that uses iron as the anode and ambient air (oxygen) as the cathode reactant. Iron rusts on discharge and the process reverses on charge. The materials - iron, water, air - are among the cheapest and most abundant on Earth.
([Wikipedia](https://en.wikipedia.org/wiki/Iron%E2%80%93air_battery))

## Electrochemistry

On discharge:
- Anode: Fe → Fe²⁺ + 2e⁻ (iron oxidizes, "rusts")
- Cathode: O₂ + H₂O + 4e⁻ → 4OH⁻ (oxygen reduction)

On charge, the process reverses: iron oxide is reduced back to iron metal. The electrolyte is aqueous potassium hydroxide.

## Economics and target use case

The technology is explicitly designed for **multi-day (100+ hour) storage** where lithium-ion is uneconomic. [[form-energy]] targets approximately [$250/kWh installed cost](https://formenergy.com/technology/), roughly [1/10th of lithium-ion at equivalent duration](https://formenergy.com/technology/), using the commodity cost of iron.

Round-trip efficiency of 40-50% is low compared to lithium-ion (~90%), but this matters less for long-duration arbitrage where the goal is shifting cheap renewable energy across multiple days rather than intraday cycling.

## Current status

[[form-energy]] is the primary commercial developer. Their [Form Factory 1 in Weirton, West Virginia began production in mid-to-late 2024](https://formenergy.com/updates/), at a [converted 55-acre site from the former Weirton Steel Mill](https://formenergy.com/updates/). The factory initially comprised 550,000 sq ft and employed ~300 people, with an expansion announced in October 2024 targeting 1M+ sq ft and 750+ employees by end of 2025.

In September 2024, Form Energy received a [$150 million DOE grant to fund a new manufacturing line with capacity of up to 20 GWh by 2027](https://www.energy.gov/lpo/form-energy).

The technology passed [UL9540A safety testing with no thermal runaway or fire under extreme fault conditions](https://formenergy.com/updates/) including continuous overcharging for seven days.

## Trade-offs vs alternatives

| Property | Iron-Air | VRFB | Li-ion (LFP) |
|---|---|---|---|
| Duration | 100+ hrs | 4-12 hrs | 1-8 hrs |
| RTE | ~45% | ~75% | ~92% |
| Target cost/kWh | ~$250 | $400-600 | $150-200 |
| Maturity | Pilot | Commercial | Mature |

## Sources

- [Wikipedia: Iron-air battery](https://en.wikipedia.org/wiki/Iron%E2%80%93air_battery)
- [Form Energy: Technology](https://formenergy.com/technology/)
- [DOE Loan Programs Office: Form Energy](https://www.energy.gov/lpo/form-energy)

## Related

[[vanadium-flow-battery]], [[form-energy]], [[round-trip-efficiency]]
