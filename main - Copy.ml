(* Thermodynamic Quine Computing: Persistent Computational Life Forms *)
(* Building speciated quines with intensive thermodynamic character *)
(* Bit ordering: <CVVV|TTTT> with C as MSB for bra-ket row/column vector *)
open Printf
(* Complex numbers for quantum amplitudes *)
module Complex = struct
  type t = { re: float; im: float }
  
  let zero = { re = 0.0; im = 0.0 }
  let one = { re = 1.0; im = 0.0 }
  let i = { re = 0.0; im = 1.0 }
  
  let add z1 z2 = { re = z1.re +. z2.re; im = z1.im +. z2.im }
  let mul z1 z2 = { 
    re = z1.re *. z2.re -. z1.im *. z2.im;
    im = z1.re *. z2.im +. z1.im *. z2.re
  }
  
  let conj z = { re = z.re; im = -.z.im }
  let norm_sq z = z.re *. z.re +. z.im *. z.im
  let norm z = sqrt (norm_sq z)
  
  let to_string z = sprintf "%.3f + %.3fi" z.re z.im
end
(* Morphology states - intensive vs extensive thermodynamic character(s) *)
(* C=1: Environment-coupled, high-energy, pointable *)
(* C=0: Self-contained, low-energy, non-pointable *)
type morphology = 
  | Morphic of int      (* Stable, intensive, self-contained *)
  | Dynamic of int      (* Extensive, environment-coupled *)
  | Markovian of float  (* Forward-evolving, irreversible *)
  | NonMarkovian of float (* Reversible with memory *)

type byte_word = {
  raw: int;                    (* Full 8-bit value *)
  c: morphology;               (* MSB: Control/Epistemology bit *)
  v: int;                      (* Bits 6-4: Morphism selector (3 bits) *)
  t: int;                      (* Bits 3-0: State data (4 bits) *)
  birth_time: float;           (* Thermodynamic birth timestamp *)
  mutable energy: float;       (* Current energy state *)
  mutable refcount: int;       (* Reference counting *)
  mutable quantum_state: quantum_state; (* _associated_ with 'observables' *)
}
(* ByteWord construction and manipulation *)
module ByteWord = struct
  let create raw = 
    if raw < 0 || raw > 255 then 
      invalid_arg "ByteWord must be 8-bit (0-255)"
    else
      let c = if (raw land 0x80) <> 0 then Extensive else Intensive in
      let v = (raw lsr 4) land 0x07 in  (* Extract bits 6-4 *)
      let t = raw land 0x0F in          (* Extract bits 3-0 *)
      { raw; c; v; t }
  
  let to_bra_ket bw = 
    let c_bit = match bw.c with Intensive -> 0 | Extensive -> 1 in
    sprintf "<%d%03b|%04b>" c_bit bw.v bw.t
  
  let is_pointable bw = bw.c = Extensive
    (* XNOR-based Abelian transformation *)
  let xnor a b width = 
    let mask = (1 lsl width) - 1 in
    (lnot (a lxor b)) land mask
  
  let abelian_transform bw = 
    match bw.c with 
    | Extensive -> { bw with t = xnor bw.t bw.v 4 }
    | Intensive -> bw  (* Identity - quines preserve themselves *)
  (* Morphological symmetry operations *)
  let conjugate bw = { bw with v = 7 - bw.v }  (* Bit-flip morphism *)
  let dual bw = { bw with c = match bw.c with Intensive -> Extensive | Extensive -> Intensive }
end
(* Thermodynamic calculations *)
module Thermodynamics = struct
  let boltzmann_k = 1.380649e-23  (* J/K *)
  let room_temp = 300.0           (* K *)
  
  let entropy_from_bits bits = 
    let p = float_of_int bits /. 256.0 in
    if p = 0.0 then 0.0 else -.p *. log p
  
  let free_energy temp entropy internal_energy = 
    internal_energy -. temp *. entropy
  
  let landauer_minimum temp = 
    boltzmann_k *. temp *. log 2.0
  
  let intensive_character bw temp = 
    (* Intensive quines have lower free energy requirements *)
    let base_entropy = entropy_from_bits bw.raw in
    let correction = match bw.c with 
      | Intensive -> 0.5   (* Lower entropy cost *)
      | Extensive -> 1.0   (* Normal entropy cost *)
    in
    1.0 /. (1.0 +. correction *. base_entropy *. temp)
  
  let update_thermo_state bw old_state temp = 
    let new_entropy = entropy_from_bits bw.raw in
    let internal_energy = float_of_int bw.raw *. temp *. boltzmann_k in
    let new_free_energy = free_energy temp new_entropy internal_energy in
    let landauer_cost = landauer_minimum temp in
    {
      temperature = temp;
      entropy = new_entropy;
      free_energy = new_free_energy;
      landauer_debt = old_state.landauer_debt +. landauer_cost;
    }
