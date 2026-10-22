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
- **Description:** Physical acoustics & architectural audio: SPL decibels, Sabine and Eyring RT60, Doppler shift, distance decay, and transmission loss
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate spl pressure {p:expr} into {target:ident}`: Sound pressure level (dB)
  - `calculate` — Pattern: `calculate sabine rt60 volume {v:expr} absorption {a:expr} into {target:ident}`: Sabine reverberation time
  - `calculate` — Pattern: `calculate eyring rt60 volume {v:expr} area {s:expr} absorption {a:expr} into {target:ident}`: Eyring reverberation time
  - `calculate` — Pattern: `calculate doppler shift freq {f:expr} source_v {vs:expr} into {target:ident}`: Doppler shifted frequency
  - `calculate` — Pattern: `calculate sound decay spl {spl:expr} r1 {r1:expr} r2 {r2:expr} into {target:ident}`: Distance SPL attenuation
  - `calculate` — Pattern: `calculate sound transmission loss mass {m:expr} freq {f:expr} into {target:ident}`: Sound transmission loss
- **Exported Functions/Symbols (127):** `ACOUSTICS_DOMAIN`, `AcousticsASTExporter`, `AcousticsDomain`, `AcousticsDomainParser`, `AcousticsRuntime`, `DomainContract`, `DomainRuntime`, `VerbSpec`, `acoustics_characteristic_impedance`, `acoustics_doppler_shift`, `acoustics_eyring_rt60`, `acoustics_inverse_square_decay`, `acoustics_sabine_rt60`, `acoustics_sound_transmission_loss`, `acoustics_spl_db`...

### 2.2 Domain: `actuarial`
- **Primary Name:** `actuarial`
- **Aliases:** `actuary`, `insurance_math`, `mortality`
- **Description:** Actuarial science: Gompertz and Makeham mortality laws, annuity present value, term life premium, loss reserves, and Chain Ladder development
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate gompertz mortality age {a:expr} base {b:expr} factor {c:expr} into {target:ident}`: Gompertz mortality
  - `calculate` — Pattern: `calculate makeham mortality age {a:expr} accident {acc:expr} base {b:expr} factor {c:expr} into {target:ident}`: Gompertz-Makeham mortality
  - `calculate` — Pattern: `calculate annuity present value payment {p:expr} rate {r:expr} years {n:expr} into {target:ident}`: Annuity present value
  - `calculate` — Pattern: `calculate term insurance premium benefit {b:expr} mortality {q:expr} rate {r:expr} term {n:expr} into {target:ident}`: Term insurance net single premium
  - `calculate` — Pattern: `calculate loss reserve claims {c:expr} severity {s:expr} rate {r:expr} into {target:ident}`: Loss reserve
  - `calculate` — Pattern: `calculate chain ladder losses {l:expr} ratio {r:expr} into {target:ident}`: Chain ladder ultimate loss projection
- **Exported Functions/Symbols (126):** `ACTUARIAL_DOMAIN`, `ActuarialASTExporter`, `ActuarialDomain`, `ActuarialDomainParser`, `ActuarialRuntime`, `DomainContract`, `DomainRuntime`, `VerbSpec`, `actuarial_annuity_present_value`, `actuarial_chain_ladder_projection`, `actuarial_gompertz_mortality_rate`, `actuarial_loss_reserve`, `actuarial_makeham_mortality_rate`, `actuarial_term_insurance_premium`, `ds_adsr_envelope`...

### 2.3 Domain: `aerospace`
- **Primary Name:** `aerospace`
- **Aliases:** `orbital_mechanics`, `rocketry`, `astronautics`
- **Description:** Aerospace & flight dynamics: Lift/drag, Mach number, Breguet range, orbital velocity, and Hohmann transfers
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate lift and drag for density {rho:expr} velocity {v:expr} area {a:expr} cl {cl:expr} cd {cd:expr} into {target:ident}`: Lift and drag
  - `calculate` — Pattern: `calculate orbital velocity for altitude {alt:expr} into {target:ident}`: Orbital velocity
  - `calculate` — Pattern: `calculate hohmann transfer r1 {r1:expr} r2 {r2:expr} into {target:ident}`: Hohmann transfer
- **Exported Functions/Symbols (126):** `AEROSPACE_DOMAIN`, `AerospaceASTExporter`, `AerospaceDomain`, `AerospaceDomainParser`, `AerospaceRuntime`, `DomainContract`, `DomainRuntime`, `VerbSpec`, `aero_breguet_range`, `aero_lift_drag`, `aero_mach_number`, `aerospace_hohmann_transfer`, `aerospace_kepler_orbit`, `aerospace_orbital_velocity`, `ds_adsr_envelope`...

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
- **Description:** Agronomy and soil science: crop evapotranspiration, growing degree days, fertilizer rates, cation exchange capacity, and soil porosity
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate crop water requirement et0 {et0:expr} kc {kc:expr} into {target:ident}`: Crop water requirement
  - `calculate` — Pattern: `calculate growing degree days tmax {tmax:expr} tmin {tmin:expr} tbase {tbase:expr} into {target:ident}`: Growing degree days
  - `calculate` — Pattern: `calculate fertilizer rate nutrient {n:expr} percent {p:expr} into {target:ident}`: Fertilizer application rate
  - `calculate` — Pattern: `calculate cation exchange ca {ca:expr} mg {mg:expr} k {k:expr} na {na:expr} into {target:ident}`: Cation exchange capacity
  - `calculate` — Pattern: `calculate soil porosity bulk {pb:expr} into {target:ident}`: Soil bulk porosity
