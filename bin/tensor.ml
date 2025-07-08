(* file: tensor.ml *)

open Complex

(* The .mli file makes 't' abstract to the outside,
  * but here we define its concrete form. *)
  (* Note: You don't need 'val' or the type signatures here, as they 
    * are inferred and checked against the .mli file. *)
type variance_t = Covariant | Contravariant

type t = {
  data: Complex.t array;
  shape: int list;
  variance: variance_t list;
  rank: int;
}
let create data shape variance =
  let rank = List.length shape in
  if rank <> List.length variance then
    failwith "Rank must match length of variance list"
  else
    (* Simple check for total size *)
    let expected_size = List.fold_left ( * ) 1 shape in
    if (Array.length data) <> expected_size then
      failwith "Data array size does not match shape"
    else
      { data; shape; variance; rank }
(* Helper to create a ket vector from a simple list *)
let ket components =
  let data = Array.of_list (List.map (fun r -> { re = r; im = 0.0 }) components) in
  create data [List.length components] [Covariant]
(* Helper to create a bra vector from a simple list *)
let bra components =
  let data = Array.of_list (List.map (fun r -> { re = r; im = 0.0 }) components) in
  create data [List.length components] [Contravariant]
let get_data tensor = tensor.data
let contract v1 v2 =
  if v1.rank <> 1 || v2.rank <> 1 then
    failwith "Simple contract only for rank-1 tensors (vectors)";
  if List.hd v1.variance = List.hd v2.variance then
    failwith "Cannot contract indices with same variance";
  if List.hd v1.shape <> List.hd v2.shape then
    failwith "Dimensions must match for contraction";

  let sum = ref Complex.zero in
  for i = 0 to (Array.length v1.data) - 1 do
    sum := Complex.add !sum (Complex.mul v1.data.(i) v2.data.(i))
  done;
  (* Create an array of size 1, containing the value !sum *)
  create (Array.make 1 !sum) [] []

let apply_gate gate state =
  if gate.rank <> 2 || state.rank <> 1 then
    failwith "Gate must be rank 2 (matrix), state must be rank 1 (vector)";
  let rows = List.nth gate.shape 0 in
  let cols = List.nth gate.shape 1 in
  if cols <> List.hd state.shape then
    failwith "Gate columns must match state vector size";
  (* The output will be a new vector of size 'rows' *)
  let new_data = Array.make rows Complex.zero in
  (*
     THIS IS EINSTEIN SUMMATION IN CODE: y_i = M_ij * x_j
     The loop over 'j' is the "summation over the repeated index".
     The loop over 'i' is the "free index" that remains in the result.
  *)
  for i = 0 to rows - 1 do
    let sum_j = ref Complex.zero in
    for j = 0 to cols - 1 do
      let m_ij = gate.data.(i * cols + j) in (* Indexing into the flat matrix array *)
      let x_j = state.data.(j) in
      sum_j := Complex.add !sum_j (Complex.mul m_ij x_j)
    done;
    new_data.(i) <- !sum_j
  done;
  (* The result is a new covariant vector (a new ket) *)
  create new_data [rows] [Covariant]
(* --- Pauli Gates --- *)
(* These are values, so we use 'let'. *)
let i_gate =
  let data = Array.map (fun r -> {re=r; im=0.0}) [| 1.; 0.; 0.; 1. |] in
  create data [2; 2] [Covariant; Contravariant]

let x_gate =
  let data = Array.map (fun r -> {re=r; im=0.0}) [| 0.; 1.; 1.; 0. |] in
  create data [2; 2] [Covariant; Contravariant]

let y_gate =
  create [|
    zero;                     (* 0 + 0i *)
    { re = 0.0; im = -1.0 };  (* 0 - 1i *)
    { re = 0.0; im =  1.0 };  (* 0 + 1i *)
    zero                      (* 0 + 0i *)
  |] [2; 2] [Covariant; Contravariant]

let z_gate =
  let data = Array.map (fun r -> {re=r; im=0.0}) [| 1.; 0.; 0.; -1. |] in
  create data [2; 2] [Covariant; Contravariant]