;;; organic-markdown.el --- Emacs integration for Organic Markdown -*- lexical-binding: t; -*-

;; Install `markdown-mode` and ensure the `omd` executable is on `exec-path`
;; before loading this file.  Yasnippet support is enabled when available.

(require 'cl-lib)

(cl-defstruct my/omd-session
  root
  name
  buffer
  process
  ready
  pending
  current
  queue)

(cl-defstruct my/omd-request
  line
  on-output
  on-complete
  output)

(defconst my/omd-session-prompt "> "
  "Prompt emitted by interactive `omd`.")

(defvar my/omd-control-sessions (make-hash-table :test #'equal)
  "Shared control OMD sessions keyed by normalized project root.")

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

(defvar-local my/omd-command-output-session nil
  "Reusable interactive OMD session dedicated to the current output buffer.")

(defvar-local my/omd-command-output-process nil
  "Fallback one-shot process for the current OMD output buffer.")

(defvar-local my/omd-command-output-backend nil
  "Backend used by the current OMD output buffer.")

(defvar my/omd-command-output-mode-map
  (let ((map (make-sparse-keymap)))
    (set-keymap-parent map special-mode-map)
    (define-key map (kbd "g") #'my/omd-command-output-rerun)
    map)
  "Keymap for OMD command output buffers.")

(define-derived-mode my/omd-command-output-mode special-mode "OMD-Run"
  "Major mode for OMD command output buffers.")

(defun my/omd-project-root (&optional directory)
  "Return the nearest Git project root for DIRECTORY."
  (let* ((directory
          (file-name-as-directory
           (expand-file-name (or directory default-directory))))
         (project-root (locate-dominating-file directory ".git")))
    (or project-root directory)))

(defun my/omd-session-normalize-root (root)
  "Return ROOT as an absolute directory name."
  (file-name-as-directory (expand-file-name root)))

(defun my/omd-session-buffer-name (root name)
  "Return the hidden session buffer name for ROOT and NAME."
  (let ((project-name
         (file-name-nondirectory
          (directory-file-name (my/omd-session-normalize-root root)))))
    (format " *omd-session:%s:%s*" project-name name)))

(defun my/omd-session-log (session text)
  "Append TEXT to SESSION's hidden log buffer."
  (let ((buffer (my/omd-session-buffer session)))
    (when (buffer-live-p buffer)
      (with-current-buffer buffer
        (let ((inhibit-read-only t))
          (goto-char (point-max))
          (insert text))))))

(defun my/omd-session-live-p (session)
  "Return non-nil when SESSION has a live subprocess."
  (and session
       (process-live-p (my/omd-session-process session))))

(defun my/omd-session-create (root name)
  "Create a new reusable OMD session for ROOT labeled NAME."
  (make-my/omd-session
   :root (my/omd-session-normalize-root root)
   :name name
   :buffer nil
   :process nil
   :ready nil
   :pending ""
   :current nil
   :queue nil))

(defun my/omd-session-complete-request (request status detail)
  "Finish REQUEST with STATUS and DETAIL."
  (let ((callback (my/omd-request-on-complete request)))
    (when callback
      (funcall callback
               (my/omd-request-output request)
               status
               detail))))

(defun my/omd-session-flush-output (session text)
  "Deliver TEXT to SESSION's current request."
  (when (> (length text) 0)
    (let ((request (my/omd-session-current session)))
      (when request
        (setf (my/omd-request-output request)
              (concat (my/omd-request-output request) text))
        (let ((callback (my/omd-request-on-output request)))
          (when callback
            (funcall callback text)))))))

(defun my/omd-session-dispatch (session)
  "Send SESSION's next queued request, if possible."
  (when (and (my/omd-session-live-p session)
             (my/omd-session-ready session)
             (null (my/omd-session-current session))
             (my/omd-session-queue session))
    (let ((request (car (my/omd-session-queue session))))
      (setf (my/omd-session-queue session)
            (cdr (my/omd-session-queue session)))
      (setf (my/omd-session-current session) request)
      (setf (my/omd-request-output request) "")
      (process-send-string
       (my/omd-session-process session)
       (concat (my/omd-request-line request) "\n")))))

(defun my/omd-session-consume (session)
  "Consume any complete prompt-delimited output pending in SESSION."
  (let ((prompt-length (length my/omd-session-prompt)))
    (unless (my/omd-session-ready session)
      (when (string-prefix-p my/omd-session-prompt
                             (my/omd-session-pending session))
        (setf (my/omd-session-pending session)
              (substring (my/omd-session-pending session) prompt-length))
        (setf (my/omd-session-ready session) t)
        (my/omd-session-dispatch session)))
    (when (my/omd-session-current session)
      (let* ((pending (my/omd-session-pending session))
             (pending-length (length pending)))
        (cond
         ((and (>= pending-length prompt-length)
               (string= (substring pending (- pending-length prompt-length))
                        my/omd-session-prompt))
          (my/omd-session-flush-output
           session
           (substring pending 0 (- pending-length prompt-length)))
          (setf (my/omd-session-pending session) "")
          (let ((request (my/omd-session-current session)))
            (setf (my/omd-session-current session) nil)
            (my/omd-session-complete-request request 'ok "finished")
            (my/omd-session-dispatch session)))
         ((> pending-length prompt-length)
          (let ((safe-output (substring pending 0 (- pending-length prompt-length))))
            (setf (my/omd-session-pending session)
                  (substring pending (- pending-length prompt-length)))
            (my/omd-session-flush-output session safe-output))))))))

(defun my/omd-session-filter (process output)
  "Handle interactive OMD OUTPUT from PROCESS."
  (let ((session (process-get process 'my/omd-session)))
    (when session
      (my/omd-session-log session output)
      (setf (my/omd-session-pending session)
            (concat (my/omd-session-pending session) output))
      (my/omd-session-consume session))))

(defun my/omd-session-sentinel (process event)
  "Handle PROCESS lifecycle EVENT for an OMD session."
  (let ((session (process-get process 'my/omd-session)))
    (when session
      (my/omd-session-log session (format "\n[%s]\n" (string-trim event)))
      (let ((request (my/omd-session-current session))
            (queued (my/omd-session-queue session))
            (detail (string-trim event)))
        (setf (my/omd-session-process session) nil)
        (setf (my/omd-session-ready session) nil)
        (setf (my/omd-session-pending session) "")
        (setf (my/omd-session-current session) nil)
        (setf (my/omd-session-queue session) nil)
        (when request
          (my/omd-session-complete-request request 'error detail))
        (dolist (queued-request queued)
          (my/omd-session-complete-request queued-request 'error detail))))))

(defun my/omd-session-start (session)
  "Ensure SESSION has a live interactive `omd` subprocess."
  (unless (my/omd-session-live-p session)
    (let* ((root (my/omd-session-root session))
           (buffer (get-buffer-create
                    (my/omd-session-buffer-name root (my/omd-session-name session))))
           (default-directory root)
           (process
            (make-process
             :name (format "omd:%s:%s"
                           (file-name-nondirectory
                            (directory-file-name root))
                           (my/omd-session-name session))
             :buffer buffer
             :command '("omd")
             :coding 'utf-8-unix
             :noquery t
             :connection-type 'pipe
             :filter #'my/omd-session-filter
             :sentinel #'my/omd-session-sentinel)))
      (setf (my/omd-session-buffer session) buffer)
      (setf (my/omd-session-process session) process)
      (setf (my/omd-session-ready session) nil)
      (setf (my/omd-session-pending session) "")
      (setf (my/omd-session-current session) nil)
      (setf (my/omd-session-queue session) nil)
      (process-put process 'my/omd-session session)))
  session)

(defun my/omd-session-stop (session)
  "Stop SESSION and clear its pending state."
  (when session
    (let ((process (my/omd-session-process session)))
      (setf (my/omd-session-current session) nil)
      (setf (my/omd-session-queue session) nil)
      (setf (my/omd-session-pending session) "")
      (setf (my/omd-session-ready session) nil)
      (setf (my/omd-session-process session) nil)
      (when (process-live-p process)
        (delete-process process)))))

(defun my/omd-session-request-line (args)
  "Return a safe interactive command line for ARGS, or nil."
  (when (cl-every (lambda (arg)
                    (and (stringp arg)
                         (> (length arg) 0)
                         (not (string-match-p "[[:space:]]" arg))))
                  args)
    (mapconcat #'identity args " ")))

(defun my/omd-session-send (session line on-complete &optional on-output)
  "Queue LINE in SESSION and install ON-COMPLETE and ON-OUTPUT callbacks."
  (my/omd-session-start session)
  (let ((request (make-my/omd-request
                  :line line
                  :on-output on-output
                  :on-complete on-complete
                  :output "")))
    (setf (my/omd-session-queue session)
          (append (my/omd-session-queue session) (list request)))
    (my/omd-session-dispatch session)
    session))

(defun my/omd-session-call (session line)
  "Synchronously send LINE through SESSION and return its output."
  (let ((done nil)
        (result nil)
        (status nil)
        (detail nil))
    (my/omd-session-send
     session
     line
     (lambda (output request-status request-detail)
       (setq result output)
       (setq status request-status)
       (setq detail request-detail)
       (setq done t)))
    (while (not done)
      (unless (accept-process-output (my/omd-session-process session) 0.1)
        (when (not (my/omd-session-live-p session))
          (setq done t)
          (setq status 'error)
          (setq detail "OMD session exited unexpectedly"))))
    (if (eq status 'ok)
        result
      (error "%s" (or detail "OMD session failed")))))

(defun my/omd-direct-call (root args)
  "Run one direct `omd` call from ROOT with ARGS and return its output."
  (let ((default-directory (my/omd-session-normalize-root root)))
    (with-temp-buffer
      (let ((status (apply #'process-file "omd" nil t nil args))
            (output (buffer-string)))
        (if (zerop status)
            output
          (error "%s"
                 (if (= 0 (length (string-trim output)))
                     "OMD command failed"
                   (string-trim output))))))))

(defun my/omd-control-session (root)
  "Return the shared control session for ROOT."
  (let* ((normalized-root (my/omd-session-normalize-root root))
         (session (gethash normalized-root my/omd-control-sessions)))
    (unless (my/omd-session-live-p session)
      (setq session (my/omd-session-create normalized-root "control"))
      (puthash normalized-root session my/omd-control-sessions))
    session))

(defun my/omd-control-call (root args &optional fresh)
  "Run ARGS from ROOT through OMD.
When FRESH is non-nil, bypass the shared interactive control session."
  (if fresh
      (my/omd-direct-call root args)
    (let ((line (my/omd-session-request-line args)))
      (if line
          (my/omd-session-call (my/omd-control-session root) line)
        (my/omd-direct-call root args)))))

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

(defun my/omd-command-output-session-complete (buffer _output status detail)
  "Append session completion status for BUFFER."
  (when (buffer-live-p buffer)
    (my/omd-command-output-append
     buffer
     (my/omd-command-output-status-line status detail))))

(defun my/omd-command-output-session-chunk (buffer chunk)
  "Append streamed session CHUNK to BUFFER."
  (my/omd-command-output-append buffer chunk))

(defun my/omd-command-output-direct-sentinel (process event)
  "Handle completion EVENT for fallback PROCESS."
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
      (pcase my/omd-command-output-backend
        ('session
         (when my/omd-command-output-session
           (my/omd-session-stop my/omd-command-output-session)))
        ('process
         (when (process-live-p my/omd-command-output-process)
           (delete-process my/omd-command-output-process))))
      (setq-local my/omd-command-output-process nil))))

(defun my/omd-command-output-start-direct (buffer root command args)
  "Run ARGS for COMMAND directly from ROOT, sending output to BUFFER."
  (let ((default-directory (my/omd-session-normalize-root root)))
    (with-current-buffer buffer
      (setq-local my/omd-command-output-backend 'process)
      (setq-local my/omd-command-output-session nil)
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
      (set-process-sentinel process #'my/omd-command-output-direct-sentinel)
      (with-current-buffer buffer
        (setq-local my/omd-command-output-process process)))))

(defun my/omd-command-output-start (root command &optional args buffer-name header)
  "Run COMMAND from ROOT in its dedicated output buffer."
  (let* ((args (or args (list "run" command)))
         (buffer-name (or buffer-name (format "*%s*" command)))
         (header (or header (format "$ omd run %s\n\n" command)))
         (buffer (get-buffer-create buffer-name))
         (line (my/omd-session-request-line args)))
    (my/omd-command-output-stop-active buffer)
    (with-current-buffer buffer
      (my/omd-command-output-mode)
      (setq-local default-directory (my/omd-session-normalize-root root))
      (setq-local my/omd-command-output-root root)
      (setq-local my/omd-command-output-command command)
      (setq-local my/omd-command-output-args args)
      (setq-local my/omd-command-output-buffer-name buffer-name)
      (setq-local my/omd-command-output-header header)
      (let ((inhibit-read-only t))
        (erase-buffer)
        (insert header)))
    (if line
        (let ((session
               (or (and (buffer-live-p buffer)
                        (buffer-local-value 'my/omd-command-output-session buffer))
                   (my/omd-session-create
                    root
                    (format "output:%s" buffer-name)))))
          (with-current-buffer buffer
            (setq-local my/omd-command-output-backend 'session)
            (setq-local my/omd-command-output-session session)
            (setq-local my/omd-command-output-process nil))
          (my/omd-session-send
           session
           line
           (apply-partially #'my/omd-command-output-session-complete buffer)
           (apply-partially #'my/omd-command-output-session-chunk buffer)))
      (my/omd-command-output-start-direct buffer root command args))
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
  (my/omd-project-root default-directory))

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
          (my/omd-control-call root '("cmds") t)))
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
  (my/omd-project-root default-directory))

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
                       (my/omd-control-call root (list "origin" name) t))
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
