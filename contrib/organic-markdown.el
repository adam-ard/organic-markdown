;;; organic-markdown.el --- Emacs integration for Organic Markdown -*- lexical-binding: t; -*-

;; Install `markdown-mode` and ensure the `omd` executable is on `exec-path`
;; before loading this file.  Yasnippet support is enabled when available.

(require 'project)

(defvar-local my/omd-command-output-root nil
  "Project root associated with the current OMD command output buffer.")

(defvar-local my/omd-command-output-command nil
  "OMD command associated with the current output buffer.")

(defvar-local my/omd-command-output-args nil
  "Argument list used to launch the current OMD output buffer.")

(defvar-local my/omd-command-output-buffer-name nil
  "Buffer name used for the current OMD output buffer.")

(defvar-local my/omd-command-output-header nil
  "Header text shown at the top of the current OMD output buffer.")

(defvar-local my/omd-command-output-process nil
  "One-shot OMD process for the current output buffer.")

(defvar my/omd-command-output-mode-map
  (let ((map (make-sparse-keymap)))
    (set-keymap-parent map special-mode-map)
    (define-key map (kbd "g") #'my/omd-command-output-rerun)
    map)
  "Keymap for OMD command output buffers.")

(define-derived-mode my/omd-command-output-mode special-mode "OMD-Run"
  "Major mode for OMD command output buffers.")

(defun my/omd-project-root (&optional directory)
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

(defun my/omd-context-directory ()
  "Return the directory that should determine the current OMD project.
For a file buffer, use the file's location rather than a potentially modified
`default-directory'."
  (if buffer-file-name
      (file-name-directory (expand-file-name buffer-file-name))
    default-directory))

(defun my/omd-normalize-root (root)
  "Return ROOT as an absolute directory name."
  (file-name-as-directory (expand-file-name root)))

(defun my/omd-direct-call (root args)
  "Run one `omd` call from ROOT with ARGS and return its output."
  (let ((default-directory (my/omd-normalize-root root)))
    (with-temp-buffer
      (let ((status (apply #'process-file "omd" nil t nil args))
            (output (buffer-string)))
        (if (zerop status)
            output
          (error "%s"
                 (if (= 0 (length (string-trim output)))
                     "OMD command failed"
                   (string-trim output))))))))

(defun my/omd-control-call (root args)
  "Run ARGS from ROOT through OMD.
The CLI starts or contacts the project daemon as needed, so Emacs keeps no
separate long-running OMD process."
  (my/omd-direct-call root args))

(defun my/omd-command-output-append (buffer text)
  "Append TEXT to BUFFER."
  (when (buffer-live-p buffer)
    (with-current-buffer buffer
      (let ((inhibit-read-only t)
            (moving (= (point) (point-max))))
        (goto-char (point-max))
        (insert text)
        (when moving
          (goto-char (point-max)))))))

(defun my/omd-command-output-status-line (status detail)
  "Return a timestamped status line for STATUS and DETAIL."
  (format "\n[%s] %s"
          (if (eq status 'ok)
              "finished"
            (or detail "error"))
          (format-time-string "%Y-%m-%d %H:%M:%S")))

(defun my/omd-command-output-sentinel (process event)
  "Handle completion EVENT for PROCESS."
  (let ((buffer (process-get process 'my/output-buffer)))
    (when (buffer-live-p buffer)
      (with-current-buffer buffer
        (setq my/omd-command-output-process nil))
      (my/omd-command-output-append
       buffer
       (my/omd-command-output-status-line
        (if (string-match-p "\\`finished" (string-trim event))
            'ok
          'error)
        (string-trim event))))))

(defun my/omd-command-output-stop-active (buffer)
  "Stop BUFFER's active OMD execution, if any."
  (when (buffer-live-p buffer)
    (with-current-buffer buffer
      (when (process-live-p my/omd-command-output-process)
        (delete-process my/omd-command-output-process))
      (setq-local my/omd-command-output-process nil))))