- **Exported Functions/Symbols (125):** `AGRONOMY_DOMAIN`, `AgronomyASTExporter`, `AgronomyDomain`, `AgronomyDomainParser`, `AgronomyRuntime`, `DomainContract`, `DomainRuntime`, `VerbSpec`, `agronomy_cation_exchange_capacity`, `agronomy_crop_water_requirement`, `agronomy_fertilizer_rate`, `agronomy_growing_degree_days`, `agronomy_soil_porosity`, `ds_adsr_envelope`, `ds_agent_confidence`...

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
- **Description:** Theoretical astrophysics & cosmology: Schwarzschild radius, Stefan-Boltzmann luminosity, Eddington limit, Hubble recession, Jeans mass, and Friedmann critical density
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate schwarzschild radius mass {m:expr} into {target:ident}`: Event horizon radius
  - `calculate` — Pattern: `calculate stellar luminosity radius {r:expr} temp {t:expr} into {target:ident}`: Stefan-Boltzmann luminosity
  - `calculate` — Pattern: `calculate eddington luminosity mass {m:expr} into {target:ident}`: Eddington luminosity limit
  - `calculate` — Pattern: `calculate hubble velocity distance {d:expr} into {target:ident}`: Hubble cosmic velocity
  - `calculate` — Pattern: `calculate jeans mass temp {t:expr} density {n:expr} into {target:ident}`: Jeans collapse mass
  - `calculate` — Pattern: `calculate critical density h0 {h0:expr} into {target:ident}`: Friedmann critical universe density
- **Exported Functions/Symbols (126):** `ASTROPHYSICS_DOMAIN`, `AstrophysicsASTExporter`, `AstrophysicsDomain`, `AstrophysicsDomainParser`, `AstrophysicsRuntime`, `DomainContract`, `DomainRuntime`, `VerbSpec`, `astro_eddington_luminosity`, `astro_friedmann_critical_density`, `astro_hubble_velocity`, `astro_jeans_mass`, `astro_schwarzschild_radius`, `astro_stefan_boltzmann_luminosity`, `ds_adsr_envelope`...

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
- **Description:** Aeronautics and flight physics: pressure & density altitude, crosswind components, turn radius, banked stall speed, and climb gradient
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate pressure altitude altimeter {alt:expr} elevation {elev:expr} into {target:ident}`: Pressure altitude
  - `calculate` — Pattern: `calculate density altitude pressure_alt {pa:expr} oat {oat:expr} into {target:ident}`: Density altitude
  - `calculate` — Pattern: `calculate wind components wind_speed {ws:expr} wind_dir {wd:expr} runway {rw:expr} into {target:ident}`: Crosswind and headwind components
  - `calculate` — Pattern: `calculate turn radius tas {tas:expr} bank {bank:expr} into {target:ident}`: Turn radius
  - `calculate` — Pattern: `calculate banked stall speed vs0 {vs:expr} bank {b:expr} into {target:ident}`: Stall speed in bank turn
  - `calculate` — Pattern: `calculate climb gradient roc {roc:expr} tas {tas:expr} into {target:ident}`: Aircraft climb gradient percentage
- **Exported Functions/Symbols (126):** `AVIATION_DOMAIN`, `AviationASTExporter`, `AviationDomain`, `AviationDomainParser`, `AviationRuntime`, `DomainContract`, `DomainRuntime`, `VerbSpec`, `aviation_banked_stall_speed`, `aviation_climb_gradient`, `aviation_density_altitude`, `aviation_pressure_altitude`, `aviation_turn_radius`, `aviation_wind_components`, `ds_adsr_envelope`...

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
- **Description:** Biomechanics and kinesiology: joint moment, multi-segment center of mass, GRF impulse, muscle tendon force, Hill's force-velocity, and limb moment of inertia
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate joint moment force {f:expr} arm {r:expr} angle {a:expr} into {target:ident}`: Joint moment/torque
  - `calculate` — Pattern: `calculate center of mass masses {m:expr} positions {p:expr} into {target:ident}`: Center of mass
  - `calculate` — Pattern: `calculate grf impulse forces {f:expr} dt {dt:expr} into {target:ident}`: GRF impulse
  - `calculate` — Pattern: `calculate muscle tendon force muscle {fm:expr} pennation {a:expr} into {target:ident}`: Muscle tendon force
  - `calculate` — Pattern: `calculate hill muscle force velocity {v:expr} f0 {f0:expr} param_a {a:expr} param_b {b:expr} into {target:ident}`: Hill's muscle force-velocity
  - `calculate` — Pattern: `calculate segment inertia mass {m:expr} radius {r:expr} into {target:ident}`: Segment moment of inertia
- **Exported Functions/Symbols (126):** `BIOMECHANICS_DOMAIN`, `BiomechanicsASTExporter`, `BiomechanicsDomain`, `BiomechanicsDomainParser`, `BiomechanicsRuntime`, `DomainContract`, `DomainRuntime`, `VerbSpec`, `biomech_center_of_mass`, `biomech_grf_impulse`, `biomech_hills_muscle_force_velocity`, `biomech_joint_moment`, `biomech_muscle_tendon_force`, `biomech_segment_moment_of_inertia_cylinder`, `ds_adsr_envelope`...

### 2.13 Domain: `cache`
- **Primary Name:** `cache`
- **Aliases:** `caching`, `lru`, `ttl`
- **Description:** Advanced caching: LRU, LFU, Bloom filters, and consistent hashing rings
- **Registered Verbs & Patterns:**
  - `create` — Pattern: `create lru cache with capacity {cap:expr} into {target:ident}`: Create LRU cache
  - `create` — Pattern: `create lfu cache with capacity {cap:expr} into {target:ident}`: Create LFU cache
  - `create` — Pattern: `create hash ring with replicas {rep:expr} into {target:ident}`: Consistent hash ring
- **Exported Functions/Symbols (135):** `BloomFilter`, `CACHE_DOMAIN`, `CacheASTExporter`, `CacheDomain`, `CacheDomainParser`, `CacheRuntime`, `ConsistentHashRing`, `DomainContract`, `DomainRuntime`, `LFUCache`, `LRUCache`, `VerbSpec`, `cache_bloom_add`, `cache_bloom_check`, `cache_create_bloom`...

### 2.14 Domain: `cartography`
- **Primary Name:** `cartography`
- **Aliases:** `carto`, `map_projection`, `geodesy`
- **Description:** Cartography and map projections: Haversine distance, initial bearing, Mercator projection, UTM zones, ground distance, and Tissot distortion
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate haversine distance lat1 {la1:expr} lon1 {lo1:expr} lat2 {la2:expr} lon2 {lo2:expr} into {target:ident}`: Haversine distance
  - `calculate` — Pattern: `calculate initial bearing lat1 {la1:expr} lon1 {lo1:expr} lat2 {la2:expr} lon2 {lo2:expr} into {target:ident}`: Initial bearing
  - `calculate` — Pattern: `calculate mercator projection lat {la:expr} lon {lo:expr} into {target:ident}`: Mercator projection
  - `calculate` — Pattern: `calculate utm zone lon {lo:expr} into {target:ident}`: UTM zone
  - `calculate` — Pattern: `calculate ground distance map_cm {cm:expr} scale {ratio:expr} into {target:ident}`: Ground distance
  - `calculate` — Pattern: `calculate mercator distortion lat {lat:expr} into {target:ident}`: Mercator scale distortion
