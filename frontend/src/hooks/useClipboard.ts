import { useState, useCallback } from 'react';

interface UseClipboardReturn {
  copy: (text: string) => Promise<boolean>;
  copied: boolean;
  error: string | null;
}

export function useClipboard(timeout: number = 2000): UseClipboardReturn {
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const legacyCopy = (text: string): boolean => {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.setAttribute('readonly', '');
    textarea.style.position = 'fixed';
    textarea.style.top = '0';
    textarea.style.left = '-9999px';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.focus();
    textarea.select();
    textarea.setSelectionRange(0, textarea.value.length);
    let success = false;
    try {
      success = document.execCommand('copy');
    } catch {
      success = false;
    }
    document.body.removeChild(textarea);
    return success;
  };

  const copy = useCallback(async (text: string): Promise<boolean> => {
    if (!text || text.trim() === '') {
      setError('Pas de contenu à copier');
      return false;
    }

    let lastError: string | null = null;

    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
        setCopied(true);
        setError(null);

        setTimeout(() => {
          setCopied(false);
        }, timeout);

        return true;
      }
    } catch (err) {
      lastError = err instanceof Error ? err.message : 'Erreur lors de la copie';
    }

    const legacySuccess = legacyCopy(text);
    if (legacySuccess) {
      setCopied(true);
      setError(null);

      setTimeout(() => {
        setCopied(false);
      }, timeout);

      return true;
    }

    setError(lastError || 'Erreur lors de la copie');
    setCopied(false);
    return false;
  }, [timeout]);

  return { copy, copied, error };
}
