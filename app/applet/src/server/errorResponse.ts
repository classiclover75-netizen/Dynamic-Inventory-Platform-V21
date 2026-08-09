export function sendSafeError(
  res: any,
  statusCode: number,
  err: any,
  fallbackMessage: string,
  context: string = ""
): void {
  const logLabel = (typeof context === "string" && context.length > 0) ? context : "Server Error";
  console.error(logLabel, err);

  if (!res || res.headersSent || typeof res.status !== "function") {
    return;
  }

  const errorMessage = (typeof fallbackMessage === "string" && fallbackMessage.length > 0) ? fallbackMessage : "Internal Server Error";
  res.status(statusCode).json({ error: errorMessage });
}