- **Exported Functions/Symbols (126):** `CARTOGRAPHY_DOMAIN`, `CartographyASTExporter`, `CartographyDomain`, `CartographyDomainParser`, `CartographyRuntime`, `DomainContract`, `DomainRuntime`, `VerbSpec`, `carto_ground_distance`, `carto_haversine_distance`, `carto_initial_bearing`, `carto_mercator_projection`, `carto_tissot_indicatrix_distortion`, `carto_utm_zone`, `ds_adsr_envelope`...

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
- **Description:** Precision timekeeping and astronomical chronology: Julian Day, GMST, Equation of Time, Special & General Relativistic dilation, and Solar declination
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate julian day year {y:expr} month {m:expr} day {d:expr} into {target:ident}`: Julian Day Number
  - `calculate` — Pattern: `calculate gmst jdn {jdn:expr} into {target:ident}`: Greenwich Mean Sidereal Time
  - `calculate` — Pattern: `calculate equation of time day {d:expr} into {target:ident}`: Equation of Time
  - `calculate` — Pattern: `calculate time dilation proper {t0:expr} velocity {v:expr} into {target:ident}`: Relativistic time dilation
  - `calculate` — Pattern: `calculate gravitational dilation proper {t0:expr} mass {m:expr} radius {r:expr} into {target:ident}`: Gravitational time dilation
  - `calculate` — Pattern: `calculate solar declination day {d:expr} into {target:ident}`: Solar declination angle
- **Exported Functions/Symbols (126):** `CHRONOMETRY_DOMAIN`, `ChronometryASTExporter`, `ChronometryDomain`, `ChronometryDomainParser`, `ChronometryRuntime`, `DomainContract`, `DomainRuntime`, `VerbSpec`, `chrono_equation_of_time`, `chrono_gravitational_time_dilation`, `chrono_greenwich_mean_sidereal_time`, `chrono_julian_day_number`, `chrono_relativistic_time_dilation`, `chrono_solar_declination`, `ds_adsr_envelope`...

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
- **Description:** Meteorology & climate: Dew point, heat index, wind chill, VPD, and radiative forcing
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate dew point for temperature {t:expr} humidity {h:expr} into {target:ident}`: Dew point
  - `calculate` — Pattern: `calculate wind chill for temperature {t:expr} wind {w:expr} into {target:ident}`: Wind chill
  - `calculate` — Pattern: `calculate vpd for temperature {t:expr} humidity {h:expr} into {target:ident}`: VPD
  - `calculate` — Pattern: `calculate radiative forcing for co2 {ppm:expr} into {target:ident}`: Radiative forcing
- **Exported Functions/Symbols (127):** `CLIMATE_DOMAIN`, `ClimateASTExporter`, `ClimateDomain`, `ClimateDomainParser`, `ClimateRuntime`, `DomainContract`, `DomainRuntime`, `VerbSpec`, `climate_barometric_altitude`, `climate_co2_equivalent`, `climate_dew_point`, `climate_heat_index`, `climate_radiative_forcing`, `climate_vapor_pressure_deficit`, `climate_wind_chill`...

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
- **Description:** Combustion engineering: equivalence ratio, Arrhenius kinetics, heat release, adiabatic flame temperature, Le Chatelier flammability limits, and Zeldovich thermal NOx
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate equivalence ratio fuel {f:expr} air {a:expr} stoich {s:expr} into {target:ident}`: Equivalence ratio
  - `calculate` — Pattern: `calculate arrhenius rate preexp {a:expr} ea {ea:expr} temp {t:expr} into {target:ident}`: Arrhenius rate
  - `calculate` — Pattern: `calculate heat release rate flow {m:expr} lhv {lhv:expr} eff {eff:expr} into {target:ident}`: Heat release rate
  - `calculate` — Pattern: `calculate adiabatic flame temp t0 {t0:expr} lhv {lhv:expr} cp {cp:expr} afr {afr:expr} into {target:ident}`: Adiabatic flame temperature
  - `calculate` — Pattern: `calculate mixture flammability fractions {y:expr} limits {lfl:expr} into {target:ident}`: Le Chatelier mixture flammability limit
  - `calculate` — Pattern: `calculate thermal nox temp {t:expr} oxygen {o2:expr} into {target:ident}`: Zeldovich thermal NOx scaling
- **Exported Functions/Symbols (126):** `COMBUSTION_DOMAIN`, `CombustionASTExporter`, `CombustionDomain`, `CombustionDomainParser`, `CombustionRuntime`, `DomainContract`, `DomainRuntime`, `VerbSpec`, `combust_adiabatic_flame_temp`, `combust_arrhenius_rate`, `combust_equivalence_ratio`, `combust_heat_release_rate`, `combust_le_chatelier_flammability_limit`, `combust_zeldovich_nox_scaling`, `ds_adsr_envelope`...

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
- **Description:** Feedback control: State-space, Kalman filter, PID tuning, sensor fusion, and Routh-Hurwitz stability
- **Registered Verbs & Patterns:**
  - `step` — Pattern: `step state space a {a:expr} b {b:expr} state {x:expr} input {u:expr} into {target:ident}`: State-space step
  - `step` — Pattern: `step kalman filter prior {x:expr} cov {p:expr} measurement {z:expr} noise {r:expr} into {target:ident}`: Kalman step
  - `check` — Pattern: `check stability for polynomial {coeffs:expr} into {target:ident}`: Routh-Hurwitz stability
- **Exported Functions/Symbols (125):** `CONTROL_DOMAIN`, `ControlASTExporter`, `ControlDomain`, `ControlDomainParser`, `ControlRuntime`, `DomainContract`, `DomainRuntime`, `VerbSpec`, `control_complementary_filter`, `control_kalman_1d_step`, `control_pid_step`, `control_routh_hurwitz_stable`, `control_state_space_step`, `ds_adsr_envelope`, `ds_agent_confidence`...

### 2.25 Domain: `crypto_zk`
- **Primary Name:** `crypto_zk`
- **Aliases:** `zkp`, `zero_knowledge`, `schnorr`, `pedersen`
- **Description:** Zero-Knowledge Proofs & Cryptography: Shamir secret sharing, Pedersen, Merkle trees, Schnorr ZK
- **Registered Verbs & Patterns:**
  - `split` — Pattern: `split secret {sec:expr} into {n:expr} shares with threshold {t:expr} into {target:ident}`: Shamir split
  - `build` — Pattern: `build merkle tree for leaves {leaves:expr} into {target:ident}`: Merkle tree
  - `generate` — Pattern: `generate schnorr zk proof for secret {s:expr} into {target:ident}`: Schnorr proof
- **Exported Functions/Symbols (128):** `CRYPTO_ZK_DOMAIN`, `CryptoZKDomain`, `CryptoZKRuntime`, `Crypto_zkASTExporter`, `Crypto_zkDomainParser`, `DomainContract`, `DomainRuntime`, `VerbSpec`, `crypto_diffie_hellman`, `crypto_merkle_tree`, `crypto_merkle_verify`, `crypto_pedersen_commit`, `crypto_schnorr_prove`, `crypto_schnorr_verify_proof`, `crypto_shamir_reconstruct`...

### 2.26 Domain: `crystallography`
- **Primary Name:** `crystallography`
- **Aliases:** `crystal`, `xray_diffraction`, `lattice`
- **Description:** Crystallography: Bragg diffraction, interplanar spacing, atomic packing factors, theoretical density, and Scherrer crystallite size
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate bragg angle wavelength {w:expr} spacing {d:expr} order {n:expr} into {target:ident}`: Bragg diffraction angle
  - `calculate` — Pattern: `calculate interplanar spacing lattice {a:expr} h {h:expr} k {k:expr} l {l:expr} into {target:ident}`: Interplanar spacing
  - `calculate` — Pattern: `calculate atomic packing factor system {s:expr} into {target:ident}`: Atomic packing factor
  - `calculate` — Pattern: `calculate crystal density atoms {n:expr} weight {a:expr} volume {v:expr} into {target:ident}`: Crystal theoretical density
  - `calculate` — Pattern: `calculate crystallite size wavelength {w:expr} fwhm {f:expr} theta {t:expr} into {target:ident}`: Scherrer crystallite domain size
