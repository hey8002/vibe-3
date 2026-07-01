export type PageKey = "home" | "schedule" | "excel" | "chatbot" | "news";

export type HealthCheckResult = {
  status: "checking" | "ok" | "error";
  message?: string;
  detail?: string;
};
