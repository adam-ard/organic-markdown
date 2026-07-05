;;; organic-markdown.el --- Emacs integration for Organic Markdown -*- lexical-binding: t; -*-

;; Install `markdown-mode` and ensure the `omd` executable is on `exec-path`
;; before enabling this integration.  Yasnippet support is available through
;; `organic-markdown-install-snippets' when Yasnippet is installed.

;;; Commentary:

;; This file provides editor conveniences for Organic Markdown projects:
;;
;; - a minor mode for `.o.md' buffers;
;; - a project command sidebar;
;; - command output buffers;
;; - jump-to-origin support for literate references;
;; - project-wide reference search for literate references;
;; - optional sidebar refresh after save;
;; - optional Yasnippet snippets.
;;
;; Loading the file defines these commands but does not change global keys,
;; markdown hooks, save hooks, or snippets.  Call `organic-markdown-setup' for
;; the standard opt-in setup, or install only the pieces you want.

;;; Code:

(require 'json)
(require 'project)
(require 'subr-x)
(require 'button)

(defgroup organic-markdown nil
  "Emacs integration for Organic Markdown."
  :group 'tools
  :prefix "organic-markdown-")

(defcustom organic-markdown-command "omd"
  "Command used to invoke Organic Markdown."
  :type 'string
  :group 'organic-markdown)

(defcustom organic-markdown-enable-auto-reparse t
  "Non-nil means `organic-markdown-mode' refreshes project metadata after save.

The name is retained for compatibility with existing user configuration.  OMD
now refreshes its parsed cache automatically during ordinary commands, so the
save hook only refreshes visible editor UI such as the command sidebar."
  :type 'boolean
  :group 'organic-markdown)