- **Exported Functions/Symbols (125):** `CRYSTALLOGRAPHY_DOMAIN`, `CrystallographyASTExporter`, `CrystallographyDomain`, `CrystallographyDomainParser`, `CrystallographyRuntime`, `DomainContract`, `DomainRuntime`, `VerbSpec`, `crystal_atomic_packing_factor`, `crystal_bragg_angle`, `crystal_cubic_interplanar_spacing`, `crystal_density`, `crystal_scherrer_crystallite_size`, `ds_adsr_envelope`, `ds_agent_confidence`...

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
- **Description:** Ecology & population dynamics: Shannon/Simpson biodiversity, Pielou evenness, Lotka-Volterra, and mark-recapture
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate shannon diversity for abundances {counts:expr} into {target:ident}`: Shannon index
  - `calculate` — Pattern: `calculate pielou evenness for abundances {counts:expr} into {target:ident}`: Pielou evenness
  - `estimate` — Pattern: `estimate population marked {n1:expr} captured {n2:expr} recaptured {m2:expr} into {target:ident}`: Lincoln-Petersen estimate
- **Exported Functions/Symbols (127):** `DomainContract`, `DomainRuntime`, `ECOLOGY_DOMAIN`, `EcologyASTExporter`, `EcologyDomain`, `EcologyDomainParser`, `EcologyRuntime`, `VerbSpec`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`, `ds_agent_recall_similar`, `ds_agent_reflect`, `ds_align_sequences_nw`...

### 2.31 Domain: `electromagnetics`
- **Primary Name:** `electromagnetics`
- **Aliases:** `em`, `emag`, `maxwell`
- **Description:** Electromagnetics: Biot-Savart law, conductor skin depth, Poynting vector, coaxial impedance, plane wave attenuation, and Faraday induced EMF
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate magnetic field wire current {i:expr} distance {r:expr} into {target:ident}`: Biot-Savart magnetic field
  - `calculate` — Pattern: `calculate skin depth freq {f:expr} conductivity {s:expr} perm {ur:expr} into {target:ident}`: Conductor skin depth
  - `calculate` — Pattern: `calculate poynting vector efield {e:expr} hfield {h:expr} into {target:ident}`: Poynting power flux
  - `calculate` — Pattern: `calculate coax impedance inner {a:expr} outer {b:expr} eps {er:expr} into {target:ident}`: Coaxial line impedance
  - `calculate` — Pattern: `calculate wave attenuation freq {f:expr} conductivity {s:expr} eps {er:expr} perm {ur:expr} into {target:ident}`: Plane wave attenuation
  - `calculate` — Pattern: `calculate faraday emf turns {n:expr} flux {dphi:expr} time {dt:expr} into {target:ident}`: Faraday induced EMF
- **Exported Functions/Symbols (126):** `DomainContract`, `DomainRuntime`, `ELECTROMAGNETICS_DOMAIN`, `ElectromagneticsASTExporter`, `ElectromagneticsDomain`, `ElectromagneticsDomainParser`, `ElectromagneticsRuntime`, `VerbSpec`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`, `ds_agent_recall_similar`, `ds_agent_reflect`, `ds_align_sequences_nw`...

### 2.32 Domain: `epidemiology`
- **Primary Name:** `epidemiology`
- **Aliases:** `disease_spread`, `outbreak`, `sir_model`
- **Description:** Epidemiological modeling: R0, herd immunity, SIR/SEIR compartmental models, and CFR analysis
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate reproduction number r0 for beta {b:expr} gamma {g:expr} into {target:ident}`: R0 calculation
  - `step` — Pattern: `step sir model s {s:expr} i {i:expr} r {r:expr} beta {b:expr} gamma {g:expr} into {target:ident}`: SIR step
  - `step` — Pattern: `step seir model s {s:expr} e {e:expr} i {i:expr} r {r:expr} beta {b:expr} sigma {sig:expr} gamma {g:expr} into {target:ident}`: SEIR step
- **Exported Functions/Symbols (125):** `DomainContract`, `DomainRuntime`, `EPIDEMIOLOGY_DOMAIN`, `EpidemiologyASTExporter`, `EpidemiologyDomain`, `EpidemiologyDomainParser`, `EpidemiologyRuntime`, `VerbSpec`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`, `ds_agent_recall_similar`, `ds_agent_reflect`, `ds_align_sequences_nw`...

