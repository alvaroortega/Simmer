import { useEffect, useState } from 'react';
import styles from './app.module.css';

type HealthStatus =
  | { state: 'loading' }
  | { state: 'ok'; status: string }
  | { state: 'error'; message: string };

export function App() {
  const [health, setHealth] = useState<HealthStatus>({ state: 'loading' });

  useEffect(() => {
    const controller = new AbortController();

    fetch('/api/health', { signal: controller.signal })
      .then(async (res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const body: { status: string } = await res.json();
        setHealth({ state: 'ok', status: body.status });
      })
      .catch((err: unknown) => {
        if (controller.signal.aborted) return;
        setHealth({
          state: 'error',
          message: err instanceof Error ? err.message : String(err),
        });
      });

    return () => controller.abort();
  }, []);

  return (
    <main className={styles.page}>
      <h1>Simmer</h1>
      <p className={styles.health} data-state={health.state}>
        API:{' '}
        {health.state === 'loading' && 'checking…'}
        {health.state === 'ok' && health.status}
        {health.state === 'error' && `unreachable (${health.message})`}
      </p>
    </main>
  );
}

export default App;
