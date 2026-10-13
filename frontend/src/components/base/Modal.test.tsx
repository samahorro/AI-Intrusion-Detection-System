import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { Modal } from "./Modal";

afterEach(cleanup);

describe("Modal", () => {
  it("does not render a dialog or respond to Escape while closed", () => {
    const onClose = vi.fn();
    render(<Modal open={false} title="Settings" onClose={onClose}>Body</Modal>);

    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    fireEvent.keyDown(window, { key: "Escape" });
    expect(onClose).not.toHaveBeenCalled();
  });

  it("renders an accessible dialog with its title and content", () => {
    render(<Modal open title="Settings" onClose={vi.fn()}>Change your settings</Modal>);

    const dialog = screen.getByRole("dialog", { name: "Settings" });
    expect(dialog).toHaveAttribute("aria-modal", "true");
    expect(screen.getByText("Change your settings")).toBeInTheDocument();
  });

  it("invokes the close handler from the named close button", () => {
    const onClose = vi.fn();
    render(<Modal open title="Settings" closeLabel="Dismiss settings" onClose={onClose}>Body</Modal>);

    fireEvent.click(screen.getByRole("button", { name: "Dismiss settings" }));
    expect(onClose).toHaveBeenCalledOnce();
  });

  it("responds to Escape only while open", () => {
    const onClose = vi.fn();
    const { rerender } = render(<Modal open title="Settings" onClose={onClose}>Body</Modal>);

    fireEvent.keyDown(window, { key: "Escape" });
    expect(onClose).toHaveBeenCalledOnce();

    rerender(<Modal open={false} title="Settings" onClose={onClose}>Body</Modal>);
    fireEvent.keyDown(window, { key: "Escape" });
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it("closes for backdrop clicks but not clicks inside the dialog", () => {
    const onClose = vi.fn();
    render(<Modal open title="Settings" onClose={onClose}>Body</Modal>);

    const dialog = screen.getByRole("dialog", { name: "Settings" });
    fireEvent.mouseDown(dialog);
    expect(onClose).not.toHaveBeenCalled();

    const backdrop = dialog.parentElement;
    expect(backdrop).not.toBeNull();
    fireEvent.mouseDown(backdrop!);
    expect(onClose).toHaveBeenCalledOnce();
  });
});