### 2.33 Domain: `ergonomics`
- **Primary Name:** `ergonomics`
- **Aliases:** `ergo`, `human_factors`, `workplace_safety`
- **Description:** Ergonomics and human factors: NIOSH lifting equation, RULA assessment, metabolic expenditure, REBA scoring, and Moore-Garg Strain Index
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate niosh lifting limit load {lc:expr} horiz {h:expr} vert {v:expr} dist {d:expr} angle {a:expr} freq {f:expr} coupling {c:expr} into {target:ident}`: NIOSH lifting limit
  - `calculate` — Pattern: `calculate rula score upper {u:expr} lower {l:expr} wrist {w:expr} neck {n:expr} trunk {t:expr} load {load:expr} into {target:ident}`: RULA posture score
  - `calculate` — Pattern: `calculate metabolic expenditure weight {w:expr} met {m:expr} minutes {t:expr} into {target:ident}`: Metabolic expenditure
  - `calculate` — Pattern: `calculate reba score trunk {t:expr} neck {n:expr} legs {l:expr} uarm {ua:expr} larm {la:expr} wrist {w:expr} into {target:ident}`: REBA entire body score
  - `calculate` — Pattern: `calculate strain index intensity {im:expr} duration {dm:expr} efforts {em:expr} posture {pm:expr} into {target:ident}`: Moore-Garg Strain Index
- **Exported Functions/Symbols (125):** `DomainContract`, `DomainRuntime`, `ERGONOMICS_DOMAIN`, `ErgonomicsASTExporter`, `ErgonomicsDomain`, `ErgonomicsDomainParser`, `ErgonomicsRuntime`, `VerbSpec`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`, `ds_agent_recall_similar`, `ds_agent_reflect`, `ds_align_sequences_nw`...

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
- **Description:** Digital forensics & malware triage: Magic byte identification, Shannon entropy, Base64 deobfuscation, and DGA detection
- **Registered Verbs & Patterns:**
  - `identify` — Pattern: `identify file type by magic bytes {header:expr} into {target:ident}`: Magic bytes
  - `calculate` — Pattern: `calculate shannon entropy for data {data:expr} into {target:ident}`: Entropy
  - `check` — Pattern: `check dga domain {d:expr} into {target:ident}`: DGA detection
- **Exported Functions/Symbols (125):** `DomainContract`, `DomainRuntime`, `FORENSICS_DOMAIN`, `ForensicsASTExporter`, `ForensicsDomain`, `ForensicsDomainParser`, `ForensicsRuntime`, `VerbSpec`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`, `ds_agent_recall_similar`, `ds_agent_reflect`, `ds_align_sequences_nw`...

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
- **Description:** GenAI, LLMs & RAG: Vector search, chunking, BM25, RRF, prompt safety, ROUGE/BLEU
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate cosine similarity between {v1:expr} and {v2:expr} into {target:ident}`: Cosine similarity
  - `fuse` — Pattern: `fuse rankings for lists {lists:expr} into {target:ident}`: RRF rank fusion
  - `check` — Pattern: `check prompt injection for text {text:expr} into {target:ident}`: Prompt injection detection
- **Exported Functions/Symbols (131):** `DomainContract`, `DomainRuntime`, `GENAI_DOMAIN`, `GenAIDomain`, `GenAIRuntime`, `GenaiASTExporter`, `GenaiDomainParser`, `VerbSpec`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`, `ds_agent_recall_similar`, `ds_agent_reflect`, `ds_align_sequences_nw`...

### 2.38 Domain: `genomics`
- **Primary Name:** `genomics`
- **Aliases:** `dna`, `rna`, `genomic_analysis`
- **Description:** Genomics & bioinformatics: Local/global alignment, CpG islands, melting temp, VCF parsing, and k-mers
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate gc content for sequence {seq:expr} into {target:ident}`: GC content
  - `align` — Pattern: `align sequences local {s1:expr} and {s2:expr} into {target:ident}`: Local alignment
  - `calculate` — Pattern: `calculate melting temp for sequence {seq:expr} into {target:ident}`: Melting temperature
- **Exported Functions/Symbols (130):** `DomainContract`, `DomainRuntime`, `GENOMICS_DOMAIN`, `GenomicsASTExporter`, `GenomicsDomain`, `GenomicsDomainParser`, `GenomicsRuntime`, `VerbSpec`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`, `ds_agent_recall_similar`, `ds_agent_reflect`, `ds_align_sequences_nw`...

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
- **Description:** Geophysical analytics: Wadati epicentral distance, Richter/Moment magnitude, Snell refraction, Bouguer anomaly, and resistivity
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate epicentral distance for p arrival {tp:expr} s arrival {ts:expr} into {target:ident}`: Epicentral distance
  - `calculate` — Pattern: `calculate moment magnitude area {a:expr} slip {s:expr} into {target:ident}`: Moment magnitude
  - `calculate` — Pattern: `calculate apparent resistivity spacing {a:expr} resistance {r:expr} into {target:ident}`: Apparent resistivity
- **Exported Functions/Symbols (127):** `DomainContract`, `DomainRuntime`, `GEOPHYSICS_DOMAIN`, `GeophysicsASTExporter`, `GeophysicsDomain`, `GeophysicsDomainParser`, `GeophysicsRuntime`, `VerbSpec`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`, `ds_agent_recall_similar`, `ds_agent_reflect`, `ds_align_sequences_nw`...

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
- **Description:** Hydrology & hydraulic engineering: Manning flow, Darcy-Weisbach head loss, hydraulic jumps, and Theis drawdown
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate manning flow for roughness {n:expr} area {a:expr} radius {r:expr} slope {s:expr} into {target:ident}`: Manning flow
  - `calculate` — Pattern: `calculate hydraulic jump for depth {y:expr} velocity {v:expr} into {target:ident}`: Hydraulic jump
- **Exported Functions/Symbols (126):** `DomainContract`, `DomainRuntime`, `HYDROLOGY_DOMAIN`, `HydrologyASTExporter`, `HydrologyDomain`, `HydrologyDomainParser`, `HydrologyRuntime`, `VerbSpec`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`, `ds_agent_recall_similar`, `ds_agent_reflect`, `ds_align_sequences_nw`...

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
- **Description:** Computational linguistics: Levenshtein, Jaro-Winkler, Soundex, Flesch, Gunning Fog, and TTR
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate edit distance for word1 {w1:expr} word2 {w2:expr} into {target:ident}`: Edit distance
  - `calculate` — Pattern: `calculate jaro winkler for word1 {w1:expr} word2 {w2:expr} into {target:ident}`: Jaro-Winkler
  - `calculate` — Pattern: `calculate gunning fog for text {text:expr} into {target:ident}`: Gunning Fog