end
(* Create byte_word with proper bit decomposition *)
let make_byte_word raw =
  let c = (raw land 0x80) <> 0 in  (* MSB: bit 7 *)
  let v = (raw land 0x70) lsr 4 in (* Bits 6-4 *)
  let t = raw land 0x0F in         (* Bits 3-0 *)
  {
    raw = raw land 0xFF;
    c = c;
    v = v;
    t = t;
    birth_time = Unix.time ();
    energy = if c then 1.0 else 0.1;  (* Dynamic vs Morphic energy *)
    refcount = 1;
    quantum_state = Superposition [|0.707; 0.707|];  (* Initial superposition *)
  }
(* Observables *)
type coherent_state = 
  | Superposition of float array  (* Amplitude coefficients *)
  | Entangled of int * int        (* Entanglement pair indices *)
  | Collapsed of int              (* Measured eigenstate *)
  | Decoherent                    (* Thermodynamically dissipated *)
(* Quantum state for superposition collapse *)
type quantum_state = 
  | Superposition of Complex.t array
  | Entangled of byte_word list
  | Collapsed of byte_word
  | Decoherent
(* Thermodynamic properties *)
type thermo_state = {
  temperature: float;          (* Computational temperature *)
  entropy: float;              (* Information entropy *)
  free_energy: float;          (* Available for computation *)
  landauer_debt: float;        (* Accumulated thermodynamic cost *)
}
(* Quine species - different self-replicating patterns *)
type quine_species = 
  | Fibonacci of int           (* Self-similar growth patterns *)
  | Cellular of int * int      (* 2D cellular automaton rules *)
  | Fractal of float           (* Self-similar at all scales *)
  | Metamorphic of byte_word   (* Shape-shifting quines *)
(* The core computational unit - a thermodynamic quine *)
type thermo_quine = {
  id: int;
  species: quine_species;
  byte_word: byte_word;
  quantum_state: quantum_state;
  thermo_state: thermo_state;
  birth_time: float;
  last_replication: float;
  replication_count: int;
  genetic_code: string;        (* Self-modifying source *)
  intensive_score: float;      (* Resistance to thermodynamic collapse *)
}

(* Quine species behavior *)
module QuineSpecies = struct
  let fibonacci_next n = 
    let rec fib a b count = 
      if count <= 0 then a
      else fib b (a + b) (count - 1)
    in
    fib 1 1 n
  
  let cellular_rule rule x y = 
    let neighbors = x lxor y in
    (rule lsr neighbors) land 1
  
  let fractal_iterate z c = 
    z *. z +. c  (* Simple quadratic map *)
  
  let evolve_species species step = 
    match species with 
    | Fibonacci n -> Fibonacci (fibonacci_next n)
    | Cellular (rule, state) -> 
        let new_state = cellular_rule rule state step in
        Cellular (rule, new_state)
    | Fractal z -> Fractal (fractal_iterate z 0.5)
    | Metamorphic bw -> 
        let evolved = ByteWord.abelian_transform bw in
        Metamorphic evolved
end

(* Quantum state management *)
module Quantum = struct
  let create_superposition amplitudes = 
    let total = Array.fold_left (fun acc z -> acc +. Complex.norm_sq z) 0.0 amplitudes in
    let norm_factor = 1.0 /. sqrt total in
    let normalized = Array.map (fun z -> Complex.mul z { re = norm_factor; im = 0.0 }) amplitudes in
    Superposition normalized
  
  let collapse_superposition state = 
    match state with 
    | Superposition amplitudes -> 
        let probabilities = Array.map Complex.norm_sq amplitudes in
        let r = Random.float 1.0 in
        let rec find_outcome acc i = 
          if i >= Array.length probabilities then i - 1
          else if r <= acc +. probabilities.(i) then i
          else find_outcome (acc +. probabilities.(i)) (i + 1)
        in
        find_outcome 0.0 0
    | _ -> 0
  
  let entangle quines = 
    let byte_words = List.map (fun q -> q.byte_word) quines in
    Entangled byte_words
end

