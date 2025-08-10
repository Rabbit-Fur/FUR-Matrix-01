/**
 * MATRIX GitHub SDK – Minimal OAuth + REST Helpers (fetch-based)
 * - Authorization Code flow
 * - Auto-injects Accept + X-GitHub-Api-Version headers
 */

export type OAuthConfig = {
  clientId: string;
  redirectUri: string;
  scope?: string; // e.g. "public_repo read:org user:email"
  state?: string;
  allowSignup?: boolean; // default true
};

export function buildAuthUrl(cfg: OAuthConfig) {
  const p = new URLSearchParams({
    client_id: cfg.clientId,
    redirect_uri: cfg.redirectUri,
    scope: cfg.scope ?? "public_repo",
    state: cfg.state ?? crypto.getRandomValues(new Uint32Array(1))[0].toString(16),
    allow_signup: String(cfg.allowSignup ?? true),
  });
  return `https://github.com/login/oauth/authorize?${p.toString()}`;
}

export async function exchangeCodeForToken(
  code: string,
  clientId: string,
  clientSecret: string,
  redirectUri: string
): Promise<string> {
  // NOTE: In Produktion unbedingt serverseitig proxien; Client-Secret nicht im Browser halten!
  const res = await fetch("https://github.com/login/oauth/access_token", {
    method: "POST",
    headers: { Accept: "application/json" },
    body: new URLSearchParams({
      client_id: clientId,
      client_secret: clientSecret,
      code,
      redirect_uri: redirectUri,
    }),
  });
  if (!res.ok) throw new Error(`Token exchange failed: ${res.status}`);
  const data = (await res.json()) as { access_token?: string; error?: string };
  if (!data.access_token) throw new Error(data.error || "No access_token");
  return data.access_token;
}

export type ClientOptions = {
  token: string;
  apiVersion?: string; // default 2022-11-28
  baseUrl?: string; // default https://api.github.com
};

export class GitHubClient {
  private token: string;
  private apiVersion: string;
  private baseUrl: string;

  constructor(opts: ClientOptions) {
    this.token = opts.token;
    this.apiVersion = opts.apiVersion ?? "2022-11-28";
    this.baseUrl = opts.baseUrl ?? "https://api.github.com";
  }

  private async request<T>(path: string, init: RequestInit = {}): Promise<T> {
    const url = path.startsWith("http") ? path : `${this.baseUrl}${path}`;
    const headers: Record<string, string> = {
      Accept: "application/vnd.github+json",
      Authorization: `Bearer ${this.token}`,
      "X-GitHub-Api-Version": this.apiVersion,
    };
    init.headers = { ...headers, ...(init.headers as Record<string, string>) };
    const res = await fetch(url, init);
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`GitHub ${res.status}: ${text}`);
    }
    if (res.status === 204) return undefined as T; // no content
    return (await res.json()) as T;
  }

  // ===== Users =====
  getUser() {
    return this.request<{ login: string; id: number; email?: string }>(`/user`);
  }

  // ===== Contents =====
  getFile(owner: string, repo: string, path: string, ref?: string) {
    const q = ref ? `?ref=${encodeURIComponent(ref)}` : "";
    return this.request<{ content: string; encoding: string; sha: string; path: string }>(
      `/repos/${owner}/${repo}/contents/${encodeURIComponent(path)}${q}`
    );
  }

  putFile(
    owner: string,
    repo: string,
    path: string,
    body: {
      message: string;
      content: string; // base64
      sha?: string;
      branch?: string;
      committer?: { name: string; email: string };
    }
  ) {
    return this.request(`/repos/${owner}/${repo}/contents/${encodeURIComponent(path)}`, {
      method: "PUT",
      body: JSON.stringify(body),
      headers: { "Content-Type": "application/json" },
    });
  }

  // ===== Pull Requests =====
  listPulls(owner: string, repo: string, state: "open" | "closed" | "all" = "open") {
    return this.request(`/repos/${owner}/${repo}/pulls?state=${state}`);
  }

  createPull(
    owner: string,
    repo: string,
    body: { title: string; head: string; base: string; draft?: boolean; body?: string }
  ) {
    return this.request(`/repos/${owner}/${repo}/pulls`, {
      method: "POST",
      body: JSON.stringify(body),
      headers: { "Content-Type": "application/json" },
    });
  }

  mergePull(
    owner: string,
    repo: string,
    pull_number: number,
    body?: { commit_title?: string; commit_message?: string; merge_method?: "merge" | "squash" | "rebase" }
  ) {
    return this.request(`/repos/${owner}/${repo}/pulls/${pull_number}/merge`, {
      method: "PUT",
      body: body ? JSON.stringify(body) : undefined,
      headers: body ? { "Content-Type": "application/json" } : undefined,
    });
  }

  // ===== Commits =====
  listCommits(owner: string, repo: string, sha?: string) {
    const q = sha ? `?sha=${encodeURIComponent(sha)}` : "";
    return this.request(`/repos/${owner}/${repo}/commits${q}`);
  }

  compare(owner: string, repo: string, base: string, head: string) {
    return this.request(`/repos/${owner}/${repo}/compare/${encodeURIComponent(base)}...${encodeURIComponent(head)}`);
  }

  // ===== Issues =====
  listIssues(owner: string, repo: string) {
    return this.request(`/repos/${owner}/${repo}/issues`);
  }

  createIssue(
    owner: string,
    repo: string,
    body: { title: string; body?: string; assignees?: string[] }
  ) {
    return this.request(`/repos/${owner}/${repo}/issues`, {
      method: "POST",
      body: JSON.stringify(body),
      headers: { "Content-Type": "application/json" },
    });
  }
}

// ========= Example usage =========
// const url = buildAuthUrl({ clientId: GITHUB_CLIENT_ID, redirectUri: REDIRECT_URI, scope: "repo read:org user:email" });
// window.location.href = url;
//
// // After redirect: parse ?code=...
// const token = await exchangeCodeForToken(code, GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, REDIRECT_URI);
// const gh = new GitHubClient({ token });
// const me = await gh.getUser();
// console.log(me.login);
