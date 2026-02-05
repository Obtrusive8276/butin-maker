import { useState, useCallback } from 'react';

interface UseClipboardReturn {
  copy: (text: string) => Promise<boolean>;
  copied: boolean;
  error: string | null;
}

export function useClipboard(timeout: number = 2000): UseClipboardReturn {
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const copy = useCallback(async (text: string): Promise<boolean> => {
    if (!text || text.trim() === '') {
      setError('Pas de contenu à copier');
      return false;
    }

    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setError(null);
      
      setTimeout(() => {
        setCopied(false);
      }, timeout);
      
      return true;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erreur lors de la copie';
      setError(errorMessage);
      setCopied(false);
      return false;
    }
  }, [timeout]);

  return { copy, copied, error };
}
