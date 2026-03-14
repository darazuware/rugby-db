import type { APIRoute } from 'astro';

export const GET: APIRoute = () => {
  return new Response(
    JSON.stringify({
      status: "error",
      message: "Access denied. Automated collection is prohibited.",
      reason: "Honey pot trap triggered."
    }),
    {
      status: 403,
      headers: {
        'Content-Type': 'application/json'
      }
    }
  );
};
