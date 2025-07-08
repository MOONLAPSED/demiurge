[@@@warning "-32-37"]
(* 
https://github.com/MOONLAPSED/demiurge Morphological Source Code &
Demiurge © 2025 by Moonlapsed is licensed under:
https://creativecommons.org/licenses/by/4.0/ CC BY 4.0
*)

open Tensor

let () =
  print_endline "Testing the new Tensor module...";

  (* Now you can use the functions directly because of 'open' *)
  let my_ket = ket [1.0; 0.0] in
  let my_bra = bra [0.0; 1.0] in
  
  let result = contract my_bra my_ket in
  let value = (get_data result).(0) in
  Printf.printf "<1|0> = %f + %fi\n" value.Complex.re value.Complex.im;

  (* Alternatively, without 'open', you use dot notation *)
  let ket_1 = Tensor.apply_gate Tensor.x_gate my_ket in
  let ket_1_data = Tensor.get_data ket_1 in
  Printf.printf "X|0> = [%f; %f]\n" ket_1_data.(0).re ket_1_data.(1).re;