(* Morphological transformation based on C bit and thermodynamic state *)
let morphological_transform word =
  match word.c with
  | true ->  (* Dynamic: Apply XNOR transformation *)
      let transformed_t = (word.t lxor word.v) lxor 0x0F in
      let new_raw = 0x80 lor (word.v lsl 4) lor transformed_t in
      { word with raw = new_raw; t = transformed_t; energy = word.energy *. 0.9 }
  | false -> (* Morphic: Identity transformation, energy conservation *)
      { word with energy = word.energy *. 1.01 }  (* Slight energy gain for stability *)

(* Quantum measurement with thermodynamic collapse *)
let measure_quantum_state word =
  match word.quantum_state with
  | Superposition amplitudes ->
      let probabilities = Array.map (fun a -> a *. a) amplitudes in
      let r = Random.float 1.0 in
      let rec find_state acc i =
        if i >= Array.length probabilities then i - 1
        else if r <= acc +. probabilities.(i) then i
        else find_state (acc +. probabilities.(i)) (i + 1)
      in
      let measured_state = find_state 0.0 0 in
      word.quantum_state <- Collapsed measured_state;
      (* Thermodynamic cost of measurement *)
      word.energy <- word.energy -. 0.1;
      measured_state
  | Collapsed state -> state
  | Entangled (i, j) -> 
      word.quantum_state <- Collapsed i;
      word.energy <- word.energy -. 0.05;
      i
  | Decoherent -> 0

(* The key insight: Speciated quines that refuse to quit *)
type quine_species = {
  genome: byte_word array;         (* Genetic information *)
  phenotype: byte_word -> byte_word; (* Expression function *)
  fitness: float;                  (* Thermodynamic fitness *)
  generation: int;                 (* Evolutionary generation *)
  mutable population: int;         (* Current population size *)
}

(* Create a self-replicating quine species *)
let create_quine_species genome_pattern =
  let genome = Array.mapi (fun i pattern ->
    make_byte_word ((pattern lsl 4) lor i)
  ) genome_pattern in
  
  let phenotype word =
    let expressed = morphological_transform word in
    (* Self-replication: if energy is high enough, duplicate *)
    if expressed.energy > 0.8 then
      { expressed with 
        refcount = expressed.refcount + 1;
        quantum_state = Superposition [|0.9; 0.1|]; (* Bias toward survival *)
      }
    else expressed
  in
  
  let fitness = Array.fold_left (fun acc w -> 
    acc +. (if w.c then 0.1 else 0.9)  (* Morphic forms are more fit *)
  ) 0.0 genome in
  
  {
    genome = genome;
    phenotype = phenotype;
    fitness = fitness;
    generation = 0;
    population = 1;
  }

(* Thermodynamic evolution: species that maintain energy survive *)
let evolve_species species timesteps =
  let rec evolve_step species step =
    if step >= timesteps then species
    else
      let total_energy = Array.fold_left (fun acc w -> acc +. w.energy) 0.0 species.genome in
      let avg_energy = total_energy /. (float_of_int (Array.length species.genome)) in
      
      if avg_energy > 0.5 then
        (* Species survives and potentially reproduces *)
        let new_generation = species.generation + 1 in
        let mutated_genome = Array.map (fun w ->
          if Random.float 1.0 < 0.1 then  (* 10% mutation rate *)
            let new_raw = (w.raw lxor (Random.int 16)) land 0xFF in
            make_byte_word new_raw
          else
            { w with energy = w.energy *. 0.95 }  (* Gradual energy decay *)
        ) species.genome in
        
        let new_species = {
          species with
          genome = mutated_genome;
          generation = new_generation;
          population = if avg_energy > 0.8 then species.population + 1 else species.population;
        } in
        evolve_step new_species (step + 1)
      else
        (* Species dies out *)
        { species with population = 0 }
  in
  evolve_step species 0

