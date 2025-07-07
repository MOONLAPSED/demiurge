#lang racket

;; ============================================================================
;; MORPHOLOGICAL QUINE COLLISION DYNAMICS
;; A stochastic system for quine evolution through random collisions
;; ============================================================================

(require racket/random)

;; ByteWord structure: 8-bit morphological entity
(struct byteword (value) #:transparent)

;; Extract T/V/C bits from byteword
(define (extract-tvc bw)
  (let ([val (byteword-value bw)])
    (values (arithmetic-shift val -4)     ; T: upper 4 bits
            (bitwise-and (arithmetic-shift val -1) #b111)  ; V: middle 3 bits
            (bitwise-and val #b1))))      ; C: lower 1 bit

;; Create byteword from T/V/C components
(define (make-tvc t v c)
  (byteword (bitwise-ior (arithmetic-shift t 4)
                         (arithmetic-shift v 1)
                         c)))

;; Morphological state predicates
(define (dynamic? bw)
  (let-values ([(t v c) (extract-tvc bw)])
    (= c 1)))

(define (morphic? bw)
  (let-values ([(t v c) (extract-tvc bw)])
    (= c 0)))

(define (dead? bw)
  (let-values ([(t v c) (extract-tvc bw)])
    (and (= c 0) (= v 0))))  ; DunderC = 0

;; ============================================================================
;; TOPOLOGICAL CONSTRAINTS (Chemical Bonding Rules)
;; ============================================================================

;; A quine is a sequence of bytewords that satisfies topological constraints
(struct quine (words) #:transparent)

;; Check if a sequence forms a topological cycle
(define (has-topological-cycle? words)
  (and (>= (length words) 2)
       (let ([dynamics (filter dynamic? words)])
         (and (not (null? dynamics))
              ;; Topological constraint: T-values must form closed loop
              (let ([t-values (map (lambda (bw) 
                                   (let-values ([(t v c) (extract-tvc bw)]) t))
                                 dynamics)])
                (= (modulo (apply + t-values) 16) 0))))))

;; Check if quine has morphological coherence
(define (has-morphological-coherence? words)
  (let* ([total-words (length words)]
         [dynamic-count (length (filter dynamic? words))]
         [morphic-count (length (filter morphic? words))]
         [dead-count (length (filter dead? words))])
    ;; Coherence rule: must have balance between states
    (and (> dynamic-count 0)
         (< dead-count (quotient total-words 2))
         ;; V-bit entropy constraint
         (let ([v-values (map (lambda (bw)
                               (let-values ([(t v c) (extract-tvc bw)]) v))
                             words)])
           (> (length (remove-duplicates v-values)) 1)))))

;; Check if quine satisfies all topological constraints
(define (valid-quine? q)
  (let ([words (quine-words q)])
    (and (not (null? words))
         (>= (length words) 2)
         (has-topological-cycle? words)
         (has-morphological-coherence? words))))

;; ============================================================================
;; STOCHASTIC MORPHOLOGICAL DYNAMICS
;; ============================================================================

;; Generate random byteword with bias toward interesting states
(define (random-byteword)
  (if (< (random) 0.3)
      ;; 30% chance of interesting configurations
      (let ([t (random 16)]
            [v (+ 1 (random 7))]  ; Avoid v=0 for more dynamics
            [c (random 2)])
        (make-tvc t v c))
      ;; 70% chance of pure random
      (byteword (random 256))))

;; Generate random quine of given length
(define (random-quine length)
  (quine (build-list length (lambda (_) (random-byteword)))))

;; Gaussian-inspired mutation with topological preservation
(define (mutate-byteword bw sigma)
  (let* ([val (byteword-value bw)]
         [t (arithmetic-shift val -4)]
         [v (bitwise-and (arithmetic-shift val -1) #b111)]
         [c (bitwise-and val #b1)])
    ;; Mutate each component separately with different rates
    (let ([new-t (modulo (+ t (- (random (* 2 sigma)) sigma)) 16)]
          [new-v (modulo (+ v (- (random sigma) (quotient sigma 2))) 8)]
          [new-c (if (< (random) 0.1) (- 1 c) c)])  ; 10% chance to flip C
      (make-tvc new-t new-v new-c))))

;; Mutate entire quine with adaptive mutation rates
(define (mutate-quine q sigma)
  (let* ([words (quine-words q)]
         [mutated-words (map (lambda (bw) (mutate-byteword bw sigma)) words)])
    ;; Occasionally add/remove words for structural evolution
    (cond
      [(and (< (random) 0.05) (> (length mutated-words) 2))
       ;; 5% chance to remove a word
       (quine (remove (list-ref mutated-words (random (length mutated-words)))
                      mutated-words))]
      [(< (random) 0.05)
       ;; 5% chance to add a word
       (quine (append mutated-words (list (random-byteword))))]
      [else
       (quine mutated-words)])))

;; ============================================================================
;; COLLISION DYNAMICS - THE HEART OF THE SYSTEM
;; ============================================================================

;; Collision creates morphological fragments through topological mixing
(define (collide-quines q1 q2)
  (let* ([words1 (quine-words q1)]
         [words2 (quine-words q2)]
         [all-words (append words1 words2)]
         [shuffled (shuffle all-words)]
         [len (length shuffled)])
    
    ;; Create multiple fragments with different topological properties
    (let* ([split-points (sort (list (random len) (random len)) <)]
           [point1 (car split-points)]
           [point2 (cadr split-points)])
      
      (list 
       ;; Fragment 1: First section
       (quine (take shuffled point1))
       ;; Fragment 2: Middle section  
       (quine (take (drop shuffled point1) (- point2 point1)))
       ;; Fragment 3: Recombined ends
       (quine (append (drop shuffled point2) (take shuffled point1)))))))

;; ============================================================================
;; MORPHOLOGICAL EVOLUTION ENGINE
;; ============================================================================

;; Population of quines with thermodynamic properties
(struct population (quines generation energy temperature) #:transparent)

;; Initialize random population
(define (init-population size quine-length)
  (population (build-list size (lambda (_) (random-quine quine-length)))
              0
              1000.0
              1.0))  ; Starting temperature

;; Thermodynamic selection - valid quines have lower energy
(define (calculate-fitness q)
  (if (valid-quine? q)
      (let* ([words (quine-words q)]
             [complexity (length words)]
             [dynamics (length (filter dynamic? words))]
             [coherence (if (has-morphological-coherence? words) 10 0)])
        (+ coherence dynamics (- 20 complexity)))  ; Prefer coherent, dynamic, compact quines
      -100))  ; Invalid quines have very low fitness

;; Evolve population for one generation
(define (evolve-generation pop mutation-rate)
  (let* ([quines (population-quines pop)]
         [gen (population-generation pop)]
         [energy (population-energy pop)]
         [temp (population-temperature pop)]
         [valid-quines (filter valid-quine? quines)]
         [num-valid (length valid-quines)])
    
    (if (< num-valid 2)
        ;; Not enough valid quines - inject fresh random ones
        (population (append valid-quines 
                           (build-list (- 20 num-valid) 
                                     (lambda (_) (random-quine 3))))
                    (+ gen 1)
                    (* energy 0.98)
                    (* temp 0.99))
        
        ;; Perform stochastic thermodynamic evolution
        (let* ([;; Mutation phase
                mutated (map (lambda (q) (mutate-quine q mutation-rate))
                            valid-quines)]
               
               [;; Collision phase - random collisions create fragments
                collision-pairs (build-list (quotient num-valid 2)
                                           (lambda (_) 
                                             (list (list-ref valid-quines (random num-valid))
                                                   (list-ref valid-quines (random num-valid)))))]
               
               [collision-products (apply append 
                                         (map (lambda (pair) 
                                               (collide-quines (car pair) (cadr pair)))
                                             collision-pairs))]
               
               [;; Combine all candidates
                all-candidates (append mutated collision-products)]
               
               [;; Thermodynamic selection
                fitness-pairs (map (lambda (q) (cons q (calculate-fitness q)))
                                  all-candidates)]
               
               [;; Boltzmann selection based on fitness and temperature
                survivors (filter (lambda (fp) 
                                   (> (exp (/ (cdr fp) temp)) (random)))
                                 fitness-pairs)]
               
               [final-quines (if (null? survivors)
                                (list (random-quine 3))  ; Emergency quine
                                (map car survivors))])
          
          (population (take final-quines (min 20 (length final-quines)))
                      (+ gen 1)
                      (* energy 0.95)
                      (* temp 0.98))))))

;; ============================================================================
;; SIMULATION RUNNER
;; ============================================================================

;; Run morphological evolution simulation
(define (run-simulation generations pop-size quine-length mutation-rate)
  (let loop ([pop (init-population pop-size quine-length)]
             [gen 0])
    (if (>= gen generations)
        pop
        (let* ([evolved (evolve-generation pop mutation-rate)]
               [valid-count (length (filter valid-quine? 
                                          (population-quines evolved)))]
               [avg-fitness (/ (apply + (map calculate-fitness 
                                           (population-quines evolved)))
                              (length (population-quines evolved)))])
          (printf "Gen ~a: ~a valid quines, avg fitness: ~a, temp: ~a~n" 
                  gen valid-count 
                  (real->decimal-string avg-fitness 2)
                  (real->decimal-string (population-temperature evolved) 3))
          (loop evolved (+ gen 1))))))

;; ============================================================================
;; ANALYSIS FUNCTIONS
;; ============================================================================

(define (tvc-string bw)
  (let-values ([(t v c) (extract-tvc bw)])
    (format "T:~a V:~a C:~a" t v c)))

;; Analyze topological diversity in population
(define (analyze-topology pop)
  (let* ([quines (population-quines pop)]
         [valid-quines (filter valid-quine? quines)]
         [tvc-patterns (map (lambda (q)
                              (map tvc-string (quine-words q)))
                            valid-quines)])
    (printf "~nTopological Analysis:~n")
    (printf "  Total quines: ~a~n" (length quines))
    (printf "  Valid quines: ~a~n" (length valid-quines))
    (printf "  Unique patterns: ~a~n" (length (remove-duplicates tvc-patterns)))
    
    ;; Show best quines
    (let* ([fitness-pairs (map (lambda (q) (cons q (calculate-fitness q)))
                              valid-quines)]
           [sorted-pairs (sort fitness-pairs (lambda (a b) (> (cdr a) (cdr b))))]
           [best-quines (take sorted-pairs (min 3 (length sorted-pairs)))])
      
      (printf "~nBest Quines:~n")
      (for ([qp best-quines] [i (in-naturals)])
        (printf "  #~a (fitness ~a): ~a~n" 
                (+ i 1) (cdr qp)
                (string-join (map tvc-string (quine-words (car qp))) " | "))))))

;; ============================================================================
;; MAIN EXECUTION
;; ============================================================================

(printf "=== MORPHOLOGICAL QUINE COLLISION DYNAMICS ===~n")
(printf "Initializing stochastic evolution in 256-state space...~n~n")

;; Run the simulation!
(define final-pop (run-simulation 100 20 4 2))
(analyze-topology final-pop)

;; Show emergent topological structures
(printf "~nEmergent Morphological Structures:~n")
(let ([valid-quines (filter valid-quine? (population-quines final-pop))])
  (for ([q valid-quines] [i (in-naturals)])
    (when (< i 5)  ; Show first 5
      (let* ([words (quine-words q)]
             [cycle-sum (apply + (map (lambda (bw) 
                                      (let-values ([(t v c) (extract-tvc bw)]) t))
                                    (filter dynamic? words)))])
        (printf "Structure ~a: ~a (T-cycle: ~a)~n" 
                (+ i 1)
                (string-join (map tvc-string words) " → ")
                (modulo cycle-sum 16))))))

(printf "~n=== SIMULATION COMPLETE ===~n")
(printf "Your quines have evolved through ~a generations of stochastic collision dynamics!~n" 
        (population-generation final-pop))