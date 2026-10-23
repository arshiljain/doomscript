# DoomScript Capability & Syntax Reference

> **Auto-generated directly from live DomainRegistry and Compiler Core**
> *Enforces Principle 4: Eliminates documentation drift between advertised syntax and runtime implementation.*

## Table of Contents
1. [Core Language Syntax & Architectural Principles](#1-core-language-syntax--architectural-principles)
   - [1.1 Canonical Comparison & Equality Synonyms](#11-canonical-comparison--equality-synonyms)
   - [1.2 Collection Filtering & Selection](#12-collection-filtering--selection)
   - [1.3 Composable Expressions & Slicing](#13-composable-expressions--slicing)
   - [1.4 Quantifiers & Record Predicates](#14-quantifiers--record-predicates)
   - [1.5 Diagnostic Suggestion Engine](#15-diagnostic-suggestion-engine)
2. [Registered Domain Packs Reference (81 Domains)](#2-registered-domain-packs-reference-81-domains)

---

## 1. Core Language Syntax & Architectural Principles

### 1.1 Canonical Comparison & Equality Synonyms
DoomScript maps intuitive comparison synonyms to unified internal comparison operations:

| Intuitive English Phrase | Canonical AST Operator | Supported Contexts |
| :--- | :--- | :--- |
| `a is b` | `ast.Eq()` | Conditionals, Filters, Pipelines |
| `a equals b` | `ast.Eq()` | Conditionals, Filters, Pipelines |
| `a equal to b` | `ast.Eq()` | Conditionals, Filters, Pipelines |
| `a is equal to b` | `ast.Eq()` | Conditionals, Filters, Pipelines |
| `a is identical to b` | `ast.Eq()` | Conditionals, Filters, Pipelines |
| `a is the same as b` | `ast.Eq()` | Conditionals, Filters, Pipelines |
| `a is not b` / `a isn't b` | `ast.NotEq()` | Conditionals, Filters, Pipelines |
| `a does not equal b` | `ast.NotEq()` | Conditionals, Filters, Pipelines |
| `a is not equal to b` | `ast.NotEq()` | Conditionals, Filters, Pipelines |
| `a is over b` / `a is above b` | `ast.Gt()` | Conditionals, Filters, Pipelines |
| `a is greater than b` / `a > b` | `ast.Gt()` | Conditionals, Filters, Pipelines |
| `a is under b` / `a is below b` | `ast.Lt()` | Conditionals, Filters, Pipelines |
| `a is less than b` / `a < b` | `ast.Lt()` | Conditionals, Filters, Pipelines |
| `a is at least b` / `a >= b` | `ast.GtE()` | Conditionals, Filters, Pipelines |
| `a is at most b` / `a <= b` | `ast.LtE()` | Conditionals, Filters, Pipelines |

### 1.2 Collection Filtering & Selection
Filtering operations accept both prefix and postfix natural forms with identical execution output:
- **Postfix Filter:** `<collection> where <condition> into <target>`
  ```doom
  items where amount is over 50 into qualifying
  ```
- **Prefix Filter:** `keep only <collection> where <condition> into <target>`
  ```doom
  keep only items where amount is over 50 into qualifying
  ```
- **Assignment Filter:** `set <target> to keep only <collection> where <condition>`

### 1.3 Composable Expressions & Slicing
Operations compose recursively without requiring temporary intermediate variables:
- **Composed Expression:**
  ```doom
  set short_label to first 2 items of words joined with " / "
  ```
- **Multi-Statement Decomposition (100% Equivalent):**
  ```doom
  first 2 items of words into short_words
  set short_label to short_words joined with " / "
  ```
- **Other Composable Participles:** `<expr> joined with <sep>`, `reversed <expr>`, `unique <expr>`, `sorted <expr>`

### 1.4 Quantifiers & Record Predicates
Quantifiers resolve property predicates on records/dictionaries and value comparisons cleanly:
- `if every <item> in <collection> is <predicate>:` (e.g. `if every guest in registrations is paid:`)
- `if every <item> in <collection> has <property>:` (e.g. `if every guest in registrations has paid:`)
- `if every <item> in <collection> has <property> equal to <val>:` (e.g. `if every guest in registrations has status equal to "confirmed":`)
- `if any <item> in <collection> is/has <predicate>:`
- `if no <item> in <collection> is/has <predicate>:`

### 1.5 Diagnostic Suggestion Engine
All syntax suggestions provided by the compiler during syntax errors are pre-validated by the parser before presentation:
- Suggestions never mutate protected keywords (e.g., `items` is never warped into `its`).
- Any suggested line that fails AST verification is discarded, guaranteeing 100% valid suggestions.

---

## 2. Registered Domain Packs Reference (81 Domains)

Total Active Registered Domains: **81**

### 2.1 Domain: `acoustics`
- **Primary Name:** `acoustics`
- **Aliases:** `sound_engineering`, `psychoacoustics`, `reverberation`
- **Description:** Deepened Acoustics domain: Sound Pressure Level, Sabine/Eyring RT60, Doppler shift, A-weighting, transmission loss, and room acoustics
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate spl pressure {p:expr} into {target:ident}`: Sound pressure level (dB SPL)
  - `calculate` — Pattern: `calculate sabine rt60 volume {v:expr} absorption {a:expr} into {target:ident}`: Sabine reverberation time
  - `calculate` — Pattern: `calculate eyring rt60 volume {v:expr} area {s:expr} absorption {alpha:expr} into {target:ident}`: Eyring reverberation time
  - `calculate` — Pattern: `calculate doppler shift freq {f:expr} source_v {vs:expr} into {target:ident}`: Doppler frequency shift
  - `calculate` — Pattern: `calculate sound decay spl {spl:expr} r1 {r1:expr} r2 {r2:expr} into {target:ident}`: Inverse square sound drop
  - `calculate` — Pattern: `calculate sound transmission loss mass {m:expr} freq {f:expr} into {target:ident}`: Sound transmission loss (mass law)
  - `calculate` — Pattern: `calculate a weighting freq {f:expr} into {target:ident}`: IEC A-weighting filter
  - `calculate` — Pattern: `calculate schroeder frequency volume {v:expr} rt60 {rt:expr} into {target:ident}`: Schroeder cutoff frequency
- **Exported Functions/Symbols (125):** `AcousticsRuntime`, `DomainRuntime`, `P_REF`, `acoustics_a_weighting`, `acoustics_characteristic_impedance`, `acoustics_doppler_shift`, `acoustics_eyring_rt60`, `acoustics_inverse_square_decay`, `acoustics_phon_to_sone`, `acoustics_room_modes`, `acoustics_sabine_rt60`, `acoustics_schroeder_frequency`, `acoustics_sound_transmission_loss`, `acoustics_spl_db`, `ds_adsr_envelope`...

### 2.2 Domain: `actuarial`
- **Primary Name:** `actuarial`
- **Aliases:** `actuary`, `insurance_math`, `mortality`
- **Description:** Deepened Actuarial domain: Gompertz/Makeham mortality, life annuities, term insurance premiums, Chain Ladder loss reserving, and ruin theory
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate gompertz mortality age {age:expr} base {b:expr} factor {c:expr} into {target:ident}`: Gompertz mortality hazard rate
  - `calculate` — Pattern: `calculate makeham mortality age {age:expr} accident {a:expr} base {b:expr} factor {c:expr} into {target:ident}`: Gompertz-Makeham mortality hazard rate
  - `calculate` — Pattern: `calculate annuity present value payment {p:expr} rate {r:expr} years {n:expr} into {target:ident}`: Annuity present value
  - `calculate` — Pattern: `calculate term insurance premium benefit {b:expr} mortality {q:expr} rate {r:expr} term {n:expr} into {target:ident}`: Term insurance net single premium
  - `calculate` — Pattern: `calculate loss reserve claims {c:expr} severity {s:expr} rate {r:expr} into {target:ident}`: Discounted loss reserve
  - `calculate` — Pattern: `calculate chain ladder losses {l:expr} ratio {f:expr} into {target:ident}`: Chain ladder ultimate loss projection
  - `calculate` — Pattern: `calculate life expectancy age {age:expr} into {target:ident}`: Curtate life expectancy
  - `calculate` — Pattern: `calculate cramer lundberg ruin surplus {u:expr} premium {c:expr} frequency {lam:expr} mean_claim {mu:expr} into {target:ident}`: Cramér-Lundberg ruin probability
- **Exported Functions/Symbols (122):** `ActuarialRuntime`, `DomainRuntime`, `actuarial_annuity_present_value`, `actuarial_chain_ladder_projection`, `actuarial_chain_ladder_triangle`, `actuarial_cramer_lundberg_ruin`, `actuarial_curtate_life_expectancy`, `actuarial_gompertz_mortality_rate`, `actuarial_loss_reserve`, `actuarial_makeham_mortality_rate`, `actuarial_term_insurance_premium`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`...

### 2.3 Domain: `aerospace`
- **Primary Name:** `aerospace`
- **Aliases:** `orbital_mechanics`, `rocketry`, `astronautics`
- **Description:** Deepened Aerospace domain: Aerodynamic lift/drag, Mach numbers, Breguet range, orbital velocities, Hohmann transfers, Kepler orbits, and rocket propulsion
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate lift drag density {rho:expr} velocity {v:expr} wing {s:expr} cl {cl:expr} cd {cd:expr} into {target:ident}`: Lift and drag forces
  - `calculate` — Pattern: `calculate mach number velocity {v:expr} temp {t:expr} into {target:ident}`: Mach flight speed
  - `calculate` — Pattern: `calculate breguet range ld {ld:expr} velocity {v:expr} sfc {sfc:expr} w0 {w0:expr} w1 {w1:expr} into {target:ident}`: Breguet aircraft range
  - `calculate` — Pattern: `calculate orbital velocity altitude {alt:expr} mass {m:expr} radius {r:expr} into {target:ident}`: Circular orbit velocity
  - `calculate` — Pattern: `calculate hohmann transfer r1 {r1:expr} r2 {r2:expr} into {target:ident}`: Hohmann transfer orbit delta-v
  - `calculate` — Pattern: `calculate kepler orbit periapsis {rp:expr} apoapsis {ra:expr} into {target:ident}`: Keplerian orbital parameters
  - `calculate` — Pattern: `calculate rocket delta v isp {isp:expr} m0 {m0:expr} mf {mf:expr} into {target:ident}`: Tsiolkovsky rocket equation
  - `calculate` — Pattern: `calculate normal shock mach {m1:expr} into {target:ident}`: Normal shock wave properties
- **Exported Functions/Symbols (124):** `AerospaceRuntime`, `DomainRuntime`, `G0_STANDARD`, `G_CONST`, `aero_breguet_range`, `aero_lift_drag`, `aero_lift_drag_forces`, `aero_mach_number`, `aerospace_hohmann_transfer`, `aerospace_kepler_orbit`, `aerospace_normal_shock`, `aerospace_orbital_velocity`, `aerospace_tsiolkovsky_rocket`, `ds_adsr_envelope`, `ds_agent_confidence`...

### 2.4 Domain: `agent`
- **Primary Name:** `agent`
- **Aliases:** `agents`, `multiagent`, `ai_agent`
- **Description:** AI Agents, LLM system prompts, memory contexts, tools, and multi-agent teams
- **Registered Verbs & Patterns:**
  - `create_agent` — Pattern: `create agent {role:expr} [with tools {tools:expr}] into {target:ident}`: Instantiate autonomous AI agent with role and tools
  - `ask_agent` — Pattern: `ask agent {agent_var:ident} {prompt:expr} into {target:ident}`: Send conversational prompt to agent and receive reply
  - `tell_agent` — Pattern: `tell agent {agent_var:ident} {message:expr}`: Append information to agent conversational memory without expecting response
  - `create_team` — Pattern: `create team {name:expr} with agents {agents:expr} into {target:ident}`: Form multi-agent collaborative team
  - `run_team` — Pattern: `run team {team_var:ident} on {task:expr} into {target:ident}`: Execute multi-agent collaborative task execution workflow
  - `agent_memory` — Pattern: `memory of agent {agent_var:ident} into {target:ident}`: Retrieve conversation message history from agent
  - `clear_memory` — Pattern: `clear memory of agent {agent_var:ident}`: Reset agent context window and memory
- **Exported Functions/Symbols (171):** `Agent`, `AgentMemoryBuffer`, `AgentRuntime`, `AgentSpec`, `AgentTeam`, `DomainIR`, `DomainRuntime`, `HTNPlanner`, `HierarchicalTaskNetworkHTNPlanner`, `MCTSNode`, `MonteCarloTreeSearchEngine`, `MonteCarloTreeSearchMCTS`, `MultiAgentDebate`, `ReActAgent`, `Record`...

### 2.5 Domain: `agronomy`
- **Primary Name:** `agronomy`
- **Aliases:** `agri`, `crop_science`, `soil_science`
- **Description:** Soil physics, crop water modeling, irrigation, fertility, and soil conservation.
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate crop water requirement et0 {et0:expr} kc {kc:expr} into {target:ident}`: Calculates crop water requirement ETc
  - `calculate` — Pattern: `calculate growing degree days tmax {tmax:expr} tmin {tmin:expr} into {target:ident}`: Calculates Growing Degree Days GDD
  - `calculate` — Pattern: `calculate fertilizer rate nutrient {n:expr} percent {p:expr} into {target:ident}`: Calculates bulk fertilizer application rate
  - `calculate` — Pattern: `calculate cation exchange ca {ca:expr} mg {mg:expr} k {k:expr} na {na:expr} into {target:ident}`: Calculates CEC and base saturation
  - `calculate` — Pattern: `calculate soil porosity bulk {pb:expr} into {target:ident}`: Calculates soil total porosity fraction
  - `calculate` — Pattern: `calculate usle erosion r {r:expr} k {k:expr} ls {ls:expr} c {c:expr} p {p:expr} into {target:ident}`: Calculates annual USLE soil erosion loss
  - `calculate` — Pattern: `calculate available water capacity fc {fc:expr} pwp {pwp:expr} depth {d:expr} into {target:ident}`: Calculates plant available water capacity
  - `calculate` — Pattern: `calculate nitrogen balance om {om:expr} demand {dem:expr} into {target:ident}`: Estimates soil N mineralization and fertilizer deficit
  - `calculate` — Pattern: `calculate irrigation schedule deficit {def:expr} efficiency {eff:expr} rate {r:expr} into {target:ident}`: Calculates gross irrigation depth and runtime
  - `calculate` — Pattern: `calculate leaf area index foliage {f:expr} ground {g:expr} into {target:ident}`: Calculates Leaf Area Index and light interception
  - `calculate` — Pattern: `calculate sar na {na:expr} ca {ca:expr} mg {mg:expr} into {target:ident}`: Calculates Sodium Adsorption Ratio SAR
- **Exported Functions/Symbols (124):** `AgronomyRuntime`, `DomainRuntime`, `agronomy_available_water_capacity`, `agronomy_cation_exchange_capacity`, `agronomy_crop_water_requirement`, `agronomy_fertilizer_rate`, `agronomy_growing_degree_days`, `agronomy_irrigation_depth_schedule`, `agronomy_leaf_area_index`, `agronomy_nitrogen_mineralization_balance`, `agronomy_sodium_adsorption_ratio`, `agronomy_soil_porosity`, `agronomy_universal_soil_loss_equation`, `ds_adsr_envelope`, `ds_agent_confidence`...

### 2.6 Domain: `astronomy`
- **Primary Name:** `astronomy`
- **Aliases:** `astrodynamics`, `celestial`, `orbits`
- **Description:** Keplerian orbits, celestial coordinate transformations, Julian dates, and Hohmann transfers
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate julian date for year {y:expr} month {m:expr} day {d:expr} into {target:ident}`: Converts calendar date to astronomical Julian Date
  - `calculate` — Pattern: `calculate hohmann transfer from radius {r1:expr} to {r2:expr} into {target:ident}`: Calculates orbital transfer delta-v and flight duration
- **Exported Functions/Symbols (160):** `ASTRONOMY_DOMAIN`, `Astrodynamics`, `AstronomyASTExporter`, `AstronomyDomain`, `AstronomyDomainParser`, `AstronomyRuntime`, `AtmosphericRefraction`, `CelestialCoordinates`, `CelestialRiseSetTransit`, `CelestialTime`, `DomainASTExporter`, `DomainContract`, `DomainIR`, `DomainParser`, `DomainRuntime`...

### 2.7 Domain: `astrophysics`
- **Primary Name:** `astrophysics`
- **Aliases:** `stellar_physics`, `cosmology`, `black_holes`
- **Description:** Deepened Astrophysics domain: Schwarzschild event horizons, Stefan-Boltzmann luminosity, Eddington limits, Jeans collapse, Hubble expansion, and Hawking radiation
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate schwarzschild radius mass {m:expr} into {target:ident}`: Gravitational event horizon radius
  - `calculate` — Pattern: `calculate stellar luminosity radius {r:expr} temp {t:expr} into {target:ident}`: Stefan-Boltzmann stellar luminosity
  - `calculate` — Pattern: `calculate eddington luminosity mass {m:expr} into {target:ident}`: Eddington radiation accretion limit
  - `calculate` — Pattern: `calculate hubble velocity distance {d:expr} into {target:ident}`: Hubble cosmic expansion velocity
  - `calculate` — Pattern: `calculate jeans mass temp {t:expr} density {n:expr} into {target:ident}`: Jeans gravitational collapse mass
  - `calculate` — Pattern: `calculate critical density h0 {h0:expr} into {target:ident}`: Friedmann cosmological critical density
  - `calculate` — Pattern: `calculate hawking radiation mass {m:expr} into {target:ident}`: Hawking radiation temperature and lifetime
- **Exported Functions/Symbols (129):** `AstrophysicsRuntime`, `DomainRuntime`, `G_CONST`, `H_BAR`, `K_BOLTZMANN`, `SIGMA_SB`, `SOLAR_LUMINOSITY_W`, `SOLAR_MASS_KG`, `SPEED_OF_LIGHT`, `astro_eddington_luminosity`, `astro_einstein_radius`, `astro_friedmann_critical_density`, `astro_hawking_radiation`, `astro_hubble_velocity`, `astro_jeans_mass`...

### 2.8 Domain: `audio`
- **Primary Name:** `audio`
- **Aliases:** `sound`, `music`
- **Description:** Audio & Sound processing, waveform manipulation, trims, fades, volume, combination
- **Registered Verbs & Patterns:**
  - `load_audio` — Pattern: `load audio [from] {path_expr:expr} into {target:ident}`: Load WAV, MP3, or FLAC audio file
  - `create_blank_audio` — Pattern: `create blank audio of {duration_expr:expr} [seconds] into {target:ident}`: Create silence or blank audio buffer
  - `trim_audio` — Pattern: `trim [audio] {audio_var:ident} from {start_expr:expr} to {end_expr:expr} into {target:ident}`: Extract time slice of audio
  - `fade_audio` — Pattern: `fade (in|out) [audio] {audio_var:ident} over {duration_expr:expr} [seconds] into {target:ident}`: Apply linear or exponential volume envelope fade
  - `adjust_volume` — Pattern: `adjust volume of [audio] {audio_var:ident} by {factor_expr:expr} into {target:ident}`: Scale amplitude or dB gain
  - `combine_audio` — Pattern: `combine audio {first_var:ident} and {second_var:ident} into {target:ident}`: Concatenate two audio buffers sequentially
  - `save_audio` — Pattern: `save audio {audio_var:ident} to {path_expr:expr}`: Write audio track to disk as WAV
  - `audio_duration` — Pattern: `duration of [audio] {audio_var:ident} into {target:ident}`: Get duration of audio clip in seconds
- **Exported Functions/Symbols (184):** `AudioCombineSpec`, `AudioCreateSpec`, `AudioFadeSpec`, `AudioLoadSpec`, `AudioRuntime`, `AudioSaveSpec`, `AudioTrimSpec`, `AudioVolumeSpec`, `BiquadIIRFilterCascaded`, `CooleyTukeyFFT`, `DecibelGainReduction`, `DomainIR`, `DomainRuntime`, `DoomAudio`, `DynamicRangeCompressorLimiter`...

### 2.9 Domain: `automata`
- **Primary Name:** `automata`
- **Aliases:** `dfa`, `nfa`, `turing`, `fsm`, `regex`
- **Description:** Deterministic/Nondeterministic finite automata, Hopcroft state minimization, regex-to-DFA, and Turing machines
- **Registered Verbs & Patterns:**
  - `compile` — Pattern: `compile regex {regex:expr} to dfa into {target:ident}`: Compiles regular expression into a minimized DFA
  - `minimize` — Pattern: `minimize dfa {dfa:expr} into {target:ident}`: Minimizes DFA states using Hopcroft's algorithm
  - `check` — Pattern: `check if dfa {dfa:expr} accepts {input_str:expr} into {target:ident}`: Evaluates whether DFA accepts the input sequence
- **Exported Functions/Symbols (157):** `AUTOMATA_DOMAIN`, `AutomataASTExporter`, `AutomataDomain`, `AutomataDomainParser`, `AutomataRuntime`, `BuchiAutomaton`, `CellularAutomata1D`, `ContextFreeGrammarCYKParser`, `DFA`, `DomainContract`, `DomainIR`, `DomainRuntime`, `GameOfLife2D`, `GlushkovPositionalNFA`, `HopcroftDFAMinimizer`...

### 2.10 Domain: `aviation`
- **Primary Name:** `aviation`
- **Aliases:** `flight`, `aero`, `avionics`
- **Description:** Flight mechanics, aerodynamics, navigation, performance, and weight and balance.
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate pressure altitude altimeter {alt:expr} elevation {elev:expr} into {target:ident}`: Computes pressure altitude PA in feet
  - `calculate` — Pattern: `calculate density altitude pressure_alt {pa:expr} oat {oat:expr} into {target:ident}`: Computes density altitude DA in feet
  - `calculate` — Pattern: `calculate wind components wind_speed {ws:expr} wind_dir {wd:expr} runway {rwy:expr} into {target:ident}`: Computes crosswind and headwind components in knots
  - `calculate` — Pattern: `calculate turn radius tas {tas:expr} bank {bank:expr} into {target:ident}`: Computes coordinated level turn radius in feet
  - `calculate` — Pattern: `calculate banked stall speed vs0 {vs0:expr} bank {bank:expr} into {target:ident}`: Computes accelerated stall speed in a bank turn
  - `calculate` — Pattern: `calculate climb gradient roc {roc:expr} tas {tas:expr} into {target:ident}`: Computes aircraft climb gradient percentage
  - `calculate` — Pattern: `calculate true airspeed cas {cas:expr} pressure_alt {pa:expr} oat {oat:expr} into {target:ident}`: Computes TAS and Mach number from CAS
  - `calculate` — Pattern: `calculate glide performance ratio {gr:expr} altitude {alt:expr} into {target:ident}`: Computes unpowered glide range in nautical miles
  - `calculate` — Pattern: `calculate holding pattern drift wind_speed {ws:expr} wind_dir {wd:expr} course {crs:expr} tas {tas:expr} into {target:ident}`: Computes wind correction angles and outbound holding timer
  - `calculate` — Pattern: `calculate weight and balance empty_weight {ew:expr} empty_arm {ea:expr} stations {st:expr} into {target:ident}`: Computes gross takeoff weight and CG position
  - `calculate` — Pattern: `calculate critical mach sweep {sweep:expr} thickness {tc:expr} into {target:ident}`: Computes critical Mach and drag divergence Mach number
  - `calculate` — Pattern: `calculate standard rate turn tas {tas:expr} into {target:ident}`: Computes bank angle and load factor for standard rate 3 deg/sec turn
- **Exported Functions/Symbols (125):** `AviationRuntime`, `DomainRuntime`, `aviation_banked_stall_speed`, `aviation_climb_gradient`, `aviation_critical_mach_drag_divergence`, `aviation_density_altitude`, `aviation_glide_performance`, `aviation_holding_pattern_drift`, `aviation_pressure_altitude`, `aviation_standard_rate_turn`, `aviation_tas_from_cas`, `aviation_turn_radius`, `aviation_weight_and_balance`, `aviation_wind_components`, `ds_adsr_envelope`...

### 2.11 Domain: `bio`
- **Primary Name:** `bio`
- **Aliases:** `genomics`, `bioinformatics`
- **Description:** Bioinformatics, sequence alignment, genomics, and computational biology
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate gc content of {seq:expr} into {target:ident}`: Calculates GC percentage of a DNA or RNA sequence
  - `transcribe` — Pattern: `transcribe dna {seq:expr} into {target:ident}`: Transcribes DNA to RNA
  - `reverse` — Pattern: `reverse complement of {seq:expr} into {target:ident}`: Generates reverse complement of DNA sequence
  - `translate` — Pattern: `translate rna {seq:expr} into {target:ident}`: Translates nucleotide sequence into amino acid protein chain
  - `align` — Pattern: `align sequences {s1:expr} and {s2:expr} using needleman wunsch into {target:ident}`: Performs global Needleman-Wunsch or local Smith-Waterman sequence alignment
  - `parse` — Pattern: `parse fasta [string] {text:expr} into {target:ident}`: Parses multi-record FASTA strings into structured records
- **Exported Functions/Symbols (162):** `AMINO_ACID_WEIGHTS`, `AffineGapGotohAligner`, `BioRuntime`, `BurrowsWheelerTransformBWT`, `CODON_TABLE`, `CodonAdaptationIndex`, `CodonOptimizationSolver`, `DomainIR`, `DomainRuntime`, `FMIndexBWT`, `HiddenMarkovModelCpGIslandFinder`, `KozakConsensusScanner`, `NussinovRNA`, `NussinovRNAFoldingDynamicProgramming`, `PhylogeneticTreeNJ`...

### 2.12 Domain: `biomechanics`
- **Primary Name:** `biomechanics`
- **Aliases:** `biomech`, `kinesiology`, `human_motion`
- **Description:** Musculoskeletal modeling, kinesiology, inverse dynamics, and human movement kinetics.
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate joint moment force {f:expr} arm {r:expr} into {target:ident}`: Calculates joint torque/moment in N*m
  - `calculate` — Pattern: `calculate center of mass masses {m:expr} positions {x:expr} into {target:ident}`: Calculates 1D center of mass
  - `calculate` — Pattern: `calculate grf impulse forces {f:expr} dt {dt:expr} into {target:ident}`: Calculates ground reaction force linear impulse
  - `calculate` — Pattern: `calculate muscle tendon force muscle {f:expr} pennation {a:expr} into {target:ident}`: Calculates force transmitted along tendon
  - `calculate` — Pattern: `calculate hill muscle force velocity {v:expr} f0 {f0:expr} param_a {a:expr} param_b {b:expr} into {target:ident}`: Calculates muscle force from Hill model
  - `calculate` — Pattern: `calculate segment inertia mass {m:expr} radius {r:expr} into {target:ident}`: Calculates limb segment moment of inertia
  - `calculate` — Pattern: `calculate joint power moment {m:expr} velocity {w:expr} into {target:ident}`: Calculates joint power and mechanical work
  - `calculate` — Pattern: `calculate loading rate forces {f:expr} rate {sr:expr} weight {bw:expr} into {target:ident}`: Calculates average and instantaneous vertical loading rates
  - `calculate` — Pattern: `calculate pennation thickness {t:expr} length {l:expr} into {target:ident}`: Calculates muscle architectural pennation angle
  - `calculate` — Pattern: `calculate joint contact moment {m:expr} arm {r:expr} reaction {rx:expr} into {target:ident}`: Calculates compressive joint contact force
  - `calculate` — Pattern: `calculate gait froude velocity {v:expr} leg {l:expr} into {target:ident}`: Calculates Alexander gait Froude number
- **Exported Functions/Symbols (125):** `BiomechanicsRuntime`, `DomainRuntime`, `biomech_center_of_mass`, `biomech_gait_froude_number`, `biomech_grf_impulse`, `biomech_hills_muscle_force_velocity`, `biomech_inverse_dynamics_2d_segment`, `biomech_joint_contact_force`, `biomech_joint_moment`, `biomech_muscle_mechanical_work_power`, `biomech_muscle_tendon_force`, `biomech_pennate_muscle_aponeurosis`, `biomech_segment_moment_of_inertia_cylinder`, `biomech_vertical_loading_rate`, `ds_adsr_envelope`...

### 2.13 Domain: `cache`
- **Primary Name:** `cache`
- **Aliases:** `caching`, `lru`, `ttl`, `arc`
- **Description:** Advanced caching: LRU, LFU, ARC, 2Q, Clock, Bloom filters, consistent hashing, and XFetch
- **Registered Verbs & Patterns:**
  - `create` — Pattern: `create lru cache with capacity {cap:expr} into {target:ident}`: Create LRU cache
  - `create` — Pattern: `create lfu cache with capacity {cap:expr} into {target:ident}`: Create LFU cache
  - `create` — Pattern: `create arc cache with capacity {cap:expr} into {target:ident}`: Create ARC cache
  - `create` — Pattern: `create hash ring with replicas {rep:expr} into {target:ident}`: Consistent hash ring
  - `store` — Pattern: `store in cache {cache:expr} key {key:expr} value {val:expr}`: Store cache value
  - `fetch` — Pattern: `fetch from cache {cache:expr} key {key:expr} into {target:ident}`: Fetch cache value
- **Exported Functions/Symbols (139):** `ARCCache`, `BloomFilter`, `CacheRuntime`, `ClockCache`, `ConsistentHashRing`, `DomainRuntime`, `LFUCache`, `LRUCache`, `SegmentedLRUCache`, `TTLCache`, `TwoQueueCache`, `cache_bloom_add`, `cache_bloom_check`, `cache_create_2q`, `cache_create_arc`...

### 2.14 Domain: `cartography`
- **Primary Name:** `cartography`
- **Aliases:** `carto`, `map_projection`, `geodesy`
- **Description:** Deepened Cartography domain: Haversine distance, initial bearing, Mercator projection, UTM zones, map scales, WGS84 geodesy, and Rhumb lines
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate haversine distance lat1 {lat1:expr} lon1 {lon1:expr} lat2 {lat2:expr} lon2 {lon2:expr} into {target:ident}`: Haversine great circle distance
  - `calculate` — Pattern: `calculate initial bearing lat1 {lat1:expr} lon1 {lon1:expr} lat2 {lat2:expr} lon2 {lon2:expr} into {target:ident}`: Initial spherical azimuth
  - `calculate` — Pattern: `calculate mercator projection lat {lat:expr} lon {lon:expr} into {target:ident}`: Mercator forward projection
  - `calculate` — Pattern: `calculate utm zone lon {lon:expr} into {target:ident}`: Universal Transverse Mercator zone
  - `calculate` — Pattern: `calculate ground distance map_cm {cm:expr} scale {scale:expr} into {target:ident}`: Map scale to ground distance
  - `calculate` — Pattern: `calculate mercator distortion lat {lat:expr} into {target:ident}`: Tissot indicatrix Mercator distortion
  - `calculate` — Pattern: `calculate wgs84 ecef lat {lat:expr} lon {lon:expr} height {h:expr} into {target:ident}`: WGS84 geodetic to ECEF 3D Cartesian
- **Exported Functions/Symbols (125):** `CartographyRuntime`, `DomainRuntime`, `EARTH_RADIUS_KM`, `WGS84_A`, `WGS84_E2`, `WGS84_F`, `carto_ground_distance`, `carto_haversine_distance`, `carto_initial_bearing`, `carto_mercator_projection`, `carto_rhumb_line_distance`, `carto_tissot_indicatrix_distortion`, `carto_utm_zone`, `carto_wgs84_to_ecef`, `ds_adsr_envelope`...

### 2.15 Domain: `chain`
- **Primary Name:** `chain`
- **Aliases:** `blockchain`, `crypto_ledger`, `web3`
- **Description:** Blockchain, Merkle trees, Proof-of-Work, UTXO ledgers, and EIP-55 addresses
- **Registered Verbs & Patterns:**
  - `create` — Pattern: `create merkle tree from {leaves:expr} into {target:ident}`: Constructs a cryptographic binary Merkle tree
  - `get` — Pattern: `get merkle root of {tree:expr} into {target:ident}`: Extracts the root hash of a Merkle tree
  - `verify` — Pattern: `verify merkle proof for item {leaf:expr} with root {root:expr} and proof {proof:expr} into {target:ident}`: Cryptographically verifies a Merkle inclusion proof
  - `mine` — Pattern: `mine block with data {data:expr} and difficulty {diff:expr} into {target:ident}`: Mines a Proof-of-Work block searching for target difficulty nonce
  - `create` — Pattern: `create utxo ledger into {target:ident}`: Initializes a UTXO balance state machine
- **Exported Functions/Symbols (157):** `ChainRuntime`, `DomainIR`, `DomainRuntime`, `EVMBytecodeInterpreterStackMachine`, `MerklePatriciaTrie`, `MerkleTree`, `PatriciaMerkleTrie`, `ProofOfStakeValidator`, `RaftConsensusEngine`, `Record`, `SchnorrZKProtocol`, `ThresholdSignatureSchemeShamir`, `UtxoLedger`, `chain_add_utxo_tx`, `chain_checksum_address`...

### 2.16 Domain: `chem`
- **Primary Name:** `chem`
- **Aliases:** `chemistry`, `molecule`, `reaction`
- **Description:** Molecular formulas, atomic masses, SMILES topology, aromaticity, and stoichiometric reaction balancing
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate molecular weight of {formula:expr} into {target:ident}`: Calculates molecular weight in g/mol from a chemical formula
  - `parse` — Pattern: `parse smiles {smiles:expr} into {target:ident}`: Parses SMILES string into molecular graph topology and rings
  - `balance` — Pattern: `balance reaction {reactants:expr} -> {products:expr} into {target:ident}`: Balances reaction coefficients using exact stoichiometric nullspace
- **Exported Functions/Symbols (154):** `AcidBaseEquilibriumpH`, `ArrheniusEyringTransitionState`, `Atom`, `AutocatalyticOregonatorSimulator`, `Bond`, `CHEM_DOMAIN`, `ChemASTExporter`, `ChemDomain`, `ChemDomainParser`, `ChemRuntime`, `ChemicalStoichiometryBalancer`, `DomainContract`, `DomainIR`, `DomainRuntime`, `FormulaParser`...

### 2.17 Domain: `chronometry`
- **Primary Name:** `chronometry`
- **Aliases:** `chrono`, `horology`, `sidereal_time`
- **Description:** Deepened Chronometry domain: Julian Day Numbers, GMST, Equation of Time, Special & General Relativity, GPS clock drift, and solar ephemeris
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate julian day year {y:expr} month {m:expr} day {d:expr} into {target:ident}`: Julian Day Number
  - `calculate` — Pattern: `calculate gmst jdn {jdn:expr} into {target:ident}`: Greenwich Mean Sidereal Time
  - `calculate` — Pattern: `calculate equation of time day {d:expr} into {target:ident}`: Equation of Time
  - `calculate` — Pattern: `calculate time dilation proper {t0:expr} velocity {v:expr} into {target:ident}`: Special relativistic time dilation
  - `calculate` — Pattern: `calculate gravitational dilation proper {t0:expr} mass {m:expr} radius {r:expr} into {target:ident}`: General relativistic gravitational time dilation
  - `calculate` — Pattern: `calculate solar declination day {d:expr} into {target:ident}`: Solar declination angle
  - `calculate` — Pattern: `calculate gps drift altitude {alt:expr} velocity {v:expr} into {target:ident}`: GPS relativistic net clock drift
- **Exported Functions/Symbols (123):** `ChronometryRuntime`, `DomainRuntime`, `G_CONST`, `SPEED_OF_LIGHT`, `chrono_equation_of_time`, `chrono_gps_relativistic_drift`, `chrono_gravitational_time_dilation`, `chrono_greenwich_mean_sidereal_time`, `chrono_julian_day_number`, `chrono_relativistic_time_dilation`, `chrono_solar_declination`, `chrono_sunrise_sunset_hours`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`...

### 2.18 Domain: `circuit`
- **Primary Name:** `circuit`
- **Aliases:** `electronics`, `iot`, `hardware`
- **Description:** Electronics, Ohm's law, resistor decoding, logic gates, and GPIO pins
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate voltage with current {i:expr} and resistance {r:expr} into {target:ident}`: Calculates voltage using Ohm's Law (V = I * R)
  - `decode` — Pattern: `decode resistor colors {colors:expr} into {target:ident}`: Decodes 4-band or 5-band EIA resistor color codes
  - `evaluate` — Pattern: `evaluate logic truth table for {expr:expr} into {target:ident}`: Evaluates boolean logic truth table over all variable permutations
  - `calculate` — Pattern: `calculate pwm duty cycle for high time {ht:expr} and period {p:expr} into {target:ident}`: Calculates PWM duty cycle percentage
- **Exported Functions/Symbols (165):** `ActiveSallenKeyFilterDesigner`, `BodePlotAnalyzer`, `CircuitBoard`, `CircuitDivResult`, `CircuitRCResult`, `CircuitRuntime`, `DigitalStaticTimingAnalyzerSTA`, `DomainIR`, `DomainRuntime`, `ModifiedNodalAnalysis`, `ModifiedNodalAnalysisMNASolver`, `NonlinearDiodeSolver`, `OpAmpModel`, `QuineMcCluskeyBooleanMinimizer`, `RESISTOR_COLORS`...

### 2.19 Domain: `climate`
- **Primary Name:** `climate`
- **Aliases:** `meteorology`, `weather`, `atmosphere`
- **Description:** Meteorology & climate: Dew point, heat index, wind chill, VPD, radiative forcing, EBM, and geostrophic wind
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate dew point for temperature {t:expr} humidity {h:expr} into {target:ident}`: Dew point
  - `calculate` — Pattern: `calculate wind chill for temperature {t:expr} wind {w:expr} into {target:ident}`: Wind chill
  - `calculate` — Pattern: `calculate vpd for temperature {t:expr} humidity {h:expr} into {target:ident}`: VPD
  - `calculate` — Pattern: `calculate radiative forcing for co2 {ppm:expr} into {target:ident}`: Radiative forcing
  - `calculate` — Pattern: `calculate barometric pressure for altitude {alt:expr} into {target:ident}`: Barometric pressure
- **Exported Functions/Symbols (122):** `ClimateRuntime`, `DomainRuntime`, `climate_barometric_altitude`, `climate_co2_equivalent`, `climate_dew_point`, `climate_energy_balance_step`, `climate_geostrophic_wind`, `climate_heat_index`, `climate_radiative_forcing`, `climate_vapor_pressure_deficit`, `climate_wind_chill`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`...

### 2.20 Domain: `cloud`
- **Primary Name:** `cloud`
- **Aliases:** `s3`, `storage`, `bucket`
- **Description:** Cloud & Object Storage operations for S3 and compatible blob stores
- **Registered Verbs & Patterns:**
  - `connect_bucket` — Pattern: `connect to bucket {name:expr} (as|into) {target:ident}`: Establish connection to named cloud storage bucket
  - `upload_file` — Pattern: `upload file {local_expr:expr} to [bucket] {b_var:ident} as {remote_expr:expr}`: Upload local file to object storage path
  - `download_file` — Pattern: `download file {remote_expr:expr} from [bucket] {b_var:ident} to {local_expr:expr}`: Download remote object from bucket to local disk
  - `list_files` — Pattern: `list all files in [bucket] {b_var:ident} [matching {pat:expr}] into {target:ident}`: List keys matching prefix or pattern in bucket
  - `signed_url` — Pattern: `generate signed url for {remote_expr:expr} in [bucket] {b_var:ident} [with expiry {sec:int} seconds] into {target:ident}`: Generate pre-signed URL for direct browser access
- **Exported Functions/Symbols (187):** `BucketLifecycleEngine`, `ChandyLamportSnapshot`, `CircuitBreakerResilience`, `CloudBucket`, `CloudConnectSpec`, `CloudCostCalculator`, `CloudDownloadSpec`, `CloudListSpec`, `CloudRuntime`, `CloudSignedUrlSpec`, `CloudStorageManager`, `CloudUploadSpec`, `ContentAddressableStorage`, `DistributedConsistentHashRing`, `DomainIR`...

### 2.21 Domain: `combustion`
- **Primary Name:** `combustion`
- **Aliases:** `flame`, `thermal_combustion`, `reaction_kinetics`
- **Description:** Deepened Combustion domain: Equivalence ratio, Arrhenius reaction kinetics, heat release, adiabatic flame temperature, Le Chatelier flammability limits, and NOx scaling
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate equivalence ratio fuel {f:expr} air {a:expr} stoich {stoich:expr} into {target:ident}`: Fuel-air equivalence ratio
  - `calculate` — Pattern: `calculate arrhenius rate preexp {a:expr} ea {ea:expr} temp {t:expr} into {target:ident}`: Arrhenius reaction rate constant
  - `calculate` — Pattern: `calculate heat release rate flow {m:expr} lhv {lhv:expr} eff {eff:expr} into {target:ident}`: Thermal heat release rate (MW)
  - `calculate` — Pattern: `calculate adiabatic flame temp t0 {t0:expr} lhv {lhv:expr} cp {cp:expr} afr {afr:expr} into {target:ident}`: Adiabatic flame temperature (K)
  - `calculate` — Pattern: `calculate mixture flammability fractions {y:expr} limits {limits:expr} into {target:ident}`: Le Chatelier mixture flammability limit
  - `calculate` — Pattern: `calculate thermal nox temp {t:expr} oxygen {xo2:expr} into {target:ident}`: Thermal Zeldovich NOx forward rate index
  - `calculate` — Pattern: `calculate wobbe index hhv {hhv:expr} gravity {sg:expr} into {target:ident}`: Wobbe index for fuel gas interchangeability
- **Exported Functions/Symbols (121):** `CombustionRuntime`, `DomainRuntime`, `combust_adiabatic_flame_temp`, `combust_arrhenius_rate`, `combust_damkohler_number`, `combust_equivalence_ratio`, `combust_heat_release_rate`, `combust_le_chatelier_flammability_limit`, `combust_wobbe_index`, `combust_zeldovich_nox_scaling`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`, `ds_agent_recall_similar`...

### 2.22 Domain: `compiler`
- **Primary Name:** `compiler`
- **Aliases:** `bytecode`, `vm`, `assembler`
- **Description:** Bytecode Virtual Machine, assembler, and Pratt expression parser
- **Registered Verbs & Patterns:**
  - `assemble` — Pattern: `assemble bytecode from text {text:expr} into {target:ident}`: Assembles mnemonic assembly into bytecode instructions and constants
  - `execute` — Pattern: `execute bytecode program {prog:expr} into {target:ident}`: Executes bytecode program on stack VM
  - `parse` — Pattern: `parse pratt expression {expr:expr} into {target:ident}`: Parses arithmetic expression using Pratt parser
- **Exported Functions/Symbols (150):** `Assembler`, `BytecodeVM`, `COMPILER_DOMAIN`, `ChaitinRegisterAllocator`, `CompilerASTExporter`, `CompilerDomain`, `CompilerDomainParser`, `CompilerRuntime`, `DomainASTExporter`, `DomainContract`, `DomainIR`, `DomainParser`, `DomainRuntime`, `DominatorTreeBuilder`, `EarleyChartParser`...

### 2.23 Domain: `compression`
- **Primary Name:** `compression`
- **Aliases:** `compress`, `huffman`, `lzw`, `codec`
- **Description:** Lossless compression algorithms, RLE, Huffman prefix coding, LZ77, LZW, and Shannon entropy
- **Registered Verbs & Patterns:**
  - `compress` — Pattern: `compress text {text:expr} with huffman into {target:ident}`: Compresses text using canonical Huffman prefix coding
  - `decompress` — Pattern: `decompress huffman {encoded:expr} into {target:ident}`: Decompresses Huffman bitstream using codebook
  - `compress` — Pattern: `compress text {text:expr} with lzw into {target:ident}`: Compresses text using LZW dictionary coding
  - `decompress` — Pattern: `decompress lzw {codes:expr} into {target:ident}`: Decompresses LZW token sequence
  - `calculate` — Pattern: `calculate entropy of {text:expr} into {target:ident}`: Calculates Shannon entropy in bits per symbol
- **Exported Functions/Symbols (158):** `ArithmeticCodec`, `AsymmetricNumeralSystemsANS`, `BWTCompressor`, `ByteAlignedSnappy`, `COMPRESSION_DOMAIN`, `CompressionASTExporter`, `CompressionDomain`, `CompressionDomainParser`, `CompressionRuntime`, `ContextTreeWeightingCTW`, `DeflateEngine`, `DeltaAndBitPackingEncoder`, `DomainContract`, `DomainIR`, `DomainRuntime`...

### 2.24 Domain: `control`
- **Primary Name:** `control`
- **Aliases:** `control_systems`, `feedback`, `pid`
- **Description:** Feedback control, state-space systems, PID tuning, Kalman filtering, frequency response, and stability analysis.
- **Registered Verbs & Patterns:**
  - `step` — Pattern: `step state space a {a:expr} b {b:expr} state {x:expr} input {u:expr} into {target:ident}`: Calculates next discrete state space update
  - `step` — Pattern: `step kalman filter prior {x:expr} cov {p:expr} measurement {z:expr} noise {r:expr} into {target:ident}`: Calculates single step 1D Kalman filter estimate
  - `calculate` — Pattern: `calculate pid step for error {e:expr} dt {dt:expr} integral {i:expr} prev_err {pe:expr} kp {kp:expr} ki {ki:expr} kd {kd:expr} into {target:ident}`: Calculates PID output and updated integrator
  - `fuse` — Pattern: `fuse gyro {g:expr} accel {a:expr} prev {p:expr} into {target:ident}`: Complementary sensor fusion filter
  - `check` — Pattern: `check stability for polynomial {coeffs:expr} into {target:ident}`: Routh-Hurwitz polynomial stability check
  - `calculate` — Pattern: `calculate bode response omega_n {wn:expr} zeta {z:expr} frequencies {w:expr} into {target:ident}`: Calculates second-order Bode magnitude and phase
  - `discretize` — Pattern: `discretize pole {s:expr} sampling {t:expr} into {target:ident}`: Tustin bilinear continuous-to-discrete pole mapping
  - `calculate` — Pattern: `calculate lqr cost q {q:expr} r {r:expr} states {x:expr} inputs {u:expr} into {target:ident}`: Evaluates quadratic LQR cost trajectory
  - `evaluate` — Pattern: `evaluate step response times {t:expr} values {v:expr} target {tgt:expr} into {target:ident}`: Calculates rise time, overshoot, and settling time
  - `tune` — Pattern: `tune ziegler nichols ku {ku:expr} tu {tu:expr} into {target:ident}`: Calculates Ziegler-Nichols PID tuning gains
- **Exported Functions/Symbols (123):** `ControlRuntime`, `DomainRuntime`, `control_bode_second_order`, `control_complementary_filter`, `control_kalman_1d_step`, `control_lqr_cost_evaluation`, `control_pid_step`, `control_routh_hurwitz_stable`, `control_state_space_step`, `control_step_response_metrics`, `control_tustin_bilinear_transform`, `control_ziegler_nichols_tuning`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`...

### 2.25 Domain: `crypto_zk`
- **Primary Name:** `crypto_zk`
- **Aliases:** `zkp`, `zero_knowledge`, `schnorr`, `pedersen`
- **Description:** Zero-Knowledge Proofs & Cryptography: Shamir secret sharing, Pedersen, Merkle trees, Schnorr ZK, and Elliptic Curves
- **Registered Verbs & Patterns:**
  - `split` — Pattern: `split secret {sec:expr} into {n:expr} shares with threshold {t:expr} into {target:ident}`: Shamir split
  - `build` — Pattern: `build merkle tree for leaves {leaves:expr} into {target:ident}`: Merkle tree
  - `generate` — Pattern: `generate schnorr zk proof for secret {s:expr} into {target:ident}`: Schnorr proof
  - `reconstruct` — Pattern: `reconstruct secret from shares {shares:expr} into {target:ident}`: Shamir reconstruct
- **Exported Functions/Symbols (124):** `CryptoZKRuntime`, `DomainRuntime`, `EllipticCurve`, `PRIME`, `crypto_diffie_hellman`, `crypto_merkle_tree`, `crypto_merkle_verify`, `crypto_pedersen_commit`, `crypto_schnorr_prove`, `crypto_schnorr_verify_proof`, `crypto_shamir_reconstruct`, `crypto_shamir_split`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`...

### 2.26 Domain: `crystallography`
- **Primary Name:** `crystallography`
- **Aliases:** `crystal`, `xray_diffraction`, `lattice`
- **Description:** Deepened Crystallography domain: Bragg diffraction, cubic/hexagonal lattice interplanar spacing, atomic packing factor, unit cell density, Scherrer size, and selection rules
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate bragg angle wavelength {lam:expr} spacing {d:expr} order {n:expr} into {target:ident}`: Bragg diffraction angle
  - `calculate` — Pattern: `calculate interplanar spacing lattice {a:expr} h {h:expr} k {k:expr} l {l:expr} into {target:ident}`: Cubic interplanar spacing
  - `calculate` — Pattern: `calculate atomic packing factor system {sys:expr} into {target:ident}`: Atomic packing factor APF
  - `calculate` — Pattern: `calculate crystal density atoms {n:expr} weight {a:expr} volume {vc:expr} into {target:ident}`: Theoretical crystal density
  - `calculate` — Pattern: `calculate crystallite size wavelength {lam:expr} fwhm {beta:expr} theta {theta:expr} into {target:ident}`: Scherrer crystallite domain size
  - `check` — Pattern: `check reflection allowed lattice {lat:expr} h {h:expr} k {k:expr} l {l:expr} into {target:ident}`: Systematic extinction selection rules
- **Exported Functions/Symbols (121):** `AVOGADRO_CONSTANT`, `CrystallographyRuntime`, `DomainRuntime`, `crystal_atomic_packing_factor`, `crystal_bragg_angle`, `crystal_cubic_interplanar_spacing`, `crystal_density`, `crystal_hexagonal_interplanar_spacing`, `crystal_scherrer_crystallite_size`, `crystal_systematic_extinction_allowed`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`, `ds_agent_recall_similar`...

### 2.27 Domain: `data`
- **Primary Name:** `data`
- **Aliases:** `etl`, `pipeline`
- **Description:** Data Engineering pipelines, cleaning, relational joins, and aggregations
- **Registered Verbs & Patterns:**
  - `read_file` — Pattern: `read (csv|json|text) file {path:expr} into {target:ident}`: Read tabular CSV, JSON, or text data file into Table
  - `write_file` — Pattern: `write (csv|json) {source:ident} into [file] {path:expr}`: Serialize and write Table/records to file
  - `filter` — Pattern: `{source:ident} where {condition:expr} into {target:ident}`: Filter table or record list rows matching condition expression
  - `sort` — Pattern: `sort {source:ident} by {field:ident} [(descending|ascending)]`: Sort table or record list by column
  - `inspect_dataset` — Pattern: `inspect dataset {source:ident} [into {target:ident}]`: Inspect schema, shape, and null counts of a dataset
  - `profile_dataset` — Pattern: `profile dataset {source:ident} [into {target:ident}]`: Compute summary statistics and data quality metrics
  - `remove_duplicates` — Pattern: `remove duplicates from {source:ident} [by {field:ident}] into {target:ident}`: Deduplicate rows by primary key or all fields
  - `remove_nulls` — Pattern: `remove nulls from {source:ident} [in {field:ident}] into {target:ident}`: Drop rows containing null or missing values
  - `group_by` — Pattern: `group {source:ident} by {group_col:ident} calculating {agg_fn:ident} of {val_col:ident} into {target:ident}`: Group dataset by key column and aggregate metric
  - `join` — Pattern: `join {left:ident} and {right:ident} on {key:ident} as (inner|left|right|outer) into {target:ident}`: Relational join between two datasets
- **Exported Functions/Symbols (207):** `ColumnarTable`, `CountMinSketch`, `DataPipelineRuntime`, `DedupeStep`, `DeriveStep`, `DomainIR`, `DomainRuntime`, `FillNaStep`, `FilterStep`, `GroupByStep`, `HyperLogLogSketch`, `JoinStep`, `PipelineSpec`, `PivotTableEngine`, `Record`...

### 2.28 Domain: `db`
- **Primary Name:** `db`
- **Aliases:** `sql`, `database`
- **Description:** Relational database operations, SQL execution, schema reflection, and parameterized queries
- **Registered Verbs & Patterns:**
  - `query_table` — Pattern: `query {table:ident} [where {cond:expr}] into {target:ident}`: Select records from database table with optional filter
  - `inspect_table` — Pattern: `inspect table {table:ident} [into {target:ident}]`: Inspect schema, columns, and foreign keys of a database table
  - `execute_sql` — Pattern: `execute sql {query:expr} [into {target:ident}]`: Execute parameterized raw SQL statement
  - `insert_into` — Pattern: `insert into {table:ident} values {values:expr}`: Insert new row or records into database table
  - `count_rows` — Pattern: `count rows in {table:ident} [into {target:ident}]`: Count total rows matching in database table
- **Exported Functions/Symbols (187):** `BPlusTreeIndex`, `BPlusTreeNode`, `BTreeNode`, `BTreeStorageEnginePure`, `BitmapIndexCompressor`, `CostBasedQueryOptimizer`, `CostBasedQueryOptimizerCBO`, `DBRuntime`, `DomainIR`, `DomainRuntime`, `InMemoryRelationalDB`, `LSMTreeCompactionEngine`, `MigrationManager`, `QuerySpec`, `Record`...

### 2.29 Domain: `dsa`
- **Primary Name:** `dsa`
- **Aliases:** `algo`, `algorithms`, `dsa_benchmark`, `analysis`
- **Description:** Data structures, algorithm benchmarking, empirical Big-O fitting, and memory profiling
- **Registered Verbs & Patterns:**
  - `complexity_of` — Pattern: `[empirical] complexity of {fn_name:ident} [on sizes {sizes:expr}] into {target:ident}`: Empirical curve fitting for Big-O asymptotic runtime complexity
  - `profile_memory` — Pattern: `profile memory of {fn_name:ident} [with {arg:expr}] into {target:ident}`: Measure peak memory consumption and allocation
  - `benchmark_sizes` — Pattern: `benchmark {fn_name:ident} (with|on) sizes {sizes:expr} into {target:ident}`: Measure execution time across input problem sizes
  - `pop_from` — Pattern: `pop (min|max|left|first|right|last) from {coll:ident} into {target:ident}`: Remove and retrieve extreme element from heap or queue
  - `create_grid` — Pattern: `create [2d] grid with {rows:expr} rows and {cols:expr} columns [filled with {fill:expr}] into {target:ident}`: Create safely initialized 2D matrix without shallow reference sharing
  - `connected_components_grid` — Pattern: `find [(4-way|8-way)] connected components in {grid:ident} where cell is {cell_val:expr} into {target:ident}`: Find all connected groups of coordinates in a 2D grid
  - `create_heap` — Pattern: `create (min|max) heap into {target:ident}`: Create universal min or max priority queue
  - `build_graph` — Pattern: `build [(directed|undirected)] graph from {edges:expr} into {target:ident}`: Construct algorithmic graph supporting cycle checks and topological sort
  - `graph_cycle` — Pattern: `[check if] {graph:ident} has cycle into {target:ident}`: Detect whether graph contains cycles using 3-color DFS
  - `topological_sort` — Pattern: `topological (sort|order) of {graph:ident} into {target:ident}`: Compute topological sequence of vertices using Kahn's algorithm
  - `memoize_function` — Pattern: `memoize [function] {fn:ident}`: Automatically cache function outputs with deep argument hashing
  - `merge_intervals` — Pattern: `merge overlapping intervals in {intervals:expr} into {target:ident}`: Sort and merge overlapping interval pairs
  - `sliding_window_max` — Pattern: `sliding window maximum of {arr:expr} with size {k:expr} into {target:ident}`: Compute optimal O(n) monotonic sliding window maxima
- **Exported Functions/Symbols (324):** `AVLNode`, `AVLTree`, `AhoCorasick`, `AhoCorasickNode`, `BTree`, `BTreeNode`, `BenchmarkSpec`, `BloomFilter`, `CompactRadixTree`, `CompactRadixTreeNode`, `ComplexityReport`, `CountingBloomFilter`, `DinicFlowEdge`, `DinicMaxFlow`, `DisjointSetUnion`...

### 2.30 Domain: `ecology`
- **Primary Name:** `ecology`
- **Aliases:** `biodiversity`, `population_dynamics`, `ecosystems`
- **Description:** Deepened Ecology domain: Shannon/Simpson biodiversity, island biogeography, Lotka-Volterra dynamics, mark-recapture, and metapopulation models
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate shannon diversity abundances {abundances:expr} into {target:ident}`: Shannon-Wiener diversity index
  - `calculate` — Pattern: `calculate simpson diversity abundances {abundances:expr} into {target:ident}`: Gini-Simpson diversity index
  - `calculate` — Pattern: `calculate pielou evenness abundances {abundances:expr} into {target:ident}`: Pielou species evenness
  - `calculate` — Pattern: `calculate island biogeography area {a:expr} constant {c:expr} exponent {z:expr} into {target:ident}`: MacArthur-Wilson species-area law
  - `step` — Pattern: `step lotka volterra prey {x:expr} pred {y:expr} alpha {a:expr} beta {b:expr} gamma {g:expr} delta {d:expr} dt {dt:expr} into {target:ident}`: Lotka-Volterra predator-prey step
  - `calculate` — Pattern: `calculate logistic growth n0 {n0:expr} rate {r:expr} capacity {k:expr} time {t:expr} into {target:ident}`: Logistic population growth
  - `estimate` — Pattern: `estimate population mark recapture n1 {n1:expr} n2 {n2:expr} m2 {m2:expr} into {target:ident}`: Chapman mark-recapture estimation
- **Exported Functions/Symbols (122):** `DomainRuntime`, `EcologyRuntime`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`, `ds_agent_recall_similar`, `ds_agent_reflect`, `ds_align_sequences_nw`, `ds_amortize_loan`, `ds_audio_filter_lowpass`, `ds_audit_safety`, `ds_balance_equation`, `ds_batch_stream`, `ds_beta_coefficient`...

### 2.31 Domain: `electromagnetics`
- **Primary Name:** `electromagnetics`
- **Aliases:** `em`, `emag`, `maxwell`
- **Description:** Deepened Electromagnetics domain: Maxwell equations, Biot-Savart, skin depth, Poynting vector, coax impedance, plane waves, and RF transmission
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate magnetic field wire current {i:expr} distance {r:expr} into {target:ident}`: Biot-Savart straight wire magnetic field
  - `calculate` — Pattern: `calculate skin depth freq {f:expr} conductivity {sigma:expr} perm {ur:expr} into {target:ident}`: Electromagnetic conductor skin depth
  - `calculate` — Pattern: `calculate poynting vector efield {e:expr} hfield {h:expr} into {target:ident}`: Poynting power flux vector magnitude
  - `calculate` — Pattern: `calculate coax impedance inner {a:expr} outer {b:expr} eps {eps:expr} into {target:ident}`: Coaxial cable characteristic impedance
  - `calculate` — Pattern: `calculate wave attenuation freq {f:expr} conductivity {sigma:expr} eps {eps:expr} perm {ur:expr} into {target:ident}`: Lossy dielectric plane wave attenuation
  - `calculate` — Pattern: `calculate faraday emf turns {n:expr} flux {flux:expr} time {dt:expr} into {target:ident}`: Faraday induced electromotive force
  - `calculate` — Pattern: `calculate vswr zl {zl:expr} z0 {z0:expr} into {target:ident}`: RF transmission line VSWR and reflection
- **Exported Functions/Symbols (125):** `DomainRuntime`, `EPS_0`, `ElectromagneticsRuntime`, `MU_0`, `SPEED_OF_LIGHT`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`, `ds_agent_recall_similar`, `ds_agent_reflect`, `ds_align_sequences_nw`, `ds_amortize_loan`, `ds_audio_filter_lowpass`, `ds_audit_safety`...

### 2.32 Domain: `epidemiology`
- **Primary Name:** `epidemiology`
- **Aliases:** `disease_spread`, `outbreak`, `sir_model`
- **Description:** Compartmental epidemic modeling, reproduction numbers, herd immunity, and outbreak analytics.
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate reproduction number r0 for beta {b:expr} gamma {g:expr} into {target:ident}`: Calculates Basic Reproduction Number R0
  - `calculate` — Pattern: `calculate herd immunity threshold for r0 {r0:expr} into {target:ident}`: Calculates Herd Immunity Threshold percentage
  - `step` — Pattern: `step sir model s {s:expr} i {i:expr} r {r:expr} beta {b:expr} gamma {g:expr} into {target:ident}`: Single step of SIR compartmental model
  - `step` — Pattern: `step seir model s {s:expr} e {e:expr} i {i:expr} r {r:expr} beta {b:expr} sigma {sig:expr} gamma {g:expr} into {target:ident}`: Single step of SEIR model with latency
  - `calculate` — Pattern: `calculate cfr for cases {c:expr} deaths {d:expr} into {target:ident}`: Calculates Case Fatality Rate percentage
  - `calculate` — Pattern: `calculate effective rt r0 {r0:expr} susceptible {s:expr} into {target:ident}`: Calculates time-varying effective reproduction number Rt
  - `calculate` — Pattern: `calculate final epidemic size r0 {r0:expr} into {target:ident}`: Solves final epidemic attack rate relation
  - `calculate` — Pattern: `calculate vaccination threshold r0 {r0:expr} efficacy {e:expr} into {target:ident}`: Calculates required population vaccination coverage
  - `calculate` — Pattern: `calculate epidemic doubling time r0 {r0:expr} generation {tg:expr} into {target:ident}`: Calculates epidemic exponential doubling time
  - `calculate` — Pattern: `calculate outbreak odds ratio exp_cases {a:expr} exp_healthy {b:expr} unexp_cases {c:expr} unexp_healthy {d:expr} into {target:ident}`: Calculates Relative Risk and Odds Ratio in 2x2 table
  - `calculate` — Pattern: `calculate secondary attack rate cases {sc:expr} contacts {k:expr} into {target:ident}`: Calculates Secondary Attack Rate SAR
- **Exported Functions/Symbols (124):** `DomainRuntime`, `EpidemiologyRuntime`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`, `ds_agent_recall_similar`, `ds_agent_reflect`, `ds_align_sequences_nw`, `ds_amortize_loan`, `ds_audio_filter_lowpass`, `ds_audit_safety`, `ds_balance_equation`, `ds_batch_stream`, `ds_beta_coefficient`...

### 2.33 Domain: `ergonomics`
- **Primary Name:** `ergonomics`
- **Aliases:** `ergo`, `human_factors`, `workplace_safety`
- **Description:** Ergonomics and human factors: NIOSH lifting equation, RULA/REBA postural scoring, spinal L5/S1 compression, and anthropometrics
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate niosh lifting limit load {lc:expr} horiz {h:expr} vert {v:expr} dist {d:expr} angle {a:expr} freq {f:expr} coupling {c:expr} into {target:ident}`: NIOSH lifting limit
  - `calculate` — Pattern: `calculate rula score upper {u:expr} lower {l:expr} wrist {w:expr} neck {n:expr} trunk {t:expr} load {load:expr} into {target:ident}`: RULA posture score
  - `calculate` — Pattern: `calculate metabolic expenditure weight {w:expr} met {m:expr} minutes {t:expr} into {target:ident}`: Metabolic expenditure
  - `calculate` — Pattern: `calculate reba score trunk {t:expr} neck {n:expr} legs {l:expr} uarm {ua:expr} larm {la:expr} wrist {w:expr} into {target:ident}`: REBA entire body score
  - `calculate` — Pattern: `calculate strain index intensity {im:expr} duration {dm:expr} efforts {em:expr} posture {pm:expr} into {target:ident}`: Moore-Garg Strain Index
- **Exported Functions/Symbols (120):** `DomainRuntime`, `ErgonomicsRuntime`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`, `ds_agent_recall_similar`, `ds_agent_reflect`, `ds_align_sequences_nw`, `ds_amortize_loan`, `ds_audio_filter_lowpass`, `ds_audit_safety`, `ds_balance_equation`, `ds_batch_stream`, `ds_beta_coefficient`...

### 2.34 Domain: `finance`
- **Primary Name:** `finance`
- **Aliases:** `quant`, `trading`, `financial_ts`
- **Description:** Quantitative Finance & Time Series indicators and backtesting
- **Registered Verbs & Patterns:**
  - `fetch_stock_prices` — Pattern: `[fetch] stock prices for {ticker:str} into {target:ident}`: Fetch historical stock price series for ticker
  - `moving_average` — Pattern: `{window:int} day (moving average|sma|ema) of {source:ident} into {target:ident}`: Compute moving average over window periods
  - `relative_strength_index` — Pattern: `[calculate] rsi of {source:ident} [over {window:int} days] into {target:ident}`: Compute Relative Strength Index (RSI)
  - `daily_returns` — Pattern: `[calculate] daily returns of {source:ident} into {target:ident}`: Calculate percentage daily returns
  - `sharpe_ratio` — Pattern: `[calculate] sharpe ratio of {source:ident} into {target:ident}`: Compute annualized Sharpe ratio
  - `backtest` — Pattern: `backtest strategy on {source:ident} into {target:ident}`: Backtest trading strategy over price history
- **Exported Functions/Symbols (183):** `AnalyticalGreeks`, `BinomialCoxRossRubinstein`, `BondConvexityAndMacaulayDuration`, `DomainIR`, `DomainRuntime`, `FinanceBacktestSpec`, `FinanceFetchSpec`, `FinanceMavSpec`, `FinancePortfolioIR`, `FinanceReturnsSpec`, `FinanceRsiSpec`, `FinanceRuntime`, `FinanceSharpeSpec`, `HestonStochasticVolatility`, `HullWhiteInterestRateTree`...

### 2.35 Domain: `forensics`
- **Primary Name:** `forensics`
- **Aliases:** `digital_forensics`, `dfir`, `artifact_analysis`
- **Description:** Digital forensics & malware triage: Magic byte identification, Shannon entropy, Base64 deobfuscation, DGA detection, and timestomping
- **Registered Verbs & Patterns:**
  - `identify` — Pattern: `identify file type by magic bytes {header:expr} into {target:ident}`: Magic bytes
  - `calculate` — Pattern: `calculate shannon entropy for data {data:expr} into {target:ident}`: Entropy
  - `check` — Pattern: `check dga domain {d:expr} into {target:ident}`: DGA detection
  - `deobfuscate` — Pattern: `deobfuscate nested base64 {data:expr} into {target:ident}`: Base64 deobfuscation
- **Exported Functions/Symbols (120):** `DomainRuntime`, `ForensicsRuntime`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`, `ds_agent_recall_similar`, `ds_agent_reflect`, `ds_align_sequences_nw`, `ds_amortize_loan`, `ds_audio_filter_lowpass`, `ds_audit_safety`, `ds_balance_equation`, `ds_batch_stream`, `ds_beta_coefficient`...

### 2.36 Domain: `game`
- **Primary Name:** `game`
- **Aliases:** `gamedev`, `rpg`
- **Description:** Tabletop dice, 2D tilemaps, A* grid navigation, and RPG combat
- **Registered Verbs & Patterns:**
  - `roll` — Pattern: `roll dice {notation:expr} into {target:ident}`: Rolls standard tabletop dice notation (e.g. '3d6 + 4')
  - `pick` — Pattern: `pick from loot table {tbl:expr} into {target:ident}`: Weighted random selection from loot drops
  - `create` — Pattern: `create tilemap with width {w:expr} and height {h:expr} into {target:ident}`: Instantiates a 2D grid tilemap
  - `find` — Pattern: `find grid path in {map:expr} from {start:expr} to {goal:expr} using a star into {target:ident}`: A* pathfinding on 2D tilemap obstacle grid
  - `create` — Pattern: `create combatant {name:expr} with hp {hp:expr} and attack {atk:expr} and defense {def:expr} into {target:ident}`: Creates an RPG combatant entity
- **Exported Functions/Symbols (168):** `ActionNode`, `BTNode`, `BehaviorTree`, `BoidsFlockingEngine`, `ConditionNode`, `DiceRollResult`, `DomainIR`, `DomainRuntime`, `GameCombatant`, `GameRuntime`, `GameTilemap`, `HexagonalGridCoordinates`, `HierarchicalFiniteStateMachineHFSM`, `InverterNode`, `JumpPointSearchGrid`...

### 2.37 Domain: `genai`
- **Primary Name:** `genai`
- **Aliases:** `generative_ai`, `llm`, `embeddings`
- **Description:** GenAI, LLMs & RAG: Vector search, chunking, BM25, RRF, prompt safety, ROUGE/BLEU, Attention, RoPE, BPE
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate cosine similarity between {v1:expr} and {v2:expr} into {target:ident}`: Cosine similarity
  - `fuse` — Pattern: `fuse rankings for lists {lists:expr} into {target:ident}`: RRF rank fusion
  - `check` — Pattern: `check prompt injection for text {text:expr} into {target:ident}`: Prompt injection detection
  - `redact` — Pattern: `redact pii in text {text:expr} into {target:ident}`: PII redaction
  - `calculate` — Pattern: `calculate kv memory for layers {l:expr} heads {h:expr} dim {d:expr} seq {seq:expr} into {target:ident}`: KV cache memory calculation
  - `sample` — Pattern: `sample logits {logits:expr} with temperature {temp:expr} into {target:ident}`: Logits sampling
  - `retrieve` — Pattern: `retrieve top {k:expr} chunks from {chunks:expr} for query {query:expr} into {target:ident}`: Vector retrieval
  - `train` — Pattern: `train bpe for corpus {corpus:expr} merges {n:expr} into {target:ident}`: BPE training
- **Exported Functions/Symbols (146):** `DomainRuntime`, `GenAIRuntime`, `GenAISemanticCache`, `PagedKVCacheManager`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`, `ds_agent_recall_similar`, `ds_agent_reflect`, `ds_align_sequences_nw`, `ds_amortize_loan`, `ds_audio_filter_lowpass`, `ds_audit_safety`, `ds_balance_equation`...

### 2.38 Domain: `genomics`
- **Primary Name:** `genomics`
- **Aliases:** `dna`, `rna`, `genomic_analysis`
- **Description:** Genomics & bioinformatics: Local/global alignment, CpG islands, melting temp, VCF parsing, BWT, and Hardy-Weinberg
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate gc content for sequence {seq:expr} into {target:ident}`: GC content
  - `align` — Pattern: `align sequences local {s1:expr} and {s2:expr} into {target:ident}`: Local alignment
  - `align` — Pattern: `align sequences global {s1:expr} and {s2:expr} into {target:ident}`: Global alignment
  - `calculate` — Pattern: `calculate melting temp for sequence {seq:expr} into {target:ident}`: Melting temperature
  - `calculate` — Pattern: `calculate hardy weinberg for AA {AA:expr} Aa {Aa:expr} aa {aa:expr} into {target:ident}`: Hardy-Weinberg equilibrium test
- **Exported Functions/Symbols (131):** `DomainRuntime`, `GENETIC_CODE`, `GenomicsRuntime`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`, `ds_agent_recall_similar`, `ds_agent_reflect`, `ds_align_sequences_nw`, `ds_amortize_loan`, `ds_audio_filter_lowpass`, `ds_audit_safety`, `ds_balance_equation`, `ds_batch_stream`...

### 2.39 Domain: `geo`
- **Primary Name:** `geo`
- **Aliases:** `geospatial`, `spatial`, `gis`
- **Description:** Geospatial operations, geodesic distances, polygon containment, spatial joins, and GeoJSON
- **Registered Verbs & Patterns:**
  - `point` — Pattern: `point at lat {lat:expr} and lon {lon:expr} into {target:ident}`: Create coordinate point object
  - `polygon` — Pattern: `polygon from {coords:expr} into {target:ident}`: Create 2D geographic polygon from vertex list
  - `distance_between` — Pattern: `distance between {p1:ident} and {p2:ident} [in (km|miles|meters)] into {target:ident}`: Compute Great-Circle / Haversine distance between two coordinates
  - `point_in_polygon` — Pattern: `is {pt:ident} inside {poly:ident} into {target:ident}`: Test point-in-polygon ray-casting containment
  - `bounding_box` — Pattern: `bounding box of {geom:ident} into {target:ident}`: Compute minimum bounding envelope for geometry
  - `spatial_join` — Pattern: `spatial join {points:ident} and {polys:ident} into {target:ident}`: Relational spatial join between points and polygon boundaries
  - `to_geojson` — Pattern: `convert {geom:ident} to geojson into {target:ident}`: Export geometry to RFC 7946 GeoJSON format
- **Exported Functions/Symbols (186):** `DelaunayTriangulator`, `DomainIR`, `DomainRuntime`, `DouglasPeuckerSimplifier`, `EARTH_RADIUS_KM`, `GeoBoundingBoxSpec`, `GeoContainmentSpec`, `GeoDistanceSpec`, `GeoPointSpec`, `GeoPolygonSpec`, `GeoRuntime`, `GeoSpatialJoinSpec`, `GeohashSpatialEncoder`, `IsochroneContour`, `KrigingSpatialInterpolator`...

### 2.40 Domain: `geophysics`
- **Primary Name:** `geophysics`
- **Aliases:** `seismology`, `earth_physics`, `geodynamics`
- **Description:** Deepened Geophysics domain: Epicentral distance, Richter/Moment magnitude, seismic refraction, Bouguer anomaly, geomagnetic dipole, and apparent resistivity
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate epicentral distance for p arrival {tp:expr} s arrival {ts:expr} into {target:ident}`: Wadati epicentral distance
  - `calculate` — Pattern: `calculate richter magnitude amplitude {a:expr} distance {d:expr} into {target:ident}`: Richter magnitude ML
  - `calculate` — Pattern: `calculate moment magnitude area {a:expr} slip {s:expr} into {target:ident}`: Moment magnitude Mw
  - `calculate` — Pattern: `calculate seismic refraction angle {inc:expr} v1 {v1:expr} v2 {v2:expr} into {target:ident}`: Seismic Snell refraction
  - `calculate` — Pattern: `calculate bouguer anomaly obs {obs:expr} theo {theo:expr} elevation {h:expr} density {rho:expr} into {target:ident}`: Simple Bouguer anomaly
  - `calculate` — Pattern: `calculate apparent resistivity spacing {a:expr} resistance {r:expr} into {target:ident}`: Wenner apparent resistivity
  - `calculate` — Pattern: `calculate geothermal heat flow conductivity {k:expr} gradient {g:expr} into {target:ident}`: Terrestrial geothermal heat flow
- **Exported Functions/Symbols (123):** `DomainRuntime`, `GeophysicsRuntime`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`, `ds_agent_recall_similar`, `ds_agent_reflect`, `ds_align_sequences_nw`, `ds_amortize_loan`, `ds_audio_filter_lowpass`, `ds_audit_safety`, `ds_balance_equation`, `ds_batch_stream`, `ds_beta_coefficient`...

### 2.41 Domain: `graph`
- **Primary Name:** `graph`
- **Aliases:** `network`, `graph_theory`
- **Description:** Graph Analytics, shortest paths, PageRank, degree centrality, community detection
- **Registered Verbs & Patterns:**
  - `create_graph` — Pattern: `create (graph|directed graph|undirected graph) into {target:ident}`: Create an empty directed or undirected graph
  - `add_node` — Pattern: `add node {node_id:expr} to [graph] {g_var:ident}`: Add node vertex to graph
  - `connect_nodes` — Pattern: `connect [node] {u:expr} to [node] {v:expr} in [graph] {g_var:ident} [with weight {w:expr}]`: Add directed or undirected edge between two nodes
  - `shortest_path` — Pattern: `shortest path from {u:expr} to {v:expr} in [graph] {g_var:ident} into {target:ident}`: Compute Dijkstra / BFS shortest path node sequence
  - `pagerank` — Pattern: `pagerank of [graph] {g_var:ident} into {target:ident}`: Compute Google PageRank centrality for all nodes
  - `degrees` — Pattern: `degrees of nodes in [graph] {g_var:ident} into {target:ident}`: Compute degree distribution of graph
  - `communities` — Pattern: `detect communities in [graph] {g_var:ident} into {target:ident}`: Partition network into Louvain community clusters
- **Exported Functions/Symbols (195):** `BronKerboschMaximalCliques`, `DinicMaxFlow`, `DomainIR`, `DomainRuntime`, `DoomGraph`, `EdmondsBlossomMaximumWeightMatching`, `EdmondsKarpMaxFlow`, `GraphAddEdgeSpec`, `GraphAddNodeSpec`, `GraphCommunitiesSpec`, `GraphCreateSpec`, `GraphDegreesSpec`, `GraphPageRankSpec`, `GraphRuntime`, `GraphShortestPathSpec`...

### 2.42 Domain: `graphics`
- **Primary Name:** `graphics`
- **Aliases:** `rendering`, `framebuffer`, `rasterizer`, `draw`
- **Description:** Pure Python software rendering, 2D/3D rasterization, framebuffers, and BMP/PPM export
- **Registered Verbs & Patterns:**
  - `create` — Pattern: `create framebuffer {w:expr} by {h:expr} into {target:ident}`: Allocates 2D RGBA pixel buffer
  - `draw` — Pattern: `draw line on {fb:ident} from {x0:expr}, {y0:expr} to {x1:expr}, {y1:expr} with color {color:expr}`: Draws 2D Bresenham line
  - `draw` — Pattern: `draw circle on {fb:ident} at {cx:expr}, {cy:expr} radius {r:expr} with color {color:expr}`: Draws 2D midpoint circle
- **Exported Functions/Symbols (143):** `BilinearTextureMapper`, `BlinnPhongShader`, `BresenhamWuAntiAliasedLine`, `DepthBuffer`, `DomainContract`, `DomainIR`, `DomainRuntime`, `FrameBuffer`, `GRAPHICS_DOMAIN`, `GraphicsASTExporter`, `GraphicsDomain`, `GraphicsDomainParser`, `GraphicsRuntime`, `PolygonScanlineActiveEdgeTableRasterizer`, `Rasterizer2D`...

### 2.43 Domain: `hydrology`
- **Primary Name:** `hydrology`
- **Aliases:** `water`, `fluid_mechanics`, `open_channel`
- **Description:** Deepened Hydrology domain: Manning open channel, Darcy-Weisbach head loss, hydraulic jumps, Theis aquifer drawdown, SCS curve numbers, and Muskingum flood routing
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate manning flow for roughness {n:expr} area {a:expr} radius {r:expr} slope {s:expr} into {target:ident}`: Manning flow rate
  - `calculate` — Pattern: `calculate peak runoff c {c:expr} intensity {i:expr} area {a:expr} into {target:ident}`: Rational peak runoff
  - `calculate` — Pattern: `calculate darcy weisbach head loss friction {f:expr} length {l:expr} diameter {d:expr} velocity {v:expr} into {target:ident}`: Darcy-Weisbach friction head loss
  - `calculate` — Pattern: `calculate reynolds number velocity {v:expr} diameter {d:expr} into {target:ident}`: Reynolds number
  - `calculate` — Pattern: `calculate hydraulic jump for depth {y:expr} velocity {v:expr} into {target:ident}`: Open channel hydraulic jump
  - `calculate` — Pattern: `calculate theis drawdown discharge {q:expr} transmissivity {t:expr} storativity {s:expr} radius {r:expr} time {time:expr} into {target:ident}`: Theis well drawdown
  - `calculate` — Pattern: `calculate scs runoff curve cn {cn:expr} precipitation {p:expr} into {target:ident}`: SCS runoff curve number
  - `calculate` — Pattern: `calculate evapotranspiration rn {rn:expr} temp {t:expr} wind {w:expr} humidity {rh:expr} into {target:ident}`: FAO Penman-Monteith evapotranspiration
- **Exported Functions/Symbols (122):** `DomainRuntime`, `HydrologyRuntime`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`, `ds_agent_recall_similar`, `ds_agent_reflect`, `ds_align_sequences_nw`, `ds_amortize_loan`, `ds_audio_filter_lowpass`, `ds_audit_safety`, `ds_balance_equation`, `ds_batch_stream`, `ds_beta_coefficient`...

### 2.44 Domain: `image`
- **Primary Name:** `image`
- **Aliases:** `vision`, `media`, `img`
- **Description:** Image processing, resizing, cropping, rotation, filters, and formats
- **Registered Verbs & Patterns:**
  - `open_image` — Pattern: `open image {path_expr:expr} into {target:ident}`: Open and decode bitmap or vector image from disk
  - `create_blank_image` — Pattern: `create blank image of {width:int} by {height:int} [with color {color:expr}] into {target:ident}`: Create new empty raster canvas
  - `resize_image` — Pattern: `resize image {img_var:ident} to {width:int} by {height:int} into {target:ident}`: Scale image dimensions using bilinear interpolation
  - `crop_image` — Pattern: `crop image {img_var:ident} to {coords:expr} into {target:ident}`: Crop bounding box rectangle from image
  - `rotate_image` — Pattern: `rotate image {img_var:ident} by {deg:expr} [degrees] into {target:ident}`: Rotate image clockwise by angle degrees
  - `apply_filter` — Pattern: `apply (grayscale|blur|sharpen) to [image] {img_var:ident} into {target:ident}`: Apply convolution or color transform filter
  - `save_image` — Pattern: `save image {img_var:ident} to {path:expr}`: Write encoded image to disk as PNG or JPEG
- **Exported Functions/Symbols (192):** `BicubicImageResampler`, `CannyEdgeDetectorPure`, `ColorQuantizer`, `DomainIR`, `DomainRuntime`, `DoomImage`, `FASTCornerAndHarrisDetector`, `GeometricWarp`, `HAS_PIL`, `HarrisCornerDetectorPure`, `HoughResult`, `HoughTransformCircles`, `HoughTransformLineDetector`, `ImageCreateSpec`, `ImageCropSpec`...

### 2.45 Domain: `linguistics`
- **Primary Name:** `linguistics`
- **Aliases:** `nlp_metrics`, `text_linguistics`, `readability`
- **Description:** Computational linguistics: Levenshtein, Jaro-Winkler, Soundex, Metaphone, Flesch, Gunning Fog, TTR, Porter stemmer, and CYK
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate edit distance for word1 {w1:expr} word2 {w2:expr} into {target:ident}`: Edit distance
  - `calculate` — Pattern: `calculate jaro winkler for word1 {w1:expr} word2 {w2:expr} into {target:ident}`: Jaro-Winkler
  - `calculate` — Pattern: `calculate gunning fog for text {text:expr} into {target:ident}`: Gunning Fog
  - `calculate` — Pattern: `calculate soundex for word {w:expr} into {target:ident}`: Soundex phonetic hash
  - `stem` — Pattern: `stem word {w:expr} into {target:ident}`: Porter stemming
- **Exported Functions/Symbols (127):** `DomainRuntime`, `LinguisticsRuntime`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`, `ds_agent_recall_similar`, `ds_agent_reflect`, `ds_align_sequences_nw`, `ds_amortize_loan`, `ds_audio_filter_lowpass`, `ds_audit_safety`, `ds_balance_equation`, `ds_batch_stream`, `ds_beta_coefficient`...

### 2.46 Domain: `logistics`
- **Primary Name:** `logistics`
- **Aliases:** `supply_chain`, `inventory`, `warehouse`
- **Description:** Supply chain & logistics: EOQ, ROP, safety stock, Newsvendor model, bullwhip effect, TSP, COG, and ABC analysis
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate economic order quantity for demand {d:expr} order cost {s:expr} holding cost {h:expr} into {target:ident}`: EOQ formula
  - `calculate` — Pattern: `calculate reorder point for lead time {lt:expr} daily demand {d:expr} into {target:ident}`: Reorder point
  - `solve` — Pattern: `solve tsp nearest neighbor for matrix {m:expr} into {target:ident}`: TSP solver
  - `calculate` — Pattern: `calculate safety stock for z {z:expr} std {std:expr} lead time {lt:expr} into {target:ident}`: Safety stock
  - `calculate` — Pattern: `calculate bullwhip effect for orders {o:expr} demand {d:expr} into {target:ident}`: Bullwhip effect
- **Exported Functions/Symbols (122):** `DomainRuntime`, `LogisticsRuntime`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`, `ds_agent_recall_similar`, `ds_agent_reflect`, `ds_align_sequences_nw`, `ds_amortize_loan`, `ds_audio_filter_lowpass`, `ds_audit_safety`, `ds_balance_equation`, `ds_batch_stream`, `ds_beta_coefficient`...

### 2.47 Domain: `materials`
- **Primary Name:** `materials`
- **Aliases:** `mechanics_of_materials`, `solid_mechanics`, `stress_strain`
- **Description:** Materials science & solid mechanics: Stress-strain, Mohr's circle, fracture mechanics, composites, yield criteria, and hardness.
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate engineering stress and strain for force {f:expr} area {a:expr} delta {dl:expr} initial length {l0:expr} into {target:ident}`: Calculates stress, strain, and Young's modulus
  - `calculate` — Pattern: `calculate mohrs circle principal stresses for sigma x {sx:expr} sigma y {sy:expr} tau {txy:expr} into {target:ident}`: Calculates Mohr's circle principal stresses
  - `calculate` — Pattern: `calculate thermal expansion for length {l:expr} coeff {alpha:expr} delta temp {dt:expr} into {target:ident}`: Calculates linear thermal expansion
  - `calculate` — Pattern: `calculate stress intensity for stress {s:expr} crack {a:expr} into {target:ident}`: Calculates Mode I stress intensity factor K_I
  - `calculate` — Pattern: `calculate composite modulus fiber {ef:expr} matrix {em:expr} fraction {vf:expr} into {target:ident}`: Calculates Voigt and Reuss composite modulus
  - `evaluate` — Pattern: `evaluate yield criteria s1 {s1:expr} s2 {s2:expr} s3 {s3:expr} sy {sy:expr} into {target:ident}`: Evaluates Tresca and von Mises yield criteria
  - `calculate` — Pattern: `calculate ramberg osgood stress {s:expr} modulus {e:expr} alpha {a:expr} sigma0 {s0:expr} n {n:expr} into {target:ident}`: Calculates Ramberg-Osgood nonlinear elastoplastic strain
  - `calculate` — Pattern: `calculate johnson cook strain {ep:expr} rate {edot:expr} temp {t:expr} a {a:expr} b {b:expr} n {n:expr} c {c:expr} m {m:expr} into {target:ident}`: Calculates dynamic viscoplastic flow stress
  - `calculate` — Pattern: `calculate dbtt temps {t:expr} energies {e:expr} into {target:ident}`: Fits Charpy transition temperature
  - `calculate` — Pattern: `calculate halpin tsai fiber {ef:expr} matrix {em:expr} fraction {vf:expr} aspect {ar:expr} into {target:ident}`: Calculates Halpin-Tsai short fiber modulus
  - `convert` — Pattern: `convert hardness hb {hb:expr} into {target:ident}`: Converts Brinell hardness to HV, HRC, and UTS
- **Exported Functions/Symbols (124):** `DomainRuntime`, `MaterialsRuntime`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`, `ds_agent_recall_similar`, `ds_agent_reflect`, `ds_align_sequences_nw`, `ds_amortize_loan`, `ds_audio_filter_lowpass`, `ds_audit_safety`, `ds_balance_equation`, `ds_batch_stream`, `ds_beta_coefficient`...

### 2.48 Domain: `math3d`
- **Primary Name:** `math3d`
- **Aliases:** `3d`, `vector3d`, `linear_algebra`
- **Description:** 3D linear algebra, matrices, quaternions, ray tracing, and SDF raymarching
- **Registered Verbs & Patterns:**
  - `create` — Pattern: `create vector3 with x {x:expr} and y {y:expr} and z {z:expr} into {target:ident}`: Creates a 3D vector
  - `calculate` — Pattern: `calculate cross product of {v1:expr} and {v2:expr} into {target:ident}`: Calculates 3D cross product
  - `calculate` — Pattern: `calculate dot product of {v1:expr} and {v2:expr} into {target:ident}`: Calculates 3D dot product
  - `normalize` — Pattern: `normalize vector {v:expr} into {target:ident}`: Normalizes vector to unit length
  - `create` — Pattern: `create look at matrix from {eye:expr} to {target_pt:expr} with up {up:expr} into {target:ident}`: Creates camera view matrix
  - `create` — Pattern: `create perspective matrix with fov {fov:expr} and aspect {asp:expr} and near {znear:expr} and far {zfar:expr} into {target:ident}`: Creates perspective projection matrix
  - `slerp` — Pattern: `slerp quaternion {q1:expr} and {q2:expr} with t {t:expr} into {target:ident}`: Spherical linear interpolation between quaternions
  - `intersect` — Pattern: `intersect ray {ray:expr} with sphere at {center:expr} and radius {r:expr} into {target:ident}`: Calculates ray-sphere intersection
- **Exported Functions/Symbols (169):** `BvhSpatialTree`, `DomainASTExporter`, `DomainContract`, `DomainIR`, `DomainParser`, `DomainRuntime`, `DualQuaternion`, `DualQuaternionScLERP`, `DualQuaternionTransform`, `FrustumCuller3D`, `GJKCollision3DAndEPA`, `MATH3D_DOMAIN`, `Mat4`, `Math3DASTExporter`, `Math3DDomain`...

### 2.49 Domain: `metallurgy`
- **Primary Name:** `metallurgy`
- **Aliases:** `metal`, `alloys`, `materials_science`
- **Description:** Deepened Metallurgy domain: Hall-Petch strength, Hollomon strain hardening, Lever rule, Scheil solidification, JMAK recrystallization, and martensitic transformations
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate hall petch strength friction {s0:expr} locking {ky:expr} grain {d:expr} into {target:ident}`: Hall-Petch grain boundary strengthening
  - `calculate` — Pattern: `calculate hollomon true stress k {k:expr} strain {eps:expr} n {n:expr} into {target:ident}`: Hollomon strain hardening law
  - `calculate` — Pattern: `calculate lever rule overall {c0:expr} alpha {ca:expr} beta {cb:expr} into {target:ident}`: Binary lever rule phase fractions
  - `calculate` — Pattern: `calculate scheil composition initial {c0:expr} partition {k:expr} solid {fs:expr} into {target:ident}`: Scheil non-equilibrium solidification
  - `calculate` — Pattern: `calculate jmak recrystallization time {t:expr} k {k:expr} exponent {n:expr} into {target:ident}`: JMAK recrystallization kinetics
  - `calculate` — Pattern: `calculate arrhenius diffusion d0 {d0:expr} q {q:expr} temp {t:expr} into {target:ident}`: Arrhenius atomic diffusion coefficient
- **Exported Functions/Symbols (122):** `DomainRuntime`, `MetallurgyRuntime`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`, `ds_agent_recall_similar`, `ds_agent_reflect`, `ds_align_sequences_nw`, `ds_amortize_loan`, `ds_audio_filter_lowpass`, `ds_audit_safety`, `ds_balance_equation`, `ds_batch_stream`, `ds_beta_coefficient`...

### 2.50 Domain: `metrics`
- **Primary Name:** `metrics`
- **Aliases:** `telemetry`, `prometheus`, `observability`, `metric_stats`, `kpi_stats`
- **Description:** Prometheus-compatible counters, gauges, histograms, quantiles, and OpenMetrics plaintext export
- **Registered Verbs & Patterns:**
  - `create` — Pattern: `create counter {name:expr} into {target:ident}`: Creates or retrieves a monotonic counter
  - `create` — Pattern: `create gauge {name:expr} into {target:ident}`: Creates or retrieves a gauge metric
  - `export` — Pattern: `export openmetrics into {target:ident}`: Exports all registered metrics to OpenMetrics format
- **Exported Functions/Symbols (153):** `ConfusionMatrixMultiClassMetrics`, `Counter`, `DomainContract`, `DomainIR`, `DomainRuntime`, `EWMAAnomalyDetector`, `ExponentialDecayReservoir`, `Gauge`, `Histogram`, `KernelDensityEstimator1D`, `KolmogorovSmirnovTwoSample`, `METRICS_DOMAIN`, `MetricsASTExporter`, `MetricsDomain`, `MetricsDomainParser`...

### 2.51 Domain: `microecon`
- **Primary Name:** `microecon`
- **Aliases:** `microeconomics`, `supply_demand`, `welfare_economics`
- **Description:** Microeconomics: Price elasticity, welfare surplus, deadweight loss, Gini coefficient, Cournot & Bertrand duopolies, Cobb-Douglas optimization, and game theory
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate price elasticity for q1 {q1:expr} q2 {q2:expr} p1 {p1:expr} p2 {p2:expr} into {target:ident}`: Price elasticity of demand
  - `calculate` — Pattern: `calculate surplus for p_max {p_max:expr} p_min {p_min:expr} price {p:expr} quantity {q:expr} into {target:ident}`: Consumer and producer surplus
  - `calculate` — Pattern: `calculate deadweight loss for tax {tax:expr} quantity reduction {dq:expr} into {target:ident}`: Harberger deadweight loss triangle
  - `calculate` — Pattern: `calculate gini coefficient for incomes {inc:expr} into {target:ident}`: Gini inequality coefficient
  - `calculate` — Pattern: `calculate cournot duopoly demand intercept {a:expr} slope {b:expr} marginal cost {c:expr} into {target:ident}`: Cournot duopoly equilibrium
  - `calculate` — Pattern: `calculate hhi for shares {shares:expr} into {target:ident}`: Herfindahl-Hirschman market concentration index
  - `calculate` — Pattern: `calculate cobb douglas optimal income {inc:expr} px {px:expr} py {py:expr} alpha {a:expr} beta {b:expr} into {target:ident}`: Utility-maximizing consumption bundle
  - `calculate` — Pattern: `calculate bertrand duopoly demand intercept {a:expr} slope {b:expr} mc1 {c1:expr} mc2 {c2:expr} into {target:ident}`: Bertrand price competition equilibrium
  - `calculate` — Pattern: `calculate monopoly optimum demand intercept {a:expr} slope {b:expr} marginal cost {mc:expr} into {target:ident}`: Monopoly profit-maximizing price and quantity
  - `calculate` — Pattern: `calculate cross elasticity q1 {q1:expr} q2 {q2:expr} p1 {p1:expr} p2 {p2:expr} into {target:ident}`: Cross-price elasticity of demand
  - `find` — Pattern: `find nash equilibrium row {row:expr} col {col:expr} into {target:ident}`: Pure strategy Nash equilibria in 2x2 game
  - `calculate` — Pattern: `calculate income elasticity q1 {q1:expr} q2 {q2:expr} inc1 {i1:expr} inc2 {i2:expr} into {target:ident}`: Income elasticity of demand
- **Exported Functions/Symbols (125):** `DomainRuntime`, `MicroeconRuntime`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`, `ds_agent_recall_similar`, `ds_agent_reflect`, `ds_align_sequences_nw`, `ds_amortize_loan`, `ds_audio_filter_lowpass`, `ds_audit_safety`, `ds_balance_equation`, `ds_batch_stream`, `ds_beta_coefficient`...

### 2.52 Domain: `ml`
- **Primary Name:** `ml`
- **Aliases:** `machine_learning`, `models`
- **Description:** Machine Learning classification, regression, evaluation, and cross-validation
- **Registered Verbs & Patterns:**
  - `train_model` — Pattern: `train [model] {m_var:ident} on {dataset:ident} into {target:ident}`: Train ML model weights on supervised tabular dataset
  - `evaluate_model` — Pattern: `evaluate [model] {m_var:ident} on {dataset:ident} into {target:ident}`: Evaluate model accuracy, precision, recall, and loss
  - `predict_model` — Pattern: `predict with [model] {m_var:ident} on {features:expr} into {target:ident}`: Generate predictions for unseen input features
  - `inspect_model` — Pattern: `inspect model {m_var:ident} [into {target:ident}]`: Inspect model architecture, hyper-parameters, and learned coefficients
  - `cross_validate` — Pattern: `cross validate [model] {m_var:ident} on {dataset:ident} [with {folds:int} folds] into {target:ident}`: Perform K-fold cross validation
  - `save_model` — Pattern: `save model {m_var:ident} to {path:expr}`: Serialize trained model weights to disk
  - `load_model` — Pattern: `load model from {path:expr} into {target:ident}`: Load serialized model from disk
- **Exported Functions/Symbols (200):** `AutoencoderNeuralNetwork`, `CARTDecisionTree`, `DBSCANClusteringEngine`, `DomainIR`, `DomainRuntime`, `EvaluationReport`, `GBDTModel`, `GaussianMixtureModelEM`, `GradientBoostedTreesExact`, `IsolationForestAnomalyDetector`, `IsolationForestModel`, `IsolationTreeNode`, `KMeansPlusPlus`, `LinearSVM`, `MLModelRuntime`...

### 2.53 Domain: `net`
- **Primary Name:** `net`
- **Aliases:** `web_api`, `http_api`
- **Description:** HTTP networking, REST APIs, JSON parsing, and response validation
- **Registered Verbs & Patterns:**
  - `http_request` — Pattern: `(get|post|put|delete|patch) {url:expr} [with {params:expr}] into {target:ident}`: Execute HTTP request to endpoint
  - `inspect_response` — Pattern: `inspect response {resp:ident} [into {target:ident}]`: Inspect HTTP status code, headers, and payload size
  - `parse_response` — Pattern: `parse [response] {resp:ident} as (json|text|html) into {target:ident}`: Parse HTTP response body into Record or string
  - `save_response` — Pattern: `save response {resp:ident} to {path:expr}`: Save response payload to local file
- **Exported Functions/Symbols (182):** `ApiWorkflowSpec`, `BGP4PathVectorSimulator`, `BGPPathVectorRouter`, `CIDRPrefixTrie`, `CIDRPrefixTrieNode`, `DNSWireProtocol`, `DiffServTokenBucketPolicer`, `DijkstraLinkStateOSPF`, `DomainIR`, `DomainRuntime`, `HTTP2FrameParser`, `HttpResponseContainer`, `NetRuntime`, `PacketDissector`, `ParseStep`...

### 2.54 Domain: `neuro`
- **Primary Name:** `neuro`
- **Aliases:** `neuroscience`, `snn`, `spiking`, `lif`, `stdp`
- **Description:** Leaky Integrate-and-Fire neurons, Izhikevich dynamics, STDP synaptic plasticity, and Poisson spike trains
- **Registered Verbs & Patterns:**
  - `create` — Pattern: `create lif neuron into {target:ident}`: Instantiates biological Leaky Integrate-and-Fire neuron
  - `generate` — Pattern: `generate poisson spikes with rate {rate:expr} duration {dur:expr} into {target:ident}`: Generates stochastic Poisson point-process spike train
  - `apply` — Pattern: `apply stdp to weight {w:expr} with delta t {dt:expr} into {target:ident}`: Updates synaptic weight using Spike-Timing-Dependent Plasticity
- **Exported Functions/Symbols (156):** `AdaptiveExponentialAdExNeuron`, `BienenstockCooperMunroBCM`, `ContinuousAttractorNeuralNetworkCANN`, `DomainContract`, `DomainIR`, `DomainRuntime`, `EEGBandpowerAnalyzer`, `FitzHughNagumoNeuron`, `FitzHughNagumoSimulator`, `HodgkinHuxleyNeuron`, `HopfieldNetworkAssociativeMemory`, `IzhikevichNeuron`, `LIFNeuron`, `LiquidStateMachineLSM`, `NEURO_DOMAIN`...

### 2.55 Domain: `nlp`
- **Primary Name:** `nlp`
- **Aliases:** `text`, `text_analytics`
- **Description:** Natural Language Processing, tokenization, sentiment analysis, TF-IDF, named entity recognition
- **Registered Verbs & Patterns:**
  - `clean_text` — Pattern: `clean [text] {text_expr:expr} into {target:ident}`: Normalize case, remove punctuation, and strip whitespace
  - `tokenize` — Pattern: `tokenize {text_expr:expr} into {target:ident}`: Tokenize string into list of word tokens
  - `ngrams` — Pattern: `(bigrams|trigrams) of {text_expr:expr} into {target:ident}`: Extract consecutive N-gram word tuples
  - `sentiment` — Pattern: `[analyze] sentiment of {text_expr:expr} into {target:ident}`: Compute polarity score and sentiment label
  - `tfidf` — Pattern: `[calculate] tfidf of {corpus_expr:expr} into {target:ident}`: Compute Term Frequency - Inverse Document Frequency matrix
  - `entities` — Pattern: `entities in {text_expr:expr} into {target:ident}`: Extract named entities (people, places, dates)
- **Exported Functions/Symbols (178):** `BM25OkapiInformationRetrieval`, `BPETokenizer`, `BytePairEncoder`, `CYKProbabilisticContextFreeGrammarPCFG`, `DomainIR`, `DomainRuntime`, `ENGLISH_STOPWORDS`, `HMMPOSTagger`, `KneserNeyLanguageModel`, `LevenshteinAutomatonFuzzyMatcher`, `NEGATION_WORDS`, `NEGATIVE_WORDS`, `NLPCleanSpec`, `NLPEntitiesSpec`, `NLPNgramSpec`...

### 2.56 Domain: `nuclear`
- **Primary Name:** `nuclear`
- **Aliases:** `radioactive`, `atomic`, `radiation_physics`
- **Description:** Radioactive decay, reactor kinetics, radiation protection, and nuclear reactions.
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate radioactive decay initial {a0:expr} halflife {hl:expr} time {t:expr} into {target:ident}`: Calculates remaining radioactive activity
  - `calculate` — Pattern: `calculate decay constant halflife {hl:expr} into {target:ident}`: Calculates decay constant lambda
  - `calculate` — Pattern: `calculate nuclear q value mass_in {mi:expr} mass_out {mf:expr} into {target:ident}`: Calculates nuclear reaction Q-value in MeV
  - `calculate` — Pattern: `calculate radiation shielding initial {i0:expr} attenuation {mu:expr} thickness {x:expr} into {target:ident}`: Calculates transmitted radiation through shielding
  - `calculate` — Pattern: `calculate four factor eta {eta:expr} epsilon {eps:expr} p {p:expr} f {f:expr} into {target:ident}`: Calculates Fermi four-factor k_inf
  - `calculate` — Pattern: `calculate half value layer attenuation {mu:expr} into {target:ident}`: Calculates radiation Half-Value Layer in cm
  - `calculate` — Pattern: `calculate critical slab d {d:expr} sigma_a {sa:expr} nu_sigma_f {nsf:expr} into {target:ident}`: Calculates critical slab reactor thickness
  - `calculate` — Pattern: `calculate inhour period prompt {l:expr} beta {b:expr} lambda {lam:expr} rho {rho:expr} into {target:ident}`: Calculates reactor period using the inhour relation
  - `calculate` — Pattern: `calculate secular equilibrium t_parent {t1:expr} t_daughter {t2:expr} activity {a1:expr} time {t:expr} into {target:ident}`: Calculates Bateman parent-daughter decay activities
  - `calculate` — Pattern: `calculate binding energy protons {z:expr} neutrons {n:expr} into {target:ident}`: Calculates Bethe-Weizsacker SEMF binding energy
  - `calculate` — Pattern: `calculate gamma dose activity {a:expr} energy {e:expr} distance {r:expr} into {target:ident}`: Calculates gamma dose rate in air and tissue
  - `calculate` — Pattern: `calculate neutron flux power {p:expr} volume {v:expr} into {target:ident}`: Estimates reactor thermal neutron flux
- **Exported Functions/Symbols (125):** `DomainRuntime`, `NuclearRuntime`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`, `ds_agent_recall_similar`, `ds_agent_reflect`, `ds_align_sequences_nw`, `ds_amortize_loan`, `ds_audio_filter_lowpass`, `ds_audit_safety`, `ds_balance_equation`, `ds_batch_stream`, `ds_beta_coefficient`...

### 2.57 Domain: `oceanography`
- **Primary Name:** `oceanography`
- **Aliases:** `marine_science`, `ocean_dynamics`, `ocean_waves`
- **Description:** Physical oceanography, seawater thermodynamics, fluid dynamics, and wave kinematics.
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate seawater density temp {t:expr} salinity {s:expr} into {target:ident}`: Computes UNESCO equation of state seawater density
  - `calculate` — Pattern: `calculate coriolis parameter lat {lat:expr} into {target:ident}`: Computes planetary Coriolis frequency parameter f
  - `calculate` — Pattern: `calculate ocean wave speed wavelength {lam:expr} depth {d:expr} into {target:ident}`: Computes surface gravity wave phase velocity
  - `calculate` — Pattern: `calculate depth pressure depth {d:expr} into {target:ident}`: Computes hydrostatic gauge pressure at depth
  - `calculate` — Pattern: `calculate seawater sound speed temp {t:expr} salinity {s:expr} depth {d:expr} into {target:ident}`: Computes speed of sound using Mackenzie formula
  - `calculate` — Pattern: `calculate wind stress speed {u10:expr} into {target:ident}`: Computes surface wind shear stress
  - `calculate` — Pattern: `calculate ekman depth wind {u10:expr} lat {lat:expr} into {target:ident}`: Computes Ekman boundary layer depth and surface drift
  - `calculate` — Pattern: `calculate buoyancy frequency density {rho:expr} depth {z:expr} into {target:ident}`: Computes Brunt-Vaisala stratification frequency N^2
  - `calculate` — Pattern: `calculate sverdrup transport curl {c:expr} lat {lat:expr} into {target:ident}`: Computes wind-driven Sverdrup volume transport
  - `analyze` — Pattern: `analyze sound channel temp {t:expr} salinity {s:expr} depths {z:expr} into {target:ident}`: Finds SOFAR channel axis depth and acoustic ducting profile
  - `classify` — Pattern: `classify water mass temp {t:expr} salinity {s:expr} into {target:ident}`: Analyzes T-S diagram potential density and classifies water mass
  - `calculate` — Pattern: `calculate tidal form factor m2 {m2:expr} s2 {s2:expr} k1 {k1:expr} o1 {o1:expr} into {target:ident}`: Computes Courtier tidal form factor and regime
- **Exported Functions/Symbols (127):** `DomainRuntime`, `OMEGA_EARTH`, `OceanographyRuntime`, `R_EARTH`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`, `ds_agent_recall_similar`, `ds_agent_reflect`, `ds_align_sequences_nw`, `ds_amortize_loan`, `ds_audio_filter_lowpass`, `ds_audit_safety`, `ds_balance_equation`...

### 2.58 Domain: `office`
- **Primary Name:** `office`
- **Aliases:** `sheet`, `spreadsheet`, `document`, `docx`
- **Description:** Office automation for spreadsheets (.xlsx/.csv) and Word documents (.docx)
- **Registered Verbs & Patterns:**
  - `create_spreadsheet` — Pattern: `create spreadsheet into {target:ident}`: Create a new in-memory spreadsheet workbook
  - `add_row` — Pattern: `add row {row_expr:expr} to [spreadsheet] {sheet_var:ident}`: Append single row to spreadsheet
  - `add_rows` — Pattern: `add rows [from] {rows_expr:expr} to [spreadsheet] {sheet_var:ident}`: Append multiple rows or Table records to spreadsheet
  - `save_spreadsheet` — Pattern: `save spreadsheet {sheet_var:ident} to {path_expr:expr}`: Export spreadsheet workbook to .xlsx or .csv on disk
  - `create_word_document` — Pattern: `create word document into {target:ident}`: Create a new Word document
  - `add_heading` — Pattern: `add heading {text_expr:expr} to [document] {doc_var:ident} [at level {level:int}]`: Add heading section to Word document
  - `add_paragraph` — Pattern: `add paragraph {text_expr:expr} to [document] {doc_var:ident}`: Add paragraph body text to Word document
  - `save_word_document` — Pattern: `save word document {doc_var:ident} to {path_expr:expr}`: Export Word document to .docx file
- **Exported Functions/Symbols (174):** `CSVDialectSniffer`, `DomainIR`, `DomainRuntime`, `DoomDocument`, `DoomOfficeDocument`, `DoomSpreadsheet`, `DoomWordDocument`, `OfficeAddHeadingSpec`, `OfficeAddParagraphSpec`, `OfficeAddRowSpec`, `OfficeDocumentSpec`, `OfficeRuntime`, `OfficeSaveDocumentSpec`, `OfficeSaveSpreadsheetSpec`, `OfficeSpreadsheetSpec`...

### 2.59 Domain: `opt`
- **Primary Name:** `opt`
- **Aliases:** `optimization`, `operations_research`, `lp`
- **Description:** Linear programming, simplex algorithm, dual bounds, and operations research solvers
- **Registered Verbs & Patterns:**
  - `solve_lp` — Pattern: `solve [linear program] {lp_var:ident} into {target:ident}`: Solve linear programming problem using Simplex method
- **Exported Functions/Symbols (175):** `ActiveSetQuadraticProgramming`, `AdaptiveSimulatedAnnealing`, `BranchAndBoundMILP`, `CMAESContinuousOptimization`, `DifferentialEvolutionOptimizer`, `DomainIR`, `DomainRuntime`, `InteriorPointPrimalDualLP`, `LinearProgramSpec`, `NelderMeadSimplexDirectSearch`, `NelderMeadSimplexOptimizer`, `OptRuntime`, `ParticleSwarmOptimizer`, `PrimalDualInteriorPoint`, `Record`...

### 2.60 Domain: `optics`
- **Primary Name:** `optics`
- **Aliases:** `ray_optics`, `wave_optics`, `photonics`
- **Description:** Geometrical & wave optics: Snell's law, thin lenses, Fresnel reflection, Rayleigh resolution, ABCD matrices, Gaussian beams, and fiber NA
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate thin lens focal {f:expr} distance {do:expr} into {target:ident}`: Thin lens image distance
  - `calculate` — Pattern: `calculate snell refraction n1 {n1:expr} n2 {n2:expr} angle {theta:expr} into {target:ident}`: Snell refraction angle
  - `calculate` — Pattern: `calculate fresnel reflectance n1 {n1:expr} n2 {n2:expr} into {target:ident}`: Fresnel normal reflection
  - `calculate` — Pattern: `calculate rayleigh resolution wavelength {lam:expr} na {na:expr} into {target:ident}`: Rayleigh optical resolution limit
  - `calculate` — Pattern: `calculate brewster angle n1 {n1:expr} n2 {n2:expr} into {target:ident}`: Brewster polarizing angle
  - `calculate` — Pattern: `calculate fiber aperture core {n1:expr} clad {n2:expr} into {target:ident}`: Fiber numerical aperture
  - `calculate` — Pattern: `calculate gaussian beam wavelength {lam:expr} waist {w0:expr} distance {z:expr} into {target:ident}`: Gaussian beam propagation
- **Exported Functions/Symbols (127):** `DomainRuntime`, `OpticsRuntime`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`, `ds_agent_recall_similar`, `ds_agent_reflect`, `ds_align_sequences_nw`, `ds_amortize_loan`, `ds_audio_filter_lowpass`, `ds_audit_safety`, `ds_balance_equation`, `ds_batch_stream`, `ds_beta_coefficient`...

### 2.61 Domain: `petroleum`
- **Primary Name:** `petroleum`
- **Aliases:** `petro`, `oilgas`, `reservoir`
- **Description:** Petroleum & reservoir engineering: Darcy radial flow, Archie water saturation, API gravity, GOR, Standing bubble point, Arps decline, Vogel IPR, and gas Z-factor
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate darcy radial flow perm {k:expr} pay {h:expr} pres {pr:expr} pwell {pw:expr} visc {mu:expr} re {re:expr} rw {rw:expr} skin {s:expr} into {target:ident}`: Darcy radial flow
  - `calculate` — Pattern: `calculate archie water saturation phi {phi:expr} rt {rt:expr} rw {rw:expr} into {target:ident}`: Archie water saturation
  - `convert` — Pattern: `convert specific gravity {sg:expr} to api into {target:ident}`: Specific gravity to API conversion
  - `calculate` — Pattern: `calculate gas oil ratio gas {g:expr} oil {o:expr} into {target:ident}`: Gas oil ratio
  - `calculate` — Pattern: `calculate bubble point gor {gor:expr} gas_grav {gg:expr} api {api:expr} temp {t:expr} into {target:ident}`: Standing bubble point
  - `calculate` — Pattern: `calculate pseudocritical gas grav {sg:expr} into {target:ident}`: Sutton pseudocritical gas
  - `forecast` — Pattern: `forecast arps decline rate {qi:expr} nominal {d:expr} time {t:expr} b_factor {b:expr} into {target:ident}`: Arps production decline
  - `calculate` — Pattern: `calculate vogel ipr qmax {qm:expr} pres {pr:expr} pwf {pwf:expr} into {target:ident}`: Vogel inflow performance
  - `calculate` — Pattern: `calculate gas z factor ppr {ppr:expr} tpr {tpr:expr} into {target:ident}`: Gas Z factor
- **Exported Functions/Symbols (123):** `DomainRuntime`, `PetroleumRuntime`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`, `ds_agent_recall_similar`, `ds_agent_reflect`, `ds_align_sequences_nw`, `ds_amortize_loan`, `ds_audio_filter_lowpass`, `ds_audit_safety`, `ds_balance_equation`, `ds_batch_stream`, `ds_beta_coefficient`...

### 2.62 Domain: `pharmacology`
- **Primary Name:** `pharmacology`
- **Aliases:** `pharm`, `pharmacokinetics`, `pk_pd`
- **Description:** Deepened Pharmacology domain: Elimination rates, steady-state plasma concentrations, volume of distribution, Hill dose-response, Michaelis-Menten kinetics, and Cockcroft-Gault CrCl
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate elimination rate halflife {t:expr} into {target:ident}`: Elimination rate constant ke
  - `calculate` — Pattern: `calculate steady state conc dose {d:expr} bioavailability {f:expr} clearance {cl:expr} interval {tau:expr} into {target:ident}`: Average steady state concentration Css
  - `calculate` — Pattern: `calculate volume distribution dose {d:expr} c0 {c0:expr} into {target:ident}`: Apparent volume of distribution Vd
  - `calculate` — Pattern: `calculate hill response conc {c:expr} emax {emax:expr} ec50 {ec50:expr} hill {n:expr} into {target:ident}`: Hill pharmacodynamic sigmoid response
  - `calculate` — Pattern: `calculate saturable elimination vmax {vmax:expr} km {km:expr} conc {c:expr} into {target:ident}`: Michaelis-Menten elimination rate
  - `calculate` — Pattern: `calculate loading dose vd {vd:expr} target {target_c:expr} bio {f:expr} into {target:ident}`: Target loading dose
  - `calculate` — Pattern: `calculate creatinine clearance age {age:expr} weight {wt:expr} scr {scr:expr} into {target:ident}`: Cockcroft-Gault creatinine clearance
- **Exported Functions/Symbols (122):** `DomainRuntime`, `PharmacologyRuntime`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`, `ds_agent_recall_similar`, `ds_agent_reflect`, `ds_align_sequences_nw`, `ds_amortize_loan`, `ds_audio_filter_lowpass`, `ds_audit_safety`, `ds_balance_equation`, `ds_batch_stream`, `ds_beta_coefficient`...

### 2.63 Domain: `physics`
- **Primary Name:** `physics`
- **Aliases:** `kinematics`, `mechanics`
- **Description:** Physics, kinematics, ballistics, polygon collisions, and PID controls
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate trajectory with velocity {v:expr} and angle {deg:expr} into {target:ident}`: Simulates 2D ballistic trajectory points
  - `calculate` — Pattern: `calculate ballistic range with velocity {v:expr} and angle {deg:expr} into {target:ident}`: Calculates flat-ground ideal ballistic range
  - `check` — Pattern: `check collision between aabb {b1:expr} and {b2:expr} into {target:ident}`: Checks collision between two 2D Axis-Aligned Bounding Boxes
  - `check` — Pattern: `check polygon collision between {p1:expr} and {p2:expr} using sat into {target:ident}`: Separating Axis Theorem collision check for convex 2D polygons
  - `create` — Pattern: `create pid controller with kp {kp:expr} and ki {ki:expr} and kd {kd:expr} into {target:ident}`: Instantiates a PID controller
  - `update` — Pattern: `update pid {pid:expr} with setpoint {sp:expr} and measurement {m:expr} into {target:ident}`: Updates PID controller and returns output control effort
- **Exported Functions/Symbols (172):** `BarnesHutNBody`, `BarnesHutNBodySimulation`, `BarnesHutNode`, `BrachistochroneCycloidCalculator`, `ClothLatticeSimulation`, `ContinuousCollisionDetectionCCD`, `CoupledOscillatorsNormalModes`, `DomainIR`, `DomainRuntime`, `ElectromagneticFieldSolver`, `FluidSPH`, `ImpulseCollision2D`, `PhysicsPID`, `PhysicsRuntime`, `QuadTreeNode`...

### 2.64 Domain: `quantum`
- **Primary Name:** `quantum`
- **Aliases:** `quantum_computing`, `qubit`
- **Description:** Quantum computing, statevectors, unitary gates, and measurement
- **Registered Verbs & Patterns:**
  - `create` — Pattern: `create quantum register with {n:expr} qubits into {target:ident}`: Initializes a multi-qubit statevector register
  - `apply` — Pattern: `apply hadamard [gate] to qubit {q:expr} in {reg:expr}`: Applies Hadamard superposition gate
  - `apply` — Pattern: `apply cnot [gate] with control {c:expr} and target {t:expr} in {reg:expr}`: Applies Controlled-NOT two-qubit entangling gate
  - `measure` — Pattern: `measure quantum register {reg:expr} with shots {s:expr} into {target:ident}`: Samples computational basis states using Monte Carlo measurement
- **Exported Functions/Symbols (159):** `DensityMatrixSimulator`, `DomainIR`, `DomainRuntime`, `GroverSearch`, `QuantumCircuitIR`, `QuantumErrorCorrection`, `QuantumFourierTransform`, `QuantumKeyDistributionBB84`, `QuantumPhaseEstimationQPE`, `QuantumRegister`, `QuantumRuntime`, `QuantumTeleportation`, `Record`, `StabilizerTableauSimulator`, `Steane7QubitCode`...

### 2.65 Domain: `queue`
- **Primary Name:** `queue`
- **Aliases:** `queues`, `priority_queue`, `fifo`
- **Description:** Queueing & messaging: FIFO, priority queues, ring buffers, token buckets, DLQs, WFQ, and Erlang-C
- **Registered Verbs & Patterns:**
  - `create` — Pattern: `create message queue with capacity {cap:expr} into {target:ident}`: FIFO queue
  - `create` — Pattern: `create priority queue into {target:ident}`: Priority queue
  - `create` — Pattern: `create ring buffer with size {sz:expr} into {target:ident}`: Ring buffer
  - `publish` — Pattern: `publish message {msg:expr} to {q:ident}`: Publish message
  - `consume` — Pattern: `consume from queue {q:expr} into {target:ident}`: Consume message
- **Exported Functions/Symbols (133):** `DeadLetterQueue`, `DeficitRoundRobin`, `DomainRuntime`, `MessageQueue`, `PriorityMessageQueue`, `QueueRuntime`, `RingBuffer`, `TokenBucket`, `WeightedFairQueue`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`, `ds_agent_recall_similar`, `ds_agent_reflect`...

### 2.66 Domain: `research`
- **Primary Name:** `research`
- **Aliases:** `autograd`, `research_stats`, `graph_research`, `math`
- **Description:** Research mathematical toolkit, automatic differentiation, statistical distributions, and graph algorithms
- **Registered Verbs & Patterns:**
  - `gradient_of` — Pattern: `gradient of {fn_name:ident} at {x_expr:expr} into {target:ident}`: Evaluate numerical or reverse-mode automatic differentiation gradient
  - `differentiate` — Pattern: `differentiate {expr:expr} with respect to {var:ident} into {target:ident}`: Symbolic differentiation with respect to target variable
  - `simulate_distribution` — Pattern: `simulate distribution {dist:ident} with {params:expr} into {target:ident}`: Generate random variables from named distribution
  - `confidence_interval` — Pattern: `confidence interval of {data:ident} [at {level:expr}] into {target:ident}`: Compute Student-t or normal confidence intervals
- **Exported Functions/Symbols (154):** `AcademicLiteratureSynthesizer`, `BenjaminiHochbergMultipleTesting`, `BibTeXEngine`, `CitationNetwork`, `DomainContract`, `DomainIR`, `DomainParser`, `DomainRuntime`, `HIndexAndCitationBibliometrics`, `LevenbergMarquardt`, `RESEARCH_DOMAIN`, `ResearchDomain`, `ResearchDomainParser`, `ResearchGraph`, `ResearchRuntime`...

### 2.67 Domain: `risk`
- **Primary Name:** `risk`
- **Aliases:** `var`, `portfolio_risk`, `risk_analytics`
- **Description:** Quantitative financial risk: VaR, CVaR, Max Drawdown, Sharpe/Sortino/Calmar ratios, Altman Z, and Merton default
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate historical var for returns {ret:expr} confidence {conf:expr} into {target:ident}`: VaR
  - `calculate` — Pattern: `calculate max drawdown for prices {prices:expr} into {target:ident}`: Max Drawdown
  - `calculate` — Pattern: `calculate portfolio volatility weights {w:expr} covariance {cov:expr} into {target:ident}`: Portfolio Volatility
  - `calculate` — Pattern: `calculate sharpe ratio for returns {ret:expr} risk free {rf:expr} into {target:ident}`: Sharpe ratio
- **Exported Functions/Symbols (123):** `DomainRuntime`, `RiskRuntime`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`, `ds_agent_recall_similar`, `ds_agent_reflect`, `ds_align_sequences_nw`, `ds_amortize_loan`, `ds_audio_filter_lowpass`, `ds_audit_safety`, `ds_balance_equation`, `ds_batch_stream`, `ds_beta_coefficient`...

### 2.68 Domain: `robotics`
- **Primary Name:** `robotics`
- **Aliases:** `kinematics_arm`, `motion_planning`
- **Description:** Forward/Inverse kinematics, Denavit-Hartenberg parameters, trajectory planning, and Kalman filtering
- **Registered Verbs & Patterns:**
  - `move` — Pattern: `move arm to x: {x:expr}, y: {y:expr} into {target:ident}`: Computes arm joint configuration to reach Cartesian coordinate
  - `read` — Pattern: `read lidar sensor into {target:ident}`: Reads range-bearing distance scans from lidar sensor
  - `calculate` — Pattern: `calculate forward kinematics for dh parameters {params:expr} into {target:ident}`: Calculates end-effector position from DH parameter chain
  - `solve` — Pattern: `solve 2link inverse kinematics with link1 {l1:expr} and link2 {l2:expr} for target {x:expr}, {y:expr} into {target:ident}`: Solves analytical inverse kinematics for 2-link planar arm
  - `create` — Pattern: `create ekf tracker with x {x:expr} and y {y:expr} into {target:ident}`: Initializes 2D Extended Kalman Filter state estimator
- **Exported Functions/Symbols (165):** `ArtificialPotentialField2D`, `DHParameter`, `DifferentialDriveKinematics`, `DomainASTExporter`, `DomainContract`, `DomainIR`, `DomainParser`, `DomainRuntime`, `DubinsCarShortestPath`, `DynamicWindowApproachDWA`, `ExtendedKalmanFilter2D`, `ForwardKinematicsChain`, `InverseKinematics2D`, `OccupancyGridMap2D`, `PurePursuitController`...

### 2.69 Domain: `sec`
- **Primary Name:** `sec`
- **Aliases:** `security`, `crypto`
- **Description:** Cybersecurity, password entropy, cryptanalysis, JWT, and vulnerability metrics
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate password entropy for {pass:expr} into {target:ident}`: Calculates Shannon password entropy in bits
  - `audit` — Pattern: `audit password strength for {pass:expr} into {target:ident}`: Audits password strength score and resistance to cracking
  - `crack` — Pattern: `crack caesar cipher {ctx:expr} into {target:ident}`: Breaks Caesar cipher using letter frequency analysis
  - `encode` — Pattern: `encode text {txt:expr} with vigenere key {key:expr} into {target:ident}`: Encrypts text using polyalphabetic Vigenere cipher
  - `decode` — Pattern: `decode vigenere {ctx:expr} with key {key:expr} into {target:ident}`: Decrypts text using Vigenere cipher
  - `verify` — Pattern: `verify jwt token {tok:expr} with secret {sec:expr} into {target:ident}`: Verifies HMAC-SHA256 signature of a JWT token
  - `generate` — Pattern: `generate hexdump of {data:expr} into {target:ident}`: Formats binary data into canonical hexdump view
- **Exported Functions/Symbols (169):** `BlindSignatureChaumRSA`, `ChaCha20Cipher`, `DomainIR`, `DomainRuntime`, `ENGLISH_FREQS`, `MerkleTreeInclusionProof`, `PBKDF2KeyDerivationFunctionPure`, `PBKDF2KeyDeriver`, `Poly1305Authenticator`, `Record`, `SecRuntime`, `Secp256k1Curve`, `ShamirSecretSharing`, `TOTPAuthenticator`, `TOTPGenerator`...

### 2.70 Domain: `signals`
- **Primary Name:** `signals`
- **Aliases:** `dsp`, `filtering`, `wavelets`
- **Description:** Discrete Wavelet Transform, FIR/IIR filters, Hilbert transform, and peak detection
- **Registered Verbs & Patterns:**
  - `decompose` — Pattern: `decompose signal {sig:expr} using haar wavelet into {target:ident}`: Performs 1D Haar Discrete Wavelet Transform
  - `apply` — Pattern: `apply fir lowpass filter to {sig:expr} with cutoff {cut:expr} and rate {rate:expr} into {target:ident}`: Applies windowed-sinc FIR lowpass filter to signal
  - `calculate` — Pattern: `calculate analytic signal of {sig:expr} using hilbert into {target:ident}`: Computes analytic signal and amplitude envelope via Hilbert transform
  - `find` — Pattern: `find peaks in signal {sig:expr} into {target:ident}`: Detects local maxima peaks in signal
- **Exported Functions/Symbols (163):** `ButterworthIIRFilter`, `ChirpZTransformCZT`, `CooleyTukeyFFT`, `CrossCorrelation`, `DomainASTExporter`, `DomainContract`, `DomainIR`, `DomainParser`, `DomainRuntime`, `EmpiricalModeDecompositionEMD`, `FilterDesign`, `HilbertTransform`, `HilbertTransformAnalyticSignal`, `KalmanFilterEstimator`, `LevinsonDurbinLPC`...

### 2.71 Domain: `sim`
- **Primary Name:** `sim`
- **Aliases:** `simulation`, `sim_opt`
- **Description:** Simulation modeling, discrete-event queueing, Monte Carlo trials, Nelder-Mead optimization
- **Registered Verbs & Patterns:**
  - `inspect_simulation` — Pattern: `inspect simulation {s_var:ident} [into {target:ident}]`: Inspect simulated queue metrics and summary stats
  - `summarize_metric` — Pattern: `summarize [uncertainty of] {s_var:ident} [into {target:ident}]`: Compute confidence intervals and variance of trial metric
  - `sample_distribution` — Pattern: `sample {count:int} from {dist:ident} [with {params:expr}] into {target:ident}`: Generate random samples from statistical distribution
  - `optimize` — Pattern: `optimize {fn_name:ident} starting at {x0:expr} into {target:ident}`: Find minimum of objective function via Nelder-Mead simplex
  - `run_trials` — Pattern: `run {n:int} trials of {sim:ident} into {target:ident}`: Execute repeated stochastic Monte Carlo trials
  - `sweep_parameter` — Pattern: `sweep parameter {param:ident} from {start_val:expr} to {end_val:expr} [in {steps:int} steps] for {sim:ident} into {target:ident}`: Evaluate simulation performance across parameter grid
- **Exported Functions/Symbols (177):** `Agent2D`, `AgentBasedEpidemicSEIRModel`, `AgentBasedModel2D`, `CellularAutomataLatticeGasHydrodynamics`, `CellularAutomaton`, `DiscreteEventQueueEngine`, `DiscreteEventSimulation`, `DiscreteEventSimulationDESEngine`, `DomainIR`, `DomainRuntime`, `GillespieExactSSA`, `JacksonQueuingNetwork`, `MCMCSampler`, `NelderMeadOptimizer`, `OptimizationSpec`...

### 2.72 Domain: `social`
- **Primary Name:** `social`
- **Aliases:** `network_analysis`, `graph_centrality`, `sna`
- **Description:** Social network analysis: Degree, Closeness, Betweenness centrality, PageRank, HITS, and clustering
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate degree centrality for graph {g:expr} into {target:ident}`: Degree centrality
  - `calculate` — Pattern: `calculate pagerank for graph {g:expr} into {target:ident}`: PageRank algorithm
  - `calculate` — Pattern: `calculate hits for graph {g:expr} into {target:ident}`: HITS algorithm
- **Exported Functions/Symbols (124):** `DomainRuntime`, `SocialRuntime`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`, `ds_agent_recall_similar`, `ds_agent_reflect`, `ds_align_sequences_nw`, `ds_amortize_loan`, `ds_audio_filter_lowpass`, `ds_audit_safety`, `ds_balance_equation`, `ds_batch_stream`, `ds_beta_coefficient`...

### 2.73 Domain: `spatial_audio`
- **Primary Name:** `spatial_audio`
- **Aliases:** `spatialaudio`, `binaural`, `ambisonics`, `hrtf`
- **Description:** Binaural audio rendering, Woodworth ITD, First-Order Ambisonics, Doppler shifting, and Schroeder reverb
- **Registered Verbs & Patterns:**
  - `spatialize` — Pattern: `spatialize audio {sig:expr} at azimuth {az:expr} into {target:ident}`: Pans mono audio into binaural stereo channels using ITD/ILD
  - `encode` — Pattern: `encode ambisonics {sig:expr} at azimuth {az:expr} elevation {el:expr} into {target:ident}`: Encodes audio into Ambisonics B-format (W, X, Y, Z)
  - `apply` — Pattern: `apply reverb to {sig:expr} with rt60 {rt60:expr} into {target:ident}`: Applies Schroeder algorithmic reverberation
- **Exported Functions/Symbols (152):** `AcousticRayTracingShoebox`, `AcousticRaytracer`, `AmbisonicsBFormat`, `AmbisonicsBFormatBinauralDecoder`, `AtmosphericAttenuation`, `BinauralPanner`, `BinauralRoomImpulseResponseBRIRGenerator`, `ConvolveImpulseResponse`, `DomainContract`, `DomainIR`, `DomainRuntime`, `DopplerEffect`, `HRTFConvolution`, `HigherOrderAmbisonics`, `HigherOrderSphericalHarmonics3D`...

### 2.74 Domain: `structural`
- **Primary Name:** `structural`
- **Aliases:** `civil_structures`, `structural_analysis`, `beams`
- **Description:** Deepened Structural Engineering domain: Beam bending moments, elastic deflections, Euler column buckling, section modulus, Mohr principal stresses, and slenderness
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate beam max moment load {w:expr} span {l:expr} into {target:ident}`: Simply supported beam max moment
  - `calculate` — Pattern: `calculate beam max deflection load {w:expr} span {l:expr} modulus {e:expr} inertia {i:expr} into {target:ident}`: Simply supported beam max deflection
  - `calculate` — Pattern: `calculate column buckling load modulus {e:expr} inertia {i:expr} length {l:expr} factor {k:expr} into {target:ident}`: Euler critical buckling load
  - `calculate` — Pattern: `calculate section modulus width {b:expr} height {h:expr} into {target:ident}`: Rectangular section modulus
  - `calculate` — Pattern: `calculate mohr principal stresses sx {sx:expr} sy {sy:expr} txy {txy:expr} into {target:ident}`: Mohr circle principal stresses
  - `calculate` — Pattern: `calculate slenderness ratio length {l:expr} radius {r:expr} into {target:ident}`: Column slenderness ratio
- **Exported Functions/Symbols (121):** `DomainRuntime`, `StructuralRuntime`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`, `ds_agent_recall_similar`, `ds_agent_reflect`, `ds_align_sequences_nw`, `ds_amortize_loan`, `ds_audio_filter_lowpass`, `ds_audit_safety`, `ds_balance_equation`, `ds_batch_stream`, `ds_beta_coefficient`...

### 2.75 Domain: `symbolic`
- **Primary Name:** `symbolic`
- **Aliases:** `cas`, `algebra`, `calculus`, `diff`
- **Description:** Exact analytical differentiation, algebraic simplification, polynomial arithmetic, and GCD
- **Registered Verbs & Patterns:**
  - `differentiate` — Pattern: `differentiate {expr:expr} with respect to {var:ident} into {target:ident}`: Calculates exact analytical derivative using calculus rules
  - `simplify` — Pattern: `simplify expression {expr:expr} into {target:ident}`: Simplifies expression using algebraic equivalence laws
  - `evaluate` — Pattern: `evaluate expression {expr:expr} with {subs:expr} into {target:ident}`: Evaluates expression numerically with variable substitutions
- **Exported Functions/Symbols (165):** `Add`, `BrentRootFinder`, `Constant`, `Cos`, `DomainContract`, `DomainIR`, `DomainRuntime`, `ExactRationalLinearSolver`, `Exp`, `Expr`, `ExpressionParser`, `GroebnerBasisBuchberger`, `Ln`, `Mul`, `PadeApproximantGenerator`...

### 2.76 Domain: `synthetic_bio`
- **Primary Name:** `synthetic_bio`
- **Aliases:** `synbio`, `genetic_circuits`, `bio_engineering`
- **Description:** Synthetic biology: Hill kinetics, Gardner toggle switch, Repressilator, Michaelis-Menten, Gibson assembly, and CRISPR design
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate hill activation for conc {x:expr} k {k:expr} n {n:expr} into {target:ident}`: Hill activation
  - `calculate` — Pattern: `calculate enzyme rate substrate {s:expr} vmax {v:expr} km {km:expr} into {target:ident}`: Michaelis-Menten rate
  - `check` — Pattern: `check gibson overlap frag1 {f1:expr} frag2 {f2:expr} into {target:ident}`: Gibson overlap
  - `design` — Pattern: `design gibson overlap frag1 {f1:expr} frag2 {f2:expr} into {target:ident}`: Gibson overlap design
- **Exported Functions/Symbols (124):** `DomainRuntime`, `SyntheticBioRuntime`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`, `ds_agent_recall_similar`, `ds_agent_reflect`, `ds_align_sequences_nw`, `ds_amortize_loan`, `ds_audio_filter_lowpass`, `ds_audit_safety`, `ds_balance_equation`, `ds_batch_stream`, `ds_beta_coefficient`...

### 2.77 Domain: `telecom`
- **Primary Name:** `telecom`
- **Aliases:** `telecommunications`, `fec`, `ecc`, `crc`
- **Description:** Forward error correction, Hamming(7,4), CRC-32/16/8, Galois field arithmetic, and Reed-Solomon coding
- **Registered Verbs & Patterns:**
  - `encode` — Pattern: `encode bits {bits:expr} with hamming74 into {target:ident}`: Encodes bitstream using Hamming(7,4) linear block code
  - `decode` — Pattern: `decode bits {bits:expr} with hamming74 into {target:ident}`: Decodes Hamming(7,4) code bits and corrects single-bit errors
  - `calculate` — Pattern: `calculate crc32 of {data:expr} into {target:ident}`: Calculates 32-bit Ethernet CRC checksum
- **Exported Functions/Symbols (156):** `AWGNChannelSimulator`, `CRC`, `CostasLoopCarrierRecovery`, `DomainContract`, `DomainIR`, `DomainRuntime`, `ExtendedHamming84`, `GF256`, `GeneralizedCRC`, `Hamming74`, `OFDMFramer`, `OFDMModulationEngine`, `QAMModem`, `ReedSolomon`, `TELECOM_DOMAIN`...

### 2.78 Domain: `thermodynamics`
- **Primary Name:** `thermodynamics`
- **Aliases:** `heat_transfer`, `thermal_physics`, `thermo`
- **Description:** Thermodynamics & heat cycles: Carnot, Rankine, Brayton, Otto cycles, entropy change, polytropic processes, and Joule-Thomson
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate carnot efficiency hot {th:expr} cold {tc:expr} into {target:ident}`: Carnot efficiency
  - `calculate` — Pattern: `calculate entropy change mass {m:expr} specific heat {c:expr} t1 {t1:expr} t2 {t2:expr} into {target:ident}`: Entropy change
  - `step` — Pattern: `step polytropic p1 {p1:expr} v1 {v1:expr} v2 {v2:expr} index {n:expr} into {target:ident}`: Polytropic gas expansion
  - `calculate` — Pattern: `calculate rankine cycle boiler {h2:expr} turbine {h3:expr} condenser {h4:expr} pump {h1:expr} into {target:ident}`: Rankine cycle efficiency
  - `calculate` — Pattern: `calculate joule thomson drop pressure {dp:expr} coefficient {mu:expr} into {target:ident}`: Joule-Thomson temperature change
- **Exported Functions/Symbols (122):** `DomainRuntime`, `ThermodynamicsRuntime`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`, `ds_agent_recall_similar`, `ds_agent_reflect`, `ds_align_sequences_nw`, `ds_amortize_loan`, `ds_audio_filter_lowpass`, `ds_audit_safety`, `ds_balance_equation`, `ds_batch_stream`, `ds_beta_coefficient`...

### 2.79 Domain: `time_series`
- **Primary Name:** `time_series`
- **Aliases:** `timeseries`, `forecasting`, `trend`, `seasonality`
- **Description:** Classical seasonal decomposition, ACF, PACF, Holt-Winters forecasting, and differencing
- **Registered Verbs & Patterns:**
  - `decompose` — Pattern: `decompose time series {series:expr} with period {period:expr} into {target:ident}`: Decomposes series into trend, seasonal, and residual components
  - `calculate` — Pattern: `calculate acf of {series:expr} with lags {lags:expr} into {target:ident}`: Calculates sample autocorrelation function up to specified lags
  - `calculate` — Pattern: `calculate pacf of {series:expr} with lags {lags:expr} into {target:ident}`: Calculates sample partial autocorrelation function via Durbin-Levinson
- **Exported Functions/Symbols (150):** `ARIMASimulator`, `AutocorrelationAnalyzer`, `AutoregressiveModelAR`, `CUSUMDetector`, `DomainContract`, `DomainIR`, `DomainRuntime`, `DynamicTimeWarping`, `DynamicTimeWarpingSakoeChiba`, `EmpiricalModeDecompositionEMD`, `ExponentialSmoothing`, `HoltWintersSmoothing`, `KalmanFilterStateSpace`, `MultivariateVectorAutoregressionVAR`, `NaturalCubicSpline`...

### 2.80 Domain: `viz`
- **Primary Name:** `viz`
- **Aliases:** `visualization`, `charts`, `plots`, `plot`
- **Description:** Grammar of Graphics data visualization with layers, scales, themes, and facets
- **Registered Verbs & Patterns:**
  - `explore` — Pattern: `explore {dataset:ident} [to understand {focus:expr}] [into {target:ident}]`: Automated exploratory visualization and statistical insights
  - `show_plot` — Pattern: `show {target_var:ident}`: Display interactive plot figure
  - `save_plot` — Pattern: `save {target_var:ident} to {path_str:expr}`: Save plot figure to PNG, SVG, or HTML file
  - `plot` — Pattern: `plot {dataset:ident} as {geom:ident} with {params:expr} [into {target:ident}]`: Construct single-layer plot figure
- **Exported Functions/Symbols (132):** `ASCIIHistogramAndBoxPlotRenderer`, `DomainASTExporter`, `DomainContract`, `DomainIR`, `DomainParser`, `DomainRuntime`, `ForceDirectedGraphLayout2D`, `PlotBuilder`, `PlotSpec`, `Record`, `VIZ_DOMAIN`, `VerbSpec`, `VizASTExporter`, `VizDomain`, `VizDomainParser`...

### 2.81 Domain: `web`
- **Primary Name:** `web`
- **Aliases:** `crawl`, `scrape`, `browser`
- **Description:** Web scraping, DOM parsing, link extraction, HTML table parsing, and media downloading
- **Registered Verbs & Patterns:**
  - `open_webpage` — Pattern: `open webpage {url:expr} into {target:ident}`: Fetch web page over HTTP and parse DOM structure
  - `parse_html` — Pattern: `parse html {html_text:expr} into {target:ident}`: Parse raw HTML document string into queryable DOM tree
  - `webpage_title` — Pattern: `title of webpage {page_var:ident} into {target:ident}`: Extract <title> meta tag from page
  - `webpage_text` — Pattern: `text in webpage {page_var:ident} into {target:ident}`: Extract cleaned inner text from page body
  - `extract_links` — Pattern: `extract [all] links from [webpage] {page_var:ident} into {target:ident}`: Extract all resolved absolute URLs from anchor elements
  - `find_table` — Pattern: `find table {index:int} in [webpage] {page_var:ident} into {target:ident}`: Parse HTML <table> into structured Table object
  - `download_media` — Pattern: `download all (images|media) from [webpage] {page_var:ident} to {dest_folder:expr} into {target:ident}`: Download all images and media assets to local folder
- **Exported Functions/Symbols (182):** `BeautifulSoup`, `CSSSelectorEngine`, `DOMBuilder`, `DOMElement`, `DOMNode`, `DomainIR`, `DomainRuntime`, `HAS_BS4`, `HTMLDOMSelector`, `HTMLParser`, `HttpChunkedTransferCodec`, `HttpHeaderParserAndNegotiator`, `RFC6265CookieJar`, `Record`, `RobotsTxtParser`...