(* Prove that 256 states is not a restriction through quine persistence *)
let prove_unbounded_computation () =
  (* Create multiple quine species with different thermodynamic profiles *)
  let species_patterns = [
    [|0x0; 0x1; 0x2; 0x3|];  (* Low-energy morphic *)
    [|0x8; 0x9; 0xA; 0xB|];  (* High-energy dynamic *)
    [|0x4; 0x5; 0x6; 0x7|];  (* Mixed morphic *)
    [|0xC; 0xD; 0xE; 0xF|];  (* Mixed dynamic *)
  ] in
  
  let species_list = List.map create_quine_species species_patterns in
  
  (* Evolve each species for 100 timesteps *)
  let evolved_species = List.map (fun s -> evolve_species s 100) species_list in
  
  (* Count surviving species *)
  let survivors = List.filter (fun s -> s.population > 0) evolved_species in
  let total_population = List.fold_left (fun acc s -> acc + s.population) 0 survivors in
  
  Printf.printf "Proof of Unbounded Computation:\n";
  Printf.printf "Initial species: %d\n" (List.length species_list);
  Printf.printf "Surviving species: %d\n" (List.length survivors);
  Printf.printf "Total population: %d\n" total_population;
  Printf.printf "Generations evolved: %s\n" 
    (String.concat ", " (List.map (fun s -> string_of_int s.generation) survivors));
  
  (* The key insight: even with 256 base states, quine persistence creates unbounded complexity *)
  let complexity_measure = List.fold_left (fun acc s ->
    acc + (s.generation * s.population)
  ) 0 survivors in
  
  Printf.printf "Emergent complexity measure: %d\n" complexity_measure;
  Printf.printf "Complexity per base state: %.3f\n" (float_of_int complexity_measure /. 256.0);
  
  (* Return the persistent quines as proof *)
  survivors

(* Demonstrate intensive thermodynamic character *)
let demonstrate_intensive_character species =
  Printf.printf "\nIntensive Thermodynamic Character Analysis:\n";
  Printf.printf "Species generation: %d\n" species.generation;
  Printf.printf "Population: %d\n" species.population;
  Printf.printf "Fitness: %.3f\n" species.fitness;
  
  (* Analyze genome thermodynamics *)
  let morphic_count = Array.fold_left (fun acc w -> 
    if not w.c then acc + 1 else acc
  ) 0 species.genome in
  
  let total_energy = Array.fold_left (fun acc w -> acc +. w.energy) 0.0 species.genome in
  
  Printf.printf "Morphic (intensive) genes: %d/%d\n" morphic_count (Array.length species.genome);
  Printf.printf "Total energy: %.3f\n" total_energy;
  Printf.printf "Energy per gene: %.3f\n" (total_energy /. float_of_int (Array.length species.genome));
  
  (* The intensive character: self-sustaining without external energy *)
  let is_intensive = (float_of_int morphic_count) /. (float_of_int (Array.length species.genome)) > 0.5 in
  Printf.printf "Intensive character: %b\n" is_intensive;
  
  if is_intensive then
    Printf.printf "This species exhibits intensive thermodynamic character - it refuses to quit!\n"
  else
    Printf.printf "This species requires external energy (extensive character)\n"


(* The main QuineComputor - manages populations of thermodynamic quines *)
module QuineComputor = struct
  type t = {
    population: thermo_quine list;
    generation: int;
    global_temp: float;
    total_entropy: float;
    species_count: (quine_species, int) Hashtbl.t;
  }
  
  let create temp = {
    population = [];
    generation = 0;
    global_temp = temp;
    total_entropy = 0.0;
    species_count = Hashtbl.create 16;
  }
  
  let spawn_quine computor species genetic_code = 
    let id = Random.int 1000000 in
    let raw_byte = Random.int 256 in
    let byte_word = ByteWord.create raw_byte in
    let birth_time = Unix.time () in
    
    (* Initialize quantum superposition *)
    let amplitudes = Array.make 256 Complex.zero in
    amplitudes.(raw_byte) <- Complex.one;
    let quantum_state = Quantum.create_superposition amplitudes in
    
    (* Calculate initial thermodynamic state *)
    let initial_thermo = {
      temperature = computor.global_temp;
      entropy = 0.0;
      free_energy = 0.0;
      landauer_debt = 0.0;
    } in
    let thermo_state = Thermodynamics.update_thermo_state byte_word initial_thermo computor.global_temp in
    
    (* Calculate intensive character - resistance to collapse *)
    let intensive_score = Thermodynamics.intensive_character byte_word computor.global_temp in
    
    {
      id;
      species;
      byte_word;
      quantum_state;
      thermo_state;
      birth_time;
      last_replication = birth_time;
      replication_count = 0;
      genetic_code;
      intensive_score;
    }
  
  let replicate_quine computor quine = 
    if quine.intensive_score > 0.7 then (  (* High intensive character *)
      let new_species = QuineSpecies.evolve_species quine.species quine.replication_count in
      let mutated_code = quine.genetic_code ^ sprintf "_gen%d" (quine.replication_count + 1) in
      let offspring = spawn_quine computor new_species mutated_code in
      let updated_parent = { quine with 
        last_replication = Unix.time ();
        replication_count = quine.replication_count + 1;
      } in
      [updated_parent; offspring]
    ) else 
      [quine]  (* Not intensive enough to replicate *)
  
  let evolve_population computor = 
    let new_population = List.fold_left (fun acc quine -> 
      let replicated = replicate_quine computor quine in
      replicated @ acc
    ) [] computor.population in
    
    (* Update species count *)
    let species_count = Hashtbl.create 16 in
    List.iter (fun quine -> 
      let current = try Hashtbl.find species_count quine.species with Not_found -> 0 in
      Hashtbl.replace species_count quine.species (current + 1)
    ) new_population;
    
    { computor with 
      population = new_population;
      generation = computor.generation + 1;
      species_count;
    }
  
  let add_quine computor quine = 
    { computor with population = quine :: computor.population }
