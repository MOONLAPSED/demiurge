#lang racket
(require racket/system
         racket/file
         racket/path
         racket/format
         racket/json)

;; -----------------------------------------------------------
;; Utility functions
;; -----------------------------------------------------------

(define (log-message msg)
  (printf "[~a] ~a\n" (current-inexact-milliseconds) msg))

;; Check if current directory is a Git repository.
(define (is-git-repo?)
  (with-handlers ([exn:fail? (λ (_e) #f)])
    (zero? (system* "git" "rev-parse" "--is-inside-work-tree"))))

;; Run a command and return its output as a string.
(define (run-command cmd args)
  (let* ([result (apply system* cmd args)]
         [output (system/output->string (apply system* cmd args))])
    (values result (string-trim output))))

;; -----------------------------------------------------------
;; Provisioning based on platform
;; -----------------------------------------------------------

(define (provision-platform)
  "Call the appropriate provisioning script based on detected OS.
   The provisioning script should return 0 on success and 1 on failure."
  (define devcontainer-dir (build-path (current-directory) ".devcontainer"))
  (cond
    [(eq? (system-type) 'unix)
     (let ([script (build-path devcontainer-dir "provision-ubuntu.sh")])
       (log-message (format "Running Ubuntu provisioning: ~a" script))
       (system* "/bin/bash" (path->string script)))]
    [(eq? (system-type) 'windows)
     (let ([script (build-path devcontainer-dir "provision-windows.ps1")])
       (log-message (format "Running Windows provisioning: ~a" script))
       (system* "powershell" "-ExecutionPolicy" "Bypass" "-File" (path->string script)))]
    [else
     (error "Unsupported platform")]))
     
(define (ensure-git-repo)
  "Ensure that the current directory is a Git repository. If not, attempt to initialize
   Git and, if that fails, run provisioning."
  (if (is-git-repo?)
      (log-message "Git repository detected; proceeding with orchestration.")
      (begin
        (log-message "No Git repo detected. Attempting to initialize Git...")
        (when (not (zero? (system* "git" "init")))
          (log-message "Git initialization failed. Running provisioning script...")
          (let ([prov-result (provision-platform)])
            (if (zero? prov-result)
                (log-message "Provisioning successful.")
                (error "Provisioning failed; aborting orchestration.")))))))

;; -----------------------------------------------------------
;; Python Runtime Bridge via Static File Communication
;; -----------------------------------------------------------
;; The Python runtime is expected to write its result (a 0 or 1)
;; into a file named "python-status.json" in the current directory.
;; This file is our simple IPC channel.

(define python-status-file "python-status.json")

(define (launch-python-runtime)
  "Launch the Python runtime. It is assumed that the Python script
   sets up its environment and writes a status code (0 for OK, 1 for error)
   to the python-status.json file when finished."
  (log-message "Starting Python runtime...")
  (define python-cmd (if (eq? (system-type) 'windows)
                         "python"  ; on Windows, assume python is in PATH
                         "python3")) ; on Unix, use python3
  (system* python-cmd "-u" "src/app.py")  ; '-u' for unbuffered output
  (log-message "Python runtime invoked."))

(define (read-python-status)
  "Read the static file from the Python runtime to get its status.
   Returns 0 if successful, or 1 otherwise."
  (if (file-exists? python-status-file)
      (with-handlers ([exn:fail? (λ (e)
                                   (log-message (format "Failed to read status: ~a" (exn-message e)))
                                   1)])
        (let ([json-data (call-with-input-file python-status-file read-json)])
          (if (and (hash? json-data) (hash-has-key? json-data 'status))
              (hash-ref json-data 'status)
              (begin
                (log-message "Invalid status file format.")
                1))))
      (begin
        (log-message "Python status file not found.")
        1)))

;; -----------------------------------------------------------
;; Main Orchestration Logic
;; -----------------------------------------------------------

(define (main)
  (log-message "Starting Morphological Source Code Orchestration...")
  ;; Step 1: Ensure Git and environment are ready
  (ensure-git-repo)
  
  ;; (Optionally, additional environment verification could go here.)
  
  ;; Step 2: Launch the Python runtime (which is our "child" process)
  (launch-python-runtime)
  
  ;; Step 3: Read the static status file from Python
  (define py-status (read-python-status))
  (log-message (format "Python runtime exited with status: ~a" py-status))
  
  ;; Based on the status, we either continue orchestration or abort.
  (if (zero? py-status)
      (begin
        (log-message "Python runtime succeeded. Proceeding with orchestration...")
        ;; Place additional orchestration logic here.
        (log-message "Orchestration complete."))
      (begin
        (log-message "Python runtime failed. Halting orchestration.")
        (exit 1))))
        
;; -----------------------------------------------------------
;; Start the orchestration
;; -----------------------------------------------------------
(main)
