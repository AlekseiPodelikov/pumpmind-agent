export async function postWebhook(url: string, body: unknown) {
  if (!url) return;
  await fetch(url, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(body) });
}
