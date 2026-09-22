import {
  useEffect,
  type PropsWithChildren,
} from "react";

import "./base.css";

export type ModalProps = PropsWithChildren<{
  open: boolean;
  title: string;
  onClose: () => void;
  closeLabel?: string;
}>;

export function Modal({
  open,
  title,
  onClose,
  closeLabel = "Close dialog",
  children,
}: ModalProps) {
  useEffect(() => {
    if (!open) {
      return;
    }

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        onClose();
      }
    }

    window.addEventListener("keydown", handleKeyDown);

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [open, onClose]);

  if (!open) {
    return null;
  }

  return (
    <div
      className="base-modal-backdrop"
      role="presentation"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) {
          onClose();
        }
      }}
    >
      <section
        className="base-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="base-modal-title"
      >
        <header className="base-modal__header">
          <h2 id="base-modal-title">{title}</h2>

          <button
            type="button"
            className="base-modal__close"
            onClick={onClose}
            aria-label={closeLabel}
          >
            x
          </button>
        </header>

        <div className="base-modal__content">
          {children}
        </div>
      </section>
    </div>
  );
}