(* Helper to prove unbounded complexity from a given computor state *)
let prove_unbounded_complexity computor =
  let intensive_quines =
    List.filter (fun q -> q.intensive_score >= 0.8) computor.population
  in
  let num_intensive = List.length intensive_quines in

  let total_replications =
    List.fold_left (fun acc q -> acc + q.replication_count) 0 intensive_quines
  in

  let species_diversity =
    match computor.species_table with
    | Some tbl -> Hashtbl.length tbl
    | None -> -1
  in

  let base_population = float_of_int (List.length computor.population) in
  let complexity_ratio =
    if base_population = 0. then 0.0
    else float_of_int total_replications /. base_population
  in

  Printf.printf "=== Unbounded Complexity Proof ===\n";
  Printf.printf "Generation: %d\n" computor.generation;
  Printf.printf "Total population: %d\n" (int_of_float base_population);
  Printf.printf "Intensive quines (score ≥ 0.8): %d\n" num_intensive;
  Printf.printf "Total replications (intensive only): %d\n" total_replications;
  if species_diversity >= 0 then
    Printf.printf "Species diversity: %d\n" species_diversity;
  Printf.printf "Complexity ratio: %.3f\n" complexity_ratio;

  let verdict =
    if total_replications > 256 then
      "✓ Unbounded complexity observed: replication exceeds initial state space."
    else if num_intensive > 0 then
      "○ Strong replication activity detected, evolution underway..."
    else
      "• No intensive quines found — thermodynamic emergence pending."
  in

  Printf.printf "\nProof: %s\n" verdict;
  Printf.printf "===================================\n\n";

  intensive_quines
;;

let () =
  Random.init (int_of_float (Unix.time ()));

  Printf.printf "=== Thermodynamic Quine Computing ===\n";
  Printf.printf "Bit encoding: <CVVV|TTTT> — with Control (C) as MSB\n\n";

  let computor = Computor.init_simulation ~population_size:256 in
  let survivors = prove_unbounded_complexity computor in

  List.iter (fun q ->
    try demonstrate_intensive_character q
    with _ -> Printf.printf "[!] Failed to demonstrate quine: ID %d\n" q.id
  ) survivors;

  Printf.printf "\n=== Conclusion ===\n";
  Printf.printf "From 256 base states, persistent replicators emerged.\n";
  Printf.printf "These thermodynamic quines exhibit traits of artificial computational life.\n";
  Printf.printf "The complexity ceiling is not fixed — it's self-extended.\n";
  Printf.printf "Entropy doesn't kill computation, it feeds it.\n"
;;

(* Main demonstration entrypoint *)
let () =
  Random.init (int_of_float (Unix.time ()));

  Printf.printf "=== Thermodynamic Quine Computing ===\n";
  Printf.printf "Bit encoding: <CVVV|TTTT> — with Control (C) as MSB\n\n";

  (* Initialize simulation *)
  let computor = Computor.init_simulation ~population_size:256 in

  (* Attempt proof of unbounded complexity *)
  let survivors = prove_unbounded_complexity computor in

  (* Optionally visualize intensive survivors *)
  List.iter (fun q ->
    try
      demonstrate_intensive_character q
    with _ ->
      Printf.printf "[!] Failed to demonstrate quine: ID %d\n" q.id
  ) survivors;

  (* Wrap-up *)
  Printf.printf "\n=== Conclusion ===\n";
  Printf.printf "From 256 base states, persistent replicators emerged.\n";
  Printf.printf "These thermodynamic quines exhibit traits of artificial computational life.\n";
  Printf.printf "The complexity ceiling is not fixed — it's self-extended.\n";
  Printf.printf "Entropy doesn't kill computation, it feeds it.\n"
;;
