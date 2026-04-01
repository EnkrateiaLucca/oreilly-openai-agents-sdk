import { useState, useCallback } from "react";
import { ApiKeyScreen } from "./ApiKeyScreen";
import { Chat } from "./Chat";

const STORAGE_KEY = "openai_api_key";

export default function App() {
  const [apiKey, setApiKey] = useState<string>(
    () => localStorage.getItem(STORAGE_KEY) ?? ""
  );

  const handleSaveKey = useCallback((key: string) => {
    localStorage.setItem(STORAGE_KEY, key);
    setApiKey(key);
  }, []);

  const handleClearKey = useCallback(() => {
    localStorage.removeItem(STORAGE_KEY);
    setApiKey("");
  }, []);

  if (!apiKey) {
    return <ApiKeyScreen onSubmit={handleSaveKey} />;
  }

  return <Chat apiKey={apiKey} onClearKey={handleClearKey} />;
}
