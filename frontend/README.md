# AM Viewer — Frontend

SvelteKit frontend for AM Viewer.

## Developing

Install dependencies then start the dev server:

```sh
npm install
npm run dev

# or open the app in a new browser tab automatically
npm run dev -- --open
```

The backend (`am_viewer`) must be running separately, or set `AMV_BIN` (see below) to have the frontend manage it.

## Building

```sh
npm run build
```

Preview the production build:

```sh
npm run preview
```

## Configuration

The frontend is configured via environment variables. All variables are read at server startup (SvelteKit SSR / Node adapter).

### Backend process

| Variable | Default | Description |
|---|---|---|
| `AMV_BIN` | _(unset)_ | Path to the `am_viewer` binary. When set, the frontend launches and manages the backend process automatically. When unset, it expects `am_viewer` to already be running. |

### Backend connection

| Variable | Default | Description |
|---|---|---|
| `AMV_BACKEND_HOST` | `localhost` | Hostname of the C++ backend. |
| `AMV_BACKEND_PORT` | `8000` | Port of the C++ backend. |
| `AMV_BACKEND_PROTOCOL` | `http` | Protocol used to reach the backend (`http` or `https`). |

### UI

| Variable | Default | Description |
|---|---|---|
| `AMV_SHOW_POWERBTN` | _(derived)_ | Controls visibility of the power/shutdown button. Set to `1` to always show it, `0` to always hide it. When unset, the button is shown if and only if `AMV_BIN` is set (i.e. the frontend owns the backend process). |