- **Exported Functions/Symbols (127):** `DomainContract`, `DomainRuntime`, `LINGUISTICS_DOMAIN`, `LinguisticsASTExporter`, `LinguisticsDomain`, `LinguisticsDomainParser`, `LinguisticsRuntime`, `VerbSpec`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`, `ds_agent_recall_similar`, `ds_agent_reflect`, `ds_align_sequences_nw`...

### 2.46 Domain: `logistics`
- **Primary Name:** `logistics`
- **Aliases:** `supply_chain`, `inventory`, `warehouse`
- **Description:** Supply chain & logistics: EOQ, ROP, safety stock, Newsvendor model, bullwhip effect, and TSP solver
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate economic order quantity for demand {d:expr} order cost {s:expr} holding cost {h:expr} into {target:ident}`: EOQ formula
  - `calculate` — Pattern: `calculate reorder point for lead time {lt:expr} daily demand {d:expr} into {target:ident}`: Reorder point
  - `solve` — Pattern: `solve tsp nearest neighbor for matrix {m:expr} into {target:ident}`: TSP solver
- **Exported Functions/Symbols (126):** `DomainContract`, `DomainRuntime`, `LOGISTICS_DOMAIN`, `LogisticsASTExporter`, `LogisticsDomain`, `LogisticsDomainParser`, `LogisticsRuntime`, `VerbSpec`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`, `ds_agent_recall_similar`, `ds_agent_reflect`, `ds_align_sequences_nw`...

### 2.47 Domain: `materials`
- **Primary Name:** `materials`
- **Aliases:** `mechanics_of_materials`, `solid_mechanics`, `stress_strain`
- **Description:** Materials science & mechanics: Stress-strain, Mohr's circle, thermal expansion, fracture mechanics, and composites
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate engineering stress and strain for force {f:expr} area {a:expr} delta {dl:expr} initial length {l0:expr} into {target:ident}`: Stress-strain
  - `calculate` — Pattern: `calculate stress intensity for stress {s:expr} crack {a:expr} into {target:ident}`: Stress intensity
- **Exported Functions/Symbols (125):** `DomainContract`, `DomainRuntime`, `MATERIALS_DOMAIN`, `MaterialsASTExporter`, `MaterialsDomain`, `MaterialsDomainParser`, `MaterialsRuntime`, `VerbSpec`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`, `ds_agent_recall_similar`, `ds_agent_reflect`, `ds_align_sequences_nw`...

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
- **Description:** Physical metallurgy: Hall-Petch strength, Hollomon strain hardening, lever rule, Scheil solidification, JMAK recrystallization, and Arrhenius diffusion
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate hall petch strength friction {s0:expr} locking {ky:expr} grain {d:expr} into {target:ident}`: Hall-Petch strength
  - `calculate` — Pattern: `calculate hollomon true stress k {k:expr} strain {eps:expr} n {n:expr} into {target:ident}`: Hollomon true stress
  - `calculate` — Pattern: `calculate lever rule overall {c0:expr} alpha {ca:expr} beta {cb:expr} into {target:ident}`: Lever rule phase weights
  - `calculate` — Pattern: `calculate scheil composition initial {c0:expr} partition {k:expr} solid {fs:expr} into {target:ident}`: Scheil solidification
  - `calculate` — Pattern: `calculate jmak recrystallization time {t:expr} k {k:expr} exponent {n:expr} into {target:ident}`: JMAK recrystallization fraction
  - `calculate` — Pattern: `calculate metal diffusion d0 {d0:expr} energy {q:expr} temp {t:expr} into {target:ident}`: Arrhenius atomic diffusion
- **Exported Functions/Symbols (126):** `DomainContract`, `DomainRuntime`, `METALLURGY_DOMAIN`, `MetallurgyASTExporter`, `MetallurgyDomain`, `MetallurgyDomainParser`, `MetallurgyRuntime`, `VerbSpec`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`, `ds_agent_recall_similar`, `ds_agent_reflect`, `ds_align_sequences_nw`...

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
- **Description:** Microeconomics: Price elasticity, welfare surplus, deadweight loss, Gini coefficient, Cournot duopoly, and HHI
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate price elasticity for q1 {q1:expr} q2 {q2:expr} p1 {p1:expr} p2 {p2:expr} into {target:ident}`: Price elasticity
  - `calculate` — Pattern: `calculate cournot duopoly demand intercept {a:expr} slope {b:expr} marginal cost {c:expr} into {target:ident}`: Cournot duopoly
- **Exported Functions/Symbols (126):** `DomainContract`, `DomainRuntime`, `MICROECON_DOMAIN`, `MicroeconASTExporter`, `MicroeconDomain`, `MicroeconDomainParser`, `MicroeconRuntime`, `VerbSpec`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`, `ds_agent_recall_similar`, `ds_agent_reflect`, `ds_align_sequences_nw`...

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
- **Description:** Nuclear physics & engineering: radioactive decay, decay constant, reaction Q-value, radiation shielding, Four-Factor Formula, and Half-Value Layer
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate radioactive decay initial {a0:expr} halflife {hl:expr} time {t:expr} into {target:ident}`: Radioactive decay
  - `calculate` — Pattern: `calculate decay constant halflife {hl:expr} into {target:ident}`: Decay constant
  - `calculate` — Pattern: `calculate nuclear q value mass_in {mi:expr} mass_out {mf:expr} into {target:ident}`: Reaction Q-value
  - `calculate` — Pattern: `calculate radiation shielding initial {i0:expr} attenuation {mu:expr} thickness {x:expr} into {target:ident}`: Radiation shielding attenuation
  - `calculate` — Pattern: `calculate four factor eta {eta:expr} epsilon {eps:expr} p {p:expr} f {f:expr} into {target:ident}`: Four-factor formula
  - `calculate` — Pattern: `calculate half value layer attenuation {mu:expr} into {target:ident}`: Half-Value Layer
