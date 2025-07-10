[@@@warning "-32-37"]
(* 
https://github.com/MOONLAPSED/demiurge Morphological Source Code &
Demiurge © 2025 by Moonlapsed is licensed under:
https://creativecommons.org/licenses/by/4.0/ CC BY 4.0
*)

(* file: tensor.mli *)
(** The type representing geometric variance: Covariant or Contravariant. *)
type variance_t = Covariant | Contravariant
(** The abstract type of a tensor. Other modules can use this type but cannot
    see its internal record structure. This is good encapsulation. *)
type t


(** [create data shape variance] creates a new tensor.
    @param data A flat array of complex numbers representing the tensor components.
    @param shape A list of integers defining the dimensions of the tensor.
    @param variance A list of [variance_t] defining the character of each axis.
    @raise Failure if data size does not match shape, or if rank does not match variance list length. *)
val create : Complex.t array -> int list -> variance_t list -> t

(** [ket components] creates a rank-1 covariant tensor (a ket vector). *)
val ket : float list -> t

(** [bra components] creates a rank-1 contravariant tensor (a bra vector). *)
val bra : float list -> t

(** [get_data tensor] safely extracts the data array from a tensor. *)
val get_data : t -> Complex.t array

(** {2 Core Interactions} *)

(** [contract v1 v2] performs a tensor contraction between two rank-1 tensors.
    This models the inner product <bra|ket>. *)
val contract : t -> t -> t

(** [apply_gate gate state] applies a rank-2 tensor (gate) to a rank-1 tensor (state).
    This models matrix-vector multiplication and is the implementation of Einstein summation. *)
val apply_gate : t -> t -> t

(** {2 Pauli Gates} *)

(** The Identity gate [I]. *)
val i_gate : t

(** The Pauli-X gate (NOT). *)
val x_gate : t

(** The Pauli-Y gate. *)
val y_gate : t

(** The Pauli-Z gate (phase-flip). *)
val z_gate : t