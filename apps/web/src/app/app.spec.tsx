import { render, screen } from '@testing-library/react';

import App from './app';

describe('App', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('shows the API status when the health check succeeds', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ status: 'ok' }), { status: 200 })
      )
    );

    render(<App />);

    expect(await screen.findByText('API: ok')).toBeTruthy();
    expect(fetch).toHaveBeenCalledWith('/api/health', expect.anything());
  });

  it('shows an error when the API is unreachable', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('Failed to fetch')));

    render(<App />);

    expect(
      await screen.findByText('API: unreachable (Failed to fetch)')
    ).toBeTruthy();
  });
});