(defcustom organic-markdown-enable-snippets t
  "Non-nil means `organic-markdown-setup' installs Yasnippet snippets."
  :type 'boolean
  :group 'organic-markdown)

(defcustom organic-markdown-sidebar-width 36
  "Width used for the Organic Markdown commands sidebar."
  :type 'integer
  :group 'organic-markdown)

(defcustom organic-markdown-global-sidebar-key (kbd "C-c o")
  "Global key installed by `organic-markdown-install-global-keybindings'.
Set this to nil before calling `organic-markdown-setup' if you do not want a
global sidebar key."
  :type '(choice (const :tag "Do not bind a global key" nil)
                 key-sequence)
  :group 'organic-markdown)

(defun organic-markdown-default-project-root (&optional directory)
  "Return the Organic Markdown execution root for DIRECTORY.
Use the root recognized by Emacs's project system.  Fall back to the nearest
Git root, then DIRECTORY itself, when no project is recognized."
  (let* ((directory
          (file-name-as-directory
           (expand-file-name (or directory default-directory))))
         (project (project-current nil directory))
         (project-root (and project (project-root project)))
         (git-root (locate-dominating-file directory ".git")))
    (file-name-as-directory
     (expand-file-name (or project-root git-root directory)))))

(defcustom organic-markdown-project-root-function
  #'organic-markdown-default-project-root
  "Function used to find the Organic Markdown project root.
The function receives one directory argument and should return the directory
where `organic-markdown-command' should run."
  :type 'function
  :group 'organic-markdown)

(defvar-local organic-markdown-command-output-root nil
  "Project root associated with the current OMD command output buffer.")

(defvar-local organic-markdown-command-output-command nil
  "OMD command associated with the current output buffer.")

(defvar-local organic-markdown-command-output-args nil
  "Argument list used to launch the current OMD output buffer.")

(defvar-local organic-markdown-command-output-buffer-name nil
  "Buffer name used for the current OMD output buffer.")

(defvar-local organic-markdown-command-output-header nil
  "Header text shown at the top of the current OMD output buffer.")

(defvar-local organic-markdown-command-output-process nil
  "One-shot OMD process for the current output buffer.")

(defvar organic-markdown-command-output-mode-map
  (let ((map (make-sparse-keymap)))
    (set-keymap-parent map special-mode-map)
    (define-key map (kbd "g") #'organic-markdown-command-output-rerun)
    map)
  "Keymap for OMD command output buffers.")

(define-derived-mode organic-markdown-command-output-mode special-mode "OMD-Run"
  "Major mode for OMD command output buffers.")

(defvar organic-markdown-mode-map
  (let ((map (make-sparse-keymap)))
    (define-key map (kbd "C-c o") #'organic-markdown-commands-sidebar-toggle)
    (define-key map (kbd "C-c @") #'organic-markdown-find-origin)
    (define-key map (kbd "M-.") #'organic-markdown-find-origin)
    (define-key map (kbd "M-?") #'organic-markdown-find-references)
    (define-key map (kbd "M-,") #'organic-markdown-pop-location)
    (define-key map (kbd "C-c x") #'organic-markdown-run-command-at-point)
    (define-key map (kbd "C-c t") #'organic-markdown-tangle-project)
    (define-key map (kbd "C-c z") #'organic-markdown-show-command-output)
    map)
  "Keymap for `organic-markdown-mode'.")

(define-minor-mode organic-markdown-mode
  "Minor mode for editing Organic Markdown `.o.md' buffers.
The mode provides local keybindings for the command sidebar, running command
blocks, tangling the current project, showing command output, and jumping to the
origin of or finding references to a literate reference.  When
`organic-markdown-enable-auto-reparse' is non-nil, enabling the mode also adds a
buffer-local `after-save-hook' that refreshes visible Organic Markdown UI after
saving `.o.md' files."
  :lighter " OMD"
  :keymap organic-markdown-mode-map
  (if organic-markdown-mode
      (when organic-markdown-enable-auto-reparse
        (add-hook 'after-save-hook
                  #'organic-markdown-refresh-after-save nil t))
    (remove-hook 'after-save-hook
                 #'organic-markdown-refresh-after-save t)))

(defun organic-markdown-buffer-p (&optional file)
  "Return non-nil when FILE, or the current buffer file, is an `.o.md' file."
  (let ((file (or file buffer-file-name)))
    (and file (string-suffix-p ".o.md" file))))

(defun organic-markdown-enable-mode ()
  "Enable `organic-markdown-mode' in `.o.md' buffers.
This function is suitable for `markdown-mode-hook'."
  (when (organic-markdown-buffer-p)
    (organic-markdown-mode 1)))

(defun organic-markdown-context-directory ()
  "Return the directory that should determine the current OMD project.
For a file buffer, use the file's location rather than a potentially modified
`default-directory'."
  (if buffer-file-name
      (file-name-directory (expand-file-name buffer-file-name))
    default-directory))

(defun organic-markdown-project-root (&optional directory)
  "Return the nearest Organic Markdown root for DIRECTORY."
  (funcall organic-markdown-project-root-function
           (or directory (organic-markdown-context-directory))))

(defun organic-markdown-normalize-root (root)
  "Return ROOT as an absolute directory name."
  (file-name-as-directory (expand-file-name root)))

(defun organic-markdown-direct-call (root args)
  "Run one `omd' call from ROOT with ARGS and return its output."
  (let ((default-directory (organic-markdown-normalize-root root)))
    (with-temp-buffer
      (let ((status (apply #'process-file
                           organic-markdown-command nil t nil args))
            (output (buffer-string)))
        (if (zerop status)
            output
          (error "%s"
                 (if (= 0 (length (string-trim output)))
                     "OMD command failed"
                   (string-trim output))))))))

(defun organic-markdown-control-call (root args)
  "Run ARGS from ROOT through OMD.
The CLI refreshes its parsed cache as needed, so Emacs keeps no separate
long-running OMD process."
  (organic-markdown-direct-call root args))

(defun organic-markdown-command-output-append (buffer text)
  "Append TEXT to BUFFER."
  (when (buffer-live-p buffer)
    (with-current-buffer buffer
      (let ((inhibit-read-only t)
            (moving (= (point) (point-max))))
        (goto-char (point-max))
        (insert text)
        (when moving
          (goto-char (point-max)))))))

(defun organic-markdown-command-output-status-line (status detail)
  "Return a timestamped status line for STATUS and DETAIL."
  (format "\n[%s] %s"
          (if (eq status 'ok)
              "finished"
            (or detail "error"))
          (format-time-string "%Y-%m-%d %H:%M:%S")))

(defun organic-markdown-command-output-sentinel (process event)
  "Handle completion EVENT for PROCESS."
  (let ((buffer (process-get process 'organic-markdown-output-buffer)))
    (when (buffer-live-p buffer)
      (with-current-buffer buffer
        (setq organic-markdown-command-output-process nil))
      (organic-markdown-command-output-append
       buffer
       (organic-markdown-command-output-status-line
        (if (string-match-p "\\`finished" (string-trim event))
            'ok
          'error)
        (string-trim event))))))

(defun organic-markdown-command-output-stop-active (buffer)
  "Stop BUFFER's active OMD execution, if any."
  (when (buffer-live-p buffer)
    (with-current-buffer buffer
      (when (process-live-p organic-markdown-command-output-process)
        (delete-process organic-markdown-command-output-process))
      (setq-local organic-markdown-command-output-process nil))))

(defun organic-markdown-command-output-start-process (buffer root command args)
  "Run ARGS for COMMAND directly from ROOT, sending output to BUFFER."
  (let ((default-directory (organic-markdown-normalize-root root)))
    (with-current-buffer buffer
      (setq-local organic-markdown-command-output-process nil))
    (let ((process
           (apply #'start-file-process
                  (format "organic-markdown:%s" command)
                  nil
                  organic-markdown-command
                  args)))
      (set-process-query-on-exit-flag process nil)
      (process-put process 'organic-markdown-output-buffer buffer)
      (set-process-filter
       process
       (lambda (proc output)
         (organic-markdown-command-output-append
          (process-get proc 'organic-markdown-output-buffer)
          output)))
      (set-process-sentinel process
                            #'organic-markdown-command-output-sentinel)
      (with-current-buffer buffer
        (setq-local organic-markdown-command-output-process process)))))

(defun organic-markdown-command-output-start
    (root command &optional args buffer-name header)
  "Run COMMAND from ROOT in its dedicated output buffer.
Optional ARGS, BUFFER-NAME, and HEADER customize the exact CLI invocation and
displayed buffer."
  (let* ((args (or args (list "run" command)))
         (buffer-name (or buffer-name (format "*%s*" command)))
         (header (or header (format "$ omd run %s\n\n" command)))
         (buffer (get-buffer-create buffer-name)))
    (organic-markdown-command-output-stop-active buffer)
    (with-current-buffer buffer
      (organic-markdown-command-output-mode)
      (setq-local default-directory (organic-markdown-normalize-root root))
      (setq-local organic-markdown-command-output-root root)
      (setq-local organic-markdown-command-output-command command)
      (setq-local organic-markdown-command-output-args args)
      (setq-local organic-markdown-command-output-buffer-name buffer-name)
      (setq-local organic-markdown-command-output-header header)
      (let ((inhibit-read-only t))
        (erase-buffer)
        (insert header)))
    (organic-markdown-command-output-start-process buffer root command args)
    (display-buffer buffer)
    buffer))

(defun organic-markdown-command-output-rerun ()
  "Rerun the OMD command associated with the current output buffer."
  (interactive)
  (unless (and organic-markdown-command-output-root
               organic-markdown-command-output-command
               organic-markdown-command-output-args)
    (user-error "Current buffer is not an OMD command output buffer"))
  (organic-markdown-command-output-start
   organic-markdown-command-output-root
   organic-markdown-command-output-command
   organic-markdown-command-output-args
   organic-markdown-command-output-buffer-name
   organic-markdown-command-output-header))

(defvar organic-markdown-commands-sidebar-buffer-name "*OMD Commands*"
  "Buffer name used for the OMD commands sidebar.")

(defvar-local organic-markdown-commands-sidebar-root nil
  "Project root associated with the current OMD commands sidebar buffer.")

(defvar organic-markdown-commands-sidebar-mode-map
  (let ((map (make-sparse-keymap)))
    (set-keymap-parent map special-mode-map)
    (define-key map (kbd "RET") #'organic-markdown-commands-sidebar-visit)
    (define-key map (kbd "g") #'organic-markdown-commands-sidebar-refresh)
    (define-key map (kbd "x") #'organic-markdown-commands-sidebar-run-command)
    map)
  "Keymap for the OMD commands sidebar.")

(define-derived-mode organic-markdown-commands-sidebar-mode
  special-mode "OMD-Commands"
  "Major mode for the OMD commands sidebar.")

(defun organic-markdown-commands-sidebar-project-root ()
  "Return the nearest Organic Markdown root used for OMD commands."
  (organic-markdown-project-root (organic-markdown-context-directory)))

(defun organic-markdown-commands-sidebar-window ()
  "Return the active OMD commands sidebar window, if one exists."
  (catch 'sidebar-window
    (dolist (window (window-list))
      (when (window-parameter window 'organic-markdown-commands-sidebar)
        (throw 'sidebar-window window)))))

(defun organic-markdown-commands-sidebar-target-window ()
  "Return the first non-sidebar window, if one exists."
  (catch 'target-window
    (dolist (window (window-list))
      (unless (window-parameter window 'window-side)
        (throw 'target-window window)))))

(defun organic-markdown-commands-sidebar-find-command-name (attributes)
  "Extract a command name from ATTRIBUTES, or nil if none exists."
  (cond
   ((string-match "name=\"\\([^\"]+\\)\"" attributes)
    (match-string 1 attributes))
   ((string-match "name=\\([^}[:space:]]+\\)" attributes)
    (match-string 1 attributes))
   (t nil)))

(defun organic-markdown-commands-sidebar-scan-fallback (root)
  "Return command metadata for ROOT by scanning `*.o.md' files directly."
  (let (entries)
    (dolist (file (directory-files-recursively root "\\.o\\.md\\'"))
      (let (commands)
        (with-temp-buffer
          (insert-file-contents file)
          (goto-char (point-min))
          (while (re-search-forward "^```.*{\\([^}\n]*\\)}" nil t)
            (let ((attributes (match-string 1)))
              (when (string-match-p "\\bmenu=true\\b" attributes)
                (let ((name
                       (organic-markdown-commands-sidebar-find-command-name
                        attributes)))
                  (when name
                    (setq commands (append commands (list name)))))))))
        (when commands
          (setq entries
                (append entries
                        (list
                         `((file . ,(concat "./"
                                             (file-relative-name file root)))
                           (cmds . ,commands))))))))
    entries))

(defun organic-markdown-commands-sidebar-fetch (root)
  "Return grouped command metadata for ROOT."
  (or
   (condition-case nil
       (let ((json-object-type 'alist)
             (json-array-type 'list)
             (json-key-type 'symbol))
         (json-read-from-string
          (organic-markdown-control-call root '("cmds"))))
     (error nil))
   (organic-markdown-commands-sidebar-scan-fallback root)))

(defun organic-markdown-commands-sidebar-render (root)
  "Render the OMD commands sidebar for ROOT in the current buffer."
  (let ((entries (organic-markdown-commands-sidebar-fetch root))
        (inhibit-read-only t))
    (erase-buffer)
    (setq-local organic-markdown-commands-sidebar-root root)
    (insert (propertize "OMD Commands" 'face 'bold) "\n")
    (insert (abbreviate-file-name root) "\n\n")
    (if entries
        (dolist (entry entries)
          (let* ((file (alist-get 'file entry))
                 (absolute-file (expand-file-name file root))
                 (commands (alist-get 'cmds entry)))
            (insert
             (propertize file
                         'face 'font-lock-keyword-face
                         'organic-markdown-file absolute-file)
             "\n")
            (dolist (command commands)
              (insert
               (propertize (format "  %s" command)
                           'organic-markdown-file absolute-file
                           'organic-markdown-command command)
               "\n"))
            (insert "\n")))
      (insert "No OMD commands found.\n"))
    (goto-char (point-min))))

(defun organic-markdown-commands-sidebar-open-file (file &optional command)
  "Open FILE in the main editing area and optionally jump to COMMAND."
  (let ((target-window (or (organic-markdown-commands-sidebar-target-window)
                           (selected-window))))
    (select-window target-window)
    (find-file file)
    (when command
      (goto-char (point-min))
      (or (re-search-forward
           (format "name=\"%s\"" (regexp-quote command))
           nil
           t)
          (re-search-forward
           (format "name=%s\\b" (regexp-quote command))
           nil
           t))
      (beginning-of-line))))

(defun organic-markdown-commands-sidebar-visit ()
  "Visit the file or command at point in the OMD commands sidebar."
  (interactive)
  (let ((file (get-text-property (point) 'organic-markdown-file))
        (command (get-text-property (point) 'organic-markdown-command)))
    (unless file
      (user-error "Point is not on an OMD commands entry"))
    (organic-markdown-commands-sidebar-open-file file command)))

(defun organic-markdown-commands-sidebar-run-command ()
  "Run the OMD command at point asynchronously."
  (interactive)
  (let ((command (get-text-property (point) 'organic-markdown-command)))
    (unless command
      (user-error "Point is not on an OMD command"))
    (organic-markdown-command-output-start
     organic-markdown-commands-sidebar-root
     command)))

(defun organic-markdown-commands-sidebar-refresh ()
  "Refresh the current OMD commands sidebar."
  (interactive)
  (unless organic-markdown-commands-sidebar-root
    (user-error "Current buffer is not an OMD commands sidebar"))
  (organic-markdown-commands-sidebar-render
   organic-markdown-commands-sidebar-root))

(defun organic-markdown-commands-sidebar-open (root)
  "Show the OMD commands sidebar for ROOT."
  (let* ((buffer (get-buffer-create
                  organic-markdown-commands-sidebar-buffer-name))
         (window (or (organic-markdown-commands-sidebar-window)
                     (display-buffer-in-side-window
                      buffer
                      `((side . right)
                        (slot . 0)
                        (window-width . ,organic-markdown-sidebar-width)
                        (preserve-size . (t . nil))
                        (window-parameters
                         . ((no-delete-other-windows . t))))))))
    (with-current-buffer buffer
      (organic-markdown-commands-sidebar-mode)
      (setq-local default-directory (organic-markdown-normalize-root root))
      (organic-markdown-commands-sidebar-render root))
    (set-window-dedicated-p window nil)
    (set-window-buffer window buffer)
    (set-window-parameter window 'organic-markdown-commands-sidebar t)
    (set-window-dedicated-p window t)
    (with-selected-window window
      (setq-local window-size-fixed 'width)
      (setq-local truncate-lines t))
    window))

(defun organic-markdown-commands-sidebar-toggle ()
  "Toggle the OMD commands sidebar for the current project."
  (interactive)
  (let* ((root (organic-markdown-commands-sidebar-project-root))
         (window (organic-markdown-commands-sidebar-window))
         (sidebar-root
          (and window
               (buffer-local-value 'organic-markdown-commands-sidebar-root
                                   (window-buffer window)))))
    (if (and window
             sidebar-root
             (string= (expand-file-name sidebar-root)
                      (expand-file-name root)))
        (delete-window window)
      (organic-markdown-commands-sidebar-open root))))

(defun organic-markdown-ref-at-point ()
  "Return the Organic Markdown block name at point, or nil."
  (save-excursion
    (let ((origin (point))
          start
          finish
          reference
          (open-marker (concat "@" "<"))
          (close-marker (concat "@" ">")))
      (when (search-backward open-marker (line-beginning-position) t)
        (setq start (point))
        (when (search-forward close-marker (line-end-position) t)
          (setq finish (point))
          (when (<= start origin finish)
            (setq reference
                  (buffer-substring-no-properties (+ start 2) (- finish 2)))
            (setq reference (string-trim reference))
            (when (string-match "[*({]" reference)
              (setq reference (substring reference 0 (match-beginning 0))))
            (string-trim reference)))))))

(defun organic-markdown-definition-at-point ()
  "Return the Organic Markdown block name defined on the current line, or nil."
  (save-excursion
    (beginning-of-line)
    (when (looking-at "^```[^`\n]*{\\([^}\n]*\\)}")
      (organic-markdown-commands-sidebar-find-command-name
       (match-string-no-properties 1)))))

(defun organic-markdown-reference-name-at-point ()
  "Return the Organic Markdown reference or definition name at point, or nil."
  (or (organic-markdown-ref-at-point)
      (organic-markdown-definition-at-point)))

(defvar organic-markdown-location-stack nil
  "Stack of locations saved before Organic Markdown navigation commands.")

(defun organic-markdown-push-location ()
  "Save the current buffer and point for `organic-markdown-pop-location'."
  (when buffer-file-name
    (push (point-marker) organic-markdown-location-stack)))

(defun organic-markdown-pop-location ()
  "Return to the previous Organic Markdown navigation location."
  (interactive)
  (let ((marker (pop organic-markdown-location-stack)))
    (unless marker
      (user-error "No previous Organic Markdown location"))
    (let ((buffer (marker-buffer marker))
          (position (marker-position marker)))
      (unless (buffer-live-p buffer)
        (user-error "Previous Organic Markdown buffer no longer exists"))
      (switch-to-buffer buffer)
      (goto-char position)
      (set-marker marker nil nil))))

(defun organic-markdown-find-origin ()
  "Jump to the file that defines the Organic Markdown reference at point."
  (interactive)
  (let ((name (organic-markdown-ref-at-point)))
    (unless name
      (user-error "Point is not on an Organic Markdown reference"))
    (let* ((root (organic-markdown-project-root))
           (origin
            (condition-case nil
                (car (split-string
                      (string-trim
                       (organic-markdown-control-call
                        root
                        (list "origin" name)))
                      "\n"
                      t))
              (error nil)))
           (origin-file
            (or (and origin (expand-file-name origin root))
                (catch 'match
                  (dolist (file (directory-files-recursively
                                 root
                                 "\\.o\\.md\\'"))
                    (with-temp-buffer
                      (insert-file-contents file)
                      (when (re-search-forward
                             (format "{[^}\n]*name=%s\\b"
                                     (regexp-quote name))
                             nil
                             t)
                        (throw 'match file))))))))
      (unless origin-file
        (user-error "Could not resolve %s" name))
      (organic-markdown-push-location)
      (find-file origin-file)
      (goto-char (point-min))
      (when (re-search-forward
             (format "{[^}\n]*name=%s\\b" (regexp-quote name))
             nil
             t)
        (beginning-of-line)))))

(define-derived-mode organic-markdown-references-mode special-mode
  "OMD-Refs"
  "Major mode for Organic Markdown reference search results.")

(defun organic-markdown-reference-regexp (name)
  "Return a regexp that matches literate references to NAME.
The delimiter after NAME keeps a search for `foo' from matching references to
`foobar', while still matching defaults, arguments, and execution refs."
  (concat (regexp-quote "@<")
          (regexp-quote name)
          "\\(?:[*({]\\|@>\\)"))

(defun organic-markdown-reference-locations (root name)
  "Return all `.o.md' reference locations for NAME under ROOT."
  (let ((regexp (organic-markdown-reference-regexp name))
        locations)
    (dolist (file (directory-files-recursively root "\\.o\\.md\\'"))
      (with-temp-buffer
        (insert-file-contents file)
        (goto-char (point-min))
        (while (re-search-forward regexp nil t)
          (let ((line (line-number-at-pos))
                (text (string-trim-right
                       (buffer-substring-no-properties
                        (line-beginning-position)
                        (line-end-position)))))
            (setq locations
                  (append locations
                          (list (list file line text))))))))
    locations))

(defun organic-markdown-references-open-location (file line)
  "Open FILE and move point to LINE."
  (organic-markdown-push-location)
  (find-file file)
  (goto-char (point-min))
  (forward-line (1- line)))

(defun organic-markdown-references-render (root name locations)
  "Render reference LOCATIONS for NAME under ROOT."
  (let ((buffer (get-buffer-create
                 (format "*OMD References: %s*" name))))
    (with-current-buffer buffer
      (organic-markdown-references-mode)
      (let ((inhibit-read-only t))
        (erase-buffer)
        (insert (format "References to %s\n" name))
        (insert (abbreviate-file-name root) "\n\n")
        (if locations
            (dolist (location locations)
              (let* ((file (nth 0 location))
                     (line (nth 1 location))
                     (text (nth 2 location))
                     (label (format "%s:%d"
                                    (file-relative-name file root)
                                    line)))
                (insert-text-button
                 label
                 'action (lambda (_button)
                           (organic-markdown-references-open-location
                            file line))
                 'follow-link t)
                (insert ": " text "\n")))
          (insert "No references found.\n")))
      (goto-char (point-min)))
    (display-buffer buffer)))

(defun organic-markdown-find-references (name)
  "Find all literate references to NAME in the current project."
  (interactive
   (let ((default (organic-markdown-reference-name-at-point)))
     (list
      (read-string
       (if default
           (format "Find references for block (default %s): " default)
         "Find references for block: ")
       nil nil default))))
  (when (string-empty-p name)
    (user-error "Missing Organic Markdown reference name"))
  (let* ((root (organic-markdown-project-root))
         (locations (organic-markdown-reference-locations root name)))
    (organic-markdown-references-render root name locations)))

(defun organic-markdown-block-attributes-at-point ()
  "Return the code block attributes from the current header line, or nil."
  (save-excursion
    (beginning-of-line)
    (when (looking-at "^```[^`\n]*{\\([^}\n]*\\)}")
      (match-string-no-properties 1))))

(defun organic-markdown-command-at-point ()
  "Return the runnable Organic Markdown command at point, or nil."
  (let ((attributes (organic-markdown-block-attributes-at-point)))
    (when (and attributes
               (string-match-p "\\bmenu=true\\b" attributes))
      (organic-markdown-commands-sidebar-find-command-name attributes))))

(defun organic-markdown-run-command-at-point ()
  "Run the Organic Markdown command declared on the current header line."
  (interactive)
  (let ((command (organic-markdown-command-at-point)))
    (unless command
      (user-error "Point is not on a runnable Organic Markdown command header"))
    (organic-markdown-command-output-start
     (organic-markdown-project-root)
     command)))

(defun organic-markdown-tangle-project ()
  "Run `omd tangle' for the current Organic Markdown project."
  (interactive)
  (let* ((root (organic-markdown-project-root))
         (project-name
          (file-name-nondirectory
           (directory-file-name (expand-file-name root)))))
    (organic-markdown-command-output-start
     root
     "tangle"
     '("tangle")
     (format "*omd-tangle: %s*" project-name)
     "$ omd tangle\n\n")))

(defun organic-markdown-show-command-output ()
  "Jump to the existing output buffer for the command header at point."
  (interactive)
  (let* ((command (organic-markdown-command-at-point))
         (buffer (and command (get-buffer (format "*%s*" command)))))
    (unless command
      (user-error "Point is not on a runnable Organic Markdown command header"))
    (unless buffer
      (user-error "No output buffer exists yet for %s" command))
    (pop-to-buffer buffer)))

(defun organic-markdown-refresh-after-save ()
  "Refresh visible Organic Markdown UI after saving an `.o.md' file."
  (when (organic-markdown-buffer-p)
    (let* ((file (expand-file-name buffer-file-name))
           (root (organic-markdown-project-root (file-name-directory file)))
           (sidebar (get-buffer organic-markdown-commands-sidebar-buffer-name)))
      (when (buffer-live-p sidebar)
        (with-current-buffer sidebar
          (when (and organic-markdown-commands-sidebar-root
                     (string= (organic-markdown-normalize-root root)
                              (organic-markdown-normalize-root
                               organic-markdown-commands-sidebar-root)))
            (condition-case error
                (organic-markdown-commands-sidebar-render root)
              (error
               (message "OMD could not refresh %s: %s"
                        (abbreviate-file-name file)
                        (error-message-string error))))))))))

(defun organic-markdown-install-global-keybindings (&optional key)
  "Bind KEY globally to `organic-markdown-commands-sidebar-toggle'.
When KEY is nil, use `organic-markdown-global-sidebar-key'.  This function is
opt-in; loading `organic-markdown.el' does not install global keybindings."
  (interactive)
  (let ((key (or key organic-markdown-global-sidebar-key)))
    (unless key
      (user-error "No Organic Markdown global sidebar key configured"))
    (global-set-key key #'organic-markdown-commands-sidebar-toggle)))

(defun organic-markdown-install-snippets ()
  "Install Organic Markdown snippets for Yasnippet's `markdown-mode'.
This function is safe to call before or after Yasnippet has loaded.  It has no
effect unless Yasnippet is installed."
  (interactive)
  (with-eval-after-load 'yasnippet
    (when (fboundp 'yas-define-snippets)
      (yas-define-snippets
       'markdown-mode
       '(("ocode"
          "#### code: ${1:name}
\\`\\`\\`${2:lang} {name=$1}
$0
\\`\\`\\`"
          "organic markdown code block")

         ("ofile"
          "#### file: ${1:path}
\\`\\`\\`${2:lang} {tangle=$1}
$0
\\`\\`\\`"
          "organic markdown file block")

         ("ocmd"
          "#### cmd: ${1:name}
\\`\\`\\`${2:lang} {name=$1 menu=true}
$0
\\`\\`\\`"
          "organic markdown command block"))))))

(defun organic-markdown-setup ()
  "Install the standard Organic Markdown Emacs integration.
This adds `organic-markdown-enable-mode' to `markdown-mode-hook', optionally
binds `organic-markdown-global-sidebar-key' globally, and optionally installs
Yasnippet snippets according to `organic-markdown-enable-snippets'."
  (interactive)
  (add-hook 'markdown-mode-hook #'organic-markdown-enable-mode)
  (when organic-markdown-global-sidebar-key
    (organic-markdown-install-global-keybindings
     organic-markdown-global-sidebar-key))
  (when organic-markdown-enable-snippets
    (organic-markdown-install-snippets)))

(provide 'organic-markdown)

;;; organic-markdown.el ends here
