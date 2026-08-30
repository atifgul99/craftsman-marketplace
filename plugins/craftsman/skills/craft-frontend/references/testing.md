# Testing

> Test design, Testing Library queries, user-event, and MSW policy → craft-testing
> `references/frontend-testing.md` — this file covers only the React Query test harness.

Patterns for testing the React-Query-backed parts of the application layer this skill produces.
The goal is confidence in the query-cache contract, not 100% coverage of incidental wiring.

---

## Contents

- [renderWithClient — React Query wrapper](#renderwithclient--react-query-wrapper)

---

## renderWithClient — React Query wrapper

Components that call `useQuery` or `useMutation` need a `QueryClient` in the tree. Wrap them once
so every test gets an isolated, test-safe client with retries and caching disabled.

```tsx
// test/utils/renderWithClient.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render } from '@testing-library/react';
import type { ReactNode } from 'react';

function makeTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,   // don't hide errors behind retry loops
        gcTime: 0,      // don't cache between tests
      },
      mutations: {
        retry: false,
      },
    },
  });
}

export function renderWithClient(ui: ReactNode) {
  const queryClient = makeTestQueryClient();
  const result = render(
    <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>,
  );
  return { ...result, queryClient };
}
```

Use it everywhere a component touches the query cache:

```tsx
import { screen } from '@testing-library/react';

it('shows the user name', async () => {
  renderWithClient(<UserCard userId="1" />);
  expect(await screen.findByText('Alice')).toBeInTheDocument();
});
```

Key choices:
- `retry: false` — a failing query fails the test immediately instead of retrying three times.
- `gcTime: 0` — the cache is cleared after each test; no state leaks between cases.
- Fresh `QueryClient` per test — tests that call `queryClient.setQueryData` don't bleed into siblings.

Testing loading/error/success states driven by React Query: render with `renderWithClient`, then
assert on the UI transition rather than on internal query state — `findBy*` queries naturally wait
out the loading state, and an injected error response (via the repo's mocking layer, see
craft-testing) drives the error branch. Query design, request mocking, and interaction simulation
are covered in craft-testing's `frontend-testing.md` — this file only owns getting a React-Query
component under test in the first place.

| Pattern | Fix |
| --- | --- |
| `useQuery`/`useMutation` component rendered without a `QueryClientProvider` | Wrap with `renderWithClient` |
| `QueryClient` shared between test cases | Create a fresh client per test — leaking cache invalidates isolation |
| `retry` not set to `false` in test query client | Add `retry: false` so errors surface immediately |