- **Exported Functions/Symbols (126):** `DomainContract`, `DomainRuntime`, `NUCLEAR_DOMAIN`, `NuclearASTExporter`, `NuclearDomain`, `NuclearDomainParser`, `NuclearRuntime`, `VerbSpec`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`, `ds_agent_recall_similar`, `ds_agent_reflect`, `ds_align_sequences_nw`...

### 2.57 Domain: `oceanography`
- **Primary Name:** `oceanography`
- **Aliases:** `marine_science`, `ocean_dynamics`, `ocean_waves`
- **Description:** Ocean physics & dynamics: seawater equation of state density, Coriolis parameter, surface gravity waves, Mackenzie sound speed, and wind stress
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate seawater density temp {t:expr} salinity {s:expr} into {target:ident}`: UNESCO seawater density
  - `calculate` — Pattern: `calculate coriolis parameter lat {lat:expr} into {target:ident}`: Coriolis frequency parameter
  - `calculate` — Pattern: `calculate ocean wave speed wavelength {l:expr} depth {d:expr} into {target:ident}`: Gravity wave phase velocity
  - `calculate` — Pattern: `calculate depth pressure depth {d:expr} into {target:ident}`: Hydrostatic pressure
  - `calculate` — Pattern: `calculate seawater sound speed temp {t:expr} salinity {s:expr} depth {d:expr} into {target:ident}`: Mackenzie underwater sound speed
  - `calculate` — Pattern: `calculate wind stress speed {u:expr} into {target:ident}`: Wind shear stress on ocean surface
- **Exported Functions/Symbols (126):** `DomainContract`, `DomainRuntime`, `OCEANOGRAPHY_DOMAIN`, `OceanographyASTExporter`, `OceanographyDomain`, `OceanographyDomainParser`, `OceanographyRuntime`, `VerbSpec`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`, `ds_agent_recall_similar`, `ds_agent_reflect`, `ds_align_sequences_nw`...

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
- **Description:** Geometrical & wave optics: Snell's law, thin lenses, Fresnel reflection, Rayleigh resolution limit, Brewster angle, and fiber NA
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate thin lens focal {f:expr} distance {do:expr} into {target:ident}`: Thin lens image distance & magnification
  - `calculate` — Pattern: `calculate snell refraction n1 {n1:expr} n2 {n2:expr} angle {theta:expr} into {target:ident}`: Snell refraction angle
  - `calculate` — Pattern: `calculate fresnel reflectance n1 {n1:expr} n2 {n2:expr} into {target:ident}`: Fresnel normal reflection
  - `calculate` — Pattern: `calculate rayleigh resolution wavelength {lam:expr} na {na:expr} into {target:ident}`: Rayleigh optical resolution limit
  - `calculate` — Pattern: `calculate brewster angle n1 {n1:expr} n2 {n2:expr} into {target:ident}`: Brewster polarizing angle
  - `calculate` — Pattern: `calculate fiber aperture core {n1:expr} clad {n2:expr} into {target:ident}`: Fiber numerical aperture
- **Exported Functions/Symbols (127):** `DomainContract`, `DomainRuntime`, `OPTICS_DOMAIN`, `OpticsASTExporter`, `OpticsDomain`, `OpticsDomainParser`, `OpticsRuntime`, `VerbSpec`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`, `ds_agent_recall_similar`, `ds_agent_reflect`, `ds_align_sequences_nw`...

### 2.61 Domain: `petroleum`
- **Primary Name:** `petroleum`
- **Aliases:** `petro`, `oilgas`, `reservoir`
- **Description:** Petroleum and reservoir engineering: Darcy flow, Archie saturation, API gravity, GOR, Standing bubble point, and Sutton gas properties
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate darcy radial flow perm {k:expr} pay {h:expr} pres {pr:expr} pwell {pw:expr} visc {mu:expr} re {re:expr} rw {rw:expr} skin {s:expr} into {target:ident}`: Darcy radial flow rate
  - `calculate` — Pattern: `calculate archie water saturation phi {phi:expr} rt {rt:expr} rw {rw:expr} into {target:ident}`: Archie water saturation
  - `convert` — Pattern: `convert specific gravity {sg:expr} to api into {target:ident}`: Specific gravity to API
  - `calculate` — Pattern: `calculate gas oil ratio gas {g:expr} oil {o:expr} into {target:ident}`: Gas-Oil Ratio
  - `calculate` — Pattern: `calculate bubble point gor {gor:expr} gas_grav {gg:expr} api {api:expr} temp {t:expr} into {target:ident}`: Standing bubble point pressure
  - `calculate` — Pattern: `calculate pseudocritical gas grav {gg:expr} into {target:ident}`: Sutton pseudocritical gas properties
- **Exported Functions/Symbols (126):** `DomainContract`, `DomainRuntime`, `PETROLEUM_DOMAIN`, `PetroleumASTExporter`, `PetroleumDomain`, `PetroleumDomainParser`, `PetroleumRuntime`, `VerbSpec`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`, `ds_agent_recall_similar`, `ds_agent_reflect`, `ds_align_sequences_nw`...

### 2.62 Domain: `pharmacology`
- **Primary Name:** `pharmacology`
- **Aliases:** `pharm`, `pharmacokinetics`, `pk_pd`
- **Description:** Pharmacology and PK/PD: elimination kinetics, steady state, volume of distribution, Hill dose-response, Michaelis-Menten clearance, and loading dose
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate elimination rate halflife {hl:expr} into {target:ident}`: Elimination rate constant
  - `calculate` — Pattern: `calculate steady state conc dose {d:expr} bioavailability {f:expr} clearance {cl:expr} interval {tau:expr} into {target:ident}`: Steady state plasma concentration
  - `calculate` — Pattern: `calculate volume distribution dose {d:expr} c0 {c0:expr} into {target:ident}`: Volume of distribution
  - `calculate` — Pattern: `calculate hill response conc {c:expr} emax {emax:expr} ec50 {ec50:expr} hill {n:expr} into {target:ident}`: Hill dose-response
  - `calculate` — Pattern: `calculate saturable elimination vmax {vm:expr} km {km:expr} conc {c:expr} into {target:ident}`: Michaelis-Menten elimination rate
  - `calculate` — Pattern: `calculate loading dose vd {vd:expr} target {ct:expr} bio {f:expr} into {target:ident}`: Target loading dose