(defun my/omd-command-output-start-process (buffer root command args)
  "Run ARGS for COMMAND directly from ROOT, sending output to BUFFER."
  (let ((default-directory (my/omd-normalize-root root)))
    (with-current-buffer buffer
      (setq-local my/omd-command-output-process nil))
    (let ((process (apply #'start-file-process command nil "omd" args)))
      (set-process-query-on-exit-flag process nil)
      (process-put process 'my/output-buffer buffer)
      (set-process-filter
       process
       (lambda (proc output)
         (my/omd-command-output-append
          (process-get proc 'my/output-buffer)
          output)))
      (set-process-sentinel process #'my/omd-command-output-sentinel)
      (with-current-buffer buffer
        (setq-local my/omd-command-output-process process)))))

(defun my/omd-command-output-start (root command &optional args buffer-name header)
  "Run COMMAND from ROOT in its dedicated output buffer."
  (let* ((args (or args (list "run" command)))
         (buffer-name (or buffer-name (format "*%s*" command)))
         (header (or header (format "$ omd run %s\n\n" command)))
         (buffer (get-buffer-create buffer-name)))
    (my/omd-command-output-stop-active buffer)
    (with-current-buffer buffer
      (my/omd-command-output-mode)
      (setq-local default-directory (my/omd-normalize-root root))
      (setq-local my/omd-command-output-root root)
      (setq-local my/omd-command-output-command command)
      (setq-local my/omd-command-output-args args)
      (setq-local my/omd-command-output-buffer-name buffer-name)
      (setq-local my/omd-command-output-header header)
      (let ((inhibit-read-only t))
        (erase-buffer)
        (insert header)))
    (my/omd-command-output-start-process buffer root command args)
    (display-buffer buffer)
    buffer))

(defun my/omd-command-output-rerun ()
  "Rerun the OMD command associated with the current output buffer."
  (interactive)
  (unless (and my/omd-command-output-root
               my/omd-command-output-command
               my/omd-command-output-args)
    (user-error "Current buffer is not an OMD command output buffer"))
  (my/omd-command-output-start
   my/omd-command-output-root
   my/omd-command-output-command
   my/omd-command-output-args
   my/omd-command-output-buffer-name
   my/omd-command-output-header))

(require 'json)

(defvar my/omd-commands-sidebar-buffer-name "*OMD Commands*"
  "Buffer name used for the OMD commands sidebar.")

(defvar-local my/omd-commands-sidebar-root nil
  "Project root associated with the current OMD commands sidebar buffer.")

(defvar my/omd-commands-sidebar-mode-map
  (let ((map (make-sparse-keymap)))
    (set-keymap-parent map special-mode-map)
    (define-key map (kbd "RET") #'my/omd-commands-sidebar-visit)
    (define-key map (kbd "g") #'my/omd-commands-sidebar-refresh)
    (define-key map (kbd "x") #'my/omd-commands-sidebar-run-command)
    map)
  "Keymap for the OMD commands sidebar.")

(define-derived-mode my/omd-commands-sidebar-mode special-mode "OMD-Commands"
  "Major mode for the OMD commands sidebar.")

(defun my/omd-commands-sidebar-project-root ()
  "Return the nearest Organic Markdown root used for OMD commands."
  (my/omd-project-root (my/omd-context-directory)))

(defun my/omd-commands-sidebar-window ()
  "Return the active OMD commands sidebar window, if one exists."
  (catch 'sidebar-window
    (dolist (window (window-list))
      (when (window-parameter window 'my/omd-commands-sidebar)
        (throw 'sidebar-window window)))))

(defun my/omd-commands-sidebar-target-window ()
  "Return the first non-sidebar window, if one exists."
  (catch 'target-window
    (dolist (window (window-list))
      (unless (window-parameter window 'window-side)
        (throw 'target-window window)))))

(defun my/omd-commands-sidebar-find-command-name (attributes)
  "Extract a command name from ATTRIBUTES, or nil if none exists."
  (cond
   ((string-match "name=\"\\([^\"]+\\)\"" attributes)
    (match-string 1 attributes))
   ((string-match "name=\\([^}[:space:]]+\\)" attributes)
    (match-string 1 attributes))
   (t nil)))

(defun my/omd-commands-sidebar-scan-fallback (root)
  "Return command metadata for ROOT by scanning `*.o.md` files directly."
  (let (entries)
    (dolist (file (directory-files-recursively root "\\.o\\.md\\'"))
      (let (commands)
        (with-temp-buffer
          (insert-file-contents file)
          (goto-char (point-min))
          (while (re-search-forward "^```.*{\\([^}\n]*\\)}" nil t)
            (let ((attributes (match-string 1)))
              (when (string-match-p "\\bmenu=true\\b" attributes)
                (let ((name (my/omd-commands-sidebar-find-command-name attributes)))
                  (when name
                    (setq commands (append commands (list name)))))))))
        (when commands
          (setq entries
                (append entries
                        (list
                         `((file . ,(concat "./" (file-relative-name file root)))
                           (cmds . ,commands))))))))
    entries))

(defun my/omd-commands-sidebar-fetch (root)
  "Return grouped command metadata for ROOT."
(or
   (condition-case nil
       (let ((json-object-type 'alist)
             (json-array-type 'list)
             (json-key-type 'symbol))
         (json-read-from-string
          (my/omd-control-call root '("cmds"))))
     (error nil))
   (my/omd-commands-sidebar-scan-fallback root)))

(defun my/omd-commands-sidebar-render (root)
  "Render the OMD commands sidebar for ROOT in the current buffer."
  (let ((entries (my/omd-commands-sidebar-fetch root))
        (inhibit-read-only t))
    (erase-buffer)
    (setq-local my/omd-commands-sidebar-root root)
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
                         'my/omd-file absolute-file)
             "\n")
            (dolist (command commands)
              (insert
               (propertize (format "  %s" command)
                           'my/omd-file absolute-file
                           'my/omd-command command)
               "\n"))
            (insert "\n")))
      (insert "No OMD commands found.\n"))
    (goto-char (point-min))))

(defun my/omd-commands-sidebar-open-file (file &optional command)
  "Open FILE in the main editing area and optionally jump to COMMAND."
  (let ((target-window (or (my/omd-commands-sidebar-target-window)
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

(defun my/omd-commands-sidebar-visit ()
  "Visit the file or command at point in the OMD commands sidebar."
  (interactive)
  (let ((file (get-text-property (point) 'my/omd-file))
        (command (get-text-property (point) 'my/omd-command)))
    (unless file
      (user-error "Point is not on an OMD commands entry"))
    (my/omd-commands-sidebar-open-file file command)))

(defun my/omd-commands-sidebar-run-command ()
  "Run the OMD command at point asynchronously."
  (interactive)
  (let ((command (get-text-property (point) 'my/omd-command)))
    (unless command
      (user-error "Point is not on an OMD command"))
    (my/omd-command-output-start my/omd-commands-sidebar-root command)))

(defun my/omd-commands-sidebar-refresh ()
  "Refresh the current OMD commands sidebar."
  (interactive)
  (unless my/omd-commands-sidebar-root
    (user-error "Current buffer is not an OMD commands sidebar"))
  (my/omd-commands-sidebar-render my/omd-commands-sidebar-root))

(defun my/omd-commands-sidebar-open (root)
  "Show the OMD commands sidebar for ROOT."
  (let* ((buffer (get-buffer-create my/omd-commands-sidebar-buffer-name))
         (window (or (my/omd-commands-sidebar-window)
                     (display-buffer-in-side-window
                      buffer
                      '((side . right)
                        (slot . 0)
                        (window-width . 36)
                        (preserve-size . (t . nil))
                        (window-parameters . ((no-delete-other-windows . t))))))))
    (with-current-buffer buffer
      (my/omd-commands-sidebar-mode)
      (setq-local default-directory (my/omd-normalize-root root))
      (my/omd-commands-sidebar-render root))
    (set-window-dedicated-p window nil)
    (set-window-buffer window buffer)
    (set-window-parameter window 'my/omd-commands-sidebar t)
    (set-window-dedicated-p window t)
    (with-selected-window window
      (setq-local window-size-fixed 'width)
      (setq-local truncate-lines t))
    window))

(defun my/omd-commands-sidebar-toggle ()
  "Toggle the OMD commands sidebar for the current project."
  (interactive)
  (let* ((root (my/omd-commands-sidebar-project-root))
         (window (my/omd-commands-sidebar-window))
         (sidebar-root
          (and window
               (buffer-local-value 'my/omd-commands-sidebar-root
                                   (window-buffer window)))))
    (if (and window
             sidebar-root
             (string= (expand-file-name sidebar-root)
                      (expand-file-name root)))
        (delete-window window)
      (my/omd-commands-sidebar-open root))))

(global-set-key (kbd "C-c o") #'my/omd-commands-sidebar-toggle)
(defun my/organic-markdown-project-root ()
  "Return the nearest Organic Markdown root used for OMD commands."
  (my/omd-project-root (my/omd-context-directory)))

(defun my/organic-markdown-ref-at-point ()
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

(defun my/organic-markdown-find-origin ()
  "Jump to the file that defines the Organic Markdown reference at point."
  (interactive)
  (let ((name (my/organic-markdown-ref-at-point)))
    (unless name
      (user-error "Point is not on an Organic Markdown reference"))
    (let* ((root (my/organic-markdown-project-root))
           (origin
            (condition-case nil
                (car (split-string
                      (string-trim
                       (my/omd-control-call root (list "origin" name)))
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
                             (format "{[^}\n]*name=%s\\b" (regexp-quote name))
                             nil
                             t)
                        (throw 'match file))))))))
      (unless origin-file
        (user-error "Could not resolve %s" name))
      (find-file origin-file)
      (goto-char (point-min))
      (when (re-search-forward
             (format "{[^}\n]*name=%s\\b" (regexp-quote name))
             nil
             t)
        (beginning-of-line)))))

(defvar my/organic-markdown-navigation-mode-map
  (let ((map (make-sparse-keymap)))
    (define-key map (kbd "C-c @") #'my/organic-markdown-find-origin)
    map)
  "Keymap for Organic Markdown navigation commands.")

(define-minor-mode my/organic-markdown-navigation-mode
  "Minor mode for Organic Markdown navigation helpers."
  :lighter nil
  :keymap my/organic-markdown-navigation-mode-map)

(defun my/organic-markdown-enable-navigation ()
  "Enable Organic Markdown navigation in `*.o.md` buffers."
  (when (and buffer-file-name
             (string-suffix-p ".o.md" buffer-file-name))
    (my/organic-markdown-navigation-mode 1)))

(add-hook 'markdown-mode-hook #'my/organic-markdown-enable-navigation)

(defun my/organic-markdown-block-attributes-at-point ()
  "Return the code block attributes from the current header line, or nil."
  (save-excursion
    (beginning-of-line)
    (when (looking-at "^```[^`\n]*{\\([^}\n]*\\)}")
      (match-string-no-properties 1))))

(defun my/organic-markdown-command-at-point ()
  "Return the runnable Organic Markdown command at point, or nil."
  (let ((attributes (my/organic-markdown-block-attributes-at-point)))
    (when (and attributes
               (string-match-p "\\bmenu=true\\b" attributes))
      (my/omd-commands-sidebar-find-command-name attributes))))

(defun my/organic-markdown-run-command-at-point ()
  "Run the Organic Markdown command declared on the current header line."
  (interactive)
  (let ((command (my/organic-markdown-command-at-point)))
    (unless command
      (user-error "Point is not on a runnable Organic Markdown command header"))
    (my/omd-command-output-start
     (my/organic-markdown-project-root)
     command)))

(defun my/organic-markdown-tangle-project ()
  "Run `omd tangle` for the current Organic Markdown project."
  (interactive)
  (let* ((root (my/organic-markdown-project-root))
         (project-name
          (file-name-nondirectory
           (directory-file-name (expand-file-name root)))))
    (my/omd-command-output-start
     root
     "tangle"
     '("tangle")
     (format "*omd-tangle: %s*" project-name)
     "$ omd tangle\n\n")))

(defun my/organic-markdown-show-command-output ()
  "Jump to the existing output buffer for the command header at point."
  (interactive)
  (let* ((command (my/organic-markdown-command-at-point))
         (buffer (and command (get-buffer (format "*%s*" command)))))
    (unless command
      (user-error "Point is not on a runnable Organic Markdown command header"))
    (unless buffer
      (user-error "No output buffer exists yet for %s" command))
    (pop-to-buffer buffer)))

(defvar my/organic-markdown-actions-mode-map
  (let ((map (make-sparse-keymap)))
    (define-key map (kbd "C-c x") #'my/organic-markdown-run-command-at-point)
    (define-key map (kbd "C-c t") #'my/organic-markdown-tangle-project)
    (define-key map (kbd "C-c z") #'my/organic-markdown-show-command-output)
    map)
  "Keymap for Organic Markdown action commands.")

(define-minor-mode my/organic-markdown-actions-mode
  "Minor mode for Organic Markdown action helpers."
  :lighter nil
  :keymap my/organic-markdown-actions-mode-map)

(defun my/organic-markdown-enable-actions ()
  "Enable Organic Markdown actions in `*.o.md` buffers."
  (when (and buffer-file-name
             (string-suffix-p ".o.md" buffer-file-name))
    (my/organic-markdown-actions-mode 1)))

(add-hook 'markdown-mode-hook #'my/organic-markdown-enable-actions)

(defun my/organic-markdown-reparse-sentinel (process event)
  "Handle completion EVENT for an automatic reparse PROCESS."
  (when (memq (process-status process) '(exit signal))
    (let ((root (process-get process 'my/omd-root))
          (file (process-get process 'my/omd-file)))
      (if (and (eq (process-status process) 'exit)
               (zerop (process-exit-status process)))
          (let ((sidebar (get-buffer my/omd-commands-sidebar-buffer-name)))
            (when (buffer-live-p sidebar)
              (with-current-buffer sidebar
                (when (and my/omd-commands-sidebar-root
                           (string= (my/omd-normalize-root root)
                                    (my/omd-normalize-root
                                     my/omd-commands-sidebar-root)))
                  (my/omd-commands-sidebar-render root)))))
        (message "OMD could not reparse %s: %s"
                 (abbreviate-file-name file)
                 (string-trim event))))))

(defun my/organic-markdown-reparse-after-save ()
  "Asynchronously update the project daemon after saving an `.o.md` file."
  (when (and buffer-file-name
             (string-suffix-p ".o.md" buffer-file-name))
    (let* ((file (expand-file-name buffer-file-name))
           (root (my/omd-project-root (file-name-directory file)))
           (default-directory root)
           (process (make-process
                     :name "omd-reparse"
                     :buffer nil
                     :command (list "omd" "reparse" file)
                     :noquery t
                     :sentinel #'my/organic-markdown-reparse-sentinel)))
      (process-put process 'my/omd-root root)
      (process-put process 'my/omd-file file))))

(defun my/organic-markdown-enable-reparse-on-save ()
  "Enable daemon reparsing after saves in `.o.md` buffers."
  (when (and buffer-file-name
             (string-suffix-p ".o.md" buffer-file-name))
    (add-hook 'after-save-hook
              #'my/organic-markdown-reparse-after-save nil t)))

(add-hook 'markdown-mode-hook #'my/organic-markdown-enable-reparse-on-save)
(with-eval-after-load 'yasnippet
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
    "organic markdown command block"))))

(provide 'organic-markdown)

;;; organic-markdown.el ends here
