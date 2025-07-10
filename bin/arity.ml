[@@@warning "-32-37"]
(* 
https://github.com/MOONLAPSED/demiurge Morphological Source Code &
Demiurge © 2025 by Moonlapsed is licensed under:
https://creativecommons.org/licenses/by/4.0/ CC BY 4.0
*)

open Printf

(* Arity as topological winding number *)
module Arity = struct
  type t = {
    magnitude_winding: int;  (* Winding around the "cardinality" hole *)
    phase_winding: int;      (* Winding around the "direction" hole *)
    total_arity: int;        (* Total number of arguments/connections *)
  }
  
  let nullary = { magnitude_winding = 0; phase_winding = 0; total_arity = 0 }
  let unary = { magnitude_winding = 1; phase_winding = 0; total_arity = 1 }
  let binary = { magnitude_winding = 1; phase_winding = 1; total_arity = 2 }
  let ternary = { magnitude_winding = 2; phase_winding = 1; total_arity = 3 }
  
  (* Toroidal composition - how arities combine *)
  let compose a1 a2 = {
    magnitude_winding = a1.magnitude_winding + a2.magnitude_winding;
    phase_winding = a1.phase_winding + a2.phase_winding;
    total_arity = a1.total_arity + a2.total_arity;
  }
  
  (* Topological invariant - Euler characteristic *)
  let euler_characteristic arity = 
    2 - 2 * (arity.magnitude_winding + arity.phase_winding)
  
  (* Church-Turing winding density *)
  let winding_density arity = 
    if arity.total_arity = 0 then 0.0
    else (float_of_int (arity.magnitude_winding + arity.phase_winding)) /. (float_of_int arity.total_arity)
end

(* Enhanced transformation rules with arity *)
module ArityTransformation = struct
  type rule = {
    base_rule: MorphologicalTypes.transformation_rule;
    arity: Arity.t;
    topological_charge: int;  (* Conserved quantity under transformations *)
  }
  
  (* Arity-aware transformation rules *)
  let identity_rule = { 
    base_rule = MorphologicalTypes.Identity; 
    arity = Arity.unary;
    topological_charge = 0;
  }
  
  let conjugate_rule = { 
    base_rule = MorphologicalTypes.Conjugate; 
    arity = Arity.unary;
    topological_charge = 1;
  }
  
  let binary_compose_rule = { 
    base_rule = MorphologicalTypes.Transpose; 
    arity = Arity.binary;
    topological_charge = 0;
  }
  
  let ternary_entangle_rule = { 
    base_rule = MorphologicalTypes.Adjoint; 
    arity = Arity.ternary;
    topological_charge = -1;
  }
  
  (* Check if transformation preserves topological charge *)
  let is_charge_conserving rule1 rule2 =
    rule1.topological_charge + rule2.topological_charge = 0
end

