[@@@warning "-32-37"]
(* 
https://github.com/MOONLAPSED/demiurge Morphological Source Code &
Demiurge © 2025 by Moonlapsed is licensed under:
https://creativecommons.org/licenses/by/4.0/ CC BY 4.0
*)

(* observation.ml *)

(** A Bohmian C-bit: carries a payload of type 'a, but remains latent
* until observed, then “collapses” to deliver its content.
* In a traditional VM or CPU, a syscall just “happens.” But in morphic ByteWord
* framework, that bit is carrying an entire latent narrative—its winding path,
* its thermodynamic character, its observer-observed history—waiting to blossom
* into full ontogeny when it’s “absorbed” by the next layer of observation *)

type 'a cbit = {
  id        : int;
  mutable seen : bool;
  payload   : 'a Lazy.t;
}

let next_id = ref 0

let make_cbit thunk =
  let id = !next_id in
  incr next_id;
  { id; seen = false; payload = Lazy.from_val thunk }

(* Observe the cbit: forces payload evaluation and marks it as seen *)
let observe c =
  if not c.seen then begin
    c.seen <- true;
    Lazy.force c.payload
  end else
    failwith (Printf.sprintf "C-bit %d already absorbed!" c.id)

(* Example usage *)
let () =
  let photon = make_cbit (fun () ->
    (* “Payload”—can be anything: computation, I/O, data *)
    Printf.printf "Payload materializing at absorption!\n";
    42
  ) in

  Printf.printf "Photon created (ID %d), unobserved.\n" photon.id;

  let result = observe photon in
  Printf.printf "Absorbed payload: %d\n" result;

  (* A second observation is disallowed: truly one-shot! *)
  (* let _ = observe photon in *)  (* would raise *)
  ()
