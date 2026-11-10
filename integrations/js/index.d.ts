export interface RunResult { query: string; exit: number; ok: boolean; task: string | null; output: string; needs_confirmation: boolean; ambiguous: boolean; candidates: string[]; }
export interface Match { name: string; score: number; args: string[]; description: string; }
export interface TaskInfo { name: string; description: string; category: string; usage: string; online: boolean; confirm: boolean; private: boolean; }
export interface Options { command?: string; args?: string[]; timeoutMs?: number; yes?: boolean; timeout?: number; }
export class JeegError extends Error {}
export function run(query: string, opts?: Options): Promise<RunResult>;
export function find(query: string, limit?: number, opts?: Options): Promise<Match[]>;
export function tasks(category?: string, opts?: Options): Promise<TaskInfo[]>;
export function info(name: string, opts?: Options): Promise<TaskInfo>;
export class Http {
  constructor(token: string, base?: string);
  run(query: string, opts?: { yes?: boolean; timeout?: number }): Promise<RunResult>;
  find(query: string, limit?: number): Promise<Match[]>;
  tasks(category?: string): Promise<TaskInfo[]>;
  info(name: string): Promise<TaskInfo>;
  health(): Promise<{ jeeg: string }>;
}
