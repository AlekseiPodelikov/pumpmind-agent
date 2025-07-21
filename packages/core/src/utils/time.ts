export const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));
export const minutes = (n: number) => n * 60_000;