(* Enhanced ByteWord with explicit arity encoding *)
module ArityByteWord = struct
  type t = {
    (* Original ByteWord fields *)
    raw: int;
    t_field: int;
    v_field: int;
    c_bit: character;
    birth_time: float;
    mutable energy: float;
    mutable refcount: int;
    mutable thermo_state: CoreTypes.thermo_state;
    mutable quantum_state: MorphologicalTypes.quantum_thermo_state;
    
    (* New arity-aware fields *)
    arity: Arity.t;
    transformation_rule: ArityTransformation.rule;
    mutable topological_charge: int;
    
    (* Toroidal topology fields *)
    mutable magnitude_position: float;  (* Position on magnitude cycle *)
    mutable phase_position: float;      (* Position on phase cycle *)
    mutable winding_history: (float * float) list;  (* Track winding path *)
  }
  
  let extract_arity_from_raw raw =
    let magnitude_wind = (raw land 0x03) in           (* Bits 0-1 *)
    let phase_wind = ((raw lsr 2) land 0x03) in       (* Bits 2-3 *)
    let total = magnitude_wind + phase_wind in
    {
      Arity.magnitude_winding = magnitude_wind;
      phase_winding = phase_wind;
      total_arity = total;
    }
  
  let arity_aware_transformation_rule v_field arity =
    let base_rule = match v_field with
      | 0 -> MorphologicalTypes.Identity
      | 1 -> MorphologicalTypes.Conjugate
      | 2 -> MorphologicalTypes.Transpose
      | 3 -> MorphologicalTypes.Adjoint
      | 4 -> MorphologicalTypes.Inverse
      | 5 -> MorphologicalTypes.Dual
      | 6 -> MorphologicalTypes.Complement
      | 7 -> MorphologicalTypes.Negation
      | _ -> failwith "Invalid v_field"
    in
    let topological_charge = match arity.total_arity with
      | 0 -> 0
      | 1 -> if v_field mod 2 = 0 then 0 else 1
      | 2 -> if v_field < 4 then 0 else -1
      | _ -> (v_field - 4) (* Higher arity transformations *)
    in
    { ArityTransformation.base_rule = base_rule; arity; topological_charge }
  
  let create ?(temp=300.0) raw =
    if raw < 0 || raw > 255 then
      invalid_arg "ByteWord must be 8-bit (0-255)"
    else
      let (t_field, v_field, c_bit) = ByteWord.extract_fields raw in
      let arity = extract_arity_from_raw raw in
      let transformation_rule = arity_aware_transformation_rule v_field arity in
      let initial_energy = match c_bit with 
        | Extensive -> 1.0 *. (float_of_int arity.total_arity)
        | Intensive -> 0.1 /. (1.0 +. float_of_int arity.total_arity)
      in
      
      let initial_thermo = ByteWord.initial_thermo_state temp in
      let initial_qstate = 
        let amplitudes = Array.make (max 2 (arity.total_arity + 1)) QComplex.zero in
        amplitudes.(0) <- QComplex.one;
        MorphologicalTypes.Superposition (amplitudes, initial_thermo) 
      in
      
      {
        raw; t_field; v_field; c_bit; arity; transformation_rule;
        birth_time = Unix.time ();
        energy = initial_energy;
        refcount = 1;
        thermo_state = initial_thermo;
        quantum_state = initial_qstate;
        topological_charge = transformation_rule.topological_charge;
        magnitude_position = 0.0;
        phase_position = 0.0;
        winding_history = [];
      }
  
  (* Toroidal evolution - move along the torus *)
  let evolve_toroidal bw dt =
    let magnitude_velocity = bw.energy *. (float_of_int bw.arity.magnitude_winding) in
    let phase_velocity = bw.energy *. (float_of_int bw.arity.phase_winding) in
    
    let new_mag_pos = bw.magnitude_position +. dt *. magnitude_velocity in
    let new_phase_pos = bw.phase_position +. dt *. phase_velocity in
    
    (* Wrap around the torus (mod 2π) *)
    bw.magnitude_position <- mod_float new_mag_pos (2.0 *. Float.pi);
    bw.phase_position <- mod_float new_phase_pos (2.0 *. Float.pi);
    
    (* Record winding history *)
    bw.winding_history <- (bw.magnitude_position, bw.phase_position) :: bw.winding_history;
    
    (* Update quantum state based on toroidal position *)
    match bw.quantum_state with
    | MorphologicalTypes.Superposition (amplitudes, thermo) ->
        let phase_factor = QComplex.{ 
          re = cos bw.phase_position; 
          im = sin bw.phase_position 
        } in
        let magnitude_factor = exp (-.bw.magnitude_position *. 0.1) in
        let evolved_amplitudes = Array.mapi (fun i z -> 
          let scaled = QComplex.scale magnitude_factor z in
          if i = 0 then QComplex.mul scaled phase_factor else scaled
        ) amplitudes in
        bw.quantum_state <- MorphologicalTypes.Superposition (evolved_amplitudes, thermo)
    | _ -> ()
  
  (* Arity-aware composition *)
  let compose_arity_aware bw1 bw2 =
    if not (ArityTransformation.is_charge_conserving bw1.transformation_rule bw2.transformation_rule) then
      failwith "Cannot compose: topological charge not conserved"
    else
      let combined_arity = Arity.compose bw1.arity bw2.arity in
      let combined_raw = (bw1.raw + bw2.raw) land 0xFF in
      let combined_bw = create combined_raw in
      
      (* Inherit toroidal positions *)
      combined_bw.magnitude_position <- (bw1.magnitude_position +. bw2.magnitude_position) /. 2.0;
      combined_bw.phase_position <- (bw1.phase_position +. bw2.phase_position) /. 2.0;
      combined_bw.winding_history <- bw1.winding_history @ bw2.winding_history;
      
      combined_bw
  
  (* Check if ByteWord has completed a full winding *)
  let has_completed_winding bw =
    let magnitude_windings = bw.magnitude_position /. (2.0 *. Float.pi) in
    let phase_windings = bw.phase_position /. (2.0 *. Float.pi) in
    
    let expected_mag_windings = float_of_int bw.arity.magnitude_winding in
    let expected_phase_windings = float_of_int bw.arity.phase_winding in
    
    (abs_float (magnitude_windings -. expected_mag_windings) < 0.1) &&
    (abs_float (phase_windings -. expected_phase_windings) < 0.1)
  
  (* Compute topological invariant *)
  let topological_invariant bw =
    let euler_char = Arity.euler_characteristic bw.arity in
    let winding_density = Arity.winding_density bw.arity in
    let charge_contribution = float_of_int bw.topological_charge in
    
    float_of_int euler_char +. winding_density +. charge_contribution
  
  (* Display toroidal state *)
  let to_toroidal_string bw =
    Printf.sprintf "Torus[mag=%.3f, phase=%.3f, arity=%d|%d, charge=%d, windings=%d]"
      bw.magnitude_position
      bw.phase_position
      bw.arity.magnitude_winding
      bw.arity.phase_winding
      bw.topological_charge
      (List.length bw.winding_history)
