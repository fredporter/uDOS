export type ThinGuiWindowOptions = {
  title: string;
  targetUrl: string;
  targetLabel?: string;
  width?: number;
  height?: number;
};

export function openThinGuiWindow({
  title,
  targetUrl,
  targetLabel,
  width = 980,
  height = 720,
}: ThinGuiWindowOptions): void {
  if (typeof window === "undefined") return;

  const params = new URLSearchParams({
    title,
    target: targetUrl,
    label: targetLabel || title,
  });
  const popupUrl = `${window.location.origin}${window.location.pathname}#thin-gui?${params.toString()}`;
  const features = [
    `width=${width}`,
    `height=${height}`,
    "menubar=no",
    "toolbar=no",
    "location=no",
    "status=no",
    "resizable=yes",
    "scrollbars=yes",
  ].join(",");
  const popup = window.open(popupUrl, "_blank", features);

  if (!popup) {
    alert(`⚠️ Could not open thin GUI window.\n\nPlease allow popups or open:\n${popupUrl}`);
  }
}
