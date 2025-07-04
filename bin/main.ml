(* Thermodynamic Quine Computing: Persistent Computational Life Forms *)
(* Building speciated quines with intensive thermodynamic character *)
open Printf
(* Bit ordering: <CVVV|TTTT> with C as MSB for bra-ket row/column vector *)
(* Complex numbers for quantum amplitudes *)
module Complex = struct
  type t = { re: float; im: float }
  let zero = { re = 0.0; im = 0.0 }
  let i = { re = 0.0; im = 1.0 }
  let one  = { re = 1.0; im = 0.0 }
  let add z1 z2 = { re = z1.re +. z2.re; im = z1.im +. z2.im }
  let mul z1 z2 = { 
    re = z1.re *. z2.re -. z1.im *. z2.im;
    im = z1.re *. z2.im +. z1.im *. z2.re
  }
  let conj z = { re = z.re; im = -. z.im }
  let norm_sq z = z.re *. z.re +. z.im *. z.im
  let norm z = sqrt (norm_sq z)
  let scale s z = { re = s *. z.re; im = s *. z.im }
  let to_string z = Printf.sprintf "%.3f + %.3fi" z.re z.im
end
(* Observables *)
(* Morphology + Character states - intensive vs extensive *)
(* C=1: Environment-coupled, high-energy, pointable *)
(* C=0: Self-contained, low-energy, non-pointable *)
type character = 
  | Intensive   (* C=0: Self-contained *)
  | Extensive   (* C=1: Environment-coupled, transformative *)
type coherent_state = 
  | Superposition of float array  (* Amplitude coefficients *)
  | Entangled of int * int        (* Entanglement pair indices *)
  | Collapsed of int              (* Measured eigenstate *)
  | Decoherent                    (* Thermodynamically dissipated *)
(* Thermodynamic properties *)
type thermo_state = {
  temperature: float;          (* Computational temperature *)
  entropy: float;              (* Information entropy *)
  free_energy: float;          (* Available for computation *)
  landauer_debt: float;        (* Accumulated thermodynamic cost *)
}
type morphology = 
  | CBitCharacter of character  (* High/Low: 1/0: dynamic/static*)
  | Morphic of string      (* Stable, intensive, self-contained *)
  | Dynamic of float      (* Extensive, environment-coupled *)
  | Markovian of int  (* Forward-evolving, irreversible *)
  | NonMarkovian of (float * float) (* Reversible with memory *)
(* ByteWord Sliding-register width, non-markovian + thermodynamics-aware *)
type byte_word = {
  raw: int;                    (* Full 8-bit value *)
  character: character;
  c: morphology;               (* MSB: Control/Epistemology bit *)
  v: int;                      (* Bits 6-4: Morphism selector (3 bits) *)
  t: int;                      (* Bits 3-0: State data (4 bits) *)
  birth_time: float;           (* Thermodynamic birth timestamp *)
  mutable energy: float;       (* Current energy state *)
  mutable refcount: int;       (* Reference counting *)
  (* mutable quantum_state: quantum_state; _associated_ with 'observables' *)
}
let extract_c_bit (bw : byte_word) : int =
  match bw.c with
  | CBitCharacter Intensive -> 0
  | CBitCharacter Extensive -> 1
  | Morphic _ -> 2
  | Markovian _ -> 3
  | NonMarkovian _ -> 4
  | Dynamic _ -> 5
(* Quantum state for superposition collapse *)
type quantum_state = 
  | Superposition of Complex.t array
  | Entangled of byte_word list
  | Collapsed of byte_word
  | Decoherent

module ByteWord = struct
  let create raw =
    if raw < 0 || raw > 255 then
      invalid_arg "ByteWord must be 8-bit (0-255)"
    else
      let c_bit = if (raw land 0x80) <> 0 then 1 else 0 in
      let v = (raw lsr 4) land 0x07 in
      let t = raw land 0x0F in
      let character = if c_bit = 1 then Extensive else Intensive in
      {
        raw;
        c = CBitCharacter character;
        character;
        v;
        t;
        birth_time = Unix.time ();
        energy = if c_bit = 1 then 1.0 else 0.1;
        refcount = 1;
      }

  let morphology_to_c_bit = function
    | CBitCharacter Intensive -> 0
    | CBitCharacter Extensive -> 1
    | Morphic _ -> 2
    | Markovian _ -> 3
    | NonMarkovian _ -> 4
    | Dynamic _ -> 5


  (* helper: convert an int to a binary string of exactly [width] bits *)
  let bin_of_int ~width n =
    let rec build bits acc =
      if bits = 0 then acc
      else
        let mask = 1 lsl (bits - 1) in
        let bit = if n land mask <> 0 then "1" else "0" in
        build (bits - 1) (acc ^ bit)
    in
    build width ""

  (* to_bra_ket using that helper *)
  let to_bra_ket bw =
    (* extract the control bit *)
    let c_bit = match bw.c with
      | CBitCharacter Intensive -> 0
      | CBitCharacter Extensive -> 1
      | _ -> failwith "to_bra_ket: unsupported morphology" in
    (* format v as 3 bits, t as 4 bits *)
    let v_str = bin_of_int ~width:3 bw.v in
    let t_str = bin_of_int ~width:4 bw.t in
    sprintf "<%d%s|%s>" c_bit v_str t_str

  let is_pointable bw =
    match bw.c with
    | CBitCharacter Extensive -> true
    | _ -> false
  (* XNOR-based Abelian transformation *)
  let xnor a b width = 
    let mask = (1 lsl width) - 1 in
    (lnot (a lxor b)) land mask
  
  let abelian_transform bw = 
    match bw.c with 
    | CBitCharacter Extensive -> { bw with t = xnor bw.t bw.v 4 }
    | CBitCharacter Intensive -> bw  (* Identity - quines preserve themselves *)
    | _ -> bw  (* default case for other morphology variants *)

  let conjugate bw = { bw with v = 7 - bw.v }  (* Bit-flip morphism *)

  let dual bw = 
    let new_c = match bw.c with
      | CBitCharacter Intensive -> CBitCharacter Extensive
      | CBitCharacter Extensive -> CBitCharacter Intensive
      | other -> other  (* preserve other morphologies *)
    in
    { bw with c = new_c }


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
(* Morphological transformation based on C bit and thermodynamic state *)
let morphological_transform word =
  match word.c with
  | true ->  (* Dynamic: Apply XNOR transformation *)
      let transformed_t = (word.t lxor word.v) lxor 0x0F in
      let new_raw = 0x80 lor (word.v lsl 4) lor transformed_t in
      { word with raw = new_raw; t = transformed_t; energy = word.energy *. 0.9 }
  | false -> (* Morphic: Identity transformation, energy conservation *)
      { word with energy = word.energy *. 1.01 }  (* Slight energy gain for stability *)

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
(* The key insight: Speciated quines that refuse to quit *)
type quine_species = {
  genome: byte_word array;         (* Genetic information *)
  phenotype: byte_word -> byte_word; (* Expression function *)
  fitness: float;                  (* Thermodynamic fitness *)
  generation: int;                 (* Evolutionary generation *)
  mutable population: int;         (* Current population size *)
}