end

(* Arity-aware computation system *)
module ArityComputation = struct
  type computation_graph = {
    nodes: ArityByteWord.t array;
    edges: (int * int * Arity.t) array;  (* (from, to, arity) *)
    mutable total_topological_charge: int;
  }
  
  let create_computation_graph nodes edges =
    let total_charge = Array.fold_left (fun acc node -> 
      acc + node.ArityByteWord.topological_charge
    ) 0 nodes in
    { nodes; edges; total_topological_charge = total_charge }
  
  (* Check if computation preserves topological invariants *)
  let is_topologically_valid graph =
    let node_charges = Array.fold_left (fun acc node ->
      acc + node.ArityByteWord.topological_charge
    ) 0 graph.nodes in
    
    let edge_contributions = Array.fold_left (fun acc (_, _, arity) ->
      acc + (Arity.euler_characteristic arity)
    ) 0 graph.edges in
    
    node_charges + edge_contributions = 0
  
  (* Execute computation with arity checking *)
  let execute_computation graph =
    if not (is_topologically_valid graph) then
      failwith "Computation violates topological invariants"
    else
      (* Evolve each node on its torus *)
      let dt = 0.01 in
      Array.iter (fun node -> ArityByteWord.evolve_toroidal node dt) graph.nodes;
      
      (* Check for completed windings *)
      let completed_nodes = Array.fold_left (fun acc node ->
        if ArityByteWord.has_completed_winding node then node :: acc else acc
      ) [] graph.nodes in
      
      completed_nodes
end

(* Example usage *)
let example_arity_computation () =
  let bw1 = ArityByteWord.create 42 in
  let bw2 = ArityByteWord.create 84 in
  let bw3 = ArityByteWord.create 126 in
  
  let nodes = [| bw1; bw2; bw3 |] in
  let edges = [| (0, 1, Arity.binary); (1, 2, Arity.unary) |] in
  
  let graph = ArityComputation.create_computation_graph nodes edges in
  
  Printf.printf "Topologically valid: %b\n" (ArityComputation.is_topologically_valid graph);
  
  (* Evolve the system *)
  let completed = ArityComputation.execute_computation graph in
  Printf.printf "Completed windings: %d nodes\n" (List.length completed);
  
  (* Show toroidal states *)
  Array.iteri (fun i node ->
    Printf.printf "Node %d: %s\n" i (ArityByteWord.to_toroidal_string node)
  ) nodes