- **Exported Functions/Symbols (126):** `DomainContract`, `DomainRuntime`, `PHARMACOLOGY_DOMAIN`, `PharmacologyASTExporter`, `PharmacologyDomain`, `PharmacologyDomainParser`, `PharmacologyRuntime`, `VerbSpec`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`, `ds_agent_recall_similar`, `ds_agent_reflect`, `ds_align_sequences_nw`...

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
- **Description:** Queueing & messaging: FIFO, priority queues, ring buffers, token buckets, and DLQs
- **Registered Verbs & Patterns:**
  - `create` — Pattern: `create message queue with capacity {cap:expr} into {target:ident}`: FIFO queue
  - `create` — Pattern: `create priority queue into {target:ident}`: Priority queue
  - `create` — Pattern: `create ring buffer with size {sz:expr} into {target:ident}`: Ring buffer
- **Exported Functions/Symbols (133):** `DeadLetterQueue`, `DomainContract`, `DomainRuntime`, `MessageQueue`, `PriorityMessageQueue`, `QUEUE_DOMAIN`, `QueueASTExporter`, `QueueDomain`, `QueueDomainParser`, `QueueRuntime`, `RingBuffer`, `TokenBucket`, `VerbSpec`, `ds_adsr_envelope`, `ds_agent_confidence`...

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
- **Description:** Quantitative financial risk: VaR, CVaR, Maximum Drawdown, Sharpe/Sortino/Calmar ratios, and portfolio volatility
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate historical var for returns {ret:expr} confidence {conf:expr} into {target:ident}`: VaR
  - `calculate` — Pattern: `calculate max drawdown for prices {prices:expr} into {target:ident}`: Max Drawdown
  - `calculate` — Pattern: `calculate portfolio volatility weights {w:expr} covariance {cov:expr} into {target:ident}`: Portfolio Volatility
- **Exported Functions/Symbols (127):** `DomainContract`, `DomainRuntime`, `RISK_DOMAIN`, `RiskASTExporter`, `RiskDomain`, `RiskDomainParser`, `RiskRuntime`, `VerbSpec`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`, `ds_agent_recall_similar`, `ds_agent_reflect`, `ds_align_sequences_nw`...

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
- **Description:** Social network analysis: Degree, Closeness, Betweenness centrality, PageRank, and clustering
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate degree centrality for graph {g:expr} into {target:ident}`: Degree centrality
  - `calculate` — Pattern: `calculate pagerank for graph {g:expr} into {target:ident}`: PageRank algorithm
- **Exported Functions/Symbols (126):** `DomainContract`, `DomainRuntime`, `SOCIAL_DOMAIN`, `SocialASTExporter`, `SocialDomain`, `SocialDomainParser`, `SocialRuntime`, `VerbSpec`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`, `ds_agent_recall_similar`, `ds_agent_reflect`, `ds_align_sequences_nw`...

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
- **Description:** Structural engineering: beam bending moment, elastic deflection, Euler buckling, section modulus, Mohr's circle principal stresses, and slenderness ratio
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate beam max moment load {w:expr} span {l:expr} into {target:ident}`: Beam maximum bending moment
  - `calculate` — Pattern: `calculate beam max deflection load {w:expr} span {l:expr} modulus {e:expr} inertia {i:expr} into {target:ident}`: Beam elastic deflection
  - `calculate` — Pattern: `calculate column buckling load modulus {e:expr} inertia {i:expr} length {l:expr} factor {k:expr} into {target:ident}`: Euler column buckling load
  - `calculate` — Pattern: `calculate section modulus width {b:expr} height {h:expr} into {target:ident}`: Elastic section modulus
  - `calculate` — Pattern: `calculate mohr principal stresses sx {sx:expr} sy {sy:expr} txy {txy:expr} into {target:ident}`: Mohr circle principal stresses
  - `calculate` — Pattern: `calculate slenderness ratio length {l:expr} radius {r:expr} into {target:ident}`: Column slenderness ratio
- **Exported Functions/Symbols (126):** `DomainContract`, `DomainRuntime`, `STRUCTURAL_DOMAIN`, `StructuralASTExporter`, `StructuralDomain`, `StructuralDomainParser`, `StructuralRuntime`, `VerbSpec`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`, `ds_agent_recall_similar`, `ds_agent_reflect`, `ds_align_sequences_nw`...

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
- **Description:** Synthetic biology: Hill kinetics, Gardner toggle switch, Repressilator, Michaelis-Menten, and Gibson assembly
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate hill activation for conc {x:expr} k {k:expr} n {n:expr} into {target:ident}`: Hill activation
  - `calculate` — Pattern: `calculate enzyme rate substrate {s:expr} vmax {v:expr} km {km:expr} into {target:ident}`: Michaelis-Menten rate
  - `check` — Pattern: `check gibson overlap frag1 {f1:expr} frag2 {f2:expr} into {target:ident}`: Gibson overlap
- **Exported Functions/Symbols (127):** `DomainContract`, `DomainRuntime`, `SYNTHETIC_BIO_DOMAIN`, `SyntheticBioASTExporter`, `SyntheticBioDomain`, `SyntheticBioRuntime`, `Synthetic_bioDomainParser`, `VerbSpec`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`, `ds_agent_recall_similar`, `ds_agent_reflect`, `ds_align_sequences_nw`...

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
- **Description:** Thermodynamics & heat cycles: Carnot efficiency, entropy change, polytropic processes, Rankine cycle, and Joule-Thomson expansion
- **Registered Verbs & Patterns:**
  - `calculate` — Pattern: `calculate carnot efficiency hot {th:expr} cold {tc:expr} into {target:ident}`: Carnot efficiency
  - `calculate` — Pattern: `calculate entropy change mass {m:expr} specific heat {c:expr} t1 {t1:expr} t2 {t2:expr} into {target:ident}`: Entropy change
  - `step` — Pattern: `step polytropic p1 {p1:expr} v1 {v1:expr} v2 {v2:expr} index {n:expr} into {target:ident}`: Polytropic gas expansion
  - `calculate` — Pattern: `calculate rankine cycle boiler {h2:expr} turbine {h3:expr} condenser {h4:expr} pump {h1:expr} into {target:ident}`: Rankine cycle efficiency
  - `calculate` — Pattern: `calculate joule thomson drop pressure {dp:expr} coefficient {mu:expr} into {target:ident}`: Joule-Thomson temperature change
- **Exported Functions/Symbols (126):** `DomainContract`, `DomainRuntime`, `THERMODYNAMICS_DOMAIN`, `ThermodynamicsASTExporter`, `ThermodynamicsDomain`, `ThermodynamicsDomainParser`, `ThermodynamicsRuntime`, `VerbSpec`, `ds_adsr_envelope`, `ds_agent_confidence`, `ds_agent_declare`, `ds_agent_handoff`, `ds_agent_recall_similar`, `ds_agent_reflect`, `ds_align_sequences_nw`...

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
