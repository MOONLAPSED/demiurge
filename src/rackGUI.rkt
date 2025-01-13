#lang racket/gui
(require racket/path)

(define obsidian-vault-path (string->path "C:\\Users\\DEV\\Downloads"))

;; Basic frame setup
(define frame 
  (new frame% 
       [label "ObsidianExplorer"]
       [width 800]
       [height 600]))

(define sizer (new vertical-panel% [parent frame]))

;; Text field for filename input
(define filename-field
  (new text-field% 
       [parent sizer]
       [label "Filename"]
       [min-width 600]
       [init-value ""]))

;; Editor area for file content display/editing
(define the-editor 
  (new text%))

(define editor 
  (new editor-canvas% 
       [parent sizer]
       [editor the-editor])) ; Use a global text% instance for interactions

;; Status message display using a text field
(define status-message 
  (new text-field% 
       [parent sizer]
       [label "Status"]
       [enabled #f]))

;; Command input field
(define command-input
  (new text-field%
       [parent sizer]
       [label "Command"]
       [init-value ""]))

;; Logging function that outputs to both console and GUI
(define (log-message msg)
  (printf "~a\n" msg)  ; Print to console
  (send status-message set-value msg)) ; Update the status message in GUI

;; Button to execute commands
(define execute-button
  (new button%
       [parent sizer]
       [label "Execute Command"]
       [callback (λ (button event)
                   (let ([input (string-trim (send command-input get-value))])
                     (log-message (format "Executing command: ~a" input))
                     (send command-input set-value "")
                     (let ([cmd (hash-ref commands (string-downcase input) 
                                          (λ () #f))])
                       (if cmd
                           (cmd)  ; Execute command if found
                           (log-message "Unknown command.")))))]))

;; Function to save content to Obsidian vault
(define (save-to-obsidian filename content)
  (log-message (format "Saving to file: ~a" filename))  ; Log saving action
  (with-output-to-file 
    (build-path obsidian-vault-path filename)
    #:exists 'replace
    (λ () (display content))))

;; Function to load content from Obsidian vault
(define (load-from-obsidian filename)
  (let ([file-path (build-path obsidian-vault-path filename)])
    (if (file-exists? file-path)
        (begin
          (log-message (format "Loading file from path: ~a" file-path))
          (with-input-from-file file-path
            (λ ()
              (let* ([content-bytes (port->bytes (current-input-port))]
                     [content (bytes->string/utf-8 content-bytes)]) ; Convert bytes to string
                (log-message (format "Content loaded: ~a" content))
                ;; Clear current content
                (send the-editor delete 0 (send the-editor last-position))
                ;; Insert new content at position 0
                (send the-editor insert content 0)
                (log-message "File loaded successfully.")))))
        (log-message (format "File '~a' does not exist." filename)))))

;; Command to save content
(define (cmd-save)
  (let ([filename (string-trim (send filename-field get-value))])
    (if (not (string=? filename ""))
        (begin
          (let ([content (send the-editor get-text)])
            (log-message (format "Content to save: ~a" content))
            (save-to-obsidian filename content))
          (log-message "File saved successfully.")
          (send filename-field set-value ""))
        (log-message "Please enter a filename."))))

;; Command to load content
(define (cmd-load)
  (let ([filename (string-trim (send filename-field get-value))])
    (if (not (string=? filename ""))
        (begin
          (log-message (format "Attempting to load: ~a" filename))
          (load-from-obsidian filename))
        (log-message "Please enter a filename to load."))))

;; Command registration system
(define (register-command name func)
  (begin
    (log-message (format "Registering command: ~a" name))
    (hash-set! commands (string-downcase name) func)))

(define commands (make-hash))

;; Register commands
(register-command "save" cmd-save)
(register-command "load" cmd-load)

;; Show the frame
(send frame show #